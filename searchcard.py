# -*- coding: utf-8 -*-
__author__ = 'Administrator'
import wx
from commonlib import constant
import logging,ConfigParser
from mythread import searchCardThread,flashCardThread,commitThread,flashCardToFlashCard
import datetime,xlwt
import wx.lib.hyperlink as hyperlink


class SearchCard(wx.Panel):

    def __init__(self, parent,myHttpRequest,database,path):
        wx.Panel.__init__(self, parent=parent)
        self.myHttpRequest = myHttpRequest
        self.database = database
        self.path = path
        #主题列表
        self.themeIdList = []
        self.themeNameList = []
        self.seachThemeIndex = -1
        self.priceList = []
        self.search_index = -1
        #搜索到的卡友列表
        self.seachTime = ''
        self.seachCardFriendNum = 0
        self.cardFriendList = []
        self.ignoreEvtText = False
        #变卡相关
        self.flash_index = -1
        self.flash_card_name_list = []
        self.flash_card_theme_id_list = []
        self.flash_normal_theme_id_list = []
        self.src_price = 44
        self.des_price = 120
        self.middle_price = 40
        #提交卡组
        self.commit_index = -1
        #---------------超链接-----------
        self.cardFriendLinkSizer = wx.BoxSizer(wx.HORIZONTAL)

        self.userIdChoice = wx.ComboBox(self,-1,pos=wx.DefaultPosition,size=wx.DefaultSize,choices=[],style=wx.CB_DROPDOWN)
        self.userIdChoice.Bind(wx.EVT_CHOICE,self.onCardUserChoice)
        self.hyper = hyperlink.HyperLinkCtrl(self,-1,u"卡友链接")
        self.hyper.AutoBrowse(False)
        self.hyper.Bind(hyperlink.EVT_HYPERLINK_LEFT,self.onHyper)
        self.search_progress = wx.StaticText(self,-1,u'0/'+str(constant.CARDUSERNUM))
        self.cardFriendLinkSizer.Add(self.hyper,0,wx.ALL,5)
        self.cardFriendLinkSizer.Add(self.userIdChoice,0,wx.ALL,5)
        self.cardFriendLinkSizer.Add(self.search_progress)

        #---------------提交套卡-----------
        sb  = wx.StaticBox(self,label = u'免素材提交卡册')
        self.commit_card_theme_sizer = wx.StaticBoxSizer(sb,wx.HORIZONTAL)
        self.commit_card_theme_label = wx.StaticText(self,-1,u'提交的套卡')
        self.commit_theme_choice = wx.ComboBox(self,-1,pos=wx.DefaultPosition,size=wx.DefaultSize,choices=self.getCollectTheme(),style=wx.CB_DROPDOWN)
        self.commit_theme_choice.Bind(wx.EVT_COMBOBOX ,self.on_commit_theme_select)
        self.commit_theme_choice.Bind(wx.EVT_TEXT, self.EvtText2)
        self.commit_theme_choice.Bind(wx.EVT_CHAR, self.EvtChar)
        self.commit_button = wx.Button(self,-1,u'提交套卡')
        self.commit_button.Bind(wx.EVT_BUTTON,self.on_theme_commit)
        self.commit_card_theme_sizer.Add(self.commit_card_theme_label,0,wx.ALL,5)
        self.commit_card_theme_sizer.Add(self.commit_theme_choice,0,wx.ALL,5)
        self.commit_card_theme_sizer.Add(self.commit_button,0,wx.ALL,5)
        #-------------额外的操作---------
        self.other_operate = wx.BoxSizer(wx.HORIZONTAL)
        self.searchOnlyCheckBox = wx.CheckBox(self,-1,u'只搜索炼制该套卡的卡友')
        self.searchOnlyCheckBox.Bind(wx.EVT_CHECKBOX,self.on_check)
        self.is_show_flash_card = wx.CheckBox(self,-1,u'搜索结果不显示闪卡卡友')
        self.search_range_theme_choice = wx.ComboBox(self,-1,pos=wx.DefaultPosition,size=wx.DefaultSize,choices=self.getCollectTheme(),style=wx.CB_DROPDOWN)
        self.search_range_theme_choice.Enable(False)
        self.search_range_theme_choice.Bind(wx.EVT_COMBOBOX ,self.on_search_theme_range_select)
        self.search_range_theme_choice.Bind(wx.EVT_TEXT, self.EvtText4)
        self.search_range_theme_choice.Bind(wx.EVT_CHAR, self.EvtChar)
        self.other_operate.Add(self.is_show_flash_card,0,wx.ALL,5)
        self.other_operate.Add(self.searchOnlyCheckBox,0,wx.ALL,5)
        self.other_operate.Add(self.search_range_theme_choice,0,wx.ALL,5)
        self.other_operate.Add(self.cardFriendLinkSizer,0,wx.ALL,5)

        #-------------炉子操作----------
        sb  = wx.StaticBox(self,label = u'需要搜索的套卡')
        self.sloveOperateSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.cardLabel = wx.StaticText(self,-1,u'套卡')
        self.collectThemeChoice = wx.ComboBox(self,-1,pos=wx.DefaultPosition,size=wx.DefaultSize,choices=self.getCollectTheme(),style=wx.CB_DROPDOWN|wx.TE_PROCESS_ENTER)
        self.collectThemeChoice.Bind(wx.EVT_COMBOBOX ,self.onCollectThemeChoice)
        self.collectThemeChoice.Bind(wx.EVT_TEXT_ENTER ,self.onCollectThemeSearch)
        self.collectThemeChoice.Bind(wx.EVT_TEXT, self.EvtText)
        self.collectThemeChoice.Bind(wx.EVT_CHAR, self.EvtChar)
        self.cardPriceLabel = wx.StaticText(self,-1,u'面值')
        self.searchCardPriceChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,[])
        self.searchCardPriceChoice.Bind(wx.EVT_CHOICE,self.onCardPriceChoice)
        self.detailCardLabel = wx.StaticText(self,-1,u'卡片')
        self.detailCardChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,[])
        self.detailCardChoice.Enable(False)
        self.searchBt = wx.Button(self,-1,u'搜索')
        self.searchStop = wx.Button(self,-1,u'停止')
        self.searchBt.Bind(wx.EVT_BUTTON, self.searchTheme)
        self.searchStop.Bind(wx.EVT_BUTTON, self.stopSearchTheme)
        self.sloveOperateSizer.Add(self.cardLabel,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.collectThemeChoice,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.cardPriceLabel,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchCardPriceChoice,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.detailCardLabel,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.detailCardChoice,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchBt,0,wx.ALL,5)
        self.sloveOperateSizer.Add(self.searchStop,0,wx.ALL,5)

        self.sloveOperateSizer2 = wx.StaticBoxSizer(sb,wx.VERTICAL)
        self.sloveOperateSizer2.Add(self.sloveOperateSizer,0,wx.ALL,5)
        self.sloveOperateSizer2.Add(self.other_operate,0,wx.ALL,5)
        #-------------变卡操作----------
        self.flash_type = [u'44面值闪120',u'44面值变普卡40',u'闪120变闪240',u'闪120变闪360',u'普480闪1440']
        self.flash_card_num = [u'5',u'10',u'15',u'20',u'30',u'40']
        self.flash_card_theme = [u'']
        sb2  = wx.StaticBox(self,label = u'变卡')
        self.sloveFlashCardSizer = wx.StaticBoxSizer(sb2,wx.HORIZONTAL)
        self.cardLabel = wx.StaticText(self,-1,u'选择变卡类型')
        self.flash_type_choice = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.flash_type)
        self.flash_type_choice.Bind(wx.EVT_CHOICE ,self.on_flash_type_change)
        self.flash_type_choice.SetSelection(0)
        self.card_theme_label = wx.StaticText(self,-1,u'变卡主题')
        self.flash_card_num_label = wx.StaticText(self,-1,u'变卡张数')
        self.flash_card_num_choice = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.flash_card_num)
        #处理闪卡的一些数据
        flash_theme_list = self.database.get_flash_card_list()
        for flash_card in flash_theme_list:
            self.flash_card_name_list.append(flash_card[1])
            self.flash_card_theme_id_list.append(flash_card[0])
            self.flash_normal_theme_id_list.append(flash_card[2])
        self.flash_card_theme_choic = wx.ComboBox(self,-1,pos=wx.DefaultPosition,size=wx.DefaultSize,choices=self.flash_card_name_list,style=wx.CB_DROPDOWN)
        self.flash_card_theme_choic.Bind(wx.EVT_COMBOBOX ,self.on_flash_theme_select)
        self.flash_card_theme_choic.Bind(wx.EVT_TEXT, self.EvtText3)
        self.flash_card_theme_choic.Bind(wx.EVT_CHAR, self.EvtChar)
        self.card_flash = wx.Button(self,-1,u'变卡')
        self.card_flash.Bind(wx.EVT_BUTTON, self.on_card_flash)
        self.sloveFlashCardSizer.Add(self.cardLabel,0,wx.ALL,5)
        self.sloveFlashCardSizer.Add(self.flash_type_choice,0,wx.ALL,5)
        self.sloveFlashCardSizer.Add(self.card_theme_label,0,wx.ALL,5)
        self.sloveFlashCardSizer.Add(self.flash_card_theme_choic,0,wx.ALL,5)
        self.sloveFlashCardSizer.Add(self.flash_card_num_label,0,wx.ALL,5)
        self.sloveFlashCardSizer.Add(self.flash_card_num_choice,0,wx.ALL,5)
        self.sloveFlashCardSizer.Add(self.card_flash,0,wx.ALL,5)

        #---------------LOG部分---------------
        sb2  = wx.StaticBox(self,label = u'Log')
        self.log_sizer = wx.StaticBoxSizer(sb2,wx.HORIZONTAL)
        self.msgLog = wx.TextCtrl(self,-1,size=(240,400),style=wx.TE_MULTILINE)
        self.import_log = wx.TextCtrl(self,-1,size=(450,400),style=wx.TE_MULTILINE)
        self.msgLog.SetBackgroundColour((227,237,205))
        self.import_log.SetBackgroundColour((227,237,205))
        self.searchStop.Enable(False)
        self.log_sizer.Add(self.msgLog,0,wx.ALL,5)
        self.log_sizer.Add(self.import_log,1,wx.ALL,5)

        #---------------总的布局----------

        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.sloveOperateSizer2, 0, wx.EXPAND)
        self.sizer.Add(self.commit_card_theme_sizer, 0, wx.EXPAND)
        self.sizer.Add(self.sloveFlashCardSizer,0,wx.EXPAND)
        self.sizer.Add(self.log_sizer, 1, wx.EXPAND)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.Center()
        self.Show(True)


    def on_check(self,e):
        '''
        当复选框选择时
        :param e:
        :return:
        '''
        if self.searchOnlyCheckBox.GetValue():
            self.search_range_theme_choice.Enable(True)
        else:
            self.search_range_theme_choice.Enable(False)

    def on_theme_commit(self,e):
        '''
        点击提交按钮时
        :param e:
        :return:
        '''

        commit_thread = commitThread.CommitThread(self,self.myHttpRequest,int(self.themeIdList[self.commit_index]))
        commit_thread.start()

    def on_commit_theme_select(self,e):
        '''
        提交的卡组被选择
        :param e:
        :return:
        '''
        self.commit_index = self.commit_theme_choice.GetSelection()
        e.Skip()

    def on_search_theme_range_select(self,e):
        '''
        提交的卡组被选择
        :param e:
        :return:
        '''
        self.search_index = self.search_range_theme_choice.GetSelection()
        e.Skip()


    def on_flash_theme_select(self,e):
        '''
        变卡卡组的选择
        :return:
        '''
        self.flash_index = self.flash_card_theme_choic.GetSelection()
        e.Skip()

    def on_flash_type_change(self,e):
        '''
        变卡类型改变时
        :return:
        '''
        type = self.flash_type_choice.GetSelection()
        print 'type',type
        logging.info(u'选择变卡方式为'+self.flash_type_choice.GetStringSelection())
        self.flash_card_name_list = []
        self.flash_normal_theme_id_list = []
        self.flash_card_theme_id_list = []
        theme_name_list = []
        self.flash_card_theme_choic.Enable(True)
        self.flash_card_num_choice.Enable(True)
        if type==0:
            flash_theme_list = self.database.get_flash_card_list()
            self.src_price = 44
            self.middle_price = 40
            self.des_price = 120
            for flash_card in flash_theme_list:
                theme_name_list.append(flash_card[1])
                self.flash_card_name_list.append(flash_card[1])
                self.flash_card_theme_id_list.append(flash_card[0])
                self.flash_normal_theme_id_list.append(flash_card[2])
        elif type==1:
            self.src_price = 44
            self.middle_price =-1
            self.des_price = 40
            flash_theme_list = self.database.get_grounding_card_list()
            print flash_theme_list
            for flash_card in flash_theme_list:
                theme_name_list.append('['+str(flash_card[2])+u"星]"+flash_card[1])
                self.flash_card_name_list.append(flash_card[1])
                self.flash_normal_theme_id_list.append(flash_card[0])
        elif type==2:
            self.src_price = 120
            self.des_price = 240
            self.flash_card_theme_choic.Enable(False)
            self.flash_card_num_choice.Enable(False)
        elif type==3:
            self.src_price = 120
            self.des_price = 360
            self.flash_card_theme_choic.Enable(False)
            self.flash_card_num_choice.Enable(False)
        elif type==4:
            self.src_price = 480
            self.des_price = 1440
            self.flash_card_theme_choic.Enable(False)
            self.flash_card_num_choice.Enable(False)
        self.flash_card_theme_choic.SetItems(theme_name_list)
        e.Skip()

    def on_card_flash(self,e):
        '''
        变卡
        :param e:
        :return:
        '''
        middle_theme_id  = -1
        if self.flash_type_choice.GetSelection()<2 and self.flash_index!=-1:
            if len(self.flash_card_theme_id_list)!=0:
                middle_theme_id=self.flash_normal_theme_id_list[self.flash_index]
                des_theme_id = self.flash_card_theme_id_list[self.flash_index]
            else:
                des_theme_id = self.flash_normal_theme_id_list[self.flash_index]
            dlgs = wx.MessageDialog(self,u"确定要变卡吗？",caption=u'提示',style=wx.YES_NO|wx.ICON_QUESTION)
            retCode = dlgs.ShowModal()
            if retCode == wx.ID_YES:
                print middle_theme_id,des_theme_id,self.src_price,self.des_price
                card_theme_list = [422,middle_theme_id,des_theme_id]
                card_price_list = [self.src_price,self.middle_price,self.des_price]
                flash_card_thread = flashCardThread.FlashCardThread(self,self.myHttpRequest,card_theme_list,
                                                                    int(self.flash_card_num_choice.GetStringSelection()),card_price_list)
                flash_card_thread.start()
        elif  self.flash_type_choice.GetSelection()>=2:
            if self.flash_type_choice.GetSelection()== 4:
                flash_card_thread = flashCardToFlashCard.FlashCardToFlashCardThread(self,self.myHttpRequest,self.src_price,self.des_price,1)
            else:
                flash_card_thread = flashCardToFlashCard.FlashCardToFlashCardThread(self,self.myHttpRequest,self.src_price,self.des_price)
            flash_card_thread.start()
            pass
        else:
            dlg = wx.MessageDialog(self,u"请选择要变的卡组",caption=u'提示',style=wx.OK,pos=wx.DefaultPosition)
            retCode = dlg.ShowModal()
            if retCode == wx.ID_OK:
                dlg.Destroy()

        e.Skip()
    '''选择搜索套卡事件
    '''
    def onCollectThemeChoice(self,e):
        self.priceList = []
        self.priceList.append(u'全部')
        self.seachThemeIndex = self.collectThemeChoice.GetSelection()
        self.search_index = self.seachThemeIndex
        self.search_range_theme_choice.SetSelection(self.search_index)
        self.database.cu.execute("select price from cardinfo where  themeid=?",
                                 (int(self.themeIdList[self.seachThemeIndex]),))
        result =self.database.cu.fetchall()
        for item in result:
            price = item[0]
            if not str(price) in self.priceList:
                self.priceList.append(str(price))
        self.searchCardPriceChoice.SetItems(self.priceList)
        self.searchCardPriceChoice.SetSelection(0)
        self.ignoreEvtText = True
        e.Skip()


    '''使用输入搜索的方式
    '''
    def onCollectThemeSearch(self,e):
        self.priceList = []
        self.priceList.append(u'全部')
        self.database.cu.execute("select price from cardinfo where  themeid=?",
                                 (int(self.themeIdList[self.seachThemeIndex]),))
        result =self.database.cu.fetchall()
        for item in result:
            price = item[0]
            if not str(price) in self.priceList:
                self.priceList.append(str(price))
        self.searchCardPriceChoice.SetItems(self.priceList)
        self.searchCardPriceChoice.SetSelection(0)
        self.ignoreEvtText = True
        e.Skip()

    '''comboBox键盘监听事件
    '''
    def EvtChar(self, event):
        if event.GetKeyCode() == 8:
            self.ignoreEvtText = True
        event.Skip()

    '''commbobox内容变化事件
    '''
    def EvtText(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString()
        print currentText
        found = False
        for i,choice in enumerate(self.themeNameList) :
            if choice.startswith(currentText):
                self.ignoreEvtText = True
                self.collectThemeChoice.SetValue(choice)
                self.collectThemeChoice.SetInsertionPoint(len(currentText))
                self.collectThemeChoice.SetMark(len(currentText), len(choice))
                self.seachThemeIndex = i
                self.search_index = i
                found = True
                break
        if not found:
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
                self.commit_theme_choice.SetValue(choice)
                self.commit_theme_choice.SetInsertionPoint(len(currentText))
                self.commit_theme_choice.SetMark(len(currentText), len(choice))
                self.commit_index = i
                found = True
                break
        if not found:
            event.Skip()

    '''commbobox内容变化事件
    '''
    def EvtText3(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString()
        print currentText
        found = False
        for i,choice in enumerate(self.flash_card_name_list) :
            if choice.startswith(currentText):
                self.ignoreEvtText = True
                self.flash_card_theme_choic.SetValue(choice)
                self.flash_card_theme_choic.SetInsertionPoint(len(currentText))
                self.flash_card_theme_choic.SetMark(len(currentText), len(choice))
                self.flash_index = i
                found = True
                break
        if not found:
            event.Skip()

    '''commbobox内容变化事件
    '''
    def EvtText4(self, event):
        if self.ignoreEvtText:
            self.ignoreEvtText = False
            return
        currentText = event.GetString()
        print currentText
        found = False
        for i,choice in enumerate(self.themeNameList) :
            if choice.startswith(currentText):
                self.ignoreEvtText = True
                self.search_range_theme_choice.SetValue(choice)
                self.search_range_theme_choice.SetInsertionPoint(len(currentText))
                self.search_range_theme_choice.SetMark(len(currentText), len(choice))
                self.search_index = i
                found = True
                break
        if not found:
            event.Skip()



    '''选择卡片价格事件
    '''
    def onCardPriceChoice(self,e):
        if self.searchCardPriceChoice.GetSelection()!=0:
            self.detailCardChoice.Enable(True)
            self.database.cu.execute("select name from cardinfo where  themeid=? and price=?",
                                 (int(self.themeIdList[self.seachThemeIndex]),
                                  int(self.searchCardPriceChoice.GetStringSelection())))
            result =self.database.cu.fetchall()
            cardNameList = []
            cardNameList.append(u'全部')
            for item in result:
                cardName = item[0]
                cardNameList.append(cardName)
            self.detailCardChoice.SetItems(cardNameList)
            self.detailCardChoice.SetSelection(0)
        else:
            self.detailCardChoice.Enable(False)


    '''搜索主题
    '''
    def searchTheme(self,e):
        self.selectNum = -1
        self.cardFriendList=[]
        try:
            cardDetail = self.detailCardChoice.GetStringSelection()
            if cardDetail==u'全部' or cardDetail=='':
                cardDetail = -1
        except:
            cardDetail = -1
        if self.searchOnlyCheckBox.GetValue():
            search_range_theme_id = self.themeIdList[self.search_index]
        else:
            search_range_theme_id = -1
        self.searchThread = searchCardThread.SearchCardThread(self,self.myHttpRequest,
                                                         int(self.themeIdList[self.seachThemeIndex]),
                                                              self.searchCardPriceChoice.GetStringSelection(),
                                                              cardDetail,search_range_theme_id,self.is_show_flash_card.GetValue())
        self.searchThread.start()
        self.searchStop.Enable(True)
        self.searchBt.Enable(False)
        self.collectThemeChoice.Enable(False)
        self.detailCardChoice.Enable(False)
        self.searchCardPriceChoice.Enable(False)
        self.msgLog.SetValue("")
        self.import_log.SetValue("")
        self.seachTime = datetime.datetime.strftime(datetime.datetime.now(), '%Y_%m_%d_%H_%M_%S')
        self.userIdChoice.SetItems([])

        #创建excel
        self.wb = xlwt.Workbook()
        self.seachCardFriendNum = 0
        self.ws = self.wb.add_sheet(u'卡友信息')
        self.ws.write(0,0,u'QQ号')
        self.ws.write(0,1,u'卡片信息')
        self.ws.write(0,2,u'需交换的卡组')
        e.Skip()

    '''停止搜索
    '''
    def stopSearchTheme(self,e):
        self.searchThread.stop()
        self.searchStop.Enable(False)
        self.searchBt.Enable(True)
        self.collectThemeChoice.Enable(True)
        self.detailCardChoice.Enable(True)
        self.searchCardPriceChoice.Enable(True)

    '''完成搜索
    '''
    def searchComplete(self):
        #进行excel文件的保存
        self.wb.save(self.seachTime+u'搜索套卡'+self.themeNameList[self.seachThemeIndex]+u'卡友.xls')

    '''更新操作日志
    '''
    def updateLog(self,msg):
        self.msgLog.AppendText(msg+'\n')

    def update_import_log(self,msg):
        self.import_log.AppendText(msg+'\n')

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

    '''更新搜索到的卡友信息
    '''
    def updateCardFriend(self,user,msg,exchangTheme):

        self.cardFriendList.append(user)
        self.userIdChoice.SetItems(self.cardFriendList)
        self.userIdChoice.SetSelection(self.selectNum)
        self.seachCardFriendNum +=1
        self.ws.write(self.seachCardFriendNum,0,user)
        self.ws.write(self.seachCardFriendNum,1,msg)
        self.ws.write(self.seachCardFriendNum,2,exchangTheme)


    def update_search_progress(self,num):
        '''
        更新搜索的进度
        :param num:
        :return:
        '''
        self.search_progress.SetLabel(str(num)+"/"+str(constant.CARDUSERNUM))


    '''卡友列表被选择时
    '''
    def onCardUserChoice(self,e):
        self.selectNum = self.userIdChoice.GetSelection()
        self.hyper.SetURL(r'http://appimg2.qq.com/card/index_v3.html#opuin='+str(self.userIdChoice.GetValue()))
        e.Skip()

    def onHyper(self,e):
        print self.userIdChoice.GetValue()
        self.hyper.GotoURL(r'http://appimg2.qq.com/card/index_v3.html#opuin='+str(self.userIdChoice.GetValue()))