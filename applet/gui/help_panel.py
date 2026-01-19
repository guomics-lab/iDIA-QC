import wx

from applet import common_utils
from applet.gui.common_config import introduce_font, version_font

common_config = common_utils.read_yml()


class HelpPanel(wx.Panel):

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition, size=wx.Size(400, 100), style=wx.TAB_TRAVERSAL,
                 name=wx.EmptyString):
        wx.Panel.__init__(self, parent, id=id, pos=pos, size=size, style=style, name=name)

        self.about_text = wx.StaticText(self, label=common_config['help']['text'])
        self.about_text.SetFont(introduce_font)
        self.about_text.SetWindowStyleFlag(wx.ALIGN_CENTER | wx.ALIGN_CENTER_VERTICAL)
        # self.about_text.SetSize((-1, 600))

        about_text_sizer = wx.BoxSizer(wx.HORIZONTAL)
        # 在StaticText周围添加间距空白
        about_text_sizer.AddSpacer(100)  # 左侧间距
        about_text_sizer.Add(self.about_text, 1, wx.EXPAND)
        about_text_sizer.AddSpacer(100)  # 右侧间距

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(about_text_sizer, 3, wx.EXPAND | wx.ALL, 10)

        self.SetSizer(sizer)

    def __del__(self):
        pass
