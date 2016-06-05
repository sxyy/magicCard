# -*- coding: utf-8 -*-
import  wx
from commonlib import myhttp
import StringIO
import urllib2
class Reward(wx.Panel):

    def __init__(self, parent):
        wx.Panel.__init__(self, parent=parent)
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cardLabel = wx.StaticText(self, -1, u'熊熊助手离不开各位的支持，不强迫。哈哈,感谢：\n 兔子,龙浩,浅笑的支持')
        self.qqShowImage=wx.StaticBitmap(self, -1,  pos=(30,50), size=(300,300))
        self.sizer.Add(self.cardLabel, 0, wx.ALL, 5)
        self.sizer.Add(self.qqShowImage, 0, wx.ALL, 5)
        base_url = r'https://testerhome.com/user/big_qrcode/2269.jpg'
        buf = urllib2.urlopen(base_url).read()
        sbuf = StringIO.StringIO(buf)
        Image = wx.ImageFromStream(sbuf).ConvertToBitmap()
        self.qqShowImage.SetBitmap(Image)
        self.sizer.Layout()
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.Center()
        self.Show(True)