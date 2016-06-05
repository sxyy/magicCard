# -*- coding: utf-8 -*-
import wx
import  accountManage
import wx.lib.mixins.listctrl as listmix
import threading
from commonlib import  commons,constant
from mythread import exchangCardThread
import main

class TestListCtrl(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):

    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        # self.setResizeColumn(5)
        self.selectItem = -1
        self.account_select = []
        self.windows = self.GetParent()
        self.menu_title_by_id = {1:u'查找有同面值的小号'}
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,self.onItemRightClick)

    def onItemRightClick(self,e):
        self.selectCardId = self.windows.cardIdDict[int(e.GetText())]
        self.windows.select_card_id = self.selectCardId
        menu = wx.Menu()
        for (menu_id,title) in self.menu_title_by_id.items():
            menu.Append(menu_id, title)
            wx.EVT_MENU( menu, menu_id, self.MenuSelectionCb )
        self.PopupMenu(menu,e.GetPoint())
        menu.Destroy()


    def MenuSelectionCb(self, event ):
        #accountManage.AccountManage.account_http_dic.items()
        if 1==event.GetId():
            t = threading.Thread(target=self.getSubAccountCard)
            t.start()
            pass

    #获取拥有卡的小号字典
    def getSubAccountCard(self):

        self.has_card_account_dic = {}
        self.windows.exchang_card_dic = {}
        self.exchang_card_info_dic = {}
        magic_info = commons.getMagicInfo(main.RefinedCard.main_http_request,constant.USERNAME)
        exchangBox = commons.get_type_info(constant.EXCHANGEBOX,magic_info)
        storeBox = commons.get_type_info(constant.STOREBOX,magic_info)

        select_card_info = self.windows.database.getCardInfo(self.selectCardId)
        print select_card_info

        count = 1
        for i,card_id in enumerate(exchangBox):
            if card_id == 0:
                continue
            card_info = self.windows.database.getCardInfo(card_id)
            if card_info[2] == select_card_info[2]:
                self.windows.exchang_card_dic[count] = u'使用'+card_info[0]+u'交换'
                self.windows.exchang_card_info_dic[count] = [0,i,card_id]
                count += 1

        for i,card_id in enumerate(storeBox):
            if card_id == 0:
                continue
            card_info = self.windows.database.getCardInfo(card_id)
            if card_info[2] == select_card_info[2]:
                self.windows.exchang_card_dic[count] = u'使用'+card_info[0]+u'交换'
                self.windows.exchang_card_info_dic[count] = [1,i,card_id]
                count += 1


        self.windows.sloveBoxList2.DeleteAllItems()
        for key,value in accountManage.AccountManage.account_http_dic.items():
            if str(key) == str(constant.USERNAME) :
                continue
            magic_info = commons.getMagicInfo(value,key)
            print 'key',key
            account_exchangBox = commons.get_type_info(constant.EXCHANGEBOX,magic_info)
            account_storeBox  = commons.get_type_info(constant.STOREBOX,magic_info)
            if int(self.selectCardId) in account_exchangBox or int(self.selectCardId) in account_storeBox:
                self.has_card_account_dic[key] = value
                self.windows.sloveBoxList2.Append([str(key)])



    def OnCheckItem(self, index, flag):
        print(index, flag)
        if flag:
            self.selectItem = index
            self.selectCardName = self.GetItemText(index,1)

