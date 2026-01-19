import wx
import wx.grid

from applet import common_utils
from applet.gui.common_config import common_font

common_config = common_utils.read_yml()

btn_width = 200


class DataInfoPanel(wx.Notebook):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(400, 100), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Notebook.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        self.dia_page = DataInfoDIAPanel(self)
        self.diann_info_page = DiaNNInfoPanel(self)

        self.AddPage(self.dia_page, "DIA")
        self.AddPage(self.diann_info_page, "DIA-NN info")
        self.Layout()

    def __del__(self):
        pass


class DataInfoDIAPanel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(400, 100), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        run_info_gb_sizer = wx.GridBagSizer(0, 0)
        run_info_gb_sizer.SetFlexibleDirection(wx.BOTH)
        run_info_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.run_data_panel = RunDataPanel(self)
        self.data_control_panel = DataControlPanel(self)

        run_info_gb_sizer.Add(self.run_data_panel, wx.GBPosition(0, 0), wx.GBSpan(6, 10), wx.ALL | wx.EXPAND, 5)
        run_info_gb_sizer.Add(self.data_control_panel, wx.GBPosition(6, 0), wx.GBSpan(3, 10), wx.ALL | wx.EXPAND, 5)

        run_info_gb_sizer.AddGrowableRow(5)
        run_info_gb_sizer.AddGrowableCol(9)

        self.SetSizer(run_info_gb_sizer)
        self.Layout()

    def __del__(self):
        pass


class DataControlPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(-1, 150), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        run_info_gb_sizer = wx.GridBagSizer(0, 0)
        run_info_gb_sizer.SetFlexibleDirection(wx.BOTH)
        run_info_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.output_path_choose_button = wx.Button(self, wx.ID_ANY, u"Output dir",
                                                   wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        self.output_path_choose_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.output_path_choose_button, wx.GBPosition(0, 0), wx.GBSpan(1, 2),
                              wx.ALIGN_RIGHT | wx.ALL, 5)

        self.pic_output_dir_text = wx.TextCtrl(self, wx.ID_ANY, '',
                                               wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.pic_output_dir_text.SetFont(common_font)
        run_info_gb_sizer.Add(self.pic_output_dir_text, wx.GBPosition(0, 2), wx.GBSpan(1, 10),
                              wx.ALL | wx.EXPAND, 5)

        self.draw_all_button = wx.Button(self, wx.ID_ANY, u"Draw all files", wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        self.draw_all_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.draw_all_button, wx.GBPosition(1, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        self.draw_selected_button = wx.Button(self, wx.ID_ANY, u"Draw selected files", wx.DefaultPosition, wx.Size(btn_width, -1),
                                              0)
        self.draw_selected_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.draw_selected_button, wx.GBPosition(1, 2), wx.GBSpan(1, 2), wx.ALL, 5)

        self.draw_search_button = wx.Button(self, wx.ID_ANY, u"Draw search files", wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        self.draw_search_button.SetFont(common_font)

        run_info_gb_sizer.Add(self.draw_search_button, wx.GBPosition(1, 4), wx.GBSpan(1, 2), wx.ALL, 5)

        self.export_pred_button = wx.Button(self, wx.ID_ANY, u"Export prediction results", wx.DefaultPosition, wx.Size(btn_width, -1), 0)
        self.export_pred_button.SetFont(common_font)
        run_info_gb_sizer.Add(self.export_pred_button, wx.GBPosition(2, 0), wx.GBSpan(1, 2), wx.ALL, 5)

        run_info_gb_sizer.AddGrowableCol(10)

        self.SetSizer(run_info_gb_sizer)
        self.Layout()

    def __del__(self):
        pass


class CheckboxRenderer(wx.grid.GridCellBoolRenderer):
    def __init__(self, is_selected):
        wx.grid.GridCellBoolRenderer.__init__(self)
        self.isSelected = is_selected

    def Draw(self, grid, attr, dc, rect, row, col, isSelected):
        self.Draw(grid, attr, dc, rect, row, col, isSelected)


class RunDataPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(800, 400), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        rd_sb = wx.StaticBox(self, wx.ID_ANY, u"Raw file")
        rd_sb.SetFont(common_font)

        info_panel_sb_sizer = wx.StaticBoxSizer(rd_sb, wx.VERTICAL)

        info_panel_gb_sizer = wx.GridBagSizer(0, 0)
        info_panel_gb_sizer.SetFlexibleDirection(wx.BOTH)
        info_panel_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.ins_id_label = wx.StaticText(self, wx.ID_ANY, u"Instrument type",
                                          wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.ins_id_label.SetFont(common_font)

        self.ins_id_label.Wrap(-1)
        info_panel_gb_sizer.Add(self.ins_id_label, wx.GBPosition(0, 0), wx.GBSpan(1, 2), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.ins_id_choice_list = common_config['inst'].copy()
        self.ins_id_choice_list.insert(0, 'All')
        self.ins_id_choice = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.ins_id_choice_list, 0)
        self.ins_id_choice.SetFont(common_font)

        info_panel_gb_sizer.Add(self.ins_id_choice, wx.GBPosition(0, 2), wx.GBSpan(1, 2), wx.ALL, 5)

        self.num_label = wx.StaticText(self, wx.ID_ANY, u"Num",
                                       wx.DefaultPosition, wx.Size(-1, -1), 0)
        self.num_label.SetFont(common_font)

        self.num_label.Wrap(-1)
        info_panel_gb_sizer.Add(self.num_label, wx.GBPosition(0, 4), wx.GBSpan(1, 2), wx.ALIGN_RIGHT | wx.ALL, 5)

        self.num_list = ['All', '30', '40', '50']
        self.num_choice = wx.Choice(self, wx.ID_ANY, wx.DefaultPosition, wx.DefaultSize, self.num_list, 0)
        self.num_choice.SetFont(common_font)

        info_panel_gb_sizer.Add(self.num_choice, wx.GBPosition(0, 6), wx.GBSpan(1, 2), wx.ALL, 5)

        self.run_data_radio = wx.RadioButton(self, wx.ID_ANY, u"Manual mode", wx.DefaultPosition,
                                             wx.DefaultSize, wx.RB_GROUP)
        info_panel_gb_sizer.Add(self.run_data_radio, wx.GBPosition(0, 8), wx.GBSpan(1, 2), wx.ALL, 5)

        self.monitor_data_radio = wx.RadioButton(self, wx.ID_ANY, u"Monitoring mode",
                                                 wx.DefaultPosition, wx.DefaultSize, 0)
        info_panel_gb_sizer.Add(self.monitor_data_radio, wx.GBPosition(0, 10), wx.GBSpan(1, 2), wx.ALL, 5)

        self.search_button = wx.Button(self, wx.ID_ANY, u"Search", wx.DefaultPosition, wx.DefaultSize, 0)
        self.search_button.SetFont(common_font)

        info_panel_gb_sizer.Add(self.search_button, wx.GBPosition(0, 13), wx.GBSpan(1, 2), wx.ALL, 5)

        self.run_data_list_run_grid = wx.grid.Grid(info_panel_sb_sizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                                   wx.Size(-1, -1), 0)
        self.run_data_list_run_grid.SetFont(common_font)

        # Grid
        self.run_data_list_run_grid.CreateGrid(1, 22)
        self.run_data_list_run_grid.EnableEditing(True)
        self.run_data_list_run_grid.EnableGridLines(True)
        self.run_data_list_run_grid.EnableDragGridSize(False)
        self.run_data_list_run_grid.SetMargins(0, 0)

        # Columns
        current_panel_width = 550
        self.run_data_list_run_grid.SetColSize(0, current_panel_width * 0.1)
        self.run_data_list_run_grid.SetColSize(1, current_panel_width * 0.25)
        self.run_data_list_run_grid.SetColSize(2, current_panel_width * 0.25)
        self.run_data_list_run_grid.SetColSize(3, current_panel_width * 0.65)
        self.run_data_list_run_grid.SetColSize(21, current_panel_width * 0.35)
        self.run_data_list_run_grid.EnableDragColMove(False)
        self.run_data_list_run_grid.EnableDragColSize(True)
        self.run_data_list_run_grid.SetColLabelValue(0, u"")
        self.run_data_list_run_grid.SetColLabelValue(1, u"Instrument")
        self.run_data_list_run_grid.SetColLabelValue(2, u"Raw ID")
        self.run_data_list_run_grid.SetColLabelValue(3, 'Raw name')
        self.run_data_list_run_grid.SetColLabelValue(4, 'LC')
        self.run_data_list_run_grid.SetColLabelValue(5, 'F1')
        self.run_data_list_run_grid.SetColLabelValue(6, 'F2')
        self.run_data_list_run_grid.SetColLabelValue(7, 'F3')
        self.run_data_list_run_grid.SetColLabelValue(8, 'MS')
        self.run_data_list_run_grid.SetColLabelValue(9, 'F4')
        self.run_data_list_run_grid.SetColLabelValue(10, 'F5')
        self.run_data_list_run_grid.SetColLabelValue(11, 'F6')
        self.run_data_list_run_grid.SetColLabelValue(12, 'F7')
        self.run_data_list_run_grid.SetColLabelValue(13, 'F8')
        self.run_data_list_run_grid.SetColLabelValue(14, 'F9')
        self.run_data_list_run_grid.SetColLabelValue(15, 'F10')
        self.run_data_list_run_grid.SetColLabelValue(16, 'F11')
        self.run_data_list_run_grid.SetColLabelValue(17, 'F12')
        self.run_data_list_run_grid.SetColLabelValue(18, 'F13')
        self.run_data_list_run_grid.SetColLabelValue(19, 'F14')
        self.run_data_list_run_grid.SetColLabelValue(20, 'F15')
        self.run_data_list_run_grid.SetColLabelValue(21, 'Create time')
        self.run_data_list_run_grid.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        attr = wx.grid.GridCellAttr()
        attr.SetEditor(wx.grid.GridCellBoolEditor())
        attr.SetRenderer(wx.grid.GridCellBoolRenderer())
        self.run_data_list_run_grid.SetColAttr(0, attr)

        attr_read_only = wx.grid.GridCellAttr()
        attr_read_only.SetReadOnly(True)
        self.run_data_list_run_grid.SetColAttr(1, attr_read_only)

        attr_read_only2 = wx.grid.GridCellAttr()
        attr_read_only2.SetReadOnly(True)
        self.run_data_list_run_grid.SetColAttr(2, attr_read_only2)

        attr_read_only3 = wx.grid.GridCellAttr()
        attr_read_only3.SetReadOnly(True)
        self.run_data_list_run_grid.SetColAttr(3, attr_read_only3)

        # Rows
        self.run_data_list_run_grid.EnableDragRowSize(True)
        self.run_data_list_run_grid.SetRowLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        # Cell Defaults
        self.run_data_list_run_grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        info_panel_gb_sizer.Add(self.run_data_list_run_grid, wx.GBPosition(1, 0), wx.GBSpan(1, 18), wx.ALL | wx.EXPAND,
                                5)

        self.run_data_list_run_grid.SetMaxSize(self.GetSize())

        info_panel_sb_sizer.Add(info_panel_gb_sizer, 1, wx.EXPAND, 5)

        info_panel_gb_sizer.AddGrowableCol(17)
        info_panel_gb_sizer.AddGrowableRow(1)

        self.SetSizer(info_panel_sb_sizer)
        self.Layout()

    def __del__(self):
        pass


class DiaNNInfoPanel(wx.Panel):
    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(400, 100), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        run_info_gb_sizer = wx.GridBagSizer(0, 0)
        run_info_gb_sizer.SetFlexibleDirection(wx.BOTH)
        run_info_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.run_diann_info_panel = RunDataDiaNNPanel(self)

        run_info_gb_sizer.Add(self.run_diann_info_panel, wx.GBPosition(0, 0), wx.GBSpan(6, 10), wx.ALL | wx.EXPAND, 5)

        run_info_gb_sizer.AddGrowableRow(5)
        run_info_gb_sizer.AddGrowableCol(9)

        self.SetSizer(run_info_gb_sizer)
        self.Layout()

    def __del__(self):
        pass

class RunDataDiaNNPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(800, 400), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        rd_sb = wx.StaticBox(self, wx.ID_ANY, u"DiaNN info")
        rd_sb.SetFont(common_font)

        info_panel_sb_sizer = wx.StaticBoxSizer(rd_sb, wx.VERTICAL)

        info_panel_gb_sizer = wx.GridBagSizer(0, 0)
        info_panel_gb_sizer.SetFlexibleDirection(wx.BOTH)
        info_panel_gb_sizer.SetNonFlexibleGrowMode(wx.FLEX_GROWMODE_SPECIFIED)

        self.search_button = wx.Button(self, wx.ID_ANY, u"Search", wx.DefaultPosition, wx.DefaultSize, 0)
        self.search_button.SetFont(common_font)

        info_panel_gb_sizer.Add(self.search_button, wx.GBPosition(0, 13), wx.GBSpan(1, 2), wx.ALL, 5)

        self.run_data_list_run_grid = wx.grid.Grid(info_panel_sb_sizer.GetStaticBox(), wx.ID_ANY, wx.DefaultPosition,
                                                   wx.Size(-1, -1), 0)
        self.run_data_list_run_grid.SetFont(common_font)

        # Grid
        self.run_data_list_run_grid.CreateGrid(1, 5)
        self.run_data_list_run_grid.EnableEditing(True)
        self.run_data_list_run_grid.EnableGridLines(True)
        self.run_data_list_run_grid.EnableDragGridSize(False)
        self.run_data_list_run_grid.SetMargins(0, 0)

        # Columns
        current_panel_width = 500
        self.run_data_list_run_grid.SetColSize(0, current_panel_width * 0.1)
        self.run_data_list_run_grid.SetColSize(1, current_panel_width * 0.25)
        self.run_data_list_run_grid.SetColSize(2, current_panel_width * 0.15)
        self.run_data_list_run_grid.SetColSize(3, current_panel_width * 0.65)
        self.run_data_list_run_grid.SetColSize(4, current_panel_width * 0.25)
        self.run_data_list_run_grid.EnableDragColMove(False)
        self.run_data_list_run_grid.EnableDragColSize(True)
        self.run_data_list_run_grid.SetColLabelValue(0, u"")
        self.run_data_list_run_grid.SetColLabelValue(1, u"Run prefix")
        self.run_data_list_run_grid.SetColLabelValue(2, 'Raw name')
        self.run_data_list_run_grid.SetColLabelValue(3, 'Peptide number')
        self.run_data_list_run_grid.SetColLabelValue(4, 'Protein number')
        self.run_data_list_run_grid.SetColLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        attr = wx.grid.GridCellAttr()
        attr.SetEditor(wx.grid.GridCellBoolEditor())
        attr.SetRenderer(wx.grid.GridCellBoolRenderer())
        self.run_data_list_run_grid.SetColAttr(0, attr)

        attr_read_only = wx.grid.GridCellAttr()
        attr_read_only.SetReadOnly(True)
        self.run_data_list_run_grid.SetColAttr(1, attr_read_only)

        attr_read_only2 = wx.grid.GridCellAttr()
        attr_read_only2.SetReadOnly(True)
        self.run_data_list_run_grid.SetColAttr(2, attr_read_only2)

        attr_read_only3 = wx.grid.GridCellAttr()
        attr_read_only3.SetReadOnly(True)
        self.run_data_list_run_grid.SetColAttr(3, attr_read_only3)

        # Rows
        self.run_data_list_run_grid.EnableDragRowSize(True)
        self.run_data_list_run_grid.SetRowLabelAlignment(wx.ALIGN_CENTER, wx.ALIGN_CENTER)

        # Cell Defaults
        self.run_data_list_run_grid.SetDefaultCellAlignment(wx.ALIGN_LEFT, wx.ALIGN_TOP)
        info_panel_gb_sizer.Add(self.run_data_list_run_grid, wx.GBPosition(1, 0), wx.GBSpan(1, 18), wx.ALL | wx.EXPAND,
                                5)

        self.run_data_list_run_grid.SetMaxSize(self.GetSize())

        info_panel_sb_sizer.Add(info_panel_gb_sizer, 1, wx.EXPAND, 5)

        info_panel_gb_sizer.AddGrowableCol(17)
        info_panel_gb_sizer.AddGrowableRow(1)

        self.SetSizer(info_panel_sb_sizer)
        self.Layout()

    def __del__(self):
        pass

