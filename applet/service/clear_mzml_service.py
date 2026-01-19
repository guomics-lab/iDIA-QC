import os
import shutil
import time

from applet.default_config import setting
from applet.obj.Entity import FileInfo
from applet.service import common_service


class ClearMzmlService(common_service.CommonService):

    def __init__(self, base_output_path, file_list: [FileInfo], logger, step=13,
                 pub_channel='analysis_info', start_time=0, conn_send=None):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time, conn_send=conn_send)

    def deal_process(self):
        logger = self.logger
        try:
            self.is_running = True
            self.send_msg(9, 'Removing mzXML file and mzML file', with_time=True)
            # mzXML_output_path = os.path.join(self.base_output_path, setting.output_dir_s1)
            # if os.path.exists(mzXML_output_path):
            #     file_list = os.listdir(mzXML_output_path)
            #     for file_name in file_list:
            #         if file_name.endswith('.mzML') or file_name.endswith('.mzXML'):
            #             os.remove(os.path.join(os.path.join(mzXML_output_path, file_name)))
            return True
        except Exception as e:
            logger.exception('Deal Removing mzXML file and mzML file exception')
            self.send_msg(3, 'Deal Removing mzXML file and mzML file exception: {}'.format(e))
            return False
        finally:
            self.is_running = False
