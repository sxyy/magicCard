# -*- coding: utf-8 -*-
import wx,time,thread
import commonlib.Tea as Tea
import wx.lib.mixins.listctrl as listmix
from bs4 import  BeautifulSoup
import mythread.getInfoThread as mythread
import setting
from commonlib import constant
from commonlib import myhttp,commons
import accountManage,accountsupport,searchcard,reward
import logging,StringIO,ConfigParser
import sys,os,random
import base64

class MyDialog(wx.Dialog):
    def __init__(self, image_code):
        wx.Dialog.__init__(self, None, -1, u'输入验证码,尽量使用大写字母', size=(250,170))
        self.code = ''
        sizer_1 = wx.BoxSizer(wx.VERTICAL)
        self.codeImage=wx.StaticBitmap(self, -1,  pos=(30,50), size=(150,80))
        self.codeInput = wx.TextCtrl(self,-1)
        # self.codeInput.Bind(wx.EVT_TEXT, self.OnChar)
        self.codeInput.SetMaxLength(4)
        self.commit = wx.Button(self,-1,u'确定', pos=(150,10))
        self.commit.Bind(wx.EVT_BUTTON,self.on_submit)
        Image = wx.ImageFromStream(StringIO.StringIO(image_code)).ConvertToBitmap()
        self.codeImage.SetBitmap(Image)
        sizer_1.Add(self.codeImage,0,wx.ALL,5)
        sizer_1.Add(self.codeInput,0,wx.ALL,5)
        # sizer_1.Add(self.commit,0,wx.ALL,5)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
    def on_submit(self,e):
        constant.NEWCODE = str(self.codeInput.GetValue())
        self.Destroy()
        e.Skip()
    def OnClose(self,e):
        constant.NEWCODE = 'CLOSE'
        self.Destroy()
        e.Skip()

class TaskBarIcon(wx.TaskBarIcon):
    ID_Hello = wx.NewId()
    def __init__(self, frame):
        wx.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(wx.Icon(name='magic.ico', type=wx.BITMAP_TYPE_ICO), u'魔卡')
        self.Bind(wx.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick)

    def OnTaskBarLeftDClick(self, event):
        if self.frame.IsIconized():
           self.frame.Iconize(False)
        if not self.frame.IsShown():
           self.frame.Show(True)
        self.frame.Raise()
        event.Skip()


class TestListCtrl(wx.ListCtrl, listmix.CheckListCtrlMixin, listmix.ListCtrlAutoWidthMixin):
    def __init__(self, *args, **kwargs):
        wx.ListCtrl.__init__(self, *args, **kwargs)
        listmix.CheckListCtrlMixin.__init__(self)
        listmix.ListCtrlAutoWidthMixin.__init__(self)
        self.setResizeColumn(5)
        self.selectItem = -1

    def OnCheckItem(self, index, flag):
        print(index, flag)
        if flag:
            self.selectItem = index
            self.selectCardName = self.GetItemText(index,1)
        
class TabPanel(wx.Panel):
    #----------------------------------------------------------------------
    def __init__(self, parent,headlist):
        """"""
        wx.Panel.__init__(self, parent=parent)
       
        self.sloveBoxList = TestListCtrl(self,style=wx.LC_REPORT)
        self.sloveBoxList.SetBackgroundColour((227,237,205))
        for col,text in enumerate (headlist):
            self.sloveBoxList.InsertColumn(col,text)
            self.sloveBoxList.SetColumnWidth(col,150)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.sloveBoxList, 1,wx.EXPAND)
        self.SetSizer(sizer)
    
    def updateSlove(self,msgList):
        self.sloveBoxList.DeleteAllItems()
        for msg in msgList:
            if len(msg)!=0:
                self.sloveBoxList.Append(["",msg[0],msg[3],msg[1]])
            else:
                self.sloveBoxList.Append(["","","",""])
                

class TabPanel2(wx.Panel):
    #----------------------------------------------------------------------
    def __init__(self, parent):
        """"""
        wx.Panel.__init__(self, parent=parent)
        self.opreateLog = wx.TextCtrl(self,-1,style=wx.TE_MULTILINE)
        self.opreateLog.SetBackgroundColour((227,237,205))
        #不可编辑
        self.opreateLog.SetEditable(False)
        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.opreateLog, 1,wx.EXPAND)
        self.SetSizer(sizer)




