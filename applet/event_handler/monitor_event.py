import json
import multiprocessing
import os.path

import wx
from pubsub import pub
import signal

from applet import common_utils
from applet.default_config import setting
from applet.event_handler.monitor_config_add_panel_envent_handler import MonitorConfigPanelEventHandler
from applet.gui.monitor_config_add_frame import MonitorControlAddFrame
from applet.gui.monitor_info_panel import MonitorPanel
from loguru import logger
from applet.obj.runtime_data_obj import runtime_monitor_config_data
from applet.thread_util.analysis_monitor_thread import AnalysisMonitorThread
from applet.thread_util.monitor_process_log_thread import AnalysisMonitorLogThread
import sys
common_config = common_utils.read_yml()
ins_list = common_config['inst']

RUNNING_COLOR = '#f8c108'
OVER_COLOR = '#27c14c'
ERROR_COLOR = '#e91b40'


class MonitorEventHandler(object):

    def __init__(self, monitor_panel: MonitorPanel):
        self.monitor_panel = monitor_panel
        # self.an_monitor_process = None
        self.monitor_log_thread = None
        self.stop_event = None

    def diann_choose(self, event):
        filesFilter = "DiaNN.exe"
        file_choose_bt = wx.FileDialog(self.monitor_panel, message='Choose DiaNN.exe', wildcard=filesFilter,
                                       style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_panel.monitor_control_panel.diann_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    def msconvert_choose(self, event):
        filesFilter = "msconvert.exe"
        file_choose_bt = wx.FileDialog(self.monitor_panel, message='Choose msconvert.exe', wildcard=filesFilter,
                                       style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_panel.monitor_control_panel.msconvert_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    def add_monitor_config(self, event):
        config_add_frame = MonitorControlAddFrame()
        config_add_frame.Show()
        ee_handler = MonitorConfigPanelEventHandler(config_add_frame)
        ee_handler.bind_event()

    def fasta_choose(self, event):
        file_choose_bt = wx.FileDialog(self.monitor_panel, message='choose FASTA file', style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_panel.monitor_control_panel.fasta_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    def format_monitor_dir(self, monitor_dir):
        monitor_dir_list = str(monitor_dir).split(';')
        new_dir_list = []
        for current_dir in monitor_dir_list:
            current_dir = current_dir.rstrip()
            if len(current_dir) == 0:
                continue
            new_dir_list.append(current_dir)
        return list(set(new_dir_list))

    def signal_handler(self, sig, frame):
        print("\nShutting down gracefully...")
        if self.stop_event:
            self.stop_event.set()
        sys.exit(0)

    def monitor_start_click(self, event):
        try:
            msconvert_path = self.monitor_panel.monitor_control_panel.msconvert_path_text.GetValue()
            diann_path = self.monitor_panel.monitor_control_panel.diann_path_text.GetValue()
            fragpipe_path = setting.fragpipe_path

            scan_time = self.monitor_panel.monitor_control_panel.scan_time_ctrl.GetValue()
            interval_time = self.monitor_panel.monitor_control_panel.interval_time_ctrl.GetValue()

            notify_email = self.monitor_panel.monitor_control_panel.notify_email_text.GetValue()
            notify_wx_token = self.monitor_panel.monitor_control_panel.wx_token_text.GetValue()

            setting.config_data_list = json.dumps([dd.__dict__ for dd in runtime_monitor_config_data.config_data_list])
            setting.scan_time = str(scan_time)
            setting.interval_time = str(interval_time)
            setting.notify_email = notify_email
            setting.wx_token = notify_wx_token
            setting.save_config()

            self.monitor_panel.monitor_control_panel.monitor_start_button.SetLabel('Running')
            self.monitor_panel.monitor_control_panel.monitor_status_button.SetBackgroundColour(RUNNING_COLOR)
            self.monitor_panel.monitor_control_panel.monitor_start_button.Disable()

            logger.info('Start analysis monitor thread')
            cwd = os.getcwd()

            self.conn_send, self.conn_recv = multiprocessing.Pipe()

            fast_mode = self.get_fast_mode_checked()

            self.stop_event = multiprocessing.Event()

            self.an_monitor_process = AnalysisMonitorThread(os.path.join(cwd, diann_path),
                                                            os.path.join(cwd, fragpipe_path),
                                                            msconvert_path,
                                                            runtime_monitor_config_data.config_data_list,
                                                            scan_time,
                                                            interval_time,
                                                            './resource/model/unisplit', notify_email, notify_wx_token,
                                                            fast_mode,
                                                            self.conn_send, self.stop_event)
            # self.an_monitor_thread.daemon = True
            self.monitor_panel.monitor_log_panel.log_text.SetValue('')
            self.an_monitor_process.start()
            signal.signal(signal.SIGINT, self.signal_handler)
            signal.signal(signal.SIGTERM, self.signal_handler)

            self.monitor_log_thread = AnalysisMonitorLogThread(self.conn_recv,
                                                               self.monitor_panel.monitor_log_panel.log_text)
            self.monitor_log_thread.start()
        except Exception:
            logger.exception('start error')

    def monitor_stop_click(self, event):
        self.conn_send.close()
        self.conn_recv.close()

        if self.stop_event:
            self.stop_event.set()

        if self.monitor_log_thread:
            self.monitor_log_thread.stop()
            self.monitor_log_thread.join()
        self.monitor_panel.monitor_control_panel.monitor_start_button.SetLabel('Run')
        self.monitor_panel.monitor_control_panel.monitor_start_button.Enable()
        self.monitor_panel.monitor_control_panel.monitor_status_button.SetBackgroundColour(None)
        self.monitor_panel.monitor_log_panel.log_text.AppendText('Monitor stop\n')

    def on_context_menu(self, event):
        menu = wx.Menu()
        edit_item = menu.Append(wx.ID_EDIT, "Edit")
        delete_item = menu.Append(wx.ID_DELETE, "Delete")
        self.monitor_panel.GetParent().GetParent().Bind(wx.EVT_MENU, self.edit_list_item, edit_item)
        self.monitor_panel.GetParent().GetParent().Bind(wx.EVT_MENU, self.delete_list_item, delete_item)

        self.monitor_panel.GetParent().GetParent().PopupMenu(menu)
        menu.Destroy()

    def edit_list_item(self, event):
        index = self.monitor_panel.monitor_control_panel.monitor_data_list.GetFirstSelected()
        if index != -1:
            config_add_frame = MonitorControlAddFrame(data_index=index, init_info=runtime_monitor_config_data.config_data_list[index])
            config_add_frame.Show()
            ee_handler = MonitorConfigPanelEventHandler(config_add_frame)
            ee_handler.bind_event()

    def delete_list_item(self, event):
        index = self.monitor_panel.monitor_control_panel.monitor_data_list.GetFirstSelected()
        if index != -1:
            del runtime_monitor_config_data.config_data_list[index]
            pub.sendMessage('load_monitor_config', msg='')

    '''
    '''

    def get_filter_type_checked(self):
        if self.monitor_panel.monitor_control_panel.file_filter_panel.reserve_btn.GetValue():
            return 1
        elif self.monitor_panel.monitor_control_panel.file_filter_panel.remove_btn.GetValue():
            return 2
        else:
            return None

    def get_file_type_checked(self):
        if self.monitor_panel.monitor_control_panel.dia_btn.GetValue():
            return 'DIA'
        # elif self.monitor_panel.monitor_control_panel.dda_btn.GetValue():
        #     return 'DDA'
        else:
            return None

    def click_dia(self, event):
        self.monitor_panel.monitor_control_panel.diann_exe_btn.SetLabel('DIA-NN.exe')
        self.monitor_panel.monitor_control_panel.diann_path_text.SetValue(setting.diann_exe_path)

    def click_dda(self, event):
        self.monitor_panel.monitor_control_panel.diann_exe_btn.SetLabel('FragPipe dir')
        self.monitor_panel.monitor_control_panel.diann_path_text.SetValue('./FragPipe-jre-21.1\\fragpipe')

    def load_monitor_data_list(self, msg):
        self.monitor_panel.monitor_control_panel.monitor_data_list.DeleteAllItems()
        total = len(runtime_monitor_config_data.config_data_list)
        for dd, each_data in enumerate(runtime_monitor_config_data.config_data_list):
            indexItem = self.monitor_panel.monitor_control_panel.monitor_data_list.InsertItem(total,
                                                                                              each_data.monitor_dir)
            self.monitor_panel.monitor_control_panel.monitor_data_list.SetItem(indexItem, 1,
                                                                               each_data.lib_path if each_data.lib_path else '')
            self.monitor_panel.monitor_control_panel.monitor_data_list.SetItem(indexItem, 2, each_data.raw_file_type)
            self.monitor_panel.monitor_control_panel.monitor_data_list.SetItem(indexItem, 3, each_data.output_dir)
            self.monitor_panel.monitor_control_panel.monitor_data_list.SetItem(indexItem, 4, each_data.inst_name)
            self.monitor_panel.monitor_control_panel.monitor_data_list.SetItem(indexItem, 5, each_data.run_prefix)
            self.monitor_panel.monitor_control_panel.monitor_data_list.SetItem(indexItem, 6,
                                                                               str(each_data.file_filter_size))
            self.monitor_panel.monitor_control_panel.monitor_data_list.SetItem(indexItem, 7,
                                                                               str(each_data.filter_type_remark) + ':' + str(
                                                                                   each_data.filter_file_name))


    def get_fast_mode_checked(self):
        if self.monitor_panel.monitor_control_panel.fast_mode_checkBox.IsChecked():
            return True
        return False
