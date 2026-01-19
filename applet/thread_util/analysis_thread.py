import json
import os.path
import shutil
import threading
import time
from threading import Thread

from loguru import logger
from pubsub import pub

from applet.ai_service.prediction_score_service import PredictionScoreService
from applet.default_config import setting
from applet.obj.Entity import FileInfo
from applet.obj.Msg import AnalysisInfoMsg
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
from applet.service.file_init_service import FileInitService
from applet.service.mzxml_build_service import MzxmlService


class AnalysisThread(Thread):
    def __init__(self, diann_path, msconvert_path, output_path, inst_name, run_prefix, choose_file_list: [FileInfo],
                 raw_file_type,
                 notify_email, notify_wx_token,
                 model_dir_path='./resource/model/unisplit'):
        Thread.__init__(self)
        self.diann_path = diann_path
        self.msconvert_path = msconvert_path
        self.output_path = output_path
        self.choose_file_list = choose_file_list

        self.raw_file_type = raw_file_type
        self.run_flag = True
        self.notify_email = notify_email
        self.notify_wx_token = notify_wx_token

        self.inst_name = inst_name
        self.run_prefix = run_prefix
        self.model_dir_path = model_dir_path

    def init_service_dia(self, start_time):
        self.file_init_service = FileInitService(self.output_path, self.inst_name, self.run_prefix,
                                                 self.choose_file_list, self.logger,
                                                 start_time=start_time)
        self.msconvert_service = DIAMSConvertService(self.msconvert_path, self.output_path, self.choose_file_list,
                                                     self.logger, start_time=start_time)
        self.diann_analysis_service = DiannAnalysisService(self.diann_path, self.output_path,
                                                           self.choose_file_list, self.logger, start_time=start_time)
        self.mzxml_build_service = MzxmlService(self.inst_name, self.run_prefix, self.output_path,
                                                self.choose_file_list, self.logger, start_time=start_time)

        self.s3_deal_service = S3Service(self.output_path, os.path.join(self.output_path, setting.output_dir_s3),
                                         self.choose_file_list, self.logger, start_time=start_time)
        self.s4_deal_service = S4Service(self.output_path, os.path.join(self.output_path, setting.output_dir_s4),
                                         os.path.join(self.output_path, setting.output_dir_s4,
                                                      setting.output_file_S4_result), self.choose_file_list,
                                         self.logger, start_time=start_time)
        self.s5_deal_service = S5Service(self.output_path, setting.output_dir_s5, setting.output_file_S5_ms1_chazi,
                                         os.path.join(self.output_path, setting.output_dir_s4,
                                                      setting.output_file_S4_result),
                                         self.choose_file_list, self.logger, start_time=start_time)
        self.s6_deal_service = S6Service(self.output_path,
                                         setting.output_dir_s6, setting.output_file_S6_ms1_chazi,
                                         setting.output_file_S6_ms2_chazi,
                                         setting.output_file_S6_ms1_org_area, setting.output_file_S6_ms2_org_area,
                                         setting.output_file_S6_ms1_under_chazi, setting.output_file_S6_ms2_under_chazi,
                                         os.path.join(self.output_path, setting.output_dir_s4,
                                                      setting.output_file_S4_result),
                                         self.choose_file_list, self.logger, start_time=start_time)

        self.clear_service = ClearMzmlService(self.output_path, self.choose_file_list, self.logger,
                                              start_time=start_time)

        self.data_save_deal_service = DIADataSaveService(0, self.output_path,
                                                         os.path.join(self.output_path, setting.output_dir_s3),
                                                         os.path.join(self.output_path, setting.output_dir_s7),
                                                         self.choose_file_list, self.logger, start_time=start_time)

        self.pic_deal_service = PicService(self.output_path, None, self.logger, start_time=start_time)
        self.pre_score_service = PredictionScoreService(self.model_dir_path, self.output_path, self.choose_file_list,
                                                        self.logger, start_time=start_time)

        self.dia_notify_service = DIANotifyService(self.notify_email, self.notify_wx_token, self.output_path,
                                                   self.choose_file_list,
                                                   self.logger, start_time=start_time)

        self.service_list = [self.file_init_service, self.msconvert_service,
                             self.diann_analysis_service, self.mzxml_build_service,
                             self.s3_deal_service, self.s4_deal_service, self.s5_deal_service, self.s6_deal_service,
                             self.clear_service]

    def set_run_flag(self, run_flag):
        self.run_flag = run_flag
        self.msconvert_service.run_flag = run_flag
        self.diann_analysis_service.run_flag = run_flag
        self.mzxml_build_service.run_flag = run_flag
        self.s3_deal_service.run_flag = run_flag
        self.s4_deal_service.run_flag = run_flag
        self.s5_deal_service.run_flag = run_flag
        self.s6_deal_service.run_flag = run_flag
        self.data_save_deal_service.run_flag = run_flag

    def run(self):
        thread_id = threading.get_ident()
        thread_logger = logger.bind(thread_id=thread_id)

        os.makedirs(self.output_path, exist_ok=True)
        self.logger_path = os.path.join(self.output_path, 'idia-qc-analysis.log')
        file_handler_id = thread_logger.add(self.logger_path, level="INFO",
                                            filter=lambda record: record["extra"].get("thread_id") == thread_id)
        self.logger = thread_logger
        # logger = self.logger
        start_time = time.time()

        if self.raw_file_type == 'DIA':
            self.init_service_dia(start_time)
            run_result_flag = self.run_dia(thread_logger, start_time)
            if not run_result_flag:
                return False

        info_msg = AnalysisInfoMsg(12, 9, 'Log saved to {}'.format(self.logger_path))
        pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))

        info_msg = AnalysisInfoMsg(12, 99, 'Finished')
        pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))

        info_msg = AnalysisInfoMsg(12, 9,
                                   '\n\nPlease cite:\n(iDIAQC) iDIA-QC: AI-empowered Data-Independent Acquisition Mass Spectrometry-based Quality Control\n(DIA-NN) MSFragger: ultrafast and comprehensive peptide identification in mass spectrometry–based proteomics. Nat Methods 14:513 (2017)\n(Msconvert) Fast deisotoping algorithm and its implementation in the MSFragger search engine. J. Proteome Res. 20:498 (2021)')
        pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))

        now_time = time.time()
        minutes, seconds = divmod(now_time - start_time, 60)
        minutes = int(minutes)
        seconds = int(seconds)
        info_msg = AnalysisInfoMsg(12, 9,
                                   '=================ALL JOBS DONE IN {}.{} MINUTES========='.format(minutes, seconds))
        pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))

        self.delete_temp_file()
        thread_logger.remove(file_handler_id)

    def run_dia(self, thread_logger, start_time):
        try:
            thread_logger.info('*****************Start analysis*********************')
            info_msg = AnalysisInfoMsg(0, 0, '')
            pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))

            for step, this_service in enumerate(self.service_list):
                result_flag = this_service.deal_process()
                if not self.run_flag:
                    info_msg = AnalysisInfoMsg(step, 2, 'Stop analysis')
                    pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))
                    return False

                if not result_flag:
                    thread_logger.error('process deal error')
                    info_msg = AnalysisInfoMsg(step, 3, 'Analysis deal error')
                    pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))
                    return False

            self.data_save_deal_service.f4_file_path = self.s6_deal_service.ms1_chazi_file_path
            self.data_save_deal_service.f8_file_path = self.s6_deal_service.ms1_org_area_file_path
            self.data_save_deal_service.f11_file_path = self.s6_deal_service.ms2_org_area_file_path

            delete_run_info, save_data_list, diann_data_list = self.data_save_deal_service.build_save_data()

            save_pred_info_list = self.pre_score_service.deal_prediction_score(save_data_list)

            save_result = self.data_save_deal_service.deal_data_save(delete_run_info, save_data_list,
                                                                     save_pred_info_list, diann_data_list)
            thread_logger.info('Data save success')
            info_msg = AnalysisInfoMsg(9, 1, '')
            pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))

            if not save_result:
                info_msg = AnalysisInfoMsg(9, 3, 'Save data error, stop')
                pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))
                return False

            self.pre_score_service.save_to_csv(self.output_path, 0)

            draw_result = self.pic_deal_service.draw_pic_all(0)
            if not draw_result:
                info_msg = AnalysisInfoMsg(11, 3, 'Draw pic error, stop')
                pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))
                return False
            thread_logger.info('End draw pic')

            self.dia_notify_service.deal_process()

            thread_logger.info('-----end analysis------')
            return True
        except Exception as e:
            thread_logger.exception('deal analysis exception')
            info_msg = AnalysisInfoMsg(0, 3, 'Deal analysis Exception: {}'.format(e))
            pub.sendMessage('analysis_info', msg=json.dumps(info_msg.__dict__))
            return False

    def delete_temp_file(self):
        thread_logger = self.logger
        thread_logger.info('Start clear temp mzXML file.')
        temp_mzml_dir = os.path.join(self.output_path, 'mzXML')
        shutil.rmtree(temp_mzml_dir)
        thread_logger.info('Clear temp mzXML file over.')
