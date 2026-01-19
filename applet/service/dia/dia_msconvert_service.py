# coding:utf-8
"""This module is for mzxml msconvert"""

import os
import subprocess
import time

from applet.default_config import setting
from applet.obj.Entity import FileTypeEnum, FileInfo
from applet.service import common_service


class DIAMSConvertService(common_service.CommonService):
    def __init__(self, msconvert_path, base_output_path, file_list: [FileInfo], logger, step=2,
                 pub_channel='analysis_info', start_time=0, conn_send=None):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time, conn_send=conn_send)
        self.msconvert_path = msconvert_path

    #
    def deal_process(self):
        logger = self.logger
        try:
            # self.send_msg(0, msg='Start deal msconvert process, {} files will be processed'.format(len(self.file_list)))
            self.send_msg(0, msg='')
            self.is_running = True
            if len(self.file_list) == 0:
                self.send_msg(3, msg='File count is zero, stop')
                return False
            deal_count = 0
            mzXML_output_path = os.path.join(self.base_output_path, setting.output_dir_s1)
            logger.info('start msconvert, file count is: {}, mzXML_output_path is: {}'.format(len(self.file_list),
                                                                                              mzXML_output_path))
            if not os.path.exists(mzXML_output_path):
                os.makedirs(mzXML_output_path)
            for file_info in self.file_list:
                t1 = time.time()
                if not self.run_flag:
                    self.send_msg(2, msg='Click stop')
                    logger.error('msconvert stop')
                    return False
                file_info.mzXML_file_path = os.path.join(mzXML_output_path, file_info.mzXML_file_name)
                file_info.mzML_file_path = os.path.join(mzXML_output_path, file_info.mzML_file_name)

                file_info.mzxml_file_relative_path = os.path.join(setting.output_dir_s1, file_info.mzXML_file_name)
                self.deal_one_convert(mzXML_output_path, file_info)
                deal_count += 1
                t2 = time.time()
                logger.info('msconvert_time, file: {}, run_prefix: {}, speed_time: {}, '.format(file_info.file_name, file_info.run_prefix, t2 - t1))
                logger.info('end msconvert file {}, {}/{}'.format(file_info.file_name, deal_count, len(self.file_list)))
                if os.path.exists(file_info.mzXML_file_path):
                    continue
                else:
                    logger.error('fail msconvert file {}'.format(file_info.file_name))
                    self.send_msg(3, msg='fail msconvert file {}'.format(file_info.file_name))
                    return False
            #
            logger.info('success msconvert, file count is: {}, mzXML_output_path is: {}'.format(len(self.file_list),
                                                                                                mzXML_output_path))
            self.send_msg(1, msg='Finished\nmsconvert exited')

            return True
        except Exception as e:
            logger.exception('deal msconvert exception')
            self.send_msg(3, msg='Msconvert exception: {}'.format(e))
            return False
        finally:
            self.is_running = False

    def deal_one_convert(self, mzXML_output_path, file_info: FileInfo):
        logger = self.logger
        file_path = file_info.file_path
        file_name = file_info.file_name
        file_type = file_info.file_type
        mzXML_file = file_info.mzXML_file_name
        mzML_file = file_info.mzML_file_name
        if file_type == FileTypeEnum.D:
            cmd = "\"{}\" --inten64 --mzXML --zlib --combineIonMobilitySpectra --filter \"threshold count 150 most-intense\" --filter \"scanSumming precursorTol=0.05 scanTimeTol=5 ionMobilityTol=0.1\" {} -o {} --outfile {}".format(
                self.msconvert_path, file_path, mzXML_output_path, mzXML_file)

            cmd_mzml = "\"{}\" --inten64 --mzML --zlib --combineIonMobilitySpectra --filter \"threshold count 150 most-intense\" --filter \"scanSumming precursorTol=0.05 scanTimeTol=5 ionMobilityTol=0.1\" {} -o {} --outfile {}".format(
                self.msconvert_path, file_path, mzXML_output_path, mzML_file)

            self.msconvert_one(cmd, cmd_mzml, file_info)
        elif file_type == FileTypeEnum.RAW or file_type == FileTypeEnum.WIFF:
            cmd = "\"{}\" --inten64 --mzXML --zlib --filter \"peakPicking true [1,2]\" {} -o {} --outfile {}".format(
                self.msconvert_path, file_path, mzXML_output_path, mzXML_file)

            cmd_mzml = "\"{}\" --inten64 --mzML --zlib --filter \"peakPicking true [1,2]\" {} -o {} --outfile {}".format(
                self.msconvert_path, file_path, mzXML_output_path, mzML_file)

            self.msconvert_one(cmd, cmd_mzml, file_info)
        else:
            logger.error('fail msconvert file {}, file type is error.'.format(file_info.file_name))
            self.send_msg(9, msg='File type not valid,{}'.format(file_name))
            return None

    #
    def msconvert_one(self, cmd, cmd_mzml, file_info):
        logger = self.logger
        logger.info('start msconvert file {}, '.format(file_info.file_name))
        # self.send_msg(10, msg='Start msconvert, {}'.format(file_info.file_name))
        self.send_msg(10, msg='')
        self.send_msg(9, msg='{}'.format(cmd), with_time=True)
        logger.info('cmd: {}'.format(cmd))
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=134217728)
        try:
            stdout, errs = p.communicate(timeout=1800)
            self.send_msg(9, msg='{}'.format(stdout), with_time=True)
        except Exception:

            self.logger.exception('MSConvert process error')
            self.send_msg(9, msg='MSConvert process error', with_time=True)
        self.send_msg(9, 'Finished the conversion of file to mzXML', True)

        self.send_msg(9, 'Finished the conversion of file to mzML format', True)
        self.send_msg(11, '')
