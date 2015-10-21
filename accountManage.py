# -*- coding: utf-8 -*-
import wx,time
import thread,json,logging,re,StringIO
import wx.lib.mixins.listctrl as listmix
from commonlib import constant
from commonlib import myhttp
from commonlib import commons
import mythread.getInfoThread as mythread
from bs4 import  BeautifulSoup
import commonlib.Tea as Tea
import threading
import urllib
import random



class TestListCtrl(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        # self.setResizeColumn(5)
        self.selectItem = -1
        self.account_select = []
        self.windows = self.GetParent()
        self.menu_title_by_id = {1:u'查看卡箱信息',2:u'锁交换箱',3:u'解锁交换箱'}
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK,self.onItemRightClick)

    def onItemRightClick(self,e):
        self.selectAccount = self.windows.clientIdDict[int(e.GetText())]
        menu = wx.Menu()
        for (menu_id,title) in self.menu_title_by_id.items():
            menu.Append(menu_id, title)
            wx.EVT_MENU( menu, menu_id, self.MenuSelectionCb )
        self.PopupMenu(menu,e.GetPoint())
        menu.Destroy()

    def MenuSelectionCb(self, event ):
            print event.GetId()

            if 1==event.GetId():

                postData = {
                                   'code':'',
                                   'uin':self.selectAccount
                }
                try:
                    self.myHttpRequest = self.windows.account_http_dic[self.selectAccount]
                    self.windows.current_account = self.selectAccount
                    self.windows.myHttpRequest = self.myHttpRequest
                    base_url =  self.getUrl(constant.CARDLOGINURL)
                    page_content = self.myHttpRequest.get_response(base_url,postData)
                    self.magicCardInfo= page_content.read()
                       #print self.magicCardInfo
                    self.getBoxInfo()
                except KeyError:
                    self.windows.operateLogUpdate(u'获取卡箱信息失败,请检查该账号是否登录')

    def getBoxInfo(self):
         infoThread1 = mythread.GetInfoThread(self.magicCardInfo,constant.EXCHANGEBOX,self.windows,self.myHttpRequest)
         infoThread1.start()
         infoThread2 = mythread.GetInfoThread(self.magicCardInfo,constant.STOREBOX,self.windows,self.myHttpRequest)
         infoThread2.start()



    #获取对应的url
    def getUrl(self,url):
        skey = ''
        for ck in self.myHttpRequest.cj:
                if ck.name=='skey':
                    skey = ck.value
        base_url = url
        base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
        return base_url


    def OnCheckItem(self, index, flag):
        print(index, flag)
        if flag:
            self.account_select[index] = 1
            self.selectItem = index
            self.selectCardName = self.GetItemText(index,1)
        else:
            self.account_select[index] = 0


