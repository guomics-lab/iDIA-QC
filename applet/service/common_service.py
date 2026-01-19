import json
import time

from pubsub import pub

from applet.obj.Entity import FileInfo
from applet.obj.Msg import AnalysisInfoMsg


class CommonService(object):

    def __init__(self, base_output_path, file_list: [FileInfo], logger, step, pub_channel='analysis_info',
                 start_time=0, conn_send=None):
        self.base_output_path = base_output_path
        self.file_list = file_list
        self.run_flag = True
        self.is_running = False
        self.logger = logger
        self.step = step
        self.pub_channel = pub_channel
        self.start_time = start_time
        self.conn_send = conn_send
        pub.subscribe(self.change_run_flag, 'change_run_flag')

    def change_run_flag(self, msg):
        self.run_flag = False

    def deal_process(self):
        pass

    def send_msg(self, status, msg=None, with_time=False):
        if self.conn_send:
            self.conn_send.send(msg)
        else:
            if self.pub_channel:
                if with_time and self.pub_channel == 'analysis_info':
                    msg = self.get_now_use_time() + ' ' + msg
                info_msg = AnalysisInfoMsg(self.step, status, msg)
                pub.sendMessage(self.pub_channel, msg=json.dumps(info_msg.__dict__))

    def get_now_use_time(self):
        now_time = time.time()
        minutes, seconds = divmod(now_time - self.start_time, 60)
        minutes = int(minutes)
        seconds = int(seconds)
        return '[{}:{}]'.format(minutes, str(seconds).zfill(2))
