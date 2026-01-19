import json

import wx
import wx.grid
from pubsub import pub

from applet import common_utils
from applet.event_handler.data_info_event_handler import DataInfoDIAEventHandler, \
    DataInfoDiaNNEventHandler
from applet.event_handler.data_run_event_handler import DataRunPanelEventHandler
from applet.event_handler.monitor_event import MonitorEventHandler
from applet.gui.about_panel import AboutInfoPanel
from applet.gui.common_config import common_font
from applet.gui.data_info_panel import DataInfoPanel
from applet.gui.monitor_info_panel import MonitorPanel
from applet.gui.run_info_panel import RunInfoPanel

from loguru import logger
from applet.obj.runtime_data_obj import runtime_data


class MyListBook(wx.Listbook):

    def __init__(self, parent):
        wx.Listbook.__init__(self, parent, wx.ID_ANY)

        imagelist = wx.ImageList(64, 64)
        imagelist.Add(wx.Bitmap('./resource/icon/about.png', wx.BITMAP_TYPE_ANY))
        imagelist.Add(wx.Bitmap('./resource/icon/param.png', wx.BITMAP_TYPE_ANY))
        imagelist.Add(wx.Bitmap('./resource/icon/draw.png', wx.BITMAP_TYPE_ANY))
        imagelist.Add(wx.Bitmap('./resource/icon/ai.png', wx.BITMAP_TYPE_ANY))
        imagelist.Add(wx.Bitmap('./resource/icon/mini.png', wx.BITMAP_TYPE_ANY))
        imagelist.Add(wx.Bitmap('./resource/icon/set.png', wx.BITMAP_TYPE_ANY))
        # imagelist.Add(wx.Bitmap('./resource/icon/help.png', wx.BITMAP_TYPE_ANY))
        self.AssignImageList(imagelist)


