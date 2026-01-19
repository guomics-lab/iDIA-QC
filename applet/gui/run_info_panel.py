import os

import wx

from applet import common_utils
from applet.default_config import setting
from applet.gui.common_config import common_font

btn_width = 120

common_config = common_utils.read_yml()


class RunInfoPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(400, 100), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        run_info_gb_sizer = wx.GridBagSizer(0, 0)
        run_info_gb_sizer.SetFlexibleDirection(wx.BOTH)
        run_info_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.config_panel = ConfigPanel(self)
        self.input_panel = InputPanel(self)
        self.run_control_panel = RunControlPanel(self)
        self.output_panel = OutputPanel(self)
        self.log_panel = LogPanel(self)

        run_info_gb_sizer.Add(self.config_panel, wx.GBPosition(0, 0), wx.GBSpan(2, 7), wx.ALL, 5)
        run_info_gb_sizer.Add(self.input_panel, wx.GBPosition(2, 0), wx.GBSpan(2, 7), wx.ALL, 5)
        run_info_gb_sizer.Add(self.run_control_panel, wx.GBPosition(4, 0), wx.GBSpan(1, 7), wx.ALL, 5)
        run_info_gb_sizer.Add(self.output_panel, wx.GBPosition(0, 7), wx.GBSpan(2, 4), wx.ALL | wx.EXPAND, 5)
        run_info_gb_sizer.Add(self.log_panel, wx.GBPosition(2, 7), wx.GBSpan(4, 4), wx.ALL | wx.EXPAND, 5)

        run_info_gb_sizer.AddGrowableRow(5)
        run_info_gb_sizer.AddGrowableCol(9)

        self.SetSizer(run_info_gb_sizer)
        self.Layout()

    def __del__(self):
        pass


class ConfigPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(600, 240), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        input_sb = wx.StaticBox(self, wx.ID_ANY, u"Configuration")
        input_sb.SetFont(common_font)
        input_sb_sizer = wx.StaticBoxSizer(input_sb, wx.VERTICAL)

        input_gb_sizer = wx.GridBagSizer(0, 0)
        input_gb_sizer.SetFlexibleDirection(wx.BOTH)
        input_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        file_type_button = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"File type",
                                     wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        file_type_button.SetFont(common_font)

        input_gb_sizer.Add(file_type_button, wx.GBPosition(0, 0), wx.GBSpan(1, 2),
                           wx.ALIGN_RIGHT | wx.ALL, 5)

        self.dia_btn = wx.RadioButton(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"DIA", wx.DefaultPosition,
                                      wx.DefaultSize, wx.RB_GROUP)
        input_gb_sizer.Add(self.dia_btn, wx.GBPosition(0, 2), wx.GBSpan(1, 2), wx.ALL, 5)

        # self.dda_btn = wx.RadioButton(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"DDA",
        #                               wx.DefaultPosition, wx.DefaultSize, 0)
        # input_gb_sizer.Add(self.dda_btn, wx.GBPosition(0, 4), wx.GBSpan(1, 2), wx.ALL, 5)


        self.diann_exe_btn = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"DIA-NN.exe", wx.DefaultPosition,
                                       wx.Size(btn_width, -1), 0)
        self.diann_exe_btn.SetFont(common_font)

        input_gb_sizer.Add(self.diann_exe_btn, wx.GBPosition(1, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.diann_path_text = wx.TextCtrl(input_sb_sizer.GetStaticBox(), wx.ID_ANY, setting.diann_exe_path,
                                           wx.DefaultPosition, wx.Size(250, -1), 0)
        self.diann_path_text.SetFont(common_font)

        input_gb_sizer.Add(self.diann_path_text, wx.GBPosition(1, 2), wx.GBSpan(1, 6), wx.ALL | wx.EXPAND, 5)

        self.msconvert_btn = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"MSConvert", wx.DefaultPosition,
                                       wx.Size(btn_width, -1), 0)
        self.msconvert_btn.SetFont(common_font)

        input_gb_sizer.Add(self.msconvert_btn, wx.GBPosition(2, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.msconvert_path_text = wx.TextCtrl(input_sb_sizer.GetStaticBox(), wx.ID_ANY, setting.ms_exe_path,
                                               wx.DefaultPosition, wx.Size(250, -1), 0)
        self.msconvert_path_text.SetFont(common_font)

        input_gb_sizer.Add(self.msconvert_path_text, wx.GBPosition(2, 2), wx.GBSpan(1, 6), wx.ALL | wx.EXPAND, 5)

        '''Inst id'''
        inst_btn_btn = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Instrument type", wx.DefaultPosition,
                                 wx.Size(btn_width, -1), 0)
        inst_btn_btn.SetFont(common_font)
        input_gb_sizer.Add(inst_btn_btn, wx.GBPosition(3, 0), wx.GBSpan(1, 2), wx.ALL, 5)
        self.ins_id_choice_list = common_config['inst']
        self.ins_id_choice = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.ins_id_choice_list, 0)
        self.ins_id_choice.SetFont(common_font)
        input_gb_sizer.Add(self.ins_id_choice, wx.GBPosition(3, 2), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        run_prefix_btn_btn = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Instrument ID", wx.DefaultPosition,
                                 wx.Size(btn_width, -1), 0)
        run_prefix_btn_btn.SetFont(common_font)
        input_gb_sizer.Add(run_prefix_btn_btn, wx.GBPosition(3, 4), wx.GBSpan(1, 2), wx.ALL, 5)

        self.run_prefix_text = wx.TextCtrl(input_sb_sizer.GetStaticBox(), wx.ID_ANY, setting.inst_id,
                                               wx.DefaultPosition, wx.Size(100, -1), 0)
        self.run_prefix_text.SetFont(common_font)
        input_gb_sizer.Add(self.run_prefix_text, wx.GBPosition(3, 6), wx.GBSpan(1, 2), wx.ALL | wx.EXPAND, 5)

        '''***************************'''

        '''email address'''
        notify_email_btn = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Email address", wx.DefaultPosition,
                                     wx.Size(btn_width, -1), 0)
        notify_email_btn.SetFont(common_font)
        # notify_email_btn.Disable()

        input_gb_sizer.Add(notify_email_btn, wx.GBPosition(4, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.notify_email_text = wx.TextCtrl(input_sb_sizer.GetStaticBox(), wx.ID_ANY,
                                             setting.notify_email,
                                             wx.DefaultPosition,
                                             wx.Size(250, -1), 0)
        self.notify_email_text.SetFont(common_font)

        input_gb_sizer.Add(self.notify_email_text, wx.GBPosition(4, 2), wx.GBSpan(1, 6), wx.ALL | wx.EXPAND, 5)
        '''***************************'''

        '''wx token'''
        wx_token_btn = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Wechat token", wx.DefaultPosition,
                                     wx.Size(btn_width, -1), 0)
        wx_token_btn.SetFont(common_font)

        input_gb_sizer.Add(wx_token_btn, wx.GBPosition(5, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.wx_token_text = wx.TextCtrl(input_sb_sizer.GetStaticBox(), wx.ID_ANY,
                                             setting.wx_token,
                                             wx.DefaultPosition,
                                             wx.Size(250, -1), 0)
        self.wx_token_text.SetFont(common_font)

        input_gb_sizer.Add(self.wx_token_text, wx.GBPosition(5, 2), wx.GBSpan(1, 6), wx.ALL | wx.EXPAND, 5)
        '''***************************'''

        input_sb_sizer.Add(input_gb_sizer, 1, wx.EXPAND, 5)

        input_gb_sizer.AddGrowableCol(6)

        self.SetSizer(input_sb_sizer)
        self.Layout()

    def __del__(self):
        pass


class InputPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(600, 320), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        input_sb = wx.StaticBox(self, wx.ID_ANY, u"Input")
        input_sb.SetFont(common_font)
        input_sb_sizer = wx.StaticBoxSizer(input_sb, wx.VERTICAL)

        input_gb_sizer = wx.GridBagSizer(0, 0)
        input_gb_sizer.SetFlexibleDirection(wx.BOTH)
        input_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.raw_select_button = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u".raw", wx.DefaultPosition,
                                           wx.Size(btn_width, -1), 0)
        self.raw_select_button.SetFont(common_font)

        input_gb_sizer.Add(self.raw_select_button, wx.GBPosition(0, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.d_select_button = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u".d", wx.DefaultPosition,
                                         wx.Size(btn_width, -1), 0)
        self.d_select_button.SetFont(common_font)

        input_gb_sizer.Add(self.d_select_button, wx.GBPosition(0, 2), wx.GBSpan(1, 2), wx.ALL, 5)

        self.wiff_select_button = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u".wiff", wx.DefaultPosition,
                                            wx.Size(btn_width, -1), 0)
        self.wiff_select_button.SetFont(common_font)

        input_gb_sizer.Add(self.wiff_select_button, wx.GBPosition(0, 4), wx.GBSpan(1, 2), wx.ALL, 5)

        self.clear_button = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Clear", wx.DefaultPosition,
                                      wx.Size(btn_width, -1), 0)
        self.clear_button.SetFont(common_font)

        input_gb_sizer.Add(self.clear_button, wx.GBPosition(0, 6), wx.GBSpan(1, 2), wx.ALL, 5)

        self.raw_file_path_text = wx.TextCtrl(input_sb_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                              wx.DefaultPosition, wx.Size(350, 200), wx.TE_MULTILINE | wx.TE_RICH2)
        self.raw_file_path_text.SetFont(common_font)

        input_gb_sizer.Add(self.raw_file_path_text, wx.GBPosition(1, 0), wx.GBSpan(5, 8), wx.ALL | wx.EXPAND, 5)


        self.output_path_choose_button = wx.Button(input_sb_sizer.GetStaticBox(), wx.ID_ANY, u"Output dir",
                                                   wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        self.output_path_choose_button.SetFont(common_font)

        input_gb_sizer.Add(self.output_path_choose_button, wx.GBPosition(6, 0), wx.GBSpan(1, 2),
                           wx.ALIGN_RIGHT | wx.ALL, 5)

        self.file_output_dir_text = wx.TextCtrl(input_sb_sizer.GetStaticBox(), wx.ID_ANY, setting.output_dir_base,
                                                wx.DefaultPosition, wx.Size(250, -1), 0)
        self.file_output_dir_text.SetFont(common_font)

        input_gb_sizer.Add(self.file_output_dir_text, wx.GBPosition(6, 2), wx.GBSpan(1, 6), wx.ALL | wx.EXPAND, 5)

        input_gb_sizer.AddGrowableCol(6)

        input_sb_sizer.Add(input_gb_sizer, 1, wx.EXPAND, 5)

        self.SetSizer(input_sb_sizer)
        self.Layout()

    def __del__(self):
        pass


class RunControlPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(600, 100), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        run_info_gb_sizer = wx.GridBagSizer(0, 0)
        run_info_gb_sizer.SetFlexibleDirection(wx.BOTH)
        run_info_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.run_button = wx.Button(self, wx.ID_ANY, u"Run", wx.DefaultPosition, wx.DefaultSize, 0)
        self.run_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.run_button, wx.GBPosition(1, 4), wx.GBSpan(1, 2), wx.ALL, 5)

        self.run_status_button = wx.Button(self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.Size(25, -1),
                                           wx.BU_NOTEXT)
        run_info_gb_sizer.Add(self.run_status_button, wx.GBPosition(1, 7), wx.GBSpan(1, 1), wx.ALL, 5)

        self.run_status_label = wx.StaticText(self, wx.ID_ANY, u"Finished", wx.DefaultPosition, wx.DefaultSize, 0)
        self.run_status_label.SetFont(common_font)

        self.run_status_label.Wrap(-1)

        run_info_gb_sizer.Add(self.run_status_label, wx.GBPosition(1, 8), wx.GBSpan(1, 1), wx.ALIGN_CENTER | wx.ALL, 5)

        self.stop_button = wx.Button(self, wx.ID_ANY, u"Stop", wx.DefaultPosition, wx.DefaultSize, 0)
        self.stop_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.stop_button, wx.GBPosition(1, 10), wx.GBSpan(1, 2), wx.ALL, 5)

        self.SetSizer(run_info_gb_sizer)
        self.Layout()

    def __del__(self):
        pass


