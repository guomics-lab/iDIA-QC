import os.path
import os.path
import shutil
import time
import multiprocessing
# from threading import Thread

from loguru import logger
import pandas as pd

from applet.db import db_utils_run_data
from applet.default_config import setting
from applet.obj.DBEntity import DIAOutputInfo
from applet.obj.Entity import FileInfo
from applet.obj.Entity import FileScanParam
from applet.obj.Entity import FileTypeEnum
from applet.service.dia.dia_base_notify_service import DIABaseNotifyService
from applet.service.dia.diann_analysis_service import DiannAnalysisService
from applet.service.file_scan_service import FileScanService
from applet.utils import convert_utils


class DiannAnalysisThread(multiprocessing.Process):
    def __init__(self, diann_path, monitor_config_data_list, scan_time, interval_time, notify_wx_token,
                 conn_send, run_flag):
        #
        super().__init__()
        self.daemon = True

        self.diann_path = diann_path
        self.monitor_config_data_list = monitor_config_data_list
        self.interval_time = interval_time
        self.scan_time = scan_time
        self.notify_wx_token = notify_wx_token

        self.conn_send = conn_send

        self.run_flag = run_flag

    def stop(self):
        pass

    def send_msg(self, msg):
        self.conn_send.send(msg)
        pass

    def run(self):
        logger.add('logs/diann.log', rotation="10 MB", level="INFO")
        while not self.run_flag.is_set():
            self.only_run_process()
            time.sleep(self.scan_time)

    def only_run_process(self):
        for each_monitor_config in self.monitor_config_data_list:
            if self.run_flag.is_set():
                break
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

        try:
            #
            logger.info('There is {} DIA files wait to deal'.format(len(wait_deal_file)))
            if len(wait_deal_file) == 0:
                return
            for index, file_info in enumerate(wait_deal_file):
                file_name = file_info[0]
                file_path = file_info[1]
                try:
                    if self.run_flag.is_set():
                        break
                    analysis_result = self.process_one_file(file_name, file_path, each_monitor_config)


                    if not analysis_result:
                        parent_dir_path = os.path.split(each_monitor_config.monitor_dir)[0]
                        error_data_dir = os.path.join(parent_dir_path, 'error_data')
                        if not os.path.exists(error_data_dir):
                            os.mkdir(error_data_dir)
                        error_file_path = os.path.join(error_data_dir, file_name)
                        shutil.move(file_path, error_file_path)
                    self.send_msg('Process [{}/{}]'.format(index + 1, len(wait_deal_file)))
                except Exception:
                    self.send_msg('Deal file: {} exception'.format(file_path))
                    logger.exception('deal file: {} exception'.format(file_path))

        except Exception:
            logger.exception('Monitor exception')
            self.send_msg('Monitor exception')

    def process_one_file(self, file_name, file_abs_path, each_monitor_config):
        logger.info('Start deal DIA file {}'.format(file_abs_path))

        choose_file_list = self.build_file_list(file_name, file_abs_path,
                                                each_monitor_config)
        file_info = choose_file_list[0]
        diann_out_path = os.path.join(each_monitor_config.output_dir, setting.output_dir_s2)
        diann_result_out_path = os.path.join(diann_out_path, setting.output_dir_s2 + '_result')

        diann_result_file_name = '{}_mainoutput.tsv'.format(file_info.base_file_name)
        file_info.diann_result_file_name = diann_result_file_name

        file_info.diann_result_file_path = os.path.join(diann_result_out_path, file_info.diann_result_file_name)
        file_info.diann_result_stats_file_path = os.path.join(diann_result_out_path, '{}_mainoutput.stats.tsv'.format(
            file_info.base_file_name))
        if db_utils_run_data.query_diann_data_exist(5, file_info.file_name):
            return True

        diann_service = DiannAnalysisService(self.diann_path, each_monitor_config.output_dir, choose_file_list,
                                             logger,
                                             pub_channel=None, lib_path=each_monitor_config.lib_path,
                                             conn_send=self.conn_send, run_cmd=True)
        diann_run_result = diann_service.deal_process()
        if self.run_flag.is_set():
            return False
        if not diann_run_result:
            self.send_msg('DIA-NN run error, skip. {}'.format(file_abs_path))
            return False

        diann_data_list = []
        diann_output_df = pd.read_csv(file_info.diann_result_stats_file_path, sep='\t')
        row_data = diann_output_df.iloc[0]
        diann_data = DIAOutputInfo()
        diann_data.seq_id = ''
        diann_data.file_name = file_info.file_name
        diann_data.data_source = 5
        diann_data.precursor_ident = int(row_data['Precursors.Identified'])
        diann_data.protein_ident = int(row_data['Proteins.Identified'])
        diann_data.total_quantity = int(row_data['Total.Quantity'])
        diann_data.ms1_signal = int(row_data['MS1.Signal'])
        diann_data.ms2_signal = int(row_data['MS2.Signal'])
        diann_data.fwhm_scans = float(row_data['FWHM.Scans'])
        diann_data.fwhm_rt = float(row_data['FWHM.RT'])
        diann_data.acc_ms1 = float(row_data['Median.Mass.Acc.MS1'])
        diann_data.acc_ms1_corr = float(row_data['Median.Mass.Acc.MS1.Corrected'])
        diann_data.acc_ms2 = float(row_data['Median.Mass.Acc.MS2'])
        diann_data.acc_ms2_corr = float(row_data['Median.Mass.Acc.MS2.Corrected'])
        diann_data.ms2_instability = float(row_data['MS2.Mass.Instability'])
        diann_data.run_prefix = file_info.run_prefix
        #
        diann_data_list.append(diann_data)

        db_utils_run_data.save_diann_data(diann_data_list)

        base_notify_service = DIABaseNotifyService(each_monitor_config.output_dir, self.notify_wx_token,
                                                   each_monitor_config.run_prefix, logger,
                                                   pub_channel='monitor_log', conn_send=self.conn_send)
        base_notify_service.deal_send_by_run_prefix(each_monitor_config.run_prefix)

        data_source = 5
        run_prefix = file_info.run_prefix
        diann_info_list = db_utils_run_data.query_all_diann_data(data_source, run_prefix=run_prefix)
        save_df = pd.DataFrame(diann_info_list)
        for name, group in save_df.groupby('run_prefix'):
            group.to_csv(os.path.join(os.path.split(each_monitor_config.output_dir)[0], f'{name}_diann_mainoutput.stats.tsv.csv'),
                         mode='w+', index=False)

        return True

    def build_file_list(self, file_name, file_abs_path, each_monitor_config) -> [
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

        file_info.inst_name = each_monitor_config.inst_name
        file_info.run_prefix = each_monitor_config.run_prefix
        file_info.run_name = file_info.mzXML_file_name.replace('.mzXML', '')

        return [file_info]
