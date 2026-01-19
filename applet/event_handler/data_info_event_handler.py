import os
from collections import defaultdict

import wx
from loguru import logger

from applet.ai_service.prediction_score_service import PredictionScoreService
from applet.db import db_utils_run_data
from applet.gui.data_info_panel import DataInfoDIAPanel, DiaNNInfoPanel
from applet.service.dia.pic_service import PicService

PRED_KEY_LIST = ['lc', 'F1', 'F2', 'F3', 'ms', 'F4', 'F5', 'F6', 'F7', 'F8', 'F9', 'F10', 'F11', 'F12', 'F13', 'F14',
                 'F15']


class DataInfoDIAEventHandler(object):
    def __init__(self, data_info_panel: DataInfoDIAPanel):
        self.data_info_panel = data_info_panel

    def get_run_pred_map(self, seq_id_list):
        pred_info_list = db_utils_run_data.query_all_pred_info(seq_id_list)
        # 先初始化
        seq_pred_dict = defaultdict(dict)
        for pred_info in pred_info_list:
            if pred_info.pred_label == 0:
                pred_label = 'Qualified '
            elif pred_info.pred_label == 1:
                pred_label = 'Unqualified'
            else:
                pred_label = 'Unknown'
            seq_pred_dict[pred_info.seq_id][pred_info.pred_key] = pred_label
        return seq_pred_dict

    '''
    
    '''

    def load_grid_data(self):
        run_data_type = self.get_run_data_type_checked()
        run_info_list = db_utils_run_data.query_run_info_all(run_data_type)
        if len(run_info_list) == 0:
            return

        ins_name_list = list(set([d.inst_name for d in run_info_list]))
        ins_name_list.insert(0, 'All')

        #
        seq_id_list = [d.seq_id for d in run_info_list]
        pred_seq_map = self.get_run_pred_map(seq_id_list)

        ope_grid = self.data_info_panel.run_data_panel.run_data_list_run_grid
        if ope_grid.NumberRows > 0:
            ope_grid.DeleteRows(pos=0, numRows=ope_grid.NumberRows)

        ope_grid.AppendRows(len(run_info_list))
        row_index = 0

        for run_info in run_info_list:
            ope_grid.SetCellValue(row_index, 1, str(run_info.inst_name))
            ope_grid.SetCellValue(row_index, 2, str(run_info.run_id))
            ope_grid.SetCellValue(row_index, 3, str(run_info.run_name))

            for d_index, pred_key in enumerate(PRED_KEY_LIST):
                if run_info.file_type != 'D' and pred_key == 'F15':
                    ope_grid.SetCellValue(row_index, d_index + 4, '-')
                else:
                    ope_grid.SetCellValue(row_index, d_index + 4, str(pred_seq_map[run_info.seq_id][pred_key]))
            ope_grid.SetCellValue(row_index, 21, str(run_info.gmt_create))
            row_index = row_index + 1

    def export_pred(self, event):
        output_path = self.data_info_panel.data_control_panel.pic_output_dir_text.GetValue()
        if output_path is None or len(output_path) == 0:
            msg_box = wx.MessageDialog(None, 'No selected output dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        try:
            data_source = self.get_run_data_type_checked()
            pred_score_service = PredictionScoreService(None, None, None, None)
            pred_score_service.save_to_csv(output_path, data_source)
            msg_box = wx.MessageDialog(None, 'Export pred csv success', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        except Exception:
            logger.exception('export pred exception')
            msg_box = wx.MessageDialog(None, 'Export pred csv exception', 'alert', wx.YES_DEFAULT | wx.ICON_ERROR)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

    def get_run_data_type_checked(self):
        if self.data_info_panel.run_data_panel.run_data_radio.GetValue():
            return 0
        elif self.data_info_panel.run_data_panel.monitor_data_radio.GetValue():
            return 1
        else:
            return None

    '''
    '''

    def load_grid_data_with_param(self, event):
        # ，
        run_data_type = self.get_run_data_type_checked()

        ins_select_id = self.data_info_panel.run_data_panel.ins_id_choice.GetSelection()
        if ins_select_id == -1 or self.data_info_panel.run_data_panel.ins_id_choice.GetItems()[ins_select_id] == 'All':
            ins_name = None
        else:
            ins_name = self.data_info_panel.run_data_panel.ins_id_choice.GetItems()[ins_select_id]

        page_num_select_id = self.data_info_panel.run_data_panel.num_choice.GetSelection()
        if page_num_select_id == -1 or self.data_info_panel.run_data_panel.num_choice.GetItems()[
            page_num_select_id] == 'All':
            page_num = None
        else:
            page_num = int(self.data_info_panel.run_data_panel.num_choice.GetItems()[page_num_select_id])
        run_info_list = db_utils_run_data.query_run_info_param(ins_name, page_num, run_data_type)

        ope_grid = self.data_info_panel.run_data_panel.run_data_list_run_grid
        if ope_grid.NumberRows > 0:
            ope_grid.DeleteRows(pos=0, numRows=ope_grid.NumberRows)

        if len(run_info_list) == 0:
            return

        #
        seq_id_list = [d.seq_id for d in run_info_list]
        pred_seq_map = self.get_run_pred_map(seq_id_list)

        #
        run_info_list.sort(key=lambda x: x.id, reverse=False)
        ope_grid.AppendRows(len(run_info_list))
        row_index = 0
        for run_info in run_info_list:
            ope_grid.SetCellValue(row_index, 1, str(run_info.inst_name))
            ope_grid.SetCellValue(row_index, 2, str(run_info.run_id))
            ope_grid.SetCellValue(row_index, 3, str(run_info.run_name))
            for d_index, pred_key in enumerate(PRED_KEY_LIST):
                if run_info.file_type != 'D' and pred_key == 'F15':
                    ope_grid.SetCellValue(row_index, d_index + 4, '-')
                else:
                    ope_grid.SetCellValue(row_index, d_index + 4, str(pred_seq_map[run_info.seq_id][pred_key]))

            ope_grid.SetCellValue(row_index, 21, str(run_info.gmt_create))
            row_index = row_index + 1

    def draw_dir_choose(self, event):
        dir_choose_bt = wx.DirDialog(self.data_info_panel, 'choose output path dir', style=wx.DD_DIR_MUST_EXIST)
        if dir_choose_bt.ShowModal() == wx.ID_OK:
            self.data_info_panel.data_control_panel.pic_output_dir_text.ChangeValue(dir_choose_bt.GetPath())
        dir_choose_bt.Destroy()

    def draw_all(self, event):
        output_path = self.data_info_panel.data_control_panel.pic_output_dir_text.GetValue()
        if output_path is None or len(output_path) == 0:
            msg_box = wx.MessageDialog(None, 'No selected output dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        data_source = self.get_run_data_type_checked()

        try:
            pic_deal_service = PicService(output_path, None, logger, None, pub_channel='')
            draw_result = pic_deal_service.draw_pic_all(data_source)
            if draw_result:
                msg_box = wx.MessageDialog(None, 'Draw pic success', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
                if msg_box.ShowModal() == wx.ID_YES:
                    msg_box.Destroy()
                return
            else:
                msg_box = wx.MessageDialog(None, 'Draw pic fail', 'alert', wx.YES_DEFAULT | wx.ICON_ERROR)
                if msg_box.ShowModal() == wx.ID_YES:
                    msg_box.Destroy()
                return
        except Exception:
            logger.exception('export pred exception')
            msg_box = wx.MessageDialog(None, 'Draw pic exception', 'alert', wx.YES_DEFAULT | wx.ICON_ERROR)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

    def draw_selected(self, event):
        selected_run_id = []
        run_grid = self.data_info_panel.run_data_panel.run_data_list_run_grid
        row_nums = run_grid.NumberRows
        if row_nums > 0:
            for row_index in range(row_nums):
                if run_grid.GetCellValue(row_index, 0):
                    selected_run_id.append(str(run_grid.GetCellValue(row_index, 2)))

        if len(selected_run_id) == 0:
            msg_box = wx.MessageDialog(None, 'No selected raw file', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

        output_path = self.data_info_panel.data_control_panel.pic_output_dir_text.GetValue()
        if output_path is None or len(output_path) == 0:
            msg_box = wx.MessageDialog(None, 'No selected output dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        try:
            pic_deal_service = PicService(output_path, None, logger, selected_run_id, pub_channel='')
            draw_result = pic_deal_service.draw_pic_select()
            if draw_result:
                msg_box = wx.MessageDialog(None, 'Draw pic success', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
                if msg_box.ShowModal() == wx.ID_YES:
                    msg_box.Destroy()
                return
            else:
                msg_box = wx.MessageDialog(None, 'Draw pic fail', 'alert', wx.YES_DEFAULT | wx.ICON_ERROR)
                if msg_box.ShowModal() == wx.ID_YES:
                    msg_box.Destroy()
                return
        except Exception:
            logger.exception('export pred exception')
            msg_box = wx.MessageDialog(None, 'Draw pic exception', 'alert', wx.YES_DEFAULT | wx.ICON_ERROR)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return

    def draw_search(self, event):
        #
        param_dict = {}
        output_path = self.data_info_panel.data_control_panel.pic_output_dir_text.GetValue()
        if output_path is None or len(output_path) == 0:
            msg_box = wx.MessageDialog(None, 'No selected output dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        ins_select_id = self.data_info_panel.run_data_panel.ins_id_choice.GetSelection()
        if ins_select_id == -1 or self.data_info_panel.run_data_panel.ins_id_choice.GetItems()[ins_select_id] == 'All':
            inst_name = None
        else:
            inst_name = self.data_info_panel.run_data_panel.ins_id_choice.GetItems()[ins_select_id]

        page_num_select_id = self.data_info_panel.run_data_panel.num_choice.GetSelection()
        if page_num_select_id == -1 or self.data_info_panel.run_data_panel.num_choice.GetItems()[
            page_num_select_id] == 'All':
            search_num = None
        else:
            search_num = int(self.data_info_panel.run_data_panel.num_choice.GetItems()[page_num_select_id])

        run_data_type = self.get_run_data_type_checked()

        param_dict['inst_name'] = inst_name
        param_dict['search_num'] = search_num
        param_dict['run_data_type'] = run_data_type

        output_path = self.data_info_panel.data_control_panel.pic_output_dir_text.GetValue()
        if output_path is None or len(output_path) == 0:
            msg_box = wx.MessageDialog(None, 'No selected output dir', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return
        try:
            pic_deal_service = PicService(output_path, None, logger, None, pub_channel='')
            draw_result = pic_deal_service.draw_pic_param(param_dict)
            if draw_result:
                msg_box = wx.MessageDialog(None, 'Draw pic success', 'alert', wx.YES_DEFAULT | wx.ICON_QUESTION)
                if msg_box.ShowModal() == wx.ID_YES:
                    msg_box.Destroy()
                return
            else:
                msg_box = wx.MessageDialog(None, 'Draw pic fail', 'alert', wx.YES_DEFAULT | wx.ICON_ERROR)
                if msg_box.ShowModal() == wx.ID_YES:
                    msg_box.Destroy()
                return
        except Exception:
            logger.exception('export pred exception')
            msg_box = wx.MessageDialog(None, 'Draw pic exception', 'alert', wx.YES_DEFAULT | wx.ICON_ERROR)
            if msg_box.ShowModal() == wx.ID_YES:
                msg_box.Destroy()
            return


class DataInfoDiaNNEventHandler(object):

    def __init__(self, data_info_panel: DiaNNInfoPanel):
        self.data_info_panel = data_info_panel

    '''
    
    '''

    def load_grid_data_with_param(self, event):

        ope_grid = self.data_info_panel.run_diann_info_panel.run_data_list_run_grid
        if ope_grid.NumberRows > 0:
            ope_grid.DeleteRows(pos=0, numRows=ope_grid.NumberRows)

        # 查询run data
        run_data_list = db_utils_run_data.query_diann_data()

        ope_grid.AppendRows(len(run_data_list))
        row_index = 0
        for run_info in run_data_list:
            ope_grid.SetCellValue(row_index, 1, str(run_info.run_prefix))
            ope_grid.SetCellValue(row_index, 2, str(run_info.file_name))
            ope_grid.SetCellValue(row_index, 3, str(run_info.precursor_ident))
            ope_grid.SetCellValue(row_index, 4, str(run_info.protein_ident))

            row_index = row_index + 1
