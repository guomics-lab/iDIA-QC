import shutil

import wx
from pubsub import pub

from applet import common_utils
from applet.gui.monitor_config_add_frame import MonitorControlAddFrame
from applet.obj.runtime_data_obj import runtime_monitor_config_data, MonitorConfigDataObj

common_config = common_utils.read_yml()
ins_list = common_config['inst']


class MonitorConfigPanelEventHandler(object):

    def __init__(self, monitor_config_add_frame: MonitorControlAddFrame):
        self.monitor_config_add_frame = monitor_config_add_frame

    def bind_event(self):

        self.monitor_config_add_frame.Bind(wx.EVT_BUTTON, self.monitor_dir_choose_click,
                                           self.monitor_config_add_frame.config_panel.monitor_dir_choose_button)

        self.monitor_config_add_frame.Bind(wx.EVT_BUTTON, self.lib_choose_click,
                                           self.monitor_config_add_frame.config_panel.lib_choose_button)

        self.monitor_config_add_frame.Bind(wx.EVT_BUTTON, self.output_dir_choose,
                                           self.monitor_config_add_frame.config_panel.output_path_choose_button)

        self.monitor_config_add_frame.Bind(wx.EVT_BUTTON, self.config_add_button_click,
                                           self.monitor_config_add_frame.config_panel.config_add_button)
        self.monitor_config_add_frame.Bind(wx.EVT_BUTTON, self.config_cancel_button_click,
                                           self.monitor_config_add_frame.config_panel.config_cancel_button)

    def monitor_dir_choose_click(self, event):
        dir_choose_bt = wx.DirDialog(self.monitor_config_add_frame, 'Choose monitor dir path',
                                     style=wx.DD_DIR_MUST_EXIST)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_config_add_frame.config_panel.monitor_dir_text.ChangeValue(dir_choose_bt.GetPath())
        dir_choose_bt.Destroy()

    def lib_choose_click(self, event):

        dir_choose_bt = wx.FileDialog(self.monitor_config_add_frame, 'Choose lib path', style=wx.FD_DEFAULT_STYLE)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_config_add_frame.config_panel.lib_dir_text.ChangeValue(dir_choose_bt.GetPath())
        dir_choose_bt.Destroy()

    def output_dir_choose(self, event):
        dir_choose_bt = wx.DirDialog(self.monitor_config_add_frame, 'Choose output dir path',
                                     style=wx.DD_DIR_MUST_EXIST)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            self.monitor_config_add_frame.config_panel.file_output_dir_text.ChangeValue(dir_choose_bt.GetPath())
        dir_choose_bt.Destroy()

    def config_add_button_click(self, event):
        data_index = self.monitor_config_add_frame.data_index
        monitor_dir = self.monitor_config_add_frame.config_panel.monitor_dir_text.GetValue()
        if not monitor_dir or len(monitor_dir) == 0:
            msg_box = wx.MessageDialog(None, 'Please choose monitor dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        lib_path = self.monitor_config_add_frame.config_panel.lib_dir_text.GetValue()
        if not lib_path or len(lib_path) == 0:
            lib_path = ''

        raw_file_type = self.get_file_type_checked()
        if raw_file_type is None:
            msg_box = wx.MessageDialog(None, 'Please select raw file type', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        ins_select_id = self.monitor_config_add_frame.config_panel.ins_id_choice.GetSelection()
        if ins_select_id == -1:
            msg_box = wx.MessageDialog(None, 'Instrument type is not selected', 'alert',
                                       wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        inst_name = ins_list[ins_select_id]

        run_prefix = self.monitor_config_add_frame.config_panel.run_prefix_text.GetValue()
        if not run_prefix or len(run_prefix) == 0:
            msg_box = wx.MessageDialog(None, 'Please input instrument id', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        output_dir = self.monitor_config_add_frame.config_panel.file_output_dir_text.GetValue()
        if not output_dir or len(output_dir) == 0:
            msg_box = wx.MessageDialog(None, 'Please choose output dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        file_filter_size = self.monitor_config_add_frame.config_panel.file_filter_panel.min_size_ctrl.GetValue()
        filter_type, filter_type_remark = self.get_filter_type_checked()
        filter_file_name = self.monitor_config_add_frame.config_panel.file_filter_panel.filter_name_text.GetValue()

        data_obj = MonitorConfigDataObj()
        data_obj.monitor_dir = monitor_dir
        data_obj.lib_path = lib_path
        data_obj.raw_file_type = raw_file_type
        data_obj.filter_type_remark = filter_type_remark
        data_obj.ins_select_id = ins_select_id
        data_obj.inst_name = inst_name
        data_obj.run_prefix = run_prefix
        data_obj.output_dir = output_dir
        data_obj.file_filter_size = file_filter_size
        data_obj.filter_type = filter_type
        data_obj.filter_file_name = filter_file_name
        if data_index is not None:
            runtime_monitor_config_data.config_data_list[data_index] = data_obj
        else:
            runtime_monitor_config_data.config_data_list.append(data_obj)

        pub.sendMessage('load_monitor_config', msg='load')

        self.monitor_config_add_frame.Close()

    def config_cancel_button_click(self, event):
        self.monitor_config_add_frame.Close()

    def get_file_type_checked(self):
        if self.monitor_config_add_frame.config_panel.dia_btn.GetValue():
            return 'DIA'
        else:
            return None

    def get_filter_type_checked(self):
        if self.monitor_config_add_frame.config_panel.file_filter_panel.reserve_btn.GetValue():
            return 1, 'Inclusion'
        elif self.monitor_config_add_frame.config_panel.file_filter_panel.remove_btn.GetValue():
            return 2, 'Exclusion'
        else:
            return None

