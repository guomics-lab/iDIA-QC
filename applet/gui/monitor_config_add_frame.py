import wx
from applet import common_utils
from applet.obj.runtime_data_obj import MonitorConfigDataObj

btn_width = 120
common_config = common_utils.read_yml()

common_font = wx.Font()

class MonitorControlAddFrame(wx.Frame):

    def __init__(self, data_index=None, init_info=None, *args, **kwargs):
        if not data_index is None:
            wx.Frame.__init__(self, None, title='Edit config',
                              size=(800, 400))
        else:
            wx.Frame.__init__(self, None, title='Add config',
                              size=(800, 400))
        self.Centre(wx.BOTH)
        self.data_index = data_index
        if init_info is None:
            self.init_info = MonitorConfigDataObj()
            self.init_info.data_index = ''
            self.init_info.monitor_dir = ''
            self.init_info.lib_path = ''
            self.init_info.raw_file_type = None
            self.init_info.ins_select_id = None
            self.init_info.run_prefix = ''
            self.init_info.output_dir = ''
            self.init_info.file_filter_size = 0
            self.init_info.filter_file_name = ''
        else:
            self.init_info = init_info
            if self.init_info.lib_path is None:
                self.init_info.lib_path = ''

        sizer = wx.BoxSizer(wx.VERTICAL)

        # main_panel = wx.Panel(self)
        self.config_panel = MonitorControlPanel(self)
        sizer.Add(self.config_panel, 1, wx.ALL | wx.EXPAND, 5)


class MonitorControlPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(-1, 600), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        self.init_info = parent.init_info
        self.data_index = parent.data_index

        run_info_gb_sizer = wx.GridBagSizer(0, 0)
        run_info_gb_sizer.SetFlexibleDirection(wx.BOTH)
        run_info_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.monitor_dir_choose_button = wx.Button(self, wx.ID_ANY, u"Monitor dir*",
                                                   wx.DefaultPosition, wx.Size(120, -1), 0)
        self.monitor_dir_choose_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.monitor_dir_choose_button, wx.GBPosition(0, 0), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)

        self.monitor_dir_text = wx.TextCtrl(self, wx.ID_ANY, self.init_info.monitor_dir,
                                            wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.monitor_dir_text.SetFont(common_font)
        run_info_gb_sizer.Add(self.monitor_dir_text, wx.GBPosition(0, 2), wx.GBSpan(1, 16),
                              wx.ALL | wx.EXPAND, 5)


        self.lib_choose_button = wx.Button(self, wx.ID_ANY, u"Lib",
                                                   wx.DefaultPosition, wx.Size(120, -1), 0)
        self.lib_choose_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.lib_choose_button, wx.GBPosition(1, 0), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)

        self.lib_dir_text = wx.TextCtrl(self, wx.ID_ANY, self.init_info.lib_path,
                                            wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.lib_dir_text.SetFont(common_font)
        run_info_gb_sizer.Add(self.lib_dir_text, wx.GBPosition(1, 2), wx.GBSpan(1, 16),
                              wx.ALL | wx.EXPAND, 5)

        file_type_button = wx.Button(self, wx.ID_ANY, u"File type*",
                                     wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        file_type_button.SetFont(common_font)

        run_info_gb_sizer.Add(file_type_button, wx.GBPosition(2, 0), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)

        self.dia_btn = wx.RadioButton(self, wx.ID_ANY, u"DIA", wx.DefaultPosition,
                                      wx.DefaultSize, wx.RB_GROUP)
        if self.init_info.raw_file_type == 'DIA':
            self.dia_btn.SetValue(True)
        run_info_gb_sizer.Add(self.dia_btn, wx.GBPosition(2, 2), wx.GBSpan(1, 2), wx.ALL, 5)

        # self.dda_btn = wx.RadioButton(self, wx.ID_ANY, u"DDA",
        #                               wx.DefaultPosition, wx.DefaultSize, 0)
        # if self.init_info.raw_file_type == 'DDA':
        #     self.dda_btn.SetValue(True)
        # run_info_gb_sizer.Add(self.dda_btn, wx.GBPosition(2, 4), wx.GBSpan(1, 2), wx.ALL, 5)

        self.output_path_choose_button = wx.Button(self, wx.ID_ANY, u"Output dir*",
                                                   wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        self.output_path_choose_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.output_path_choose_button, wx.GBPosition(3, 0), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)

        self.file_output_dir_text = wx.TextCtrl(self, wx.ID_ANY, self.init_info.output_dir,
                                                wx.DefaultPosition, wx.Size(250, -1), 0)
        self.file_output_dir_text.SetFont(common_font)

        run_info_gb_sizer.Add(self.file_output_dir_text, wx.GBPosition(3, 2), wx.GBSpan(1, 16), wx.ALL | wx.EXPAND, 5)

        inst_btn_btn = wx.Button(self, wx.ID_ANY, u"Instrument type*", wx.DefaultPosition,
                                 wx.Size(btn_width, -1), 0)
        inst_btn_btn.SetFont(common_font)
        run_info_gb_sizer.Add(inst_btn_btn, wx.GBPosition(4, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.ins_id_choice_list = common_config['inst']
        self.ins_id_choice = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.ins_id_choice_list, 0)
        self.ins_id_choice.SetFont(common_font)

        if self.init_info.ins_select_id is not None:
            self.ins_id_choice.Select(self.init_info.ins_select_id)

        run_info_gb_sizer.Add(self.ins_id_choice, wx.GBPosition(4, 2), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        run_prefix_btn_btn = wx.Button(self, wx.ID_ANY, u"Instrument ID*", wx.DefaultPosition,
                                       wx.Size(btn_width, -1), 0)
        run_prefix_btn_btn.SetFont(common_font)
        run_info_gb_sizer.Add(run_prefix_btn_btn, wx.GBPosition(4, 4), wx.GBSpan(1, 2), wx.ALL, 5)

        self.run_prefix_text = wx.TextCtrl(self, wx.ID_ANY, self.init_info.run_prefix,
                                           wx.DefaultPosition, wx.Size(100, -1), 0)
        self.run_prefix_text.SetFont(common_font)
        run_info_gb_sizer.Add(self.run_prefix_text, wx.GBPosition(4, 6), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        self.file_filter_panel = FileFilterInfoPanel(self)
        run_info_gb_sizer.Add(self.file_filter_panel, wx.GBPosition(5, 0), wx.GBSpan(2, 18), wx.ALL| wx.EXPAND, 5)

        if not self.data_index is None:
            self.config_add_button = wx.Button(self, wx.ID_ANY, u"Edit config", wx.DefaultPosition, wx.Size(120, -1), 0)
        else:
            self.config_add_button = wx.Button(self, wx.ID_ANY, u"Add config", wx.DefaultPosition, wx.Size(120, -1), 0)
        self.config_add_button.SetFont(common_font)
        run_info_gb_sizer.Add(self.config_add_button, wx.GBPosition(7, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.config_cancel_button = wx.Button(self, wx.ID_ANY, u"Cancel", wx.DefaultPosition, wx.Size(120, -1),
                                              0)
        self.config_cancel_button.SetFont(common_font)
        run_info_gb_sizer.Add(self.config_cancel_button, wx.GBPosition(7, 3), wx.GBSpan(1, 2), wx.ALL, 5)

        run_info_gb_sizer.AddGrowableCol(17)

        self.SetSizer(run_info_gb_sizer)
        self.Layout()

    def __del__(self):
        pass



'''
文件过滤模块
'''
class FileFilterInfoPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(-1, 120), style=wx.TAB_TRAVERSAL|wx.ALL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        rd_sb = wx.StaticBox(self, wx.ID_ANY, u"File filtering")
        # rd_sb.SetFont(common_font)

        self.init_info = parent.init_info

        info_panel_sb_sizer = wx.StaticBoxSizer(rd_sb, wx.VERTICAL)

        info_panel_gb_sizer = wx.GridBagSizer(0, 0)
        info_panel_gb_sizer.SetFlexibleDirection(wx.BOTH)
        info_panel_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        ''' file size'''
        min_size_button = wx.Button(self, wx.ID_ANY, u"Min size(MB)",
                                    wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        # min_size_button.SetFont(common_font)

        info_panel_gb_sizer.Add(min_size_button, wx.GBPosition(0, 0), wx.GBSpan(1, 2), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.min_size_ctrl = wx.SpinCtrl(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize,
                                         wx.SP_ARROW_KEYS, 0, 2000, self.init_info.file_filter_size)
        # self.min_size_ctrl.SetFont(common_font)
        info_panel_gb_sizer.Add(self.min_size_ctrl, wx.GBPosition(0, 2), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        ''' filtering file name  '''
        self.reserve_btn = wx.RadioButton(info_panel_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Inclusion", wx.DefaultPosition,
                                          wx.DefaultSize, wx.RB_GROUP)
        if self.init_info.filter_type == 1:
            self.reserve_btn.SetValue(True)
        info_panel_gb_sizer.Add(self.reserve_btn, wx.GBPosition(1, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.remove_btn = wx.RadioButton(info_panel_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Exclusion",
                                         wx.DefaultPosition, wx.DefaultSize, 0)
        if self.init_info.filter_type == 2:
            self.remove_btn.SetValue(True)

        info_panel_gb_sizer.Add(self.remove_btn, wx.GBPosition(1, 2), wx.GBSpan(1, 2), wx.ALL, 5)

        filter_name_button = wx.Button(self, wx.ID_ANY, u"Key words",
                                       wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        filter_name_button.SetFont(common_font)
        # filter_name_button.Disable()

        info_panel_gb_sizer.Add(filter_name_button, wx.GBPosition(1, 4), wx.GBSpan(1, 2), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.filter_name_text = wx.TextCtrl(self, wx.ID_ANY, self.init_info.filter_file_name,
                                            wx.DefaultPosition, wx.Size(250, -1), 0)
        self.filter_name_text.SetFont(common_font)
        info_panel_gb_sizer.Add(self.filter_name_text, wx.GBPosition(1, 11), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        info_panel_gb_sizer.AddGrowableCol(11)
        info_panel_sb_sizer.Add(info_panel_gb_sizer, 1, wx.EXPAND, 5)

        self.SetSizer(info_panel_sb_sizer)
        self.Layout()

    def __del__(self):
        pass