class SubAccountListCtrl(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):

    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        # self.setResizeColumn(5)
        self.selectItem = -1
        self.account_select = []
        self.windows = self.GetParent()
        # self.menu_title_by_id = {1:u'查找有同面值的小号'}
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,self.onItemRightClick)

    def onItemRightClick(self,e):
        self.selectAccount =  e.GetText()
        menu = wx.Menu()
        for (menu_id,title) in self.windows.exchang_card_dic.items():
            menu.Append(menu_id, title)
            wx.EVT_MENU( menu, menu_id, self.MenuSelectionCb )
        self.PopupMenu(menu,e.GetPoint())
        menu.Destroy()


    def MenuSelectionCb(self, event ):
        print event.GetId()

        card_info = commons.getMagicInfo2(main.RefinedCard.main_http_request,self.selectAccount)

        self.httpRequest = accountManage.AccountManage.account_http_dic[self.selectAccount]

        exchange_box = commons.get_type_info(constant.EXCHANGEBOX,card_info)
        store_box = commons.get_type_info(constant.STOREBOX,card_info)

        dst_card_id = self.windows.select_card_id
        dst_type = 0
        dst_position = -1



        if self.windows.select_card_id in exchange_box:
            dst_position = exchange_box.index(self.windows.select_card_id)
        elif self.windows.select_card_id in store_box:
            src_position = store_box.index(self.windows.select_card_id)
            if 0 in exchange_box:
                dst_position = exchange_box.index(0)
                postData = {
                             'dest':dst_position,
                             'src':src_position,
                             'type':1,
                             'uin':self.selectAccount,
                }
                base_url = commons.getUrl(constant.CARDINPUTSTOREBOX,self.httpRequest)
                self.httpRequest.get_response(base_url,postData).read().decode('utf-8')

        if dst_position != -1:

            base_url1 = commons.getUrl(constant.SETTHEME,self.httpRequest)
            post_data = {
                'themes':0
            }
            self.httpRequest.get_response(base_url1,post_data).read().decode('utf-8')

            dst = str(dst_card_id)+"_"+str(dst_position)+"_"+str(dst_type)
            card_info = self.windows.exchang_card_info_dic[event.GetId()]
            src = str(card_info[2])+"_"+str(card_info[1])+"_"+str(card_info[0])
            base_url = commons.getUrl(constant.EXCHANGECARD,main.RefinedCard.main_http_request)
            post_data ={
                'cmd':1,
                'isFriend':0,
                'frnd':str(self.selectAccount),
                'uin':str(constant.USERNAME),
                'dst':dst,
                'src':src
            }
            page_content =  main.RefinedCard.main_http_request.get_response(base_url,post_data).read().decode('utf-8')
            post_data = {
                'themes':153
            }
            self.httpRequest.get_response(base_url1,post_data).read().decode('utf-8')
            if 'code="0"' in page_content:
                dlg = wx.MessageDialog(None, u"换卡成功", u"提示", wx.OK | wx.ICON_QUESTION)

            else:
                dlg = wx.MessageDialog(None, u"换卡成功", u"提示", wx.OK | wx.ICON_QUESTION)

            if dlg.ShowModal() == wx.ID_YES:
                self.Close(True)
                dlg.Destroy()
        else:
            dlg = wx.MessageDialog(None, u"换卡箱已满或卡片不存在", u"提示", wx.OK | wx.ICON_QUESTION)
            if dlg.ShowModal() == wx.ID_YES:
                self.Close(True)
            dlg.Destroy()


        #accountManage.AccountManage.account_http_dic.items()
        if 1==event.GetId():
            pass
            # t = threading.Thread(target=self.getSubAccountCard)
            # t.start()
            # pass



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
        self.head_list = [u'序号',u'面值',u'名称',u'主号数量']
        self.head_list2 = [u'账号']
        self.operate_list = [u'换卡']
        self.exchang_card_dic = {}
        self.exchang_card_info_dic = {}
        self.select_card_id = ''
         #主题列表
        self.themeIdList = []
        self.themeNameList = []
        #查询卡组序号
        self.commit_index = -1
        self.ignoreEvtText = False

        self.cardIdDict = {}


        #-------------炉子操作----------
        sb  = wx.StaticBox(self,label = u'需要交换的套卡')
        # self.sloveOperateSizer = wx.BoxSizer(wx.HORIZONTAL)
        # self.cardLabel = wx.StaticText(self,-1,u'套卡')
        # self.collectThemeChoice = wx.ComboBox(self,-1,pos=wx.DefaultPosition,size=wx.DefaultSize,choices=self.getCollectTheme(),style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)
        # self.collectThemeChoice.Bind(wx.EVT_COMBOBOX ,self.onCollectThemeChoice)
        # self.collectThemeChoice.Bind(wx.EVT_TEXT_ENTER ,self.onCollectThemeSearch)
        # self.collectThemeChoice.Bind(wx.EVT_TEXT, self.EvtText)
        # self.collectThemeChoice.Bind(wx.EVT_CHAR, self.EvtChar)
        # self.cardPriceLabel = wx.StaticText(self,-1,u'面值')
        # self.searchCardPriceChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,[])
        # self.searchCardPriceChoice.Bind(wx.EVT_CHOICE,self.onCardPriceChoice)
        # self.detailCardLabel = wx.StaticText(self,-1,u'卡片')
        # self.detailCardChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,[])
        # self.detailCardChoice.Enable(False)
        # self.operateChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.operate_list)
        # self.operateChoice.SetSelection(0)
        # self.searchBt = wx.Button(self,-1,u'开始')
        # self.searchStop = wx.Button(self,-1,u'停止')
        # self.searchBt.Bind(wx.EVT_BUTTON, self.searchTheme)
        # self.searchStop.Bind(wx.EVT_BUTTON, self.stopSearchTheme)
        # self.sloveOperateSizer.Add(self.cardLabel,0,wx.ALL,5)
        # self.sloveOperateSizer.Add(self.collectThemeChoice,0,wx.ALL,5)
        # self.sloveOperateSizer.Add(self.cardPriceLabel,0,wx.ALL,5)
        # self.sloveOperateSizer.Add(self.searchCardPriceChoice,0,wx.ALL,5)
        # self.sloveOperateSizer.Add(self.detailCardLabel,0,wx.ALL,5)
        # self.sloveOperateSizer.Add(self.detailCardChoice,0,wx.ALL,5)
        # self.sloveOperateSizer.Add(self.operateChoice,0,wx.ALL,5)
        # self.sloveOperateSizer.Add(self.searchBt,0,wx.ALL,5)
        # self.sloveOperateSizer.Add(self.searchStop,0,wx.ALL,5)


        #-------------额外的操作---------
        # self.other_operate = wx.BoxSizer(wx.HORIZONTAL)

        # self.is_show_flash_card = wx.CheckBox(self,-1,u'交换大号不重复的卡')
        # self.other_operate.Add(self.is_show_flash_card,0,wx.ALL,5)

        self.sloveOperateSizer2 = wx.StaticBoxSizer(sb,wx.VERTICAL)
        # self.sloveOperateSizer2.Add(self.sloveOperateSizer,0,wx.ALL,5)
        # self.sloveOperateSizer2.Add(self.other_operate,0,wx.ALL,5)


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

        #-----------------------列表2-------------
        sb2 = wx.StaticBox(self,label=u'可能存在对应卡的小号')
        self.listSizer2 = wx.StaticBoxSizer(sb2,wx.HORIZONTAL)
        self.sloveBoxList2 = SubAccountListCtrl(self,style=wx.LC_REPORT)
        self.sloveBoxList2.SetBackgroundColour((227,237,205))
        for col,text in enumerate (self.head_list2):
            self.sloveBoxList2.InsertColumn(col,text)
            self.sloveBoxList2.SetColumnWidth(col,100)
        self.listSizer2.Add(self.sloveBoxList2,1,wx.EXPAND,5)

        # self.accountSb = wx.StaticBox(self,label=u'小号信息')

        #------------------------------------------

        # self.msgLog = wx.TextCtrl(self,-1,size=(240,400),style=wx.TE_MULTILINE)

        # self.list_sizer = wx.StaticBoxSizer(self.sb,wx.VERTICAL)
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sloveOperateSizer2,0,wx.ALL,5)

        self.horizontalSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.verticalSizer = wx.BoxSizer(wx.VERTICAL)
        self.verticalSizer.Add(self.buttonSizer,0,wx.ALL,5)
        self.verticalSizer.Add(self.listSizer,1,wx.ALL,5)
        # self.horizontalSizer.Add(self.msgLog,0,wx.ALL,5)self.listSizer2
        self.horizontalSizer.Add(self.verticalSizer,1,wx.EXPAND,5)
        self.horizontalSizer.Add(self.listSizer2,1,wx.EXPAND,5)
        self.sizer.Add(self.horizontalSizer,1,wx.EXPAND,5)
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
        magic_info = commons.getMagicInfo(main.RefinedCard.main_http_request,constant.USERNAME)
        exchangBox = commons.get_type_info(constant.EXCHANGEBOX,magic_info)
        storeBox = commons.get_type_info(constant.STOREBOX,magic_info)

        # account_exchangBox_list = []
        # account_storeBox_list = []
        # for key,value in accountManage.AccountManage.account_http_dic.items():
        #     magic_info = commons.getMagicInfo(value,key)
        #     account_exchangBox_list.append(commons.get_type_info(constant.EXCHANGEBOX,magic_info))
        #     account_storeBox_list.append(commons.get_type_info(constant.STOREBOX,magic_info))
        for i,card_item in enumerate(card_info):
            card_id = card_item[0]
            self.cardIdDict[i] = card_id
            #card_count = 0
            # for account_exchangBox in account_exchangBox_list:
            #     card_count+=account_exchangBox.count(card_id)
            # for account_storeBox in account_storeBox_list:
            #     card_count+=account_storeBox.count(card_id)
            self.sloveBoxList.Append([str(i),card_item[1],card_item[2],str(exchangBox.count(card_id)+storeBox.count(card_id))])
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