class TestListCtrl2(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        # self.setResizeColumn(5)
        self.selectItem = -1
        self.windows = self.GetParent()


    def OnCheckItem(self, index, flag):
        print(index, flag)
        if flag:
            self.selectItem = index
            self.selectCardName = self.GetItemText(index,1)


class AccountManage(wx.Panel):


    account_http_dic = {}
    def __init__(self, parent,database):
        wx.Panel.__init__(self, parent=parent)
        self.head_list = [u'序号',u'账号',u'昵称',u'登陆状态']
        self.exchangeBoxlistHead = [u'换',u'卡片',u'卡片类型',u'价格']
        self.safeBoxlistHead = [u'保',u'卡片',u'卡片类型',u'价格']
        self.operate_list = [u'一键领取登陆礼包',u'一键领取100面值卡片',u'一键送礼物卡',u'一键小号420魔力']
        self.myHttpRequest = myhttp.MyHttpRequest()
        #当前的选择的账号

        self.current_account = 0
        self.clientIdDict = {}
        self.exchangeBox = []
        self.storeBox =[]
        self.stoveBox = []
        self.account_list = []
        self.accout_sid_dic = {}
        self.account_dic = {}
        self.database = database

        self.sb = wx.StaticBox(self,label=u'账号管理')
        self.list_sizer = wx.StaticBoxSizer(self.sb,wx.VERTICAL)
        self.button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.import_account_bt = wx.Button(self,-1,u'一键账号导入')
        self.import_account_bt.Bind(wx.EVT_BUTTON,self.OnOpen)
        self.account_login_bt = wx.Button(self,-1,u'一键账号登陆')
        self.account_login_bt.Bind(wx.EVT_BUTTON,self.OnLogin)
        self.account_choice = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.operate_list)
        self.account_choice.Bind(wx.EVT_CHOICE,self.onOperateSelect)
        self.account_send_gift_label = wx.StaticText(self,-1,u'QQ号')
        self.account_send_gift_text = wx.TextCtrl(self,-1)
        self.account_send_gift_text.Enable(False)
        self.account_action = wx.Button(self,-1,u'执行')
        self.account_action.Bind(wx.EVT_BUTTON,self.onAction)
        self.codeImage=wx.StaticBitmap(self, -1,  pos=wx.DefaultPosition, size=(150,80))
        self.codeLabel = wx.StaticText(self,-1,u'验证码')#-1的意义为id由系统分配
        self.codeInput = wx.TextCtrl(self,-1)
        self.codeInput.Bind(wx.EVT_TEXT, self.OnChar)
        # self.submit.Bind(wx.EVT_BUTTON,self.on_submit)
        self.codeLabel.Show(False)
        self.codeInput.Show(False)
        self.codeImage.Show(False)
        self.button_sizer.Add(self.import_account_bt,0,wx.ALL,5)
        self.button_sizer.Add(self.account_login_bt,0,wx.ALL,5)
        self.button_sizer.Add(self.account_choice,0,wx.ALL,5)
        self.button_sizer.Add(self.account_send_gift_label,0,wx.ALL,5)
        self.button_sizer.Add(self.account_send_gift_text,0,wx.ALL,5)
        self.button_sizer.Add(self.account_action,0,wx.ALL,5)
        self.button_sizer.Add(self.codeLabel,0,wx.ALL,5)
        self.button_sizer.Add(self.codeInput,0,wx.ALL,5)
        self.button_sizer.Add(self.codeImage,0,wx.ALL,1)
        self.sloveBoxList = TestListCtrl(self,style=wx.LC_REPORT)
        self.sloveBoxList.SetBackgroundColour((227,237,205))
        self.opreateLog = wx.TextCtrl(self,-1,size=(450,300),style=wx.TE_MULTILINE)
        self.opreateLog.SetBackgroundColour((227,237,205))

        # self.list_sizer.Add(self.sloveBoxList,1,wx.ALL,5)
        # self.list_sizer.Add(self.opreateLog,1,wx.ALL,5)
        for col,text in enumerate (self.head_list):
            self.sloveBoxList.InsertColumn(col,text)
            self.sloveBoxList.SetColumnWidth(col,100)

        #-------------换卡箱----------
        self.exchangesb  = wx.StaticBox(self,label = u'换卡箱')
        self.exchangeBoxSizer = wx.StaticBoxSizer(self.exchangesb,wx.VERTICAL)
        #添加一个列表控件 style使用报表的模式 并且插入头
        self.exchangeBoxlist = TestListCtrl2(self,style=wx.LC_REPORT)
        self.exchangeBoxlist.SetBackgroundColour((227,237,205))
        for col,text in enumerate (self.exchangeBoxlistHead):
            self.exchangeBoxlist.InsertColumn(col,text)
        self.exchangeBoxlist.Arrange()
        #-------------换卡箱按钮的集合----------
        self.exchangeBoxButtonSize = wx.BoxSizer(wx.HORIZONTAL)
        self.inputSafeBox = wx.Button(self,-1,u'放入保险箱')
        self.saleSelectCard = wx.Button(self,-1,u'出售勾选卡片')
        self.saleSelectCard.Bind(wx.EVT_BUTTON,self.saleCardEvent)
        self.inputSafeBox.Bind(wx.EVT_BUTTON, self.inputCardToStore)
        self.exchangeBoxButtonSize.Add(self.inputSafeBox,0,wx.ALL,5)
        self.exchangeBoxButtonSize.Add(self.saleSelectCard,0,wx.ALL,5)
        self.exchangeBoxSizer.Add(self.exchangeBoxlist,0,wx.ALL,5)
        self.exchangeBoxSizer.Add(self.exchangeBoxButtonSize,0,wx.ALL,5)


        #------------保险箱---------------------
        self.safeSB  = wx.StaticBox(self,label = u'保险箱')
        self.safeBoxSizer = wx.StaticBoxSizer(self.safeSB,wx.VERTICAL)
        #添加一个列表控件 style使用报表的模式 并且插入头
        # self.safeBoxLabel = wx.StaticText(self,-1,u'0/0')
        self.safeBoxlist = TestListCtrl2(self,style=wx.LC_REPORT)
        self.safeBoxlist.SetBackgroundColour((227,237,205))
        for col,text in enumerate (self.safeBoxlistHead):
            self.safeBoxlist.InsertColumn(col,text)
        self.inputExchangeBox = wx.Button(self,-1,u'放入换卡箱')
        self.inputExchangeBox.Bind(wx.EVT_BUTTON, self.inputCardToExchange)
        # self.safeBoxSizer.Add(self.safeBoxLabel,0,wx.ALL,0)
        self.safeBoxSizer.Add(self.safeBoxlist,0,wx.ALL,5)
        self.safeBoxSizer.Add(self.inputExchangeBox,0,wx.ALL,5)


        #-----------------总布局
        self.horizontal= wx.BoxSizer(wx.HORIZONTAL)
        self.vertical1= wx.BoxSizer(wx.VERTICAL)
        self.vertical2= wx.BoxSizer(wx.VERTICAL)
        self.vertical1.Add(self.sloveBoxList,1,wx.ALL,5)
        self.vertical1.Add(self.opreateLog,1,wx.ALL,5)
        self.vertical2.Add(self.exchangeBoxSizer,1,wx.ALL,5)
        self.vertical2.Add(self.safeBoxSizer,1,wx.ALL,5)
        self.horizontal.Add(self.vertical1,1,wx.ALL,5)
        self.horizontal.Add(self.vertical2,1,wx.ALL,5)
        self.list_sizer.Add(self.button_sizer,0,wx.ALL,5)
        self.list_sizer.Add(self.horizontal,0,wx.ALL,5)
        #---------------------------

        self.SetSizer(self.list_sizer)
        self.SetAutoLayout(1)
        self.Center()
        self.Show(True)



        try:
            self.readAccountFile('account_info.txt')

        except Exception:
            print 'Mfkp_config.ini not exist'



    #出售卡片事件
    def saleCardEvent(self,e):
         cardId = self.exchangeBox[self.exchangeBoxlist.selectItem]
         self.saleCard(cardId,self.exchangeBoxlist.selectItem)
         self.exchangeBoxlist.CheckItem(self.exchangeBoxlist.selectItem, False)

     #出售卡片
    def saleCard(self,cardId,slotNo):
         if cardId!=1162:
             postData = {
                             'slot_no':slotNo,
                             'uin':self.current_account,
                             'type':0,
                             'cardid':cardId
             }

             base_url =  commons.getUrl(constant.SALECARD,self.myHttpRequest)
             page_content = self.myHttpRequest.get_response(base_url,postData).read().decode('utf-8')
             print page_content
             self.operateLogUpdate(u'出售卡片 :'+self.exchangeBoxlist.GetItemText(slotNo,1))
             for i in range(1,4):
                 self.exchangeBoxlist.SetStringItem(slotNo,i,"")
             self.exchangeBox[slotNo] = 0
         else:
             self.operateLogUpdate(u'无法出售百变卡')

    #卡片放入储物箱
    def inputCardToStore(self,e):
        #先获取保险箱是否有空位
         cardId = self.exchangeBox[self.exchangeBoxlist.selectItem]
         self.card_user_storage_exchange(0, self.exchangeBoxlist.selectItem,cardId)
         self.exchangeBoxlist.CheckItem(self.exchangeBoxlist.selectItem, False)

    #卡片储物箱互换
    def card_user_storage_exchange(self,type,src,cardId):
         des = -1
         if type==0:
             logging.info(self.storeBox)
             for i,cardIdTemp in enumerate(self.storeBox):
                 if cardIdTemp == 0:
                     des = i
                     break
         else:
             des = self.exchangeBoxEmpty()

         postData = {
                         'dest':des,
                         'src':src,
                         'type':type,
                         'uin':self.current_account,
         }
         base_url = commons.getUrl(constant.CARDINPUTSTOREBOX,self.myHttpRequest)
         self.myHttpRequest.get_response(base_url,postData)
         if type==0:
             self.operateLogUpdate(u'卡片 :'+self.exchangeBoxlist.GetItemText(src,1)+u'放入保险箱')
             self.storeBox[des] = cardId
             self.exchangeBox[src]=0

         else:
             self.operateLogUpdate(u'卡片 :'+self.safeBoxlist.GetItemText(src,1)+u'放入换卡箱')
             self.exchangeBox[des] = cardId
             self.storeBox[src]=0

         for i in range(1,4):
             if type==0:
                 #print 'src',str(src),'des',str(des),'col',str(i),self.exchangeBoxlist.GetItemText(src,i)
                 self.safeBoxlist.SetStringItem(des,i,self.exchangeBoxlist.GetItemText(src,i))
                 self.exchangeBoxlist.SetStringItem(src,i,"")
             else:
                #print 'src',str(src),'des',str(des),'col',str(i),self.safeBoxlist.GetItemText(src,i)
                 self.exchangeBoxlist.SetStringItem(des,i,self.safeBoxlist.GetItemText(src,i))
                 self.safeBoxlist.SetStringItem(src,i,"")


    def inputCardToExchange(self,e):
         #先获取交换箱是否有空位
         cardId =  self.storeBox[self.safeBoxlist.selectItem]
         self.card_user_storage_exchange(1, self.safeBoxlist.selectItem, cardId)
         self.safeBoxlist.CheckItem(self.safeBoxlist.selectItem, False)

     #获取交换箱的空位
    def exchangeBoxEmpty(self):
         #先获取交换箱是否有空位
         for i,cardId in enumerate(self.exchangeBox):
             if cardId == 0:
                 return  i
         return -1


    def send_card(self):
        '''
        小号送祝福卡
        :return:
        '''
        flag = False
        send_friend = self.account_send_gift_text.GetValue()

        if send_friend=='':
            j = 0
            for account in self.account_list:
                try:
                    value =  self.__class__.account_http_dic[account]
                except KeyError:
                    continue
                base_url = commons.getUrl(constant.GQACTIVITY,value)
                post_data = {
                    'act':1
                }
                content_page = value.get_response(base_url,post_data).read().decode('utf-8')
                count = int(json.loads(content_page)['jf'])
                for i in range(0,count):
                    post_data = {
                        'act':6,
                        'opuin':int(self.account_list[j])
                    }
                    content_page = value.get_response(base_url,post_data).read().decode('utf-8')
                    if u'10份'in content_page:
                        wx.CallAfter(self.operateLogUpdate,str(send_friend)+u'该好友已经收满10份祝福卡')
                        j +=1
                    else:
                        wx.CallAfter(self.operateLogUpdate,str(account)+u'送祝福卡成功')
        else:
            for key in self.account_list:
                try:
                    value =  self.__class__.account_http_dic[key]
                except KeyError:
                    continue
                base_url = commons.getUrl(constant.GQACTIVITY,value)
                post_data = {
                    'act':1
                }
                content_page = value.get_response(base_url,post_data).read().decode('utf-8')
                count = int(json.loads(content_page)['jf'])
                # wx.CallAfter(self.operateLogUpdate,str(key)+u'有'+str(count)+u'祝福卡')

                for i in range(0,count):
                    post_data = {
                        'act':6,
                        'opuin':int(send_friend)
                    }
                    content_page = value.get_response(base_url,post_data).read().decode('utf-8')
                    print content_page
                    if u'10份'in content_page:
                        wx.CallAfter(self.operateLogUpdate,str(send_friend)+u'该好友已经收满10份祝福卡')
                        flag = True
                        break
                    else:
                        wx.CallAfter(self.operateLogUpdate,str(key)+u'送祝福卡成功')
                if flag:
                    break

    def OnChar(self,e):
        if len(self.codeInput.GetValue())>=4:
            constant.NEWCODE = str(self.codeInput.GetValue())
            self.codeInput.SetValue("")
            self.codeLabel.Show(False)
            self.codeInput.Show(False)
            self.codeImage.Show(False)
        e.Skip()


    #界面更新
    def updateInfo(self,flag,timelist=None,userInfo=None):
         if flag==constant.EXCHANGEBOX:
            print u'交换箱id信息',self.exchangeBox
            self.exchangesb.SetLabel(u'交换箱 ('+str(len(self.exchangeBox)-self.exchangeBox.count(0))+'/'+str(len(self.exchangeBox))+')')
            self.exchangeBoxlist.DeleteAllItems()
            for cardId in self.exchangeBox:
                if cardId!=0:
                    self.database.cu.execute("select name,price,themeid from cardinfo where pid=?",(cardId,))
                    result = self.database.cu.fetchone()
                    self.database.cu.execute("select name from cardtheme where pid=?",(result[2],))
                    self.exchangeBoxlist.Append(["",result[0],self.database.cu.fetchone()[0],result[1]])
                else:
                    self.exchangeBoxlist.Append(["","","",""])

         elif flag==constant.STOREBOX:
             print u'保险箱id信息',self.storeBox
             self.safeSB.SetLabel(u'保险箱 ('+str(len(self.storeBox)-self.storeBox.count(0))+'/'+str(len(self.storeBox))+')')
             self.safeBoxlist.DeleteAllItems()
             for cardId in self.storeBox:
                 if cardId!=0:
                     self.database.cu.execute("select name,price,themeid from cardinfo where pid=?",(cardId,))
                     result = self.database.cu.fetchone()

                     self.database.cu.execute("select name from cardtheme where pid=?",(result[2],))
                     self.safeBoxlist.Append(["",result[0],self.database.cu.fetchone()[0],result[1]])
                 else:
                     self.safeBoxlist.Append(["","","",""])




    def onAction(self,e):
        print self.account_choice.GetSelection()
        if self.account_choice.GetSelection()==0:
            self.operateLogUpdate(u'领取礼包会在相应时间点进行，请等待..')
            thread.start_new_thread(self.get_login_gift,())
            pass
        elif self.account_choice.GetSelection()==1:
            thread.start_new_thread(self.get_card_gift,())
            pass
        elif self.account_choice.GetSelection()==2:
            thread.start_new_thread(self.send_card_gift,())
        elif self.account_choice.GetSelection()==3:

            thread.start_new_thread(self.accountGetMana,())
        elif self.account_choice.GetSelection()==4:
            thread.start_new_thread(self.act_get_score,())
            pass
        elif self.account_choice.GetSelection()==5:
            thread.start_new_thread(self.act_egg,())
        elif self.account_choice.GetSelection()==6:
            thread.start_new_thread(self.act_exchange_score,(0,))
            pass
        elif self.account_choice.GetSelection()==7:
            thread.start_new_thread(self.act_exchange_score,(1,))
        elif self.account_choice.GetSelection()==8:
            thread.start_new_thread(self.act_exchange_score,(2,))
        elif self.account_choice.GetSelection()==9:
            thread.start_new_thread(self.act_exchange_score,(2,True))

        # elif self.account_choice.GetSelection()==9:
        #     thread.start_new_thread(self.act_get_score,())
        # elif self.account_choice.GetSelection()==10:
        #     thread.start_new_thread(self.act_egg,())
        e.Skip()


    def get_gq_gift(self,gq_id):
        '''
        领取国庆累计登录礼包
        :param gq_id:
        :return:
        '''
        for key in self.account_list:
            try:
                value =  self.__class__.account_http_dic[key]
            except KeyError:
                continue
            base_url = commons.getUrl(constant.GQGETGIFTS,value)
            post_data = {
                'act':2,
                'id':gq_id,
            }
            page_content = value.get_response(base_url,post_data).read().decode('utf--8')
            if 'sucess' in page_content:
                wx.CallAfter(self.operateLogUpdate,str(key)+u'领取国庆累计登录礼包成功')
            else:
                wx.CallAfter(self.operateLogUpdate,str(key)+u'领取国庆累计登录礼包失败')
        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')

    def account_commission(self):
        '''
        国庆任务提交
        :return:
        '''
        for key in self.account_list:
            try:
                value =  self.__class__.account_http_dic[key]
            except KeyError:
                continue
            try:
                levelup = commons.getUrl(constant.LEVELUP,value)
                post_data = {
                    'uin':key
                }
                value.get_response(levelup,post_data).read().decode('utf-8')


                mobileHttp = myhttp.MyHttpRequest()
                base_url = commons.getUrl(constant.GQACTIVITY,value)

                post_data={
                    'act':1,
                }
                value.get_response(base_url,post_data).read().decode('utf-8')
                post_data={
                    'act':2,
                }
                logging.info(value.get_response(base_url,post_data).read().decode('utf-8'))
                wx.CallAfter(self.operateLogUpdate,str(key)+u'接受国庆任务')
                post_data = {
                    'act':3,
                    'id':13,
                }
                page_content =  value.get_response(base_url,post_data).read().decode('utf-8')
                if u'没有完成' in page_content or u'系统繁忙' in page_content :
                    wx.CallAfter(self.operateLogUpdate,str(key)+u'完成每日登陆游戏失败')
                else:
                    wx.CallAfter(self.operateLogUpdate,str(key)+u'每日登陆任务已完成')

                wx.CallAfter(self.operateLogUpdate,str(key)+u'检查卡炉是否有可收的卡')
                mobile_url = constant.MOBILEMAINPAGE
                mobile_url = mobile_url.replace('SID',urllib.quote(self.accout_sid_dic[key]))
                page_content = mobileHttp.get_response(mobile_url).read().decode('utf-8')

                cardcomplete = commons.getStoveBoxInfo(commons.getMagicInfo(value,key))
                if u'取卡' in page_content and 1 in cardcomplete:
                    wx.CallAfter(self.operateLogUpdate,str(key)+u'有卡可以收获')
                    mobile_url = constant.MOBILEREFINEDCARD
                    mobile_url.replace('SID',self.accout_sid_dic[key])
                    position = cardcomplete.index(1)
                    mobile_refined_url = constant.MOBILEREFINEDCARD.replace('SID',urllib.quote(self.accout_sid_dic[key]))
                    mobile_refined_url +=str(position)
                    print mobile_refined_url
                    wx.CallAfter(self.operateLogUpdate,str(key)+u'收获卡片')
                    mobileHttp.get_response(mobile_refined_url).read().decode('utf-8')
                    wx.CallAfter(self.operateLogUpdate,str(key)+u'提交任务收获卡片任务')
                    post_data = {
                        'act':3,
                        'id':2,
                    }
                    page_content =  value.get_response(base_url,post_data).read().decode('utf-8')

                    print page_content
                    if u'没有完成' in page_content or u'系统繁忙' in page_content :
                        wx.CallAfter(self.operateLogUpdate,str(key)+u'取卡任务失败')
                    else:
                        wx.CallAfter(self.operateLogUpdate,str(key)+u'取卡任务已完成')
                    wx.CallAfter(self.operateLogUpdate,str(key)+u'进行翻牌')
                    commons.fanpai(value)
                    post_data = {
                        'act':3,
                        'id':3,
                    }
                    page_content =  value.get_response(base_url,post_data).read().decode('utf-8')
                    if u'没有完成' in page_content or u'系统繁忙' in page_content :
                        wx.CallAfter(self.operateLogUpdate,str(key)+u'翻牌任务失败')
                    else:
                        wx.CallAfter(self.operateLogUpdate,str(key)+u'翻牌任务已完成')
                else:
                    wx.CallAfter(self.operateLogUpdate,str(key)+u'没有可收获的先进行炼卡，请一小时后重新进行任务')
                    mobile_card_url = constant.MOBILELIANCARD.replace('SID',urllib.quote(self.accout_sid_dic[key]))
                    mobileHttp.get_response(mobile_card_url).read()
            except:
                wx.CallAfter(self.operateLogUpdate,str(key)+u'做任务出现异常')
        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')

    def gq_login(self):
        '''
        国庆登陆礼包领取
        :return:
        '''
        for key in self.account_list:
            try:
                value =  self.__class__.account_http_dic[key]
            except KeyError:
                continue
            base_url = commons.getUrl(constant.GQGETGIFTS,value)
            post_data = {
                'act':1
            }
            page_content = value.get_response(base_url,post_data).read().decode('utf-8')
            logging.info(page_content)
            result = ''
            if 'pack_str' in page_content:
                card_list =  re.findall('(\d+)_(.*?)_(\d+)',page_content,re.S)
                for list_item in card_list:
                    if list_item[0] in constant.GIFTDICT:
                        result += constant.GIFTDICT[list_item[0]]+'*'+list_item[2]
                    elif list_item[0] =='48':
                        if list_item[1]=='19':
                            result+=u'积分'+'*'+list_item[2]
                        elif list_item[1]=='14':
                            result+= u'7天租铺卡'+'*'+list_item[2]
                        elif list_item[1]=='8':
                            result+= u'3天累计卡'+'*'+list_item[2]
                        elif list_item[1]=='17':
                            result+= u'3天经验卡'+'*'+list_item[2]
                        elif list_item[1]=='18':
                            result+= u'7天经验卡'+'*'+list_item[2]
                        else:
                            result+= u'未知',list_item
                            logging.info(list_item[0]+','+list_item[1]+','+list_item[2])
                    result+=','
            else:
                wx.CallAfter(self.operateLogUpdate,str(key)+u'今天已经领取过了')
            if result!='':
                wx.CallAfter(self.operateLogUpdate,str(key)+result)
        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')

    def get_type_info(self,flag,magicCardInfo):
        '''
        获取卡片信息
        :param flag:
        :param magicCardInfo:
        :return:
        '''
        exchange_box = []
        store_box = []
        childlist = []
        soup = BeautifulSoup(magicCardInfo)
        if flag==constant.EXCHANGEBOX:
            childlist = soup.changebox.children
            exchange_box = [0]*int(soup.changebox['cur'])
        elif flag==constant.STOREBOX:
            childlist = soup.storebox.children
            constant.STOREBOXNUM = int(soup.storebox['cur'])
            self.store_box = [0]*constant.STOREBOXNUM

        for item in childlist:
            if item != u'\n':
                soup2 = BeautifulSoup(str(item))
                pid = int(soup2.card['id'])

                if flag==constant.EXCHANGEBOX:
                    if pid==-1:
                        exchange_box[int(soup2.card['slot'])] = 0
                    else:
                        exchange_box[int(soup2.card['slot'])] = pid
                elif flag==constant.STOREBOX:
                    store_box[int(soup2.card['slot'])] = pid

        if flag==constant.EXCHANGEBOX:
            return exchange_box
        else:
            return store_box

    def accountGetMana(self,):
        '''
        小号420魔力
        :param account:
        :param myhttpRequest:
        :return:
        '''
        for account in self.account_list:
            try:
                myhttpRequest =  self.__class__.account_http_dic[account]
            except KeyError:
                continue
            if '-1005' in commons.getMagicInfo(myhttpRequest,account):
                logging.info(u'用户未开通魔卡，开通魔卡')
                commons.registerMagic(myhttpRequest)
                commons.getMagicInfo(myhttpRequest,account)
                commons.magicCardGuide(myhttpRequest,account,102,0)
                commons.completeMission(myhttpRequest,102)
                commons.magicCardGuide(myhttpRequest,account,103,0)
                commons.magicCardGuide(myhttpRequest,account,103,0)
                commons.cardExchange(myhttpRequest,account,2,0,1)
                commons.sellCard(myhttpRequest,account,0,2373,0)
                for i in range(2,20):
                    commons.buyCard(myhttpRequest,688,85)
                    commons.cardExchange(myhttpRequest,account,0,i,0)
                for i in range(0,5):
                    commons.buyCard(myhttpRequest,688,85)
                commons.drawCard(myhttpRequest,2,5)

                if 'lgiftmana="100"'in  commons.completeMission(myhttpRequest,103):
                    wx.CallAfter(self.operateLogUpdate,account+u'step1,100魔力')
                else:

                    wx.CallAfter(self.operateLogUpdate,account+u'step1,100魔力失败')
                commons.magicCardGuide(myhttpRequest,account,104,0)
                commons.magicCardGuide(myhttpRequest,account,104,0)
                commons.completeMission(myhttpRequest,104)
                commons.magicCardGuide(myhttpRequest,account,105,0)
                commons.magicCardGuide(myhttpRequest,account,105,0)


                if 'lgiftmana="100"'in  commons.completeMission(myhttpRequest,105):
                    wx.CallAfter(self.operateLogUpdate,account+u'step2,100魔力')
                else:
                    wx.CallAfter(self.operateLogUpdate,account+u'step2,100魔力失败')

                commons.magicCardGuide(myhttpRequest,account,105,3)
                commons.magicCardGuide(myhttpRequest,account,106,0)
                commons.magicCardGuide(myhttpRequest,account,106,0)

                if 'lgiftmana="100"'in  commons.completeMission(myhttpRequest,106):
                   wx.CallAfter(self.operateLogUpdate,account+u'step3,100魔力')
                else:
                   wx.CallAfter(self.operateLogUpdate,account+u'step3,100魔力失败')

                commons.magicCardGuide(myhttpRequest,account,106,5)
                commons.completeMission(myhttpRequest,107,40)
                wx.CallAfter(self.operateLogUpdate,account+u'step4,120魔力')
            else:
                wx.CallAfter(self.operateLogUpdate,account+u'用户已开通魔卡')

        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')



    def onOperateSelect(self,e):
        if self.account_choice.GetSelection()==2 or self.account_choice.GetSelection()==6:
            self.account_send_gift_text.Enable(True)
        else:
            self.account_send_gift_text.Enable(False)
        e.Skip()

    def act_exchange_score(self,m_id,is_complete=False):
        '''
        积分兑换礼物
        :param m_id:
        :return:
        '''
        for account in self.account_list:
            try:
                value =  self.__class__.account_http_dic[account]
            except KeyError:
                continue
            base_url =  commons.getUrl(constant.ACTEGG,value)
            post_data = {
                'act':6,
                'id':m_id
            }
            page_content = value.get_response(base_url,post_data).read().decode('utf-8')
            if 'sucess' in page_content:

                wx.CallAfter(self.operateLogUpdate,str(account)+u'兑换成功')
                if m_id==2 and is_complete:
                    base_url =constant.COMMITCARD
                    base_url = base_url.replace('SID', urllib.quote(self.accout_sid_dic[account]))
                    base_url = base_url.replace('THEMEID',str(428))
                    page_content = value.get_response(base_url)
                    result_content = page_content.read().decode('utf-8')
                    print result_content
                    logging.info(result_content)
                    if u'成功放入集卡册' in result_content:
                        wx.CallAfter(self.operateLogUpdate,u'提交套卡成功')
                    elif u'找不到相应的记录' in result_content:
                        wx.CallAfter(self.operateLogUpdate,u'提交失败，请检查卡片是否齐全')

            else:
                wx.CallAfter(self.operateLogUpdate,str(account)+u'兑换失败')

        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')

    def act_open_happy_card(self):
        '''
        一键打开幸福卡
        :return:
        '''
        for account in self.account_list:
            try:
                value =  self.__class__.account_http_dic[account]
            except KeyError:
                continue
            base_url =  commons.getUrl(constant.GQACTIVITY,value)
            post_data = {
                'act':7,
            }
            page_content = value.get_response(base_url,post_data).read().decode('utf-8')
            result = ''
            if 'pack_str' in page_content:
                card_list =  re.findall('(\d+)_(.*?)_(\d+)',page_content,re.S)
                for list_item in card_list:
                    if list_item[0] in constant.GIFTDICT:
                        result += constant.GIFTDICT[list_item[0]]+'*'+list_item[2]
                    elif list_item[0] =='48':
                        if list_item[1]=='19':
                            result+=u'积分'+'*'+list_item[2]
                        elif list_item[1]=='14':
                            result+= u'7天租铺卡'+'*'+list_item[2]
                        elif list_item[1]=='8':
                            result+= u'3天累计卡'+'*'+list_item[2]
                        elif list_item[1]=='17':
                            result+= u'3天经验卡'+'*'+list_item[2]
                        elif list_item[1]=='18':
                            result+= u'7天经验卡'+'*'+list_item[2]
                        else:
                            result+= u'未知',list_item
                            logging.info(list_item[0]+','+list_item[1]+','+list_item[2])
                    result+=','
                if result!='':
                    wx.CallAfter(self.operateLogUpdate,str(account)+result)
            else:
                wx.CallAfter(self.operateLogUpdate,str(account)+u'无幸福卡打开')
        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')


    def act_get_score(self):
        '''
        查看茱萸个数
        :return:
        '''

        for key in self.account_list:
            try:
                value =  self.__class__.account_http_dic[key]
            except KeyError:
                continue
            base_url = commons.getUrl(constant.ACTEGG,value)
            post_data = {
                'act':4
            }
            content_page = value.get_response(base_url,post_data).read().decode('utf-8')
            xf_dian = int(json.loads(content_page)['vt26'])
            wx.CallAfter(self.operateLogUpdate,str(key)+u'茱萸个数：'+str(xf_dian))

        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')
    def act_egg(self):
        '''
        登高
        :return:
        '''
        for key in self.account_list:
            try:
                value =  self.__class__.account_http_dic[key]
            except KeyError:
                continue
            base_url = commons.getUrl(constant.ACTEGG,value)
            post_data = {
                'act':4
            }
            content_page = value.get_response(base_url,post_data).read().decode('utf-8')
            count = int(json.loads(content_page)['free_cnt'])
            zy_old_count = int(json.loads(content_page)['vt26'])
            base_url =  commons.getUrl(constant.ACTEGG,value)
            post_data = {
                'act':5
            }

            for i in range(count):
                page_content = value.get_response(base_url,post_data).read().decode('utf-8')
                logging.info(page_content)
                if 'sucess' in page_content:
                    zy_count = int(json.loads(page_content)['vt26'])
                    wx.CallAfter(self.operateLogUpdate,str(key)+u'获得茱萸：'+str(zy_count-zy_old_count))
                    zy_old_count = zy_count
                else:
                    wx.CallAfter(self.operateLogUpdate,str(key)+u'今天已经玩过登高了')
                    break
        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')

    def OnSendGift(self,e):
        thread.start_new_thread(self.send_card_gift,())
        e.Skip()

    def send_card_gift(self):
        '''
        送礼物卡
        :return:
        '''
        send_count = 0
        for key in self.account_list:
            try:
                value =  self.__class__.account_http_dic[key]
            except KeyError:
                continue

            base_url =  commons.getUrl(constant.SENDCARD,value)
            post_data = {
                'appid':365,
                'friends':self.account_send_gift_text.GetValue(),
                'freegift_id':random.randint(75,80),
                'sfcount':0,
                'uin':key,
                'cb':1,
                'r':'0.'+commons.getRandomNum(16),
                'qzreferrer':'http://qzs.qq.com/snsapp/app/free_gift/index.htm?appid=365&page=receive'
            }
            page_content = value.get_response(base_url,post_data).read().decode('utf-8')
            logging.info(page_content)
            if '"msg":"ok"' in page_content:
                send_count +=1
                wx.CallAfter(self.operateLogUpdate,str(key)+u'送礼物卡成功')
            else:
                wx.CallAfter(self.operateLogUpdate,str(key)+u'送礼物卡失败')
            if send_count>=45:
                break
        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')
    def OnCardGift(self,e):
        thread.start_new_thread(self.get_card_gift,())
        e.Skip()


    def get_card_gift(self):

        for key in self.account_list:
            try:
                value =  self.accout_sid_dic[key]
            except KeyError:
                continue
            myhttps = self.__class__.account_http_dic[key]
            base_url = commons.getUrl(constant.GETCARD,myhttps)
            post_data = {
                'sid':value,
                'loginuin':key,
                'actid':3006,
                'appid':200,
                'packid':612
            }
            print post_data
            pagecontent = myhttps.get_response(base_url,post_data).read().decode('utf-8')
            logging.info(pagecontent)
            if '"ecode":0' in pagecontent:
                wx.CallAfter(self.operateLogUpdate,u'领取100面值卡成功')
            elif '"ecode":9' in pagecontent:
                wx.CallAfter(self.operateLogUpdate,u'领取100达到限制')
            else:
                wx.CallAfter(self.operateLogUpdate,u'领取100面值卡失败')
        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')

    def OnLoginGift(self,e):
        self.operateLogUpdate(u'领取礼包会在相应时间点进行，请等待..')
        thread.start_new_thread(self.get_login_gift,())
        e.Skip()


    def get_login_gift(self):

        for key in self.account_list:
            try:
                value =  self.__class__.account_http_dic[key]
            except KeyError:
                continue
            while True:
                a = (abs(int(time.time())/600*600-int(time.time()))%100)
                #print a
                if 95<a<99:

                    base_url = self.getUrl(value,constant.MONEYDRAW)
                    postData = {
                           'uin':constant.USERNAME
                    }
                    page_content = value.get_response(base_url,postData).read()
                    logging.info(page_content)
                    soup = BeautifulSoup(page_content)
                    try:
                        money = soup.qqhome['money_plus']
                        if money!='0':
                            money +=u'金币'
                        else:
                            money = soup.qqhome['mn5day']
                            if money=='100':
                                money+=u'魔力'

                        wx.CallAfter(self.operateLogUpdate,str(key)+u'领取第'+soup.qqhome['days']+u'天登陆礼包'+money)
                        break
                    except:
                        wx.CallAfter(self.operateLogUpdate,u'今天已领取过礼包')
                        break
        wx.CallAfter(self.operateLogUpdate,u'一键任务完成')

     #Log记录更新
    def operateLogUpdate(self,msg):
         nowtime = time.localtime(time.time())
         self.opreateLog.AppendText('['+str(time.strftime('%H:%M:%S',nowtime))+']'+msg+'\n')


    def OnLogin(self,e):

        t = threading.Thread(target=self.login_thread)
        t.start()
        e.Skip()

    def update_list(self,row,column,value):
        self.sloveBoxList.SetStringItem(row,column,value)

    def login_thread(self):
        print self.sloveBoxList.account_select
        i = -1
        for key in self.account_list:
            value =  self.account_dic[key]
            i +=1
            if 1 in self.sloveBoxList.account_select:
                if self.sloveBoxList.account_select[i]!=1:
                    continue
            my_http_request = myhttp.MyHttpRequest()
            repeat = True
            page_content = ''
            while repeat:
                if self.getCode(my_http_request,key)==1:
                    base_url = constant.CODEPIC2
                    randomNum = commons.getRandomNum(4)
                    base_url = base_url.replace('UIN', str(key))
                    base_url = base_url.replace('RANDOM', '0.'+randomNum)
                    base_url = base_url.replace('CD', self.cap_cd)
                    page_content = my_http_request.get_response(base_url).read()
                    self.show_image_code(page_content)

                    while constant.NEWCODE=='':
                        time.sleep(1)
                    if constant.NEWCODE=='CLOSE':
                        break
                    verifysession = ''
                    for ck in my_http_request.cj:
                        if ck.name=='verifysession':
                            verifysession = ck.value

                    repeat,page_content = self.loginQQ(my_http_request,key,value,verifysession,constant.NEWCODE)
                    self.show_image_code(0)
                    constant.NEWCODE=''
                    if repeat==-2:

                        break
                else:
                    repeat,page_content = self.loginQQ(my_http_request,key,value,str(constant.SESSION),str(constant.CODE))
                    pass
            self.__class__.account_http_dic[key] = my_http_request
            if constant.NEWCODE!='CLOSE':
                if repeat==-2:
                    wx.CallAfter(self.update_list,i,3,u'账号冻结')
                else:
                    wx.CallAfter(self.update_list,i,3,u'登陆成功')
                    try:
                        result  = re.findall('\'1\',\'(.*?)\', \'(.*?)\'',page_content,re.S)
                        wx.CallAfter(self.update_list,i,2,result[0][1])
                    except:
                        pass
            constant.NEWCODE = ''

        self.codeImage.Show(False)
        self.codeLabel.Show(False)
        self.codeInput.Show(False)
        self.list_sizer.Layout()

    #获取对应的url
    def getUrl(self,myHttpRequest,url):
         skey = ''
         for ck in myHttpRequest.cj:
                 if ck.name=='skey':
                     skey = ck.value
         base_url = url
         base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
         return base_url


    def loginQQ(self,my_http_request,key,value,verifysession,code):
        # constant.PASSWORD = str(value)
        password = Tea.getTEAPass(int(key),str(value),code)
        base_url = constant.QQLOGINURL
        base_url = base_url.replace('USERNAME', str(key))
        base_url = base_url.replace('VERIFYSESSION', verifysession)
        base_url = base_url.replace('PASSWORD',password)
        base_url = base_url.replace('CODE',code)
        page_content = my_http_request.get_response(base_url).read().decode('utf-8')
        logging.info(page_content)
        print page_content
        if u'暂时' in page_content:
            return -2,page_content

        if u'登录成功' not in page_content:
            return True,page_content
        else:
            # print page_content
            sid  = re.findall('sid=(.*?)\'',page_content,re.S)
            print sid
            self.accout_sid_dic[key] = sid[0]
            return False,page_content

    def show_image_code(self,image):

         # dialog = MyDialog(image)
         # dialog.ShowModal()

        if image==0:
            self.codeImage.Show(False)
            self.codeLabel.Show(False)
            self.codeInput.Show(False)
            self.list_sizer.Layout()
        else:
            self.codeImage.Show(True)
            self.codeLabel.Show(True)
            self.codeInput.Show(True)
            self.list_sizer.Layout()
            Image = wx.ImageFromStream(StringIO.StringIO(image)).ConvertToBitmap()
            self.codeImage.SetBitmap(Image)


    def getCode(self,myHttpRequest,username):
        base_url = constant.ISNEEDCODEURL2
        randomNum = commons.getRandomNum(4)
        base_url = base_url.replace('UIN', username)
        base_url = base_url.replace('RANDOM','0.'+randomNum)
        response = myHttpRequest.get_response(base_url)
        page_content = response.read().decode('utf-8')
        print page_content
        isNeedCode = int(page_content[13:-2].split(',')[0][1:-1])
        self.code = ''
        if isNeedCode==0:
            constant.CODE = page_content[13:-2].split(',')[1][1:-1]
            constant.SESSION = str(page_content[13:-2].split(',')[3][1:-1])
        else:
            self.cap_cd = str(page_content[13:-2].split(',')[1][1:-1])
            self.loginCode = str(page_content[13:-2].split(',')[2][1:-1])
        return isNeedCode

    def OnOpen(self,e):
        """ Open a file"""
        self.dirname = ''
        dlg = wx.FileDialog(self, "Choose a file", self.dirname, "", "*.*", wx.OPEN)
        if dlg.ShowModal() == wx.ID_OK:
            self.filename = dlg.GetFilename()
            self.dirname = dlg.GetDirectory()
        dlg.Destroy()
        try:
            path = self.dirname+'\\\\'+self.filename
        except AttributeError:
            path = None
        self.account_list = []
        self.__class__.account_http_dic={}
        self.accout_sid_dic={}
        self.clientIdDict = {}
        self.codeImage.Show(False)
        self.codeLabel.Show(False)
        self.codeInput.Show(False)
        self.list_sizer.Layout()

        if path is not None:
            self.account_dic = {}
            self.sloveBoxList.DeleteAllItems()
            print path

            self.readAccountFile(path)
        e.Skip()

    def readAccountFile(self,path,is_import = True):
        '''
        读取账号信息的文本
        :param path:
        :return:
        '''
        account_file = open(path,'r')

        list_of_all_the_lines = account_file.readlines( )
        if is_import:
            account_file = open('account_info.txt','w')
        self.__class__.account_http_dic = {}
        for i,line in enumerate(list_of_all_the_lines):
            if line.strip()!='':
                try:
                    if is_import:
                        account_file.write(line)
                    account_info = line.split('----')
                    self.account_dic[account_info[0].strip()] = account_info[1].strip()
                    self.account_list.append(account_info[0].strip())
                    self.sloveBoxList.account_select.append(0)
                except:
                    self.operateLogUpdate(u'文本第'+str(i)+u'行读取失败')
        for i,account in enumerate(self.account_list):
            self.sloveBoxList.Append([str(i+1),account,u'',u'未登录'])
            self.clientIdDict[i+1] = account