import os

import wx

from applet.default_config import setting
from applet.gui.run_info_panel import RunInfoPanel

from loguru import logger
from applet.obj.Entity import FileInfo, FileTypeEnum
from applet.obj.runtime_data_obj import runtime_data
from applet import common_utils
from applet.thread_util.analysis_thread import AnalysisThread
from pubsub import pub


common_config = common_utils.read_yml()
ins_list = common_config['inst']



class DataRunPanelEventHandler(object):
    def __init__(self, run_info_panel: RunInfoPanel):
        self.run_info_panel = run_info_panel

    def click_dia(self, event):
        self.run_info_panel.config_panel.diann_exe_btn.SetLabel('DIA-NN.exe')
        self.run_info_panel.config_panel.diann_path_text.SetValue(setting.diann_exe_path)

        self.run_info_panel.output_panel.m_staticText9.SetLabel('DIA-NN progress')
        pass

    def click_dda(self, event):
        self.run_info_panel.config_panel.diann_exe_btn.SetLabel('FragPipe dir')
        self.run_info_panel.config_panel.diann_path_text.SetValue('FragPipe-jre-21.1\\fragpipe')

        self.run_info_panel.output_panel.m_staticText9.SetLabel('FragPipe progress')

    def msconvert_path_choose(self, event):
        filesFilter = "msconvert.exe"
        file_choose_bt = wx.FileDialog(self.run_info_panel, message='Choose msconvert.exe', wildcard=filesFilter,
                                       style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.run_info_panel.config_panel.msconvert_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    def raw_file_choose(self, event):
        file_filter = "*.raw"
        self.common_file_choose(file_filter, FileTypeEnum.RAW)

    def d_file_choose(self, event):
        file_filter = "*.d"
        dir_choose_bt = wx.DirDialog(self.run_info_panel, 'Choose .d file dir', style=wx.DD_DIR_MUST_EXIST)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            choose_file_path = dir_choose_bt.GetPath()
            file_info = FileInfo()
            file_info.file_path = choose_file_path
            file_info.file_type = FileTypeEnum.D
            runtime_data.choose_file_list.append(file_info)

            path_text = '\n'.join([data.file_path for data in runtime_data.choose_file_list])
            self.run_info_panel.input_panel.raw_file_path_text.ChangeValue(path_text)
            runtime_data.msconvert_all_count = len(runtime_data.choose_file_list)
            runtime_data.msconvert_deal_count = 0
            self.run_info_panel.output_panel.msconvert_gauge.SetRange(runtime_data.msconvert_all_count)
            self.run_info_panel.output_panel.msconvert_gauge.SetValue(runtime_data.msconvert_deal_count)
            self.run_info_panel.output_panel.msconvert_pro_label.SetLabel('0/{}'.format(runtime_data.msconvert_all_count))

            self.run_info_panel.output_panel.diann_gauge.SetRange(runtime_data.diann_all_count)
            runtime_data.diann_deal_count = 0
            self.run_info_panel.output_panel.diann_gauge.SetValue(runtime_data.diann_deal_count)
            self.run_info_panel.output_panel.diann_pro_label.SetLabel('0/{}'.format(runtime_data.diann_all_count))

        dir_choose_bt.Destroy()


    def wiff_file_choose(self, event):
        file_filter = "*.wiff"
        self.common_file_choose(file_filter, FileTypeEnum.WIFF)

    def common_file_choose(self, filesFilter, file_type):
        file_choose_bt = wx.FileDialog(self.run_info_panel, message='Choose raw', wildcard=filesFilter, style=wx.FD_MULTIPLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            choose_file_path_list = file_choose_bt.GetPaths()
            for choose_file_path in choose_file_path_list:
                file_info = FileInfo()
                file_info.file_path = choose_file_path
                file_info.file_type = file_type
                runtime_data.choose_file_list.append(file_info)
            path_text = '\n'.join([data.file_path for data in runtime_data.choose_file_list])
            self.run_info_panel.input_panel.raw_file_path_text.ChangeValue(path_text)
            runtime_data.msconvert_all_count = len(runtime_data.choose_file_list)
            runtime_data.msconvert_deal_count = 0
            self.run_info_panel.output_panel.msconvert_gauge.SetRange(runtime_data.msconvert_all_count)
            self.run_info_panel.output_panel.msconvert_gauge.SetValue(runtime_data.msconvert_deal_count)
            self.run_info_panel.output_panel.msconvert_pro_label.SetLabel('0/{}'.format(runtime_data.msconvert_all_count))

            runtime_data.diann_all_count = len(runtime_data.choose_file_list)
            self.run_info_panel.output_panel.diann_gauge.SetRange(runtime_data.diann_all_count)
            runtime_data.diann_deal_count = 0
            self.run_info_panel.output_panel.diann_gauge.SetValue(runtime_data.diann_deal_count)
            self.run_info_panel.output_panel.diann_pro_label.SetLabel('0/{}'.format(runtime_data.diann_all_count))

        file_choose_bt.Destroy()

    def fasta_choose(self, event):
        file_choose_bt = wx.FileDialog(self, message='choose FASTA file', style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.run_info_panel.config_panel.fasta_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()

    def clear_button_click(self, event):
        runtime_data.choose_file_list = []

        self.run_info_panel.output_panel.msconvert_gauge.SetRange(0)
        self.run_info_panel.output_panel.msconvert_gauge.SetValue(0)
        self.run_info_panel.output_panel.msconvert_pro_label.SetLabel('0/0')

        self.run_info_panel.output_panel.diann_gauge.SetRange(0)
        self.run_info_panel.output_panel.diann_gauge.SetValue(0)
        self.run_info_panel.output_panel.diann_pro_label.SetLabel('0/0')

        self.run_info_panel.output_panel.all_progress_gauge.SetRange(0)
        self.run_info_panel.output_panel.all_progress_gauge.SetValue(0)
        self.run_info_panel.output_panel.all_pro_label.SetLabel('0/0')

        self.run_info_panel.input_panel.raw_file_path_text.ChangeValue('')

    '''
    
    '''
    def output_path_choose(self, event):
        dir_choose_bt = wx.DirDialog(self.run_info_panel, 'Choose output path dir', style=wx.DD_DIR_MUST_EXIST)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            self.run_info_panel.input_panel.file_output_dir_text.ChangeValue(dir_choose_bt.GetPath())
        dir_choose_bt.Destroy()

    def diann_path_choose(self, event):
        filesFilter = "DiaNN.exe"
        file_choose_bt = wx.FileDialog(self.run_info_panel, message='Choose DiaNN.exe', wildcard=filesFilter,
                                       style=wx.FD_DEFAULT_STYLE)
        if file_choose_bt.ShowModal() == wx.ID_OK:
            self.run_info_panel.config_panel.diann_path_text.ChangeValue(file_choose_bt.GetPath())
        file_choose_bt.Destroy()


    def run_btn_click(self, event):
        logger.info('----click start analysis button-------')
        if len(runtime_data.choose_file_list) == 0:
            msg_box = wx.MessageDialog(None, 'Please choose raw file', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        cwd = os.getcwd()
        diann_path = self.run_info_panel.config_panel.diann_path_text.GetValue()
        #
        msconvert_path = self.run_info_panel.config_panel.msconvert_path_text.GetValue()

        #
        output_path = self.run_info_panel.input_panel.file_output_dir_text.GetValue()
        output_path = os.path.join(cwd, output_path)
        if output_path is None or len(output_path) == 0:
            msg_box = wx.MessageDialog(None, 'No selected output dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        #
        ins_select_id = self.run_info_panel.config_panel.ins_id_choice.GetSelection()
        if ins_select_id == -1:
            msg_box = wx.MessageDialog(None, 'Instrument type is not selected', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        inst_name = ins_list[ins_select_id]

        run_prefix = self.run_info_panel.config_panel.run_prefix_text.GetValue()
        if run_prefix is None or len(run_prefix) == 0:
            msg_box = wx.MessageDialog(None, 'Please input instrument id', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        def get_file_type_checked():
            if self.run_info_panel.config_panel.dia_btn.GetValue():
                return 'DIA'
            else:
                return None

        raw_file_type = get_file_type_checked()
        if raw_file_type is None:
            msg_box = wx.MessageDialog(None, 'Please select raw file type', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        if not os.path.exists(output_path):
            os.makedirs(output_path)
        logger.info('----start analysis-------')
        setting.output_dir_base = output_path
        setting.diann_exe_path = r'./DIA-NN\1.8\DiaNN.exe'
        setting.ms_exe_path = msconvert_path

        notify_email = self.run_info_panel.config_panel.notify_email_text.GetValue()
        wx_token = self.run_info_panel.config_panel.wx_token_text.GetValue()
        inst_id = self.run_info_panel.config_panel.run_prefix_text.GetValue()

        setting.notify_email = notify_email
        setting.wx_token = wx_token
        setting.inst_id = inst_id
        setting.save_config()

        thread_output_dir_path = output_path
        try:

            self.run_init(raw_file_type)
            self.analysis_thread = AnalysisThread(os.path.join(cwd, diann_path), msconvert_path, thread_output_dir_path, inst_name,
                                                  run_prefix, runtime_data.choose_file_list, raw_file_type, notify_email, wx_token)
            self.analysis_thread.daemon = True
            self.analysis_thread.start()
            self.analysis_start()
        except Exception as e:
            logger.info('start analysis exception')
            msg_box = wx.MessageDialog(None, 'Start analysis exception {}'.format(e), 'alert',
                                       wx.YES_DEFAULT | wx.ICON_ERROR)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

    def analysis_start(self):
        self.run_info_panel.log_panel.log_text.SetValue('')

        self.run_info_panel.run_control_panel.run_status_button.SetBackgroundColour(runtime_data.RUNNING_COLOR)
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('Running')
        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stop')
        self.run_info_panel.run_control_panel.stop_button.Enable()
        self.run_info_panel.run_control_panel.run_button.Disable()


    def run_init(self, raw_file_type):
        if raw_file_type == 'DIA':
            runtime_data.all_step_count = 11
        elif raw_file_type == 'DDA':
            runtime_data.all_step_count = 3
        runtime_data.msconvert_deal_count = 0
        self.run_info_panel.output_panel.msconvert_gauge.SetRange(runtime_data.msconvert_all_count)
        self.run_info_panel.output_panel.msconvert_gauge.SetValue(runtime_data.msconvert_deal_count)
        self.run_info_panel.output_panel.msconvert_pro_label.SetLabel('0/{}'.format(runtime_data.msconvert_all_count))

        self.run_info_panel.output_panel.diann_gauge.SetRange(runtime_data.diann_all_count)
        runtime_data.diann_deal_count = 0
        self.run_info_panel.output_panel.diann_gauge.SetValue(runtime_data.diann_deal_count)
        self.run_info_panel.output_panel.diann_pro_label.SetLabel('0/{}'.format(runtime_data.diann_all_count))

        runtime_data.deal_step = 0
        self.run_info_panel.output_panel.all_progress_gauge.SetValue(runtime_data.deal_step)
        self.run_info_panel.output_panel.all_progress_gauge.SetRange(runtime_data.all_step_count)
        self.run_info_panel.output_panel.all_pro_label.SetLabel('0/{}'.format(runtime_data.all_step_count))

    def stop_btn_click(self, event):
        logger.info('----click stop analysis button-------')
        #
        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stopping')
        self.run_info_panel.run_control_panel.stop_button.Disable()
        #
        if runtime_data.analysis_thread is not None:
            runtime_data.analysis_thread.set_run_flag(False)
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('Stopping')
        if runtime_data.analysis_thread is None:
            pub.sendMessage('analysis_over', msg=True)

