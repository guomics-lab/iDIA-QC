# coding:utf-8
"""This module is for mzxml msconvert"""

import os
import shutil
import subprocess
import time
from applet import common_utils

from applet.default_config import setting
from applet.obj.Entity import FileInfo, FileTypeEnum
from applet.service import common_service


common_config = common_utils.read_yml()

diann_thread = common_config['diann']['thread']

class DiannAnalysisService(common_service.CommonService):
    def __init__(self, diann_path, base_output_path, file_list: [FileInfo], logger, step=3,
                 pub_channel='analysis_info', start_time=0, lib_path=None, conn_send=None, run_cmd=True):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time, conn_send=conn_send)
        self.diann_path = diann_path
        self.lib_path = lib_path
        self.run_cmd = run_cmd

    #
    def deal_process(self):
        logger = self.logger
        try:
            self.is_running = True
            self.send_msg(0, msg='')
            if len(self.file_list) == 0:
                self.send_msg(3, 'File count is zero, stop')
                return False
            diann_out_path = os.path.join(self.base_output_path, setting.output_dir_s2)
            diann_temp_out_path = os.path.join(diann_out_path, setting.output_dir_s2 + '_temp')
            diann_result_out_path = os.path.join(diann_out_path, setting.output_dir_s2 + '_result')
            logger.info('start diann, file count is: {}'.format(len(self.file_list)))
            if not os.path.exists(diann_out_path):
                os.mkdir(diann_out_path)
            if not os.path.exists(diann_temp_out_path):
                os.mkdir(diann_temp_out_path)
            if not os.path.exists(diann_result_out_path):
                os.mkdir(diann_result_out_path)
            deal_count = 0
            for file_info in self.file_list:
                if not self.run_flag:
                    self.send_msg(2, 'Click stop')
                    return False
                #
                diann_temp_file_out_path = diann_temp_out_path
                if not os.path.exists(diann_temp_file_out_path):
                    os.mkdir(diann_temp_file_out_path)

                diann_temp_file_path = os.path.join(diann_temp_file_out_path,
                                                    file_info.base_file_name + '_mainoutput.tsv')
                file_info.diann_temp_file_path = diann_temp_file_path
                diann_temp_stats_file_path = os.path.join(diann_temp_file_out_path,
                                                          file_info.base_file_name + '_mainoutput.stats.tsv')
                file_info.diann_temp_stats_file_path = diann_temp_stats_file_path
                file_info.diann_result_stats_file_path = os.path.join(diann_result_out_path,
                                                                      file_info.base_file_name + '_mainoutput.stats.tsv')

                file_info.diann_result_file_name = file_info.base_file_name + '_mainoutput.tsv'
                file_info.diann_result_file_path = os.path.join(diann_result_out_path, file_info.diann_result_file_name)

                file_info.main_file_relative_path = '{}/{}_result/{}_mainoutput.tsv'. \
                    format(setting.output_dir_s2, setting.output_dir_s2, file_info.base_file_name)
                file_info.stats_file_relative_path = '{}/{}_result/{}_mainoutput.stats.tsv'. \
                    format(setting.output_dir_s2, setting.output_dir_s2, file_info.base_file_name)

                if not self.run_cmd:
                    continue
                ts1 = time.time()
                self.deal_one_diann(file_info)
                ts2 = time.time()
                logger.info('diann_time, file: {}, run_prefix: {}, speed_time: {}, '.format(file_info.file_name, file_info.run_prefix, ts2 - ts1))
                deal_count += 1
                logger.info(
                    'end diann analysis one, {}/{}'.format(file_info.file_name, deal_count, len(self.file_list)))
                if os.path.exists(file_info.diann_temp_file_path):
                    #
                    logger.info('copy result file, diann_temp_file_path is: {}, target file path is: {}'.format(
                        file_info.diann_temp_file_path, file_info.diann_result_file_path))
                    # os.system(result_file_mv_cmd)
                    shutil.copyfile(file_info.diann_temp_file_path, file_info.diann_result_file_path)

                    logger.info('copy stats file, diann_temp_stats_file_path is: {}, target file path is: {}'.format(
                        file_info.diann_temp_stats_file_path, file_info.diann_result_stats_file_path))
                    shutil.copyfile(file_info.diann_temp_stats_file_path, file_info.diann_result_stats_file_path)
                    continue
                else:
                    logger.error(
                        'diann error, result file is not exist, file name is: {}, temp file path is: {}'.format(
                            file_info.file_name, file_info.diann_temp_file_path))
                    self.send_msg(3,
                                  msg='DIA-NN error, result file is not exist, file name is: {}, temp file path is: {}'.format(
                                      file_info.file_name, file_info.diann_temp_file_path))
                    return False
            #
            self.send_msg(1, msg='DIA-NN exited.')
            return True
        except Exception as e:
            logger.exception('deal diann exception')
            self.send_msg(3, msg='Exception deal DIA-NN: {}'.format(e))
            return False
        finally:
            self.is_running = False

    #
    def deal_one_diann(self, file_info: FileInfo):
        logger = self.logger
        file_type = file_info.file_type
        if file_type == FileTypeEnum.D or file_type == FileTypeEnum.RAW:
            mass_acc_ms1 = 20
        elif file_type == FileTypeEnum.WIFF:
            mass_acc_ms1 = 30
        else:
            logger.error(
                'file type is error, file name is: {}, file_type is: {}'.format(file_info.file_name, file_type))
            return None

        if file_type == FileTypeEnum.RAW or file_type == FileTypeEnum.WIFF:
            org_file_path = file_info.file_path
        elif file_type == FileTypeEnum.D:
            org_file_path = file_info.file_path

        run_lib_path = self.lib_path
        if run_lib_path is None or len(run_lib_path) == 0 or not os.path.exists(run_lib_path):
            run_lib_path = setting.get_lib_path_by_file_type(file_info.file_type)
            logger.info('lib not exist, use default lib: {}'.format(run_lib_path))

        cmd = '"{}" --f "{}" --lib "{}" --threads {} --verbose 1 --out "{}" --qvalue 0.01 --matrices ' \
              '--met-excision --cut K*,R* --mass-acc {} --mass-acc-ms1 20 --individual-mass-acc --individual-windows --smart-profiling ' \
              '--pg-level 1 --peak-center --no-ifs-removal'.format(self.diann_path, org_file_path, run_lib_path, diann_thread,
                                                                   file_info.diann_temp_file_path,
                                                                   mass_acc_ms1)

        self.diann_analysis_one(cmd, file_info)

    #
    def diann_analysis_one(self, cmd, file_info: FileInfo):
        logger = self.logger
        logger.info('diann analysis one, file name is: {}, cmd is: {}'.format(file_info.file_name, cmd))
        self.send_msg(20, '')
        self.send_msg(9, msg='{}'.format(cmd), with_time=True)
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=134217728)
        try:
            stdout, errs = p.communicate(timeout=1800)
            self.send_msg(9, msg='{}'.format(stdout), with_time=True)
        except Exception:
            self.logger.exception('DIA-NN process error')
            self.send_msg(9, msg='DIA-NN process error', with_time=True)
        self.send_msg(21, '')
