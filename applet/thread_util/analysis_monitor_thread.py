import multiprocessing
import os
import shutil
import time

from loguru import logger

from applet import common_utils
from applet.ai_service.prediction_score_service import PredictionScoreService
from applet.db import db_utils
from applet.default_config import setting
from applet.obj.Entity import FileInfo, FileTypeEnum
from applet.obj.Entity import FileScanParam
from applet.service.clear_mzml_service import ClearMzmlService
from applet.service.dia.dia_data_save_service import DIADataSaveService
from applet.service.dia.dia_msconvert_service import DIAMSConvertService
from applet.service.dia.dia_notify_service import DIANotifyService
from applet.service.dia.diann_analysis_service import DiannAnalysisService
from applet.service.dia.pic_service import PicService
from applet.service.dia.s3_service import S3Service
from applet.service.dia.s4_service import S4Service
from applet.service.dia.s5_service import S5Service
from applet.service.dia.s6_service import S6Service
from applet.service.file_scan_service import FileScanService
from applet.service.mzxml_build_service import MzxmlService
from applet.thread_util.diann_run_thread import DiannAnalysisThread
from applet.utils import convert_utils
from applet.utils import file_utils

common_config = common_utils.read_yml()


class AnalysisMonitorThread(multiprocessing.Process):
    def __init__(self, diann_path, fragpipe_path, msconvert_path, monitor_config_data_list, scan_time, interval_time,
                 model_dir_path, notify_email, notify_wx_token, fast_mode, conn_send, stop_event):
        # 线程实例化时立即启动
        multiprocessing.Process.__init__(self)
        self.monitor_config_data_list = monitor_config_data_list
        self.model_dir_path = model_dir_path

        self.scan_time = scan_time
        self.interval_time = interval_time
        self.msconvert_path = msconvert_path
        self.diann_path = diann_path
        self.fragpipe_path = fragpipe_path

        self.diann_analysis_thread = None

        # self.run_flag = True
        # self.run_flag = multiprocessing.Event()
        self.run_flag = stop_event
        self.notify_email = notify_email
        self.notify_wx_token = notify_wx_token
        self.fast_mode = fast_mode
        self.conn_send = conn_send

        self.logger = None

    def send_msg(self, msg):
        try:
            self.conn_send.send(msg)
        except Exception:
            pass

    def run(self):
        logger_path = 'logs/idia-qc.log'
        logger.add(logger_path, rotation="50 MB", level="INFO")
        self.logger = logger
        self.logger_path = logger_path
        self.pre_score_service = PredictionScoreService(self.model_dir_path, None, [], logger,
                                                        pub_channel='monitor_log',
                                                        conn_send=self.conn_send)

        self.send_msg(
            'Start thread to monitor, scan time(sec): {}, interval time(min): {}, log path: {}'.format(self.scan_time,
                                                                                                       self.interval_time,
                                                                                                       self.logger_path))
        self.diann_analysis_thread = DiannAnalysisThread(self.diann_path, self.monitor_config_data_list, self.scan_time,
                                                         self.interval_time,
                                                         self.notify_wx_token, self.conn_send, self.run_flag)

        if not self.fast_mode:
            self.diann_analysis_thread.start()

        while not self.run_flag.is_set():
            time.sleep(self.scan_time)
            if self.fast_mode:
                self.diann_analysis_thread.only_run_process()
            else:
                self.only_run_diaqc_process()

        self.send_msg('Stop to monitor')

    def only_run_diaqc_process(self):
        for each_monitor_config in self.monitor_config_data_list:
            if self.run_flag.is_set():
                break
            self.send_msg('Start scan path: {}'.format(each_monitor_config.monitor_dir))
            scan_param = FileScanParam()
            scan_param.source_dir_path = each_monitor_config.monitor_dir
            scan_param.filter_file_name_list = each_monitor_config.filter_file_name
            scan_param.filter_type = each_monitor_config.filter_type
            scan_param.file_filter_size = each_monitor_config.file_filter_size
            scan_param.interval_time = self.interval_time
            scan_param.file_suffix_list = None
            scan_param.raw_file_type = each_monitor_config.raw_file_type
            file_scan_ser = FileScanService(scan_param)
            wait_deal_file = file_scan_ser.recursive_scanning()

            if each_monitor_config.raw_file_type == 'DIA':
                self.run_dia(each_monitor_config, wait_deal_file)

    def run_dia(self, each_monitor_config, wait_deal_file):
        logger = self.logger
        try:
            self.send_msg('There is {} files wait to deal'.format(len(wait_deal_file)))
            if len(wait_deal_file) == 0:
                return
            for index, file_info in enumerate(wait_deal_file):
                file_name = file_info[0]
                file_path = file_info[1]
                try:
                    if self.run_flag.is_set():
                        break
                    analysis_result = self.process_one_file(file_name, file_path, each_monitor_config)
                    if analysis_result is None:
                        continue

                    if not analysis_result:
                        parent_dir_path = os.path.split(each_monitor_config.monitor_dir)[0]
                        error_data_dir = os.path.join(parent_dir_path, 'error_data')
                        if not os.path.exists(error_data_dir):
                            os.mkdir(error_data_dir)
                        error_file_path = os.path.join(error_data_dir, file_name)
                        shutil.move(file_path, error_file_path)
                    else:
                        if setting.delete_success_file == '1':
                            if file_name.endswith('.wiff'):
                                os.remove(file_path)
                                os.remove(file_path + '.scan')
                            elif file_name.endswith('.d'):
                                shutil.rmtree(file_path)
                            else:
                                os.remove(file_path)
                    self.send_msg('Process [{}/{}]'.format(index + 1, len(wait_deal_file)))
                except Exception:
                    self.send_msg('Deal file: {} exception'.format(file_path))
                    logger.exception('deal file: {} exception'.format(file_path))
                    parent_dir_path = os.path.split(each_monitor_config.monitor_dir)[0]
                    error_data_dir = os.path.join(parent_dir_path, 'error_data')
                    if not os.path.exists(error_data_dir):
                        os.mkdir(error_data_dir)
                    error_file_path = os.path.join(error_data_dir, file_name)
                    shutil.move(file_path, error_file_path)
            self.delete_temp_file(each_monitor_config)
        except Exception:
            logger.exception('Monitor exception')
            self.send_msg('Monitor exception')

    def delete_temp_file(self, each_monitor_config):
        logger = self.logger
        logger.info('Start clear temp mzXML file.')
        temp_mzml_dir = os.path.join(each_monitor_config.output_dir, 'mzXML')
        if os.path.exists(temp_mzml_dir):
            shutil.rmtree(temp_mzml_dir)
        logger.info('Clear temp mzXML file over.')

    def check_wait_deal_file(self, file_list):
        wait_deal_file = []
        for file_info in file_list:
            file_name = file_info[0]
            file_abs_path = file_info[1]
            out_time_limit = file_utils.is_file_modified_days_out_minute(file_abs_path, self.interval_time)
            if not out_time_limit:
                continue
            thiz_file_size = file_utils.get_file_size(file_abs_path)
            thiz_file_mtime = file_utils.get_file_mtime(file_abs_path)

            exist_file_info = db_utils.query_run_info_by_file_name(file_name, 1)
            if exist_file_info:
                if thiz_file_size is None or thiz_file_mtime is None:
                    continue
                if exist_file_info.file_size == thiz_file_size and exist_file_info.last_modify_time == thiz_file_mtime:
                    continue
            wait_deal_file.append(file_info)
        return wait_deal_file

    def process_one_file(self, file_name, file_abs_path, each_monitor_config):
        self.send_msg('Start deal DIA file {}'.format(file_abs_path))

        thiz_file_size = file_utils.get_file_size(file_abs_path)
        thiz_file_mtime = file_utils.get_file_mtime(file_abs_path)
        choose_file_list = self.build_file_list(file_name, file_abs_path, thiz_file_size, thiz_file_mtime,
                                                each_monitor_config)

        file_info = choose_file_list[0]
        diann_out_path = os.path.join(each_monitor_config.output_dir, setting.output_dir_s2)
        diann_result_out_path = os.path.join(diann_out_path, setting.output_dir_s2 + '_result')

        diann_result_file_name = '{}_mainoutput.tsv'.format(file_info.base_file_name)
        file_info.diann_result_file_name = diann_result_file_name

        file_info.diann_result_file_path = os.path.join(diann_result_out_path, file_info.diann_result_file_name)
        file_info.diann_result_stats_file_path = os.path.join(diann_result_out_path, '{}_mainoutput.stats.tsv'.format(
            file_info.base_file_name))
        if not os.path.exists(file_info.diann_result_file_path) or not os.path.exists(
                file_info.diann_result_stats_file_path):
            return None

        msconvert_service = DIAMSConvertService(self.msconvert_path, each_monitor_config.output_dir, choose_file_list,
                                                self.logger,
                                                pub_channel='monitor_log', conn_send=self.conn_send)
        all_convert = msconvert_service.deal_process()
        if not all_convert:
            self.send_msg('MSConvert file error, skip. {}'.format(file_abs_path))
            return False
        if self.run_flag.is_set():
            return False
        diann_service = DiannAnalysisService(self.diann_path, each_monitor_config.output_dir, choose_file_list,
                                             self.logger,
                                             pub_channel='monitor_log', lib_path=each_monitor_config.lib_path,
                                             conn_send=self.conn_send, run_cmd=False)
        diann_run_result = diann_service.deal_process()
        if self.run_flag.is_set():
            return False
        if not diann_run_result:
            self.send_msg('DIA-NN run error, skip. {}'.format(file_abs_path))
            # diann_service.send_msg(3, 'DIA-NN run error, skip. {}'.format(file_abs_path))
            return False
        mzxml_build_service = MzxmlService(each_monitor_config.inst_name, each_monitor_config.run_prefix,
                                           each_monitor_config.output_dir, choose_file_list,
                                           self.logger,
                                           pub_channel='monitor_log', conn_send=self.conn_send)
        mzxml_build_service.deal_process()
        if self.run_flag.is_set():
            return False

        s3_deal_service = S3Service(each_monitor_config.output_dir,
                                    os.path.join(each_monitor_config.output_dir, setting.output_dir_s3),
                                    choose_file_list, self.logger, pub_channel='monitor_log', conn_send=self.conn_send)
        s3_result = s3_deal_service.deal_process()
        if not s3_result:
            self.send_msg('S3 error, skip. {}'.format(file_abs_path))
            # s3_deal_service.send_msg(9, 'S3 error, skip. {}'.format(file_abs_path))
            return False
        if self.run_flag.is_set():
            return False
        s4_deal_service = S4Service(each_monitor_config.output_dir,
                                    os.path.join(each_monitor_config.output_dir, setting.output_dir_s4),
                                    os.path.join(each_monitor_config.output_dir, setting.output_dir_s4,
                                                 setting.output_file_S4_result), choose_file_list, self.logger,
                                    pub_channel='monitor_log', conn_send=self.conn_send)
        s4_result = s4_deal_service.deal_process()
        if not s4_result:
            self.send_msg('S4 error, skip. {}'.format(file_abs_path))
            # s4_deal_service.send_msg(3, msg='S4 error, skip. {}'.format(file_abs_path))
            return False
        if self.run_flag.is_set():
            return False
        s5_deal_service = S5Service(each_monitor_config.output_dir, setting.output_dir_s5,
                                    setting.output_file_S5_ms1_chazi,
                                    os.path.join(each_monitor_config.output_dir, setting.output_dir_s4,
                                                 setting.output_file_S4_result),
                                    choose_file_list, self.logger, pub_channel='monitor_log', conn_send=self.conn_send)
        s5_result = s5_deal_service.deal_process()
        if not s5_result:
            self.send_msg('S5 error, skip. {}'.format(file_abs_path))
            # s5_deal_service.send_msg(3, msg='S5 error, skip. {}'.format(file_abs_path))
            return False
        if self.run_flag.is_set():
            return False

        s6_deal_service = S6Service(each_monitor_config.output_dir,
                                    setting.output_dir_s6, setting.output_file_S6_ms1_chazi,
                                    setting.output_file_S6_ms2_chazi,
                                    setting.output_file_S6_ms1_org_area, setting.output_file_S6_ms2_org_area,
                                    setting.output_file_S6_ms1_under_chazi, setting.output_file_S6_ms2_under_chazi,
                                    os.path.join(each_monitor_config.output_dir, setting.output_dir_s4,
                                                 setting.output_file_S4_result),
                                    choose_file_list, self.logger, pub_channel='monitor_log', conn_send=self.conn_send)
        s6_result = s6_deal_service.deal_process()
        if not s6_result:
            self.send_msg('S6 error, skip. {}'.format(file_abs_path))
            # s6_deal_service.send_msg(3, msg='S6 error, skip. {}'.format(file_abs_path))
            return False
        if self.run_flag.is_set():
            return False

        self.clear_service = ClearMzmlService(each_monitor_config.output_dir, choose_file_list, self.logger,
                                              pub_channel='monitor_log', conn_send=self.conn_send)
        self.clear_service.deal_process()

        data_save_deal_service = DIADataSaveService(1, each_monitor_config.output_dir,
                                                    os.path.join(each_monitor_config.output_dir,
                                                                 setting.output_dir_s3),
                                                    os.path.join(each_monitor_config.output_dir,
                                                                 setting.output_dir_s7),
                                                    choose_file_list, self.logger, pub_channel='monitor_log',
                                                    conn_send=self.conn_send)
        data_save_deal_service.f4_file_path = s6_deal_service.ms1_chazi_file_path
        data_save_deal_service.f8_file_path = s6_deal_service.ms1_org_area_file_path
        data_save_deal_service.f11_file_path = s6_deal_service.ms2_org_area_file_path
        delete_run_info, save_data_list, diann_data_list = data_save_deal_service.build_save_data()

        pred_info_list = self.pre_score_service.deal_prediction_score(save_data_list)

        save_result = data_save_deal_service.deal_data_save(delete_run_info, save_data_list, pred_info_list,
                                                            diann_data_list)
        if not save_result:
            self.send_msg('Save data error, skip. {}'.format(file_abs_path))
            # data_save_deal_service.send_msg(3, msg='Save data error, skip. {}'.format(file_abs_path))
        if self.run_flag.is_set():
            return False
        pic_dir_path = os.path.join(each_monitor_config.output_dir, 'pic')
        if not os.path.exists(pic_dir_path):
            os.mkdir(pic_dir_path)
        pic_deal_service = PicService(each_monitor_config.output_dir, None, self.logger, pub_channel='monitor_log',
                                      conn_send=self.conn_send)
        draw_result = pic_deal_service.draw_pic_all(1, draw_run_prefix=each_monitor_config.run_prefix)
        if not draw_result:
            self.send_msg('Draw result error, skip. {}'.format(file_abs_path))

        self.send_msg('Start save to csv')
        self.pre_score_service.save_to_csv(each_monitor_config.output_dir, 1, each_monitor_config.run_prefix)
        self.send_msg('End deal file {}'.format(file_abs_path))

        notify_service = DIANotifyService(self.notify_email, self.notify_wx_token, each_monitor_config.output_dir,
                                          None, self.logger,
                                          pub_channel='monitor_log', conn_send=self.conn_send)
        notify_service.deal_send_by_run_prefix(each_monitor_config.run_prefix)
        return True

    def build_file_list(self, file_name, file_abs_path, thiz_file_size, thiz_file_mtime, each_monitor_config) -> [
        FileInfo]:
        if file_name.endswith('.RAW') or file_name.endswith('.raw'):
            file_type = FileTypeEnum.RAW
        elif file_name.endswith('.WIFF') or file_name.endswith('.wiff'):
            file_type = FileTypeEnum.WIFF
        elif file_name.endswith('.d') or file_name.endswith('.D'):
            file_type = FileTypeEnum.D
        else:
            return None
        file_info = FileInfo()

        file_info.file_type = file_type
        file_info.file_path = file_abs_path
        file_info.file_name = convert_utils.convert_to_file_name(file_info.file_path)
        convert_utils.convert_to_mzXML_name(file_info)
        file_info.file_size = thiz_file_size
        file_info.last_modify_time = thiz_file_mtime

        file_info.inst_name = each_monitor_config.inst_name
        file_info.run_prefix = each_monitor_config.run_prefix
        file_info.run_name = file_info.mzXML_file_name.replace('.mzXML', '')

        file_info.run_id = self.build_run_id(each_monitor_config.run_prefix)

        return [file_info]

    def build_run_id(self, run_prefix):
        max_increase_id = db_utils.query_max_run_increase_id(run_prefix)
        if max_increase_id is None:
            max_increase_id = 0
            db_utils.insert_run_increase_id(run_prefix, 0)

        thiz_increase_id = max_increase_id + 1
        run_id = '%sU%04d' % (run_prefix, thiz_increase_id)
        # 更新回数据库
        db_utils.update_run_increase_id(run_prefix, thiz_increase_id)
        return run_id
