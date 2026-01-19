from applet import common_utils
from applet.obj.Entity import FileInfo
from applet.service import common_service

common_config = common_utils.read_yml()
ins_list = common_config['inst']


class MzxmlService(common_service.CommonService):

    def __init__(self, inst_name, run_prefix, base_output_path, file_list: [FileInfo], logger, step=4,
                 pub_channel='analysis_info', start_time=0, conn_send=None):
        common_service.CommonService.__init__(self, base_output_path, file_list, logger, step, pub_channel, start_time, conn_send=conn_send)
        self.inst_name = inst_name
        self.run_prefix = run_prefix

    def deal_process(self):
        logger = self.logger
        try:
            self.is_running = True
            self.send_msg(0, msg='')
            logger.info('Start deal build mzxml info process')

            pass
            logger.info('Success build mzxml info')
            self.send_msg(1, msg='')
            return True
        except Exception as e:
            logger.exception('Deal build mzxml info exception')
            self.send_msg(3, msg='Deal build mzxml info exception: {}'.format(e))
            return False
        finally:
            self.is_running = False