class MainBox(wx.Frame):

    def __init__(self, ):
        logger.info('start init frame')

        wx.Frame.__init__(self, None, title=common_utils.VERSION,
                          size=(1320, 700))

        self.SetIcon(wx.Icon('./resource/logo/iDIAQC-logo.png', wx.BITMAP_TYPE_PNG))

        self.Centre(wx.BOTH)

        main_panel = wx.Panel(self)

        self.notebook = MyListBook(main_panel)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.notebook, 1, wx.ALL | wx.EXPAND, 5)
        main_panel.SetSizer(sizer)

        self.about_info_panel = AboutInfoPanel(self.notebook)
        self.run_info_panel = RunInfoPanel(self.notebook)
        self.monitor_panel = MonitorPanel(self.notebook)
        self.data_info_panel = DataInfoPanel(self.notebook)

        self.notebook.AddPage(self.about_info_panel, 'About', select=True, imageId=0)
        self.notebook.AddPage(self.run_info_panel, 'Manual mode', imageId=1)
        self.notebook.AddPage(self.data_info_panel, 'Data', imageId=2)
        self.notebook.AddPage(self.monitor_panel, 'Monitoring mode', imageId=3)

        self.notebook.SetFont(common_font)

        self.data_panel_event_handler = DataInfoDIAEventHandler(self.data_info_panel.dia_page)

        # self.dda_data_panel_event_handler = DataInfoDDAEventHandler(self.data_info_panel.dda_page)

        self.diann_data_panel_event_handler = DataInfoDiaNNEventHandler(self.data_info_panel.diann_info_page)

        self.data_run_panel_event_handler = DataRunPanelEventHandler(self.run_info_panel)

        self.Bind(wx.EVT_RADIOBUTTON, self.data_run_panel_event_handler.click_dia,
                  self.run_info_panel.config_panel.dia_btn)
        # self.Bind(wx.EVT_RADIOBUTTON, self.data_run_panel_event_handler.click_dda,
        #           self.run_info_panel.config_panel.dda_btn)

        self.Bind(wx.EVT_BUTTON, self.data_run_panel_event_handler.msconvert_path_choose,
                  self.run_info_panel.config_panel.msconvert_btn)

        #
        self.Bind(wx.EVT_BUTTON, self.data_run_panel_event_handler.raw_file_choose,
                  self.run_info_panel.input_panel.raw_select_button)
        self.Bind(wx.EVT_BUTTON, self.data_run_panel_event_handler.d_file_choose,
                  self.run_info_panel.input_panel.d_select_button)
        self.Bind(wx.EVT_BUTTON, self.data_run_panel_event_handler.wiff_file_choose,
                  self.run_info_panel.input_panel.wiff_select_button)

        self.Bind(wx.EVT_BUTTON, self.data_run_panel_event_handler.clear_button_click,
                  self.run_info_panel.input_panel.clear_button)

        self.Bind(wx.EVT_BUTTON, self.data_run_panel_event_handler.run_btn_click,
                  self.run_info_panel.run_control_panel.run_button)
        self.Bind(wx.EVT_BUTTON, self.data_run_panel_event_handler.stop_btn_click,
                  self.run_info_panel.run_control_panel.stop_button)
        #
        self.Bind(wx.EVT_BUTTON, self.data_run_panel_event_handler.output_path_choose,
                  self.run_info_panel.input_panel.output_path_choose_button)

        #
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.load_grid_data_with_param,
                  self.data_info_panel.dia_page.run_data_panel.search_button)
        #
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.draw_dir_choose,
                  self.data_info_panel.dia_page.data_control_panel.output_path_choose_button)
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.draw_all,
                  self.data_info_panel.dia_page.data_control_panel.draw_all_button)
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.draw_selected,
                  self.data_info_panel.dia_page.data_control_panel.draw_selected_button)
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.draw_search,
                  self.data_info_panel.dia_page.data_control_panel.draw_search_button)

        #
        self.Bind(wx.EVT_BUTTON, self.data_panel_event_handler.export_pred,
                  self.data_info_panel.dia_page.data_control_panel.export_pred_button)

        # self.Bind(wx.EVT_BUTTON, self.dda_data_panel_event_handler.load_grid_data_with_param,
        #           self.data_info_panel.dda_page.run_data_panel.search_button)

        self.Bind(wx.EVT_BUTTON, self.diann_data_panel_event_handler.load_grid_data_with_param,
                  self.data_info_panel.diann_info_page.run_diann_info_panel.search_button)

        # self.Bind(diann_data_panel_event_handler)

        self.monitor_event_handler = MonitorEventHandler(self.monitor_panel)
        #
        self.Bind(wx.EVT_BUTTON, self.monitor_event_handler.add_monitor_config,
                  self.monitor_panel.monitor_control_panel.add_monitor_config_btn)

        self.Bind(wx.EVT_BUTTON, self.monitor_event_handler.monitor_start_click,
                  self.monitor_panel.monitor_control_panel.monitor_start_button)
        self.Bind(wx.EVT_BUTTON, self.monitor_event_handler.monitor_stop_click,
                  self.monitor_panel.monitor_control_panel.monitor_stop_button)

        # self.Bind(wx.EVT_RADIOBUTTON, self.monitor_event_handler.click_dia, self.monitor_panel.monitor_control_panel.dia_btn)
        # self.Bind(wx.EVT_RADIOBUTTON, self.monitor_event_handler.click_dda, self.monitor_panel.monitor_control_panel.dda_btn)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        # self.list.Bind(wx.EVT_CONTEXT_MENU, self.OnContextMenu)

        self.Bind(wx.EVT_CONTEXT_MENU, self.monitor_event_handler.on_context_menu,
                  self.monitor_panel.monitor_control_panel.monitor_data_list)

        self.data_panel_event_handler.load_grid_data()
        # self.dda_data_panel_event_handler.load_grid_data()

        #
        self.choose_file_list = []

        #
        pub.subscribe(self.sub_analysis_info, 'analysis_info')
        pub.subscribe(self.sub_reload_data, 'channel_reload_data')
        pub.subscribe(self.monitor_log, 'monitor_log')
        pub.subscribe(self.monitor_event_handler.load_monitor_data_list, 'load_monitor_config')

        logger.info('end init frame')

    def on_close(self, event):
        if runtime_data.analysis_thread is not None:
            runtime_data.analysis_thread.set_run_flag(False)

        if self.monitor_event_handler.stop_event is not None:
            self.monitor_event_handler.stop_event.set()

        event.Skip()

    def sub_analysis_info(self, msg):
        logger.info('receive msg: {}'.format(msg))
        # {'status': 1, 'msg': 'xxxx', 'start_time':5555}
        an_info = json.loads(msg)
        status = an_info['status']
        step = an_info['step']
        msg = an_info['msg']
        if status == 99:
            self.sub_analysis_over(msg)
        else:
            if msg is not None and len(msg) > 0:
                self.run_info_panel.log_panel.log_text.AppendText('{}\r\n'.format(an_info['msg']))
            if status == 1:
                #
                self.sub_analysis_step(None)
            elif status == 11:
                #
                self.add_one_msconvert_deal()
            elif status == 21:
                #
                self.add_one_diann_deal()
            elif status == 2:
                #
                self.analysis_stop_stopped()
            elif status == 3:
                #
                self.analysis_error_stopped()
            elif status == 9:
                pass

    def monitor_log(self, msg):
        logger.info('receive monitor msg: {}'.format(msg))
        an_info = json.loads(msg)
        msg = an_info['msg']
        self.monitor_panel.monitor_log_panel.log_text.AppendText('{}\r\n'.format(msg))

    def sub_reload_data(self, msg):
        logger.info('reload data')
        self.data_panel_event_handler.load_grid_data()

    #
    def sub_analysis_over(self, msg):
        logger.info('sub analysis over msg')
        self.run_info_panel.log_panel.log_text.AppendText('{}\r\n'.format(msg))
        self.change_status_btn_label_finished()
        self.data_panel_event_handler.load_grid_data()

    def sub_analysis_step(self, msg):
        runtime_data.deal_step += 1
        self.run_info_panel.output_panel.all_progress_gauge.SetValue(runtime_data.deal_step)
        self.run_info_panel.output_panel.all_pro_label.SetLabel(
            '{}/{}'.format(runtime_data.deal_step, runtime_data.all_step_count))

    #
    def add_one_msconvert_deal(self):
        runtime_data.msconvert_deal_count += 1
        self.run_info_panel.output_panel.msconvert_gauge.SetValue(runtime_data.msconvert_deal_count)
        self.run_info_panel.output_panel.msconvert_pro_label.SetLabel(
            '{}/{}'.format(runtime_data.msconvert_deal_count, runtime_data.msconvert_all_count))

    #
    def add_one_diann_deal(self):
        runtime_data.diann_deal_count += 1
        self.run_info_panel.output_panel.diann_gauge.SetValue(runtime_data.diann_deal_count)
        self.run_info_panel.output_panel.diann_pro_label.SetLabel(
            '{}/{}'.format(runtime_data.diann_deal_count, runtime_data.diann_all_count))


    def analysis_stop_stopped(self):
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('STOPPED')

        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stop')
        self.run_info_panel.run_control_panel.stop_button.Disable()

        self.run_info_panel.run_control_panel.run_button.Enable()


    def analysis_error_stopped(self):
        self.run_info_panel.run_control_panel.run_status_button.SetBackgroundColour(runtime_data.ERROR_COLOR)
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('ERROR')

        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stop')
        self.run_info_panel.run_control_panel.stop_button.Disable()

        self.run_info_panel.run_control_panel.run_button.Enable()


    def change_status_btn_label_finished(self):
        self.run_info_panel.run_control_panel.run_status_button.SetBackgroundColour(runtime_data.OVER_COLOR)
        self.run_info_panel.run_control_panel.run_status_label.SetLabel('Finished')

        self.run_info_panel.run_control_panel.run_button.Enable()

        self.run_info_panel.run_control_panel.stop_button.SetLabel('Stop')
        self.run_info_panel.run_control_panel.stop_button.Disable()