class RefinedCard(wx.Panel):


     main_http_request = myhttp.MyHttpRequest()

     def __init__(self, parent,myHttpRequest,steal_card_http,magicCardInfo,database):
         wx.Panel.__init__(self, parent=parent)
         self.myHttpRequest = myHttpRequest
         self.__class__.main_http_request = myHttpRequest
         self.steal_card_http = steal_card_http
         self.magicCardInfo = magicCardInfo
         self.database = database

         self.exchangeBox = []
         self.storeBox =[]
         self.stoveBox = []
         self.stealFriend = []
         self.friend_complete = {}
         self.friend_slove = {}
         #判断藏珍阁的卡片是否炼制完成了
         self.czgComplete = []
         #用来判断炼卡进度是否要更新
         self.count = 0
         #print self.magicCardInfo
         self.soup = BeautifulSoup(self.magicCardInfo)
         self.exchangeBoxlistHead = [u'换',u'卡片',u'卡片类型',u'价格']
         self.safeBoxlistHead = [u'保',u'卡片',u'卡片类型',u'价格']
         self.sloveListHead = [u'序号',u'卡片',u'卡片类型',u'炼卡结束时间']
         self.refindProcessHead = [u'序号',u'卡片',u'理',u'存',u'炼']
         self.zcgHead = [u'序号',u'炼卡结束时间',u'铺子到期时间']
         self.operateList = [u'刷新界面',u'一键收取好友分享',u'一键出售素材卡']
        #-------------换卡箱----------
         # self.exchangesb  = wx.StaticBox(self,label = u'换卡箱')
         # self.exchangeBoxSizer = wx.StaticBoxSizer(self.exchangesb,wx.VERTICAL)
         #添加一个列表控件 style使用报表的模式 并且插入头
         # self.exchangeBoxlist = TestListCtrl(self,style=wx.LC_REPORT)
         # self.exchangeBoxlist.SetBackgroundColour((227,237,205))
         # for col,text in enumerate (self.exchangeBoxlistHead):
         #     self.exchangeBoxlist.InsertColumn(col,text)
         # self.exchangeBoxlist.Arrange()

         #-------------炼卡进度----------
         self.refineCardsb  = wx.StaticBox(self,label = u'炼卡进度')
         self.refineCardSizer = wx.StaticBoxSizer(self.refineCardsb,wx.HORIZONTAL)
         self.refineCardlist = TestListCtrl(self,style=wx.LC_REPORT)
         self.refineCardlist.SetBackgroundColour((227,237,205))
         for col,text in enumerate (self.sloveListHead):
             self.refineCardlist.InsertColumn(col,text)
             self.refineCardlist.SetColumnWidth(col,170)
         self.refineCardlist.Arrange()
         self.refineCardSizer.Add(self.refineCardlist,1,wx.ALL,0)
        #-------------换卡箱按钮的集合----------
         # self.exchangeBoxButtonSize = wx.BoxSizer(wx.HORIZONTAL)
         # self.exchangeBoxLabel = wx.StaticText(self,-1,u'0/0')
         # self.inputSafeBox = wx.Button(self,-1,u'放入保险箱')
         # self.saleSelectCard = wx.Button(self,-1,u'出售勾选卡片')
         # self.randomDrawCard = wx.Button(self,-1,u'随机抽卡')
         # self.randomDrawCard.Bind(wx.EVT_BUTTON, self.randomDrawCardsEvent)
         # self.saleSelectCard.Bind(wx.EVT_BUTTON,self.saleCardEvent)
         # self.inputSafeBox.Bind(wx.EVT_BUTTON, self.inputCardToStore)
         # self.exchangeBoxButtonSize.Add(self.inputSafeBox,0,wx.ALL,5)
         # self.exchangeBoxButtonSize.Add(self.saleSelectCard,0,wx.ALL,5)
         # self.exchangeBoxButtonSize.Add(self.randomDrawCard,0,wx.ALL,5)
         # self.exchangeBoxSizer.Add(self.exchangeBoxLabel,0,wx.ALL,0)
         # self.exchangeBoxSizer.Add(self.exchangeBoxlist,0,wx.ALL,5)
         # self.exchangeBoxSizer.Add(self.exchangeBoxButtonSize,0,wx.ALL,5)


        #------------保险箱---------------------
         # self.safeSB  = wx.StaticBox(self,label = u'保险箱')
         # self.safeBoxSizer = wx.StaticBoxSizer(self.safeSB,wx.VERTICAL)
         # #添加一个列表控件 style使用报表的模式 并且插入头
         # # self.safeBoxLabel = wx.StaticText(self,-1,u'0/0')
         # self.safeBoxlist = TestListCtrl(self,style=wx.LC_REPORT)
         # self.safeBoxlist.SetBackgroundColour((227,237,205))
         # for col,text in enumerate (self.safeBoxlistHead):
         #     self.safeBoxlist.InsertColumn(col,text)
         # self.inputExchangeBox = wx.Button(self,-1,u'放入换卡箱')
         # self.inputExchangeBox.Bind(wx.EVT_BUTTON, self.inputCardToExchange)
         # # self.safeBoxSizer.Add(self.safeBoxLabel,0,wx.ALL,0)
         # self.safeBoxSizer.Add(self.safeBoxlist,0,wx.ALL,5)
         # self.safeBoxSizer.Add(self.inputExchangeBox,0,wx.ALL,5)

        #------------个人信息---------------------
         infoSB  = wx.StaticBox(self,label = u'我的信息')
         self.infoBoxSizer = wx.StaticBoxSizer(infoSB,wx.VERTICAL)
         # self.nickName = wx.StaticText(self,-1,u'昵称')
         self.user_infoSizer = wx.BoxSizer(wx.HORIZONTAL)
         self.level = wx.StaticText(self,-1,u'等级')
         self.magic = wx.StaticText(self,-1,u'魔力')
         self.user_infoSizer.Add(self.level,0,wx.ALL,5)
         self.user_infoSizer.Add(self.magic,0,wx.ALL,5)
         self.collectTheme = wx.StaticText(self, -1, u'炼制主题')
         self.runState = wx.StaticText(self, -1, u'状态   未运行')
         self.runState.SetForegroundColour((255, 0, 0))
         self.collectTheme.SetForegroundColour((255, 0, 0))
         self.infoBoxButtonSize = wx.BoxSizer(wx.HORIZONTAL)
         self.infoBoxButtonSize2 = wx.BoxSizer(wx.HORIZONTAL)
         self.operate_choice = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.operateList)
         self.operate_action = wx.Button(self,-1,u'执行')
         self.operate_action.Bind(wx.EVT_BUTTON,self.onAction)
         self.setConfig = wx.Button(self,-1,u'设置参数')
         self.start = wx.Button(self,-1,u'开始运行')
         self.infoBoxButtonSize2.Add(self.operate_choice,0,wx.ALL,5)
         self.infoBoxButtonSize2.Add(self.operate_action,0,wx.ALL,5)
         # self.refreshBt = wx.Button(self,-1,u'刷新界面')
         # self.refreshBt.Bind(wx.EVT_BUTTON,self.onRefresh)
         self.setConfig.Bind(wx.EVT_BUTTON, self.configSetting)
         self.start.Bind(wx.EVT_BUTTON,self.refresh)
         self.infoBoxButtonSize.Add(self.setConfig,0,wx.ALL,5)
         self.infoBoxButtonSize.Add(self.start,0,wx.ALL,5)
         # self.infoBoxButtonSize.Add(self.refreshBt,0,wx.ALL,5)
         # self.infoBoxSizer.Add(self.nickName,0,wx.ALL,5)
         # self.infoBoxSizer.Add(self.level,0,wx.ALL,5)
         # self.infoBoxSizer.Add(self.magic,0,wx.ALL,5)
         self.infoBoxSizer.Add(self.user_infoSizer,0,wx.ALL,5)
         self.infoBoxSizer.Add(self.collectTheme, 0, wx.ALL, 5)
         self.infoBoxSizer.Add(self.runState, 0, wx.ALL, 5)
         self.infoBoxSizer.Add(self.infoBoxButtonSize,0,wx.ALL,5)
         self.infoBoxSizer.Add(self.infoBoxButtonSize2,0,wx.ALL,5)
         self.operate_choice.SetSelection(0)
        #炼卡信息
         self.CardInfo = wx.BoxSizer(wx.HORIZONTAL)
         self.nb = wx.Notebook(self,-1,(20,40),(200,500))
         # self.tabOne = TabPanel(self.nb,self.sloveListHead)
         # self.tabOne.SetBackgroundColour((227,237,205))
         # self.nb.AddPage(self.tabOne, u"炼卡位")
         # self.tabTwo = TabPanel(self.nb,self.refindProcessHead)
         # self.tabTwo.SetBackgroundColour((227,237,205))
         # self.nb.AddPage(self.tabTwo, u"炼卡进度")
         self.tabFour = TabPanel(self.nb,self.zcgHead)
         self.tabFour.SetBackgroundColour((227,237,205))
         self.nb.AddPage(self.tabFour,u'珍藏阁')
         self.tabThree = TabPanel2(self.nb)
         self.tabThree.SetBackgroundColour((227,237,205))
         self.nb.AddPage(self.tabThree,u'操作记录')

         self.nb.SetSelection(1)
         self.CardInfo.Add(self.nb,1,wx.ALL,5)

        #---------------总的布局----------
         self.sizer = wx.BoxSizer(wx.VERTICAL)
         self.sizerHorizontal = wx.BoxSizer(wx.HORIZONTAL)
         self.sizerHorizontal.Add(self.refineCardSizer, 1, wx.EXPAND)
         # self.sizerHorizontal.Add(self.safeBoxSizer, 0, wx.EXPAND)
         self.sizerHorizontal.Add(self.infoBoxSizer, 0, wx.EXPAND)
         self.sizer.Add(self.sizerHorizontal, 0, wx.EXPAND)
         self.sizer.Add(self.CardInfo, 1, wx.EXPAND)
    #         #Layout sizers
         self.SetSizer(self.sizer)
         self.SetAutoLayout(1)
         self.Center()
         self.Show(True)
         self.operateLogUpdate(u'获取卡箱以及好友信息..')
         self.getBoxInfo()



         if constant.COLLECTTHEMEID != -1:
             self.updateUserinfo(4, self.database.getCardThemeName(constant.COLLECTTHEMEID))

         thread.start_new_thread(self.get_login_gift,())
         thread.start_new_thread(self.timeSys,())

     def onAction(self,e):
         if self.operate_choice.GetSelection()==0:
             thread.start_new_thread(self.freshRightNow,())
         elif self.operate_choice.GetSelection()==1:
             thread.start_new_thread(self.get_friend_share,())
         elif self.operate_choice.GetSelection()==2:
             thread.start_new_thread(self.card_sell,())

         e.Skip()

     def card_sell(self):
         base_url = constant.SELLCARD
         page_content = self.myHttpRequest.get_response(base_url).read().decode('utf-8')
         print page_content
         if u'成功出售' in page_content:
             wx.CallAfter(self.operateLogUpdate,u'一键出售卡片成功')
         else:
             wx.CallAfter(self.operateLogUpdate,u'一键出售卡片失败')


     def onRefresh(self,e):
         thread.start_new_thread(self.freshRightNow,())
         e.Skip()

     def get_login_gift(self):
         while True:
            a = (abs(int(time.time())/600*600-int(time.time()))%100)
            #print a
            if 95<a<99:
                print u'领魔力的时间'
                x = time.localtime(int(time.time()))
                print time.strftime('%Y-%m-%d %H:%M:%S',x)
                base_url = self.getUrl(constant.MONEYDRAW)
                postData = {
                       'uin':constant.USERNAME
                }
                page_content = self.myHttpRequest.get_response(base_url,postData).read()
                soup = BeautifulSoup(page_content)
                try:
                    money = soup.qqhome['money_plus']
                    if money!='':
                        money +=u'金币'
                    else:
                        money = soup.qqhome['mn5day']
                        if money=='100':
                            money+=u'魔力'
                        wx.CallAfter(self.operateLogUpdate,str(constant.USERNAME)+u'领取第'+soup.qqhome['days']+u'天登陆礼包'+money)
                    break
                except:
                    wx.CallAfter(self.operateLogUpdate,u'今天已领取过礼包')
                    break

            time.sleep(0.5)


     def get_friend_share(self):
         base_url = commons.getUrl(constant.USERSHARE,self.myHttpRequest)
         post_data = {
             'uin':constant.USERNAME,
             'type':0
         }
         page_content = self.myHttpRequest.get_response(base_url,post_data).read()
         print page_content
         child_list = BeautifulSoup(page_content).find_all('node')
         base_url = commons.getUrl(constant.USERSHAREGET,self.myHttpRequest)
         for item in child_list:
             node_item = BeautifulSoup(str(item)).node
             if node_item['gift']=="0":
                 post_data = {
                     'uin':constant.USERNAME,
                     'frienduin':int(node_item['frienduin']),
                     'timestamp':int(node_item['timestamp'])
                 }
                 page_content = self.myHttpRequest.get_response(base_url,post_data).read()
                 print page_content
                 wx.CallAfter(self.operateLogUpdate,u'领取好友'+node_item['frienduin']+u'分享50金币')
         wx.CallAfter(self.operateLogUpdate,u'领取好友分享完成')
         pass

     def timeSys(self):
         wx.CallAfter(self.operateLogUpdate,u'进行时间同步')
         commons.setSystemTime()
         wx.CallAfter(self.operateLogUpdate,u'时间完成')

     def show_image_code(self,image):
         '''

         :param image:
         :return:
         '''
         dialog = MyDialog(image)
         r = dialog.ShowModal()
         if r == wx.ID_OK:
            wx.MessageBox('You input:' + dialog.codeInput.GetValue(),'wxPython', wx.OK)
         dialog.Destroy()

     #获取交换箱的空位
     def exchangeBoxEmpty(self):
         #先获取交换箱是否有空位
         for i,cardId in enumerate(self.exchangeBox):
             if cardId == 0:
                 return  i
         return -1

     #随机抽卡
     def randomDrawCardsEvent(self,e):
         self.drawCard()


     def drawCard(self):
         inputPos = self.exchangeBoxEmpty()
         if inputPos==-1:
             dlg = wx.MessageDialog(self,u"交换箱已经满了。。",caption=u'提示',style=wx.OK,pos=wx.DefaultPosition)
             retCode = dlg.ShowModal()
             if retCode == wx.ID_OK:
                 dlg.Destroy()
         else:
             postData = {
                         'iSlotNo':inputPos,
                         'type':1,
             }
             base_url =  self.getUrl(constant.DRAWCARDURL)
             page_content = self.myHttpRequest.get_response(base_url,postData)
             result = page_content.read().decode('utf-8')
             print '抽取卡片',result
             logging.info(result)
             soup = BeautifulSoup(result)
             cardId = soup.card['id']
             self.exchangeBox[inputPos] = int(cardId)
             cardInfo = self.database.getCardInfo(cardId)
             self.operateLogUpdate(u'抽取卡片:'+cardInfo[0])
             # for i,item in enumerate(cardInfo):
             #     self.exchangeBoxlist.SetStringItem(inputPos,(i+1),item)

             constant.RANDCHANCE -=1
             # self.randomDrawCard.SetLabelText(u'随机抽卡'+str(constant.RANDCHANCE))


     #出售卡片事件
     # def saleCardEvent(self,e):
     #     cardId = self.exchangeBox[self.exchangeBoxlist.selectItem]
     #     self.saleCard(cardId,self.exchangeBoxlist.selectItem)
     #     self.exchangeBoxlist.CheckItem(self.exchangeBoxlist.selectItem, False)

     #出售卡片
     def saleCard(self,cardId,slotNo):

         postData = {
                         'slot_no':slotNo,
                         'uin':constant.USERNAME,
                         'type':0,
                         'cardid':cardId
         }

         base_url =  self.getUrl(constant.SALECARD)
         result = self.myHttpRequest.get_response(base_url,postData).read()
         soup = BeautifulSoup(result)
         self.updateUserinfo(2, soup.qqhome['money'])
         self.operateLogUpdate(u'出售卡片 :'+self.database.getCardInfo(cardId)[0])
         # for i in range(1,4):
         #     self.exchangeBoxlist.SetStringItem(slotNo,i,"")
         self.exchangeBox[slotNo] = 0

    #购买卡片
     def buyCard(self,cardId):

         themeId = self.database.getCardThemeid(cardId)
         postData = {
                        'card_id':cardId,
                        'theme_id':themeId,
         }
         base_url =  self.getUrl(constant.BUYCARDURL)
         page_content = self.myHttpRequest.get_response(base_url,postData)
         result = page_content.read().decode('utf-8')
         print u'买卡结果',result
         logging.info(result)
         soup = BeautifulSoup(result)
         soup2 = BeautifulSoup(str(soup.find_all('card')[0]))

         cardInfo = self.database.getCardInfo(cardId)
         self.operateLogUpdate(u'购买卡片: '+cardInfo[0])
         # for i,item in enumerate(cardInfo):
         #     self.exchangeBoxlist.SetStringItem(long(soup2.card['slot']),(i+1),item)
         self.exchangeBox[int(soup2.card['slot'])] = cardId
         #self.updateUserinfo(2, int(self.coin.GetLabelText())-20)

     #卡片放入储物箱
     # def inputCardToStore(self,e):
     #    #先获取保险箱是否有空位
     #     cardId = self.exchangeBox[self.exchangeBoxlist.selectItem]
     #     self.card_user_storage_exchange(0, self.exchangeBoxlist.selectItem,cardId)
     #     self.exchangeBoxlist.CheckItem(self.exchangeBoxlist.selectItem, False)

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
                         'uin':constant.USERNAME,
         }
         base_url =  self.getUrl(constant.CARDINPUTSTOREBOX)
         self.myHttpRequest.get_response(base_url,postData)
         cardName = self.database.getCardInfo(cardId)[0]
         if type==0:
             self.operateLogUpdate(u'卡片 :'+cardName+u'放入保险箱')
             self.storeBox[des] = cardId
             self.exchangeBox[src]=0

         else:
             self.operateLogUpdate(u'卡片 :'+cardName+u'放入换卡箱')
             self.exchangeBox[des] = cardId
             self.storeBox[src]=0

         # for i in range(1,4):
         #     if type==0:
         #         #print 'src',str(src),'des',str(des),'col',str(i),self.exchangeBoxlist.GetItemText(src,i)
         #         self.safeBoxlist.SetStringItem(des,i,self.exchangeBoxlist.GetItemText(src,i))
         #         self.exchangeBoxlist.SetStringItem(src,i,"")
         #     else:
         #        #print 'src',str(src),'des',str(des),'col',str(i),self.safeBoxlist.GetItemText(src,i)
         #         self.exchangeBoxlist.SetStringItem(des,i,self.safeBoxlist.GetItemText(src,i))
         #         self.safeBoxlist.SetStringItem(src,i,"")


     # def inputCardToExchange(self,e):
     #     #先获取交换箱是否有空位
     #     cardId =  self.storeBox[self.safeBoxlist.selectItem]
     #     self.card_user_storage_exchange(1, self.safeBoxlist.selectItem, cardId)
     #     self.safeBoxlist.CheckItem(self.safeBoxlist.selectItem, False)
     '''
           获取卡箱的内容
     '''
     def getBoxInfo(self):
         infoThread4 = mythread.GetInfoThread(self.magicCardInfo,constant.ZCG,self,self.myHttpRequest)
         infoThread4.start()
         infoThread1 = mythread.GetInfoThread(self.magicCardInfo,constant.EXCHANGEBOX,self,self.myHttpRequest)
         infoThread1.start()
         infoThread2 = mythread.GetInfoThread(self.magicCardInfo,constant.STOREBOX,self,self.myHttpRequest)
         infoThread2.start()
         time.sleep(1)
         infoThread3 = mythread.GetInfoThread(self.magicCardInfo,constant.STOVEBOX,self,self.myHttpRequest)
         infoThread3.start()

        #

    #界面更新
     def updateInfo(self,flag,timelist=None,userInfo=None,end_time_list=None):

         if flag==constant.EXCHANGEBOX:
             print u'交换箱id信息',self.exchangeBox

             self.refineCardsb.SetLabel(u'交换箱 ('+str(len(self.exchangeBox)-self.exchangeBox.count(0))+'/'+str(len(self.exchangeBox))+')'+u'保险箱 ('+str(len(self.storeBox)-self.storeBox.count(0))+'/'+str(len(self.storeBox))+')')
             # self.exchangeBoxlist.DeleteAllItems()
             # for cardId in self.exchangeBox:
             #     if cardId!=0:
             #         self.database.cu.execute("select name,price,themeid from cardinfo where pid=?",(cardId,))
             #         result = self.database.cu.fetchone()
             #         self.database.cu.execute("select name from cardtheme where pid=?",(result[2],))
             #         self.exchangeBoxlist.Append(["",result[0],self.database.cu.fetchone()[0],result[1]])
             #     else:
             #         self.exchangeBoxlist.Append(["","","",""])
             # self.randomDrawCard.SetLabelText(u'随机抽卡'+str(constant.RANDCHANCE))
             if len(userInfo) !=0:
                 for i,info in enumerate(userInfo):
                     self.updateUserinfo(i, info)
    #

         elif flag==constant.STOREBOX:
             print u'保险箱id信息',self.storeBox
             self.refineCardsb.SetLabel(u'交换箱 ('+str(len(self.exchangeBox)-self.exchangeBox.count(0))+'/'+str(len(self.exchangeBox))+')'+u'保险箱 ('+str(len(self.storeBox)-self.storeBox.count(0))+'/'+str(len(self.storeBox))+')')
             # self.safeBoxlist.DeleteAllItems()
             # for cardId in self.storeBox:
             #     if cardId!=0:
             #         self.database.cu.execute("select name,price,themeid from cardinfo where pid=?",(cardId,))
             #         result = self.database.cu.fetchone()
             #
             #         self.database.cu.execute("select name from cardtheme where pid=?",(result[2],))
             #         self.safeBoxlist.Append(["",result[0],self.database.cu.fetchone()[0],result[1]])
             #     else:
             #         self.safeBoxlist.Append(["","","",""])
         elif flag==constant.STOVEBOX:
             print u'卡炉信息',self.stoveBox
             self.refineCardlist.DeleteAllItems()
             for i,cardId in enumerate(self.stoveBox):
                 if cardId!=0:
                     self.database.cu.execute("select name,themeid from cardinfo where pid=?",(cardId,))
                     result = self.database.cu.fetchone()
                     self.database.cu.execute("select name from cardtheme where pid=?",(result[1],))
                     self.refineCardlist.Append(["",result[0],self.database.cu.fetchone()[0],timelist[i]])
                 else:
                     self.refineCardlist.Append(["","","",""])
         elif flag==constant.ZCG:
             self.tabFour.sloveBoxList.DeleteAllItems()
             for i,endTime in enumerate(timelist):
                 self.tabFour.sloveBoxList.Append(["",timelist[i],end_time_list[i]])

         self.count +=1
         # if self.count==4:
         #     self.count=0
         #    #这里是更新炼卡进度 每5分钟进行刷新一次
         #     self.tabTwo.sloveBoxList.DeleteAllItems()
         #     if constant.COLLECTTHEMEID!=-1:
         #         self.database.cu.execute("select pid,name from cardinfo where themeid=? order by price DESC",(constant.COLLECTTHEMEID,))
         #         collectCardList =  self.database.cu.fetchall()
         #         for cardInfo in collectCardList:
         #             #print cardInfo[0],u'交换箱',self.exchangeBox.count(cardInfo[0]),u'保险箱',self.storeBox.count(cardInfo[0])
         #             cardNum = self.exchangeBox.count(cardInfo[0])+self.storeBox.count(cardInfo[0])
         #             refinedCardNum = self.stoveBox.count(cardInfo[0])
         #             self.tabTwo.sloveBoxList.Append(["",cardInfo[1],'1',str(cardNum),str(refinedCardNum)])



     def updateUserinfo(self,flag,info):
         '''
         更新个人信息
         :param flag:
         :param info:
         :return:
         '''
         if flag ==0:
             pass
             # self.nickName.SetLabelText(u'昵称   '+info)
         elif flag ==1:
             self.level.SetLabelText(u'等级   '+info)
         elif flag==2:
             # self.coin.SetLabelText(u'金币   '+info)
             pass
         elif flag == 3:
             self.magic.SetLabelText(u'魔力   '+info)
         elif flag == 4:
             self.collectTheme.SetLabelText(u'主题   ' + info)
         elif flag == 5:
             self.runState.SetLabelText(u'状态   ' + info)


    #更新保险箱
     def updateStoreBox(self,cardId,pos,sloveId):
         # cardInfo = self.database.getCardInfo(cardId)
         # for i,item in enumerate(cardInfo):
         #     self.safeBoxlist.SetStringItem(long(pos),(i+1),item)

         for i in range(1,4):
             self.refineCardlist.SetStringItem(sloveId,i,"")



    #list 卡位以及交换箱还是保险箱   sloveId 炉子ID,   sloveId 对应炉子的卡片的信息
     def updateSlove(self,list,sloveId,sloveMsg):
         # for i in range(len(list)/2):
         #     if list[(i*2+1)]==0:
         #         for j in range(1,4):
         #             self.exchangeBoxlist.SetStringItem(list[i*2],j,"")
         #     else:
         #         for j in range(1,4):
         #             self.safeBoxlist.SetStringItem(list[i*2],j,"")

         for i,item in enumerate(sloveMsg):
             #检查账号不同是否sloveid会有所区别
             print sloveId,item
             if not int(sloveId)>=len(self.stoveBox):
                 self.refineCardlist.SetStringItem(long(sloveId),(i+1),item)
             else:
                 self.refineCardlist.SetStringItem(long(len(self.stoveBox)-1),(i+1),item)

    #参数设置
     def configSetting(self,e):
         setting.Setting(None,u'参数设置',self.database,self.myHttpRequest)
         e.Skip()
     #开始运行
     def refresh(self,e):

         '''这里新建一个死循环的线程 每隔多久检查是否卡片炼制完成，同时也更新界面
         '''
         if constant.COLLECTTHEMEID==-1:
             dlg = wx.MessageDialog(self,u"请先设置要炼的套卡",caption=u'提示',style=wx.OK,pos=wx.DefaultPosition)
             retCode = dlg.ShowModal()
             if retCode == wx.ID_OK:
                 dlg.Destroy()
         else:
             constant.RUNSTATE = not constant.RUNSTATE
             if constant.RUNSTATE:
                 self.updateUserinfo(5, u'已运行')
                 self.start.SetLabel(u'停止运行')
             else:
                 self.updateUserinfo(5,u'已停止')
                 self.start.SetLabel(u'开始运行')
             thread.start_new_thread(self.timerThread,(2,))

     #Log记录更新
     def operateLogUpdate(self,msg):
         nowtime = time.localtime(time.time())
         self.tabThree.opreateLog.AppendText('['+str(time.strftime('%H:%M:%S',nowtime))+']'+msg+'\n')

     #开始运行线程
     def timerThread(self,num):
        #登陆魔卡
         while constant.RUNSTATE:

             self.freshRightNow()
             time.sleep(random.randint(180,300))

     def freshRightNow(self):
         self.exchangeBox = []
         self.storeBox =[]
         self.stoveBox = []
         postData = {
                            'code':'',
                            'uin':constant.USERNAME

         }
         base_url =  self.getUrl(constant.CARDLOGINURL)
         page_content = self.myHttpRequest.get_response(base_url,postData)
         self.magicCardInfo= page_content.read()
         soup = BeautifulSoup(self.magicCardInfo)
         try:
            childlist = soup.changebox.children
            self.getBoxInfo()
         except Exception,e:
            wx.CallAfter(self.operateLogUpdate,u'账号异常尝试重新登陆')
            print e
            self.reLogin()




     def reLogin(self):
         self.myHttpRequest = myhttp.MyHttpRequest()
         if commons.getCode(self.myHttpRequest,constant.USERNAME)==0:
             password = Tea.getTEAPass(constant.USERNAME,constant.PASSWORD,str(constant.CODE))
             base_url = constant.QQLOGINURL
             base_url = base_url.replace('USERNAME', str(constant.USERNAME))
             base_url = base_url.replace('VERIFYSESSION', str(constant.SESSION))
             base_url = base_url.replace('PASSWORD',password)
             base_url = base_url.replace('CODE',str(constant.CODE).encode('utf-8'))
             page_content = self.myHttpRequest.get_response(base_url).read().decode('utf-8')
             if u'登录成功' in page_content:
                 wx.CallAfter(self.operateLogUpdate,u'账号重新登陆成功')
                 self.__class__.main_http_request = self.myHttpRequest
             else:
                 logging.info(page_content)
         else:
             wx.CallAfter(self.operateLogUpdate,u'账号重新登陆失败,停止挂机')
             constant.RUNSTATE = False
         pass

    #获取对应的url
     def getUrl(self,url):
         skey = ''
         for ck in self.myHttpRequest.cj:
                 if ck.name=='skey':
                     skey = ck.value
         base_url = url
         base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
         return base_url

