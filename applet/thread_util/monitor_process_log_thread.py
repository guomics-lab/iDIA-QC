import threading


class AnalysisMonitorLogThread(threading.Thread):

    def __init__(self, conn_recv, log_text):
        threading.Thread.__init__(self)

        self.run_flag = True
        self.conn_recv = conn_recv
        self.log_text = log_text

    def stop(self):
        self.run_flag = False

    def run(self):
        while self.run_flag:
            try:
                output = self.conn_recv.recv()
                self.log_text.AppendText('{}\r\n'.format(output))
            except Exception:
                break