class LogPanel(wx.Panel):
    def __init__(self, parent, pos=wx.DefaultPosition, style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, pos=pos, style=style, name=name)
        log_sb = wx.StaticBox(self, wx.ID_ANY, u"Log")
        log_sb.SetFont(common_font)
        log_info_box_sizer = wx.StaticBoxSizer(log_sb, wx.VERTICAL)

        log_info_sizer = wx.GridBagSizer(0, 0)
        log_info_sizer.SetFlexibleDirection(wx.BOTH)
        log_info_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.log_text = wx.TextCtrl(log_info_box_sizer.GetStaticBox(), wx.ID_ANY, wx.EmptyString,
                                    wx.DefaultPosition, wx.DefaultSize,
                                    style=wx.TE_READONLY | wx.TE_MULTILINE | wx.TE_RICH2)
        # self.log_text.Enable(False)
        self.log_text.SetFont(common_font)

        log_info_sizer.Add(self.log_text, wx.GBPosition(0, 0), wx.GBSpan(1, 1), wx.ALL | wx.EXPAND, 5)

        log_info_box_sizer.Add(log_info_sizer, 1, wx.EXPAND, 5)

        log_info_sizer.AddGrowableCol(0)
        log_info_sizer.AddGrowableRow(0)

        self.SetSizer(log_info_box_sizer)
        self.Layout()

    def __del__(self):
        pass


class OutputPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(400, 200), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        ri_sb = wx.StaticBox(self, wx.ID_ANY, u"Run info")
        ri_sb.SetFont(common_font)
        output_sb_sizer = wx.StaticBoxSizer(ri_sb, wx.VERTICAL)

        output_gb_sizer = wx.GridBagSizer(0, 0)
        output_gb_sizer.SetFlexibleDirection(wx.BOTH)
        output_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.msconvert_pro_label = wx.StaticText(output_sb_sizer.GetStaticBox(), wx.ID_ANY, u"MSConvert progress",
                                                 wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.msconvert_pro_label.SetFont(common_font)

        self.msconvert_pro_label.Wrap(-1)

        output_gb_sizer.Add(self.msconvert_pro_label, wx.GBPosition(2, 1), wx.GBSpan(1, 2), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.msconvert_gauge = wx.Gauge(output_sb_sizer.GetStaticBox(), wx.ID_ANY, 100, wx.DefaultPosition,
                                        wx.Size(240, -1), wx.GA_HORIZONTAL)
        self.msconvert_gauge.SetValue(0)
        output_gb_sizer.Add(self.msconvert_gauge, wx.GBPosition(2, 3), wx.GBSpan(1, 4), wx.ALL | wx.EXPAND, 5)

        self.msconvert_pro_label = wx.StaticText(output_sb_sizer.GetStaticBox(), wx.ID_ANY, u"0/0", wx.DefaultPosition,
                                                 wx.DefaultSize, 0)
        self.msconvert_pro_label.SetFont(common_font)

        self.msconvert_pro_label.Wrap(-1)

        output_gb_sizer.Add(self.msconvert_pro_label, wx.GBPosition(2, 7), wx.GBSpan(1, 1), wx.ALL, 5)

        self.m_staticText9 = wx.StaticText(output_sb_sizer.GetStaticBox(), wx.ID_ANY, u"DIA-NN progress",
                                           wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.m_staticText9.SetFont(common_font)

        self.m_staticText9.Wrap(-1)

        output_gb_sizer.Add(self.m_staticText9, wx.GBPosition(3, 1), wx.GBSpan(1, 2), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.diann_gauge = wx.Gauge(output_sb_sizer.GetStaticBox(), wx.ID_ANY, 100, wx.DefaultPosition,
                                    wx.Size(240, -1), wx.GA_HORIZONTAL)
        self.diann_gauge.SetValue(0)
        output_gb_sizer.Add(self.diann_gauge, wx.GBPosition(3, 3), wx.GBSpan(1, 4), wx.ALL | wx.EXPAND, 5)

        self.diann_pro_label = wx.StaticText(output_sb_sizer.GetStaticBox(), wx.ID_ANY, u"0/0", wx.DefaultPosition,
                                             wx.DefaultSize, 0)
        self.diann_pro_label.SetFont(common_font)

        self.diann_pro_label.Wrap(-1)

        output_gb_sizer.Add(self.diann_pro_label, wx.GBPosition(3, 7), wx.GBSpan(1, 1), wx.ALL, 5)

        self.all_progress_label = wx.StaticText(output_sb_sizer.GetStaticBox(), wx.ID_ANY, u"All progress",
                                                wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.all_progress_label.SetFont(common_font)

        self.all_progress_label.Wrap(-1)

        output_gb_sizer.Add(self.all_progress_label, wx.GBPosition(4, 1), wx.GBSpan(1, 2), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.all_progress_gauge = wx.Gauge(output_sb_sizer.GetStaticBox(), wx.ID_ANY, 100, wx.DefaultPosition,
                                           wx.Size(240, -1),
                                           wx.GA_HORIZONTAL)
        self.all_progress_gauge.SetValue(0)
        output_gb_sizer.Add(self.all_progress_gauge, wx.GBPosition(4, 3), wx.GBSpan(1, 4), wx.ALL | wx.EXPAND, 5)

        self.all_pro_label = wx.StaticText(output_sb_sizer.GetStaticBox(), wx.ID_ANY, u"0/0", wx.DefaultPosition,
                                           wx.DefaultSize, 0)
        self.all_pro_label.SetFont(common_font)

        self.all_pro_label.Wrap(-1)

        output_gb_sizer.Add(self.all_pro_label, wx.GBPosition(4, 7), wx.GBSpan(1, 1), wx.ALL, 5)

        output_sb_sizer.Add(output_gb_sizer, 1, wx.EXPAND, 5)

        output_gb_sizer.AddGrowableCol(4)

        self.SetSizer(output_sb_sizer)
        self.Layout()

    def __del__(self):
        pass