class Main(wx.Frame):
    
    def __init__(self, parent, title,myHttpRequest,magicCardInfo,database):




        wx.Frame.__init__(self, parent, title=title, size=(1050,700))
        self.myHttpRequest = myHttpRequest
        self.steal_card_http = myhttp.MyHttpRequest()
        self.magicCardInfo = magicCardInfo
        self.database = database



        #-----------------------总体----------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.nb = wx.Notebook(self,-1,(20,40),(1200,800))
        self.tabOne = RefinedCard(self.nb,self.myHttpRequest,self.steal_card_http, self.magicCardInfo,self.database)
        self.tabOne.SetBackgroundColour((227,237,205))
        self.nb.AddPage(self.tabOne, u"炼卡")
        self.tabTwo = searchcard.SearchCard(self.nb,self.myHttpRequest,self.database,self.cur_file_dir())
        self.tabTwo.SetBackgroundColour((227,237,205))
        self.nb.AddPage(self.tabTwo, u"搜卡")
        self.sizer.Add(self.nb,1,wx.EXPAND)
        self.tabThree = accountManage.AccountManage(self.nb,database, self.myHttpRequest)
        self.nb.AddPage(self.tabThree, u"账号管理")
        self.tabThird = accountsupport.AccountSupport(self.nb,self.myHttpRequest,database)
        self.nb.AddPage(self.tabThird, u"小号支援")
        self.tabFour = reward.Reward(self.nb)
        self.nb.AddPage(self.tabFour, u"打赏")
        self.Bind(wx.EVT_ICONIZE, self.OnIconfiy)
        self.Bind(wx.EVT_CLOSE, self.OnClose)
        self.taskBarIcon = TaskBarIcon(self)
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.Center()
        self.Show(True)

        #----------------log
        self.logger = logging.getLogger()
        #set loghandler
        files = logging.FileHandler("qqxml.log")
        self.logger.addHandler(files)
        #set formater
        formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        files.setFormatter(formatter)
        #set log level
        self.logger.setLevel(logging.NOTSET)


    def OnIconfiy(self, event):
        self.Hide()
        event.Skip()




    def OnClose(self, event):
        '''
        窗口关闭事件
        :param e:
        :return:
        '''


        config = ConfigParser.ConfigParser()
        config.add_section("userinfo")
        config.set("userinfo","username",base64.encodestring(str(constant.USERNAME)))
        config.set("userinfo","password",base64.encodestring(constant.PASSWORD))
        config.write(open('user_info.ini','w'))

        self.taskBarIcon.Destroy()
        self.Destroy()
        event.Skip()
    #获取脚本文件的当前路径
    def cur_file_dir(self):
        path = sys.path[0]
        #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path+"\\"
        elif os.path.isfile(path):
            return os.path.dirname(path)+"\\"


