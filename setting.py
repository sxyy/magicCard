# -*- coding: utf-8 -*-
'''
@author: cvtpc
'''
import wx,StringIO
import commonlib.constant as constant

class Setting(wx.Frame):

    def __init__(self, parent, title,database,myHttpRequest):
        wx.Frame.__init__(self, parent, title=title, size=(730,500))
        self.database = database
        
        self.myHttpRequest = myHttpRequest
        
    
        #-------------炉子操作----------
        sb  = wx.StaticBox(self,label = u'需要操作的套卡')
        self.sloveOperateSizer = wx.StaticBoxSizer(sb, wx.VERTICAL)

        # 第一套卡片
        self.cardOneSizer = wx.BoxSizer(wx.HORIZONTAL);
        self.cardLabel = wx.StaticText(self, -1, u'卡片1')
        self.collectThemeChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.getCollectTheme())
        self.collectThemeChoice.Bind(wx.EVT_CHOICE,self.setThemeSelect)
        self.qqShowChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,[])
        self.qqShowChoice.Bind(wx.EVT_CHOICE,self.setQQShowSelect)
        self.qqShowImage=wx.StaticBitmap(self, -1,  pos=(30,50), size=(300,300))
        self.qqShowLabel = wx.StaticText(self,-1,u'Q秀')
        self.cardOneSizer.Add(self.cardLabel, 0, wx.ALL, 5)
        self.cardOneSizer.Add(self.collectThemeChoice, 0, wx.ALL, 5)
        self.cardOneSizer.Add(self.qqShowLabel, 0, wx.ALL, 5)
        self.cardOneSizer.Add(self.qqShowChoice, 0, wx.ALL, 5)

        # 第二套卡片
        self.cardOneSizer2 = wx.BoxSizer(wx.HORIZONTAL);
        self.cardLabel2 = wx.StaticText(self, -1, u'卡片2')
        self.collectThemeChoice2 = wx.Choice(self, -1, (50, 400), wx.DefaultSize, self.getCollectTheme())
        self.collectThemeChoice2.Bind(wx.EVT_CHOICE, self.setThemeSelect2)
        self.qqShowChoice2 = wx.Choice(self, -1, (50, 400), wx.DefaultSize, [])
        self.qqShowLabel2 = wx.StaticText(self, -1, u'Q秀')
        self.cardOneSizer2.Add(self.cardLabel2, 0, wx.ALL, 5)
        self.cardOneSizer2.Add(self.collectThemeChoice2, 0, wx.ALL, 5)
        self.cardOneSizer2.Add(self.qqShowLabel2, 0, wx.ALL, 5)
        self.cardOneSizer2.Add(self.qqShowChoice2, 0, wx.ALL, 5)

        self.sloveOperateSizer.Add(self.cardOneSizer, 0, wx.ALL, 5)
        self.sloveOperateSizer.Add(self.cardOneSizer2, 0, wx.ALL, 5)




        
        
        #-------------炉子操作----------
        sb  = wx.StaticBox(self,label = u'偷炉')
        self.stealSizer = wx.StaticBoxSizer(sb,wx.VERTICAL)
        
        self.friendSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.friendLabel = wx.StaticText(self,-1,u'好友')
        self.friendChoice = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.getFriendList())
        self.friendSizer.Add(self.friendLabel,0,wx.ALL,5)
        self.friendSizer.Add(self.friendChoice,0,wx.ALL,5)
        self.friendLabel2 = wx.StaticText(self,-1,u'好友2')
        self.friendChoice2 = wx.Choice(self,-1,(50,400),wx.DefaultSize,self.getFriendList())
        if constant.ISRED==0:
            self.friendLabel2.Enable(False)
            self.friendChoice2.Enable(False)
        self.friendSizer.Add(self.friendLabel2,0,wx.ALL,5)
        self.friendSizer.Add(self.friendChoice2,0,wx.ALL,5)
        self.stealSizer.Add(self.friendSizer, 0,wx.ALL,5)

        #-------------炼卡模式----------
        # sb = wx.StaticBox(self,label = u'炼卡模式')
        # self.refinedCardModeSizer = wx.StaticBoxSizer(sb,wx.HORIZONTAL)
        # self.radio1 = wx.RadioButton(self, -1, u"普通炼卡", wx.DefaultPosition, style=wx.RB_GROUP)
        # self.radio2 = wx.RadioButton(self, -1, "Ernie", wx.DefaultPosition)
        # self.radio3 = wx.RadioButton(self, -1, "Bert", wx.DefaultPosition)
        # self.refinedCardModeSizer.Add(self.radio1,0,wx.ALL,5)
        # self.refinedCardModeSizer.Add(self.radio2,0,wx.ALL,5)
        # self.refinedCardModeSizer.Add(self.radio3,0,wx.ALL,5)
        
        #-------横向-----------------
        self.msgSizer = wx.BoxSizer(wx.VERTICAL)
        self.msgSizer.Add(self.sloveOperateSizer,0,wx.ALL,5)
        self.msgSizer.Add(self.stealSizer,0,wx.ALL,5)
        #self.msgSizer.Add(self.refinedCardModeSizer,0,wx.ALL,5)
        #------
        self.qqShowSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.qqShowSizer.Add(self.msgSizer,0,wx.ALL,5)
        self.qqShowSizer.Add(self.qqShowImage,0,wx.ALL,5)



        
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.qqShowSizer,0,wx.ALL,5)
        self.saveButton = wx.Button(self,-1,u'保存')
        self.saveButton.Bind(wx.EVT_BUTTON, self.save)
        self.sizer.Add(self.saveButton,0,wx.ALL,5)

        '''设置炼制卡片的主题
        '''
        if constant.COLLECTTHEMEID!=-1:
            self.collectThemeChoice.SetSelection(self.themeIdList.index(constant.COLLECTTHEMEID))
            if constant.QQSHOWSELECT!=-1:
                self.setQQShowChoice(1, constant.QQSHOWSELECT)
            else:
                self.setQQShowChoice(1)
            self.displayQQShow()

        if constant.COLLECTTHEMEID2 != -1:
            self.collectThemeChoice2.SetSelection(self.themeIdList.index(constant.COLLECTTHEMEID2))
            if constant.QQSHOWSELECT2 != -1:
                self.setQQShowChoice(2, constant.QQSHOWSELECT2)
            else:
                self.setQQShowChoice(2)
        
        '''设置偷炉好友的信息
        '''
        if constant.STEALFRIEND!=-1:
            try:
                self.friendChoice.SetSelection(self.friendNameList.index(constant.STEALFRIEND))
            except Exception:
                pass
        if constant.STEALFRIEND2!=-1:
            try:
                self.friendChoice2.SetSelection(self.friendNameList.index(constant.STEALFRIEND2))
            except Exception:
                pass
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        self.Center()
        self.Show(True)
        
    '''保存配置
    '''    
    def save(self,e):
        configFile = open('Mfkp_config.ini','w')
        constant.COLLECTTHEMEID = int(self.themeIdList[self.collectThemeChoice.GetSelection()])
        constant.COLLECTTHEMEID2 = int(self.themeIdList[self.collectThemeChoice2.GetSelection()])
        constant.STEALFRIEND = int(self.friendNameList[self.friendChoice.GetSelection()])
        constant.STEALFRIEND2 = int(self.friendNameList[self.friendChoice2.GetSelection()])
        configFile.write('['+str(constant.USERNAME)+']'+'\n')
        configFile.write('themeid='+str(constant.COLLECTTHEMEID)+'\n')
        configFile.write('themeid2=' + str(constant.COLLECTTHEMEID2) + '\n')
        configFile.write('friendid='+str(constant.STEALFRIEND)+'\n')
        configFile.write('qqshow='+str(self.qqShowChoice.GetSelection())+'\n')
        configFile.write('qqshowid='+str(self.qqShowChoice.GetStringSelection())+'\n')
        configFile.write('qqshow=' + str(self.qqShowChoice2.GetSelection()) + '\n')
        configFile.write('qqshowid=' + str(self.qqShowChoice2.GetStringSelection()) + '\n')
        configFile.write('friendid2='+str(constant.STEALFRIEND2)+'\n')
        configFile.close()
        self.Destroy()
        

    '''获取好友列表·
    '''
    def getFriendList(self):
        friendName = []
        self.friendNameList = []
        self.database.cu.execute("select * from userlist")
        result = self.database.cu.fetchall()
        for friend in result:
            friendName.append(friend[2])
            self.friendNameList.append(friend[1])
        return friendName
        
        
    '''
    获取要收集的主题
    '''    
    def getCollectTheme(self):
        self.themeIdList = []
        themeName = []# where type=?",(0,)
        self.database.cu.execute("select * from cardtheme")
        result = self.database.cu.fetchall()
        for themeItem in result:
            themeName.append('['+str(themeItem[3])+u"星]"+themeItem[2])
            self.themeIdList.append(themeItem[1])
        return themeName
    
    
    '''设置qq秀的选择项
    '''
    def setThemeSelect(self,e):

        self.setQQShowChoice(1)
        self.displayQQShow()

    def setThemeSelect2(self, e):
        self.setQQShowChoice(2)

    def setQQShowChoice(self, refinedCardId, pos=0):
        if refinedCardId == 1:
            self.database.cu.execute("select gift from cardtheme where pid=?",
                                     (self.themeIdList[self.collectThemeChoice.GetSelection()],))
        else:
            self.database.cu.execute("select gift from cardtheme where pid=?",
                                     (self.themeIdList[self.collectThemeChoice2.GetSelection()],))
        result = self.database.cu.fetchone()
        qqShowId = []
        for item in result[0].split('|'):
            self.database.cu.execute("select showId from gift where pid=?",(int(item),))
            showid = self.database.cu.fetchone()
            qqShowId.append(str(showid[0]))
        if refinedCardId == 1:
            self.qqShowChoice.SetItems(qqShowId)
            self.qqShowChoice.SetSelection(pos)
        else:
            self.qqShowChoice2.SetItems(qqShowId)
            self.qqShowChoice2.SetSelection(pos)
    
    
    def setQQShowSelect(self,e):
        self.displayQQShow()
        
    def displayQQShow(self):
        showId =  self.qqShowChoice.GetStringSelection()[-3:]
        print showId
        base_url = constant.QQSHOWURL
        base_url = base_url.replace('PAGENUM', str(int(showId[0])))
        base_url = base_url.replace('ITEMNUM', str(int(showId[1:])))
        base_url = base_url.replace('IMAGENUM',self.qqShowChoice.GetStringSelection())
        print base_url
        page_content = self.myHttpRequest.get_response(base_url)
        Image = wx.ImageFromStream(StringIO.StringIO(page_content.read())).ConvertToBitmap()   
        self.qqShowImage.SetBitmap(Image)
        self.sizer.Layout()
        #pass
    
    def getQQShow(self):
        pass