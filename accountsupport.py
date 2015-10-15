# -*- coding: utf-8 -*-
import wx
import  accountManage
import wx.lib.mixins.listctrl as listmix
import threading
from commonlib import  commons,constant


class TestListCtrl(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):

    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        # self.setResizeColumn(5)
        self.selectItem = -1
        self.account_select = []
        self.windows = self.GetParent()



    def OnCheckItem(self, index, flag):
        print(index, flag)
        if flag:
            self.selectItem = index
            self.selectCardName = self.GetItemText(index,1)




class AccountSupport(wx.Panel):


    def __init__(self, parent,myHttpRequest,database):
        wx.Panel.__init__(self, parent=parent)
        self.database = database
        self.myHttpRequest = myHttpRequest
        self.head_list = [u'序号',u'面值',u'名称',u'主号数量',u'小号数量']
         #主题列表
        self.themeIdList = []
        self.themeNameList = []
        #查询卡组序号
        self.commit_index = -1
        self.ignoreEvtText = False

        #----------------------按钮------------
        self.buttonSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.search_card_theme_label = wx.StaticText(self,-1,u'查询的套卡:')
        self.search_theme_choice = wx.ComboBox(self,-1,pos=wx.DefaultPosition,size=wx.DefaultSize,choices=self.getCollectTheme(),style=wx.CB_DROPDOWN)
        self.search_theme_choice.Bind(wx.EVT_COMBOBOX ,self.on_commit_theme_select)
        self.search_theme_choice.Bind(wx.EVT_TEXT, self.EvtText2)
        self.search_theme_choice.Bind(wx.EVT_CHAR, self.EvtChar)
        self.refresh = wx.Button(self,-1,u'查看')
        self.refresh.Bind(wx.EVT_BUTTON,self.refreshCard)
        self.buttonSizer.Add(self.search_card_theme_label,0,wx.ALL,5)
        self.buttonSizer.Add(self.search_theme_choice,0,wx.ALL,5)
        self.buttonSizer.Add(self.refresh,0,wx.ALL,5)

        #-----------------------列表-------------
        self.sb = wx.StaticBox(self,label=u'账号信息')
        self.listSizer = wx.StaticBoxSizer(self.sb,wx.HORIZONTAL)
        self.sloveBoxList = TestListCtrl(self,style=wx.LC_REPORT)
        self.sloveBoxList.SetBackgroundColour((227,237,205))
        for col,text in enumerate (self.head_list):
            self.sloveBoxList.InsertColumn(col,text)
            self.sloveBoxList.SetColumnWidth(col,100)
        self.listSizer.Add(self.sloveBoxList,1,wx.EXPAND)

        # self.accountSb = wx.StaticBox(self,label=u'小号信息')


        # self.list_sizer = wx.StaticBoxSizer(self.sb,wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.buttonSizer,0,wx.ALL,5)
        self.sizer.Add(self.listSizer,1,wx.ALL,5)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.Center()
        self.Show(True)

    def refreshCard(self,e):

        print accountManage.AccountManage.account_http_dic
        self.sloveBoxList.DeleteAllItems()
        t = threading.Thread(target=self.getMainAccountCardInfo)
        t.start()

        e.Skip()




    def getMainAccountCardInfo(self):
        card_info = self.database.getCardFromTheme(self.themeIdList[self.commit_index])
        magic_info = commons.getMagicInfo(self.myHttpRequest,constant.USERNAME)
        exchangBox = commons.get_type_info(constant.EXCHANGEBOX,magic_info)
        storeBox = commons.get_type_info(constant.STOREBOX,magic_info)

        account_exchangBox_list = []
        account_storeBox_list = []
        for key,value in accountManage.AccountManage.account_http_dic.items():
            magic_info = commons.getMagicInfo(value,key)
            account_exchangBox_list.append(commons.get_type_info(constant.EXCHANGEBOX,magic_info))
            account_storeBox_list.append(commons.get_type_info(constant.STOREBOX,magic_info))
        for card_item in card_info:
            card_id = card_item[0]
            card_count = 0
            for account_exchangBox in account_exchangBox_list:
                card_count+=account_exchangBox.count(card_id)
            for account_storeBox in account_storeBox_list:
                card_count+=account_storeBox.count(card_id)
            self.sloveBoxList.Append(['',card_item[1],card_item[2],str(exchangBox.count(card_id)+storeBox.count(card_id)),str(card_count)])
    '''
    获取要收集的主题
    '''
    def getCollectTheme(self):
        themeName = []
        self.database.cu.execute("select * from cardtheme order by diff ASC ")
        result = self.database.cu.fetchall()
        for themeItem in result:
            themeName.append('['+str(themeItem[3])+u"星]"+themeItem[2])
            self.themeIdList.append(themeItem[1])
            self.themeNameList.append(themeItem[2])
        return themeName

    def on_commit_theme_select(self,e):
        '''
        提交的卡组被选择
        :param e:
        :return:
        '''
        self.commit_index = self.search_theme_choice.GetSelection()
        e.Skip()

    '''comboBox键盘监听事件
    '''
    def EvtChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()


    '''commbobox内容变化事件
    '''
    def EvtText2(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString()
        print currentText
        found = False
        for i,choice in enumerate(self.themeNameList) :
            if choice.startswith(currentText):
                self.ignoreEvtText = True
                self.search_theme_choice.SetValue(choice)
                self.search_theme_choice.SetInsertionPoint(len(currentText))
                self.search_theme_choice.SetMark(len(currentText), len(choice))
                self.commit_index = i
                found = True
                break
        if not found:
            event.Skip()