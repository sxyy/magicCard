# -*- coding: utf-8 -*-
from commonlib import myhttp
from commonlib import constant
from commonlib import Tea
import  re,wx
import mythread.myThread as myThread
import thread
import main
import commonlib.carddatabase as carddatabase
import os,sys,ConfigParser
import StringIO




class MyLogin(wx.Frame):





    def __init__(self, parent, title):
        wx.Frame.__init__(self, parent, title=title, size=(750,150))
        self.cap_cd = ''
        self.isNeedCodePattern = re.compile(ur"\((.*?)\)")
        self.isNeedCode =0
        self.loginCode = ''
        self.myHttpRequest = myhttp.MyHttpRequest()
        
        #if not  os.path.exists(constant.DATABASE):

         #-------------用户信息----------
        self.userInfoSizer = wx.BoxSizer(wx.HORIZONTAL)
        self.tidLabel = wx.StaticText(self,-1,u'QQ')#-1的意义为id由系统分配
        self.tidInput = wx.TextCtrl(self,-1)
        self.tidInput.Bind(wx.EVT_KILL_FOCUS, self.OnKillFocus)
        self.tidInput.Bind(wx.EVT_KEY_DOWN, self.OnChar)
        self.aidLabel = wx.StaticText(self,-1,u'密码')
        self.aidInput = wx.TextCtrl(self,-1,style=wx.TE_PASSWORD)
        self.codeImage=wx.StaticBitmap(self, -1,  pos=(30,50), size=(150,80))
        self.codeLabel = wx.StaticText(self,-1,u'验证码')#-1的意义为id由系统分配
        self.codeInput = wx.TextCtrl(self,-1)
        self.codeLabel.Show(False)
        self.codeInput.Show(False)
        self.codeImage.Show(False)
        self.loginButton = wx.Button(self,-1,u'登陆')
        self.Bind(wx.EVT_BUTTON, self.loginQQ, self.loginButton)
        self.tipLabel = wx.StaticText(self,-1,u'正在更新数据库，请稍后点击登陆')
        self.tipLabel.SetForegroundColour((255,0,0))
        self.userInfoSizer.Add(self.tidLabel,0,wx.ALL,10)
        self.userInfoSizer.Add(self.tidInput,0,wx.ALL,10)
        self.userInfoSizer.Add(self.aidLabel,0,wx.ALL,10)
        self.userInfoSizer.Add(self.aidInput,0,wx.ALL,10)
        self.userInfoSizer.Add(self.codeImage,0,wx.TOP,10)
        self.userInfoSizer.Add(self.codeLabel,0,wx.TOP,10)
        self.userInfoSizer.Add(self.codeInput,0,wx.ALL,10)
        self.userInfoSizer.Add(self.loginButton,0,wx.ALL,10)
        self.userInfoSizer.Add(self.tipLabel,0,wx.ALL,10)
        
        #---------------总体布局----------
        self.sizer = wx.BoxSizer(wx.VERTICAL)
        self.sizer.Add(self.userInfoSizer, 0, wx.EXPAND)
        #Layout sizers
        self.SetSizer(self.sizer)
        self.SetAutoLayout(1)
        '''显示在屏幕中间
        '''
        self.Center()
        self.Show(True)

        config = ConfigParser.ConfigParser()
        try:
            config.read('user_info.ini')
            constant.USERNAME = config.get('userinfo','username')
            constant.PASSWORD = config.get('userinfo','password')
            self.tidInput.SetValue(constant.USERNAME)
            self.aidInput.SetValue(constant.PASSWORD)
            self.get_code()
        except Exception:
            print 'user_info.ini not exist'
        try:
            configFile = ConfigParser.ConfigParser()
            configFile.read("config.ini")
            constant.CARDUSERNUM = configFile.get("MagicCardConfig","searchCardNum")
            constant.ISUPDATEDB  = int(configFile.get("MagicCardConfig","isUpdateDB"))
            constant.ISSALEOFFCARD = int(configFile.get("MagicCardConfig","isSaleOffCard"))
            constant.ISCOMMITBYWEB = int(configFile.get("MagicCardConfig","isCommitByWeb"))
            constant.ISCOMPLETECOMMIT = int(configFile.get("MagicCardConfig","isCompleteCommit"))
            constant.ISSEARCHSTEALFRIEND = int(configFile.get("MagicCardConfig","isSearchStealFriend"))
        except :
            configFile = ConfigParser.ConfigParser()
            configFile.add_section("MagicCardConfig")
            configFile.set("MagicCardConfig","searchCardNum",constant.CARDUSERNUM)
            configFile.set("MagicCardConfig","isUpdateDB",1)
            configFile.set("MagicCardConfig","isSaleOffCard",0)
            configFile.set("MagicCardConfig","isCommitByWeb",1)
            configFile.set("MagicCardConfig","isCompleteCommit",0)
            configFile.set("MagicCardConfig","isSearchStealFriend",0)
            configFile.write(open('config.ini','w'))
        if constant.ISUPDATEDB ==1 :
            thread.start_new_thread(self.readFile,(1,))
        else:
            self.database = carddatabase.CardDataBase(self.cur_file_dir())
            self.tipLabel.SetLabel(u'更新完成，请登陆')



    def OnKillFocus(self,e):
        try:
            constant.USERNAME = int(self.tidInput.GetValue())
        except ValueError:
            pass;
        getCodethread = myThread.GetCodePicThread(self,self.myHttpRequest,constant.USERNAME)
        getCodethread.start()
        e.Skip()

    def OnSetFocus(self,e):
        e.Skip()
        pass

    
    '''键盘按下时
    '''
    def OnChar(self,e):
        if e.GetKeyCode()==9:
            self.aidInput.SetFocus()
        e.Skip()
    
    #显示验证码 图片
    def showTheCodePic(self,msg):
        if msg==0:
            self.codeImage.Show(False)
            self.codeLabel.Show(False)
            self.codeInput.Show(False)
            self.sizer.Layout()
        else:
            self.codeImage.Show(True)
            self.codeLabel.Show(True)
            self.codeInput.Show(True)
            self.sizer.Layout()
            Image = wx.ImageFromStream(StringIO.StringIO(msg)).ConvertToBitmap()   
            self.codeImage.SetBitmap(Image)

    def loginQQ(self,e):

        config = ConfigParser.ConfigParser()
        try:
            config.read('Mfkp_config.ini')
            constant.REFINEDTYPE = int(config.get('userconfig','refinedtype'))
            constant.COLLECTTHEMEID = int(config.get('userconfig','themeid'))
            constant.COLLECTTHEMEID2 = int(config.get('userconfig','themeid2'))
            constant.STEALFRIEND = int(config.get('userconfig','friendid'))
            constant.QQSHOWSELECT = int(config.get('userconfig','qqshow'))
            constant.QQSHOWID = int(config.get('userconfig','qqshowid'))
            constant.QQSHOWSELECT2 = int(config.get('userconfig','qqshow2'))
            constant.QQSHOWID2 = int(config.get('userconfig','qqshowid2'))
            try:
                constant.STEALFRIEND2 = int(config.get('userconfig','friendid2'))
            except :
                pass
        except Exception:
            print 'file can not find'



        verifysession = ''
        if self.codeInput.IsShown():
            code = str(self.codeInput.GetValue())
            
            for ck in self.myHttpRequest.cj:
                if ck.name=='verifysession':
                    verifysession = ck.value
        else:
            code = str(constant.CODE)
            verifysession = str(constant.SESSION)
        constant.PASSWORD = str(self.aidInput.GetValue())
        password = Tea.getTEAPass(constant.USERNAME,constant.PASSWORD,code)
        base_url = constant.QQLOGINURL
        base_url = base_url.replace('USERNAME', str(constant.USERNAME))
        base_url = base_url.replace('VERIFYSESSION', verifysession)
        base_url = base_url.replace('PASSWORD',password)
        base_url = base_url.replace('CODE',code.encode('utf-8'))
        page_content = self.myHttpRequest.get_response(base_url).read().decode('utf-8')
        try:
            print page_content
        except:
            pass
        if u'登录成功' not in page_content:
            dlg = wx.MessageDialog(self,u"密码或验证码不正确",caption=u'提示',style=wx.OK,pos=wx.DefaultPosition)
            retCode = dlg.ShowModal()
            if retCode == wx.ID_OK:
                dlg.Destroy()
            getCodethread = myThread.GetCodePicThread(self,self.myHttpRequest,constant.USERNAME)
            getCodethread.start()
        else:

            isFriend = self.getUserList()
            if isFriend:
                sid  = re.findall('sid=(.*?)\'',page_content,re.S)
                print sid
                constant.SID = sid[0]
                '''下来是如果是红钻的情况下领取奖励
                '''
                base_url = self.getUrl(constant.DAILYURL)
                postData = {
                       'uin':constant.USERNAME,
                       'type':1
                }
                page_content = self.myHttpRequest.get_response(base_url,postData)
                print page_content.read()
                self.Destroy()

                main.Main(None,u'熊熊助手-'+str(constant.USERNAME),self.myHttpRequest,self.loginCard(),self.database)
            else:
                dlg = wx.MessageDialog(self,u"对不起你没有权限登陆",caption=u'提示',style=wx.OK,pos=wx.DefaultPosition)
                retCode = dlg.ShowModal()
                if retCode == wx.ID_OK:
                    dlg.Destroy()

        
        
    #登陆魔卡
    def loginCard(self):
        skey = ''
        for ck in self.myHttpRequest.cj:
                if ck.name=='skey':
                    skey = ck.value
        postData = {
                        'code':'',
                        'uin':constant.USERNAME
                
        }            
        base_url = constant.CARDLOGINURL
        base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
        page_content = self.myHttpRequest.get_response(base_url,postData).read().decode('utf-8')
        return   page_content
    
    
    '''获取用户列表
    '''
    def getUserList(self):
        # try:
        #     self.database.cu.execute("drop table userlist")
        # except Exception:
        #     print 'table userlist exist'

        # self.database.cu.execute("create table userlist (id integer primary key,uin integer,name text NULL)")
        base_url = self.getUrl(constant.USERLISTURL)
        postData = {'uin': constant.USERNAME}
        page_content = self.myHttpRequest.get_response(base_url,postData).read()
        # userlist = BeautifulSoup(page_content.read()).find_all('user')
        # print userlist
        print page_content
        if '1105858958' in page_content or '153937484' in page_content:
            return True
        else:
            return False
        # self.database.cx.commit()

    #读取数据库信息
    def readFile(self,num):
        base_url = r'http://appimg2.qq.com/card/mk/card_info_v3.xml'
        response =self.myHttpRequest.get_response(base_url).read()
        if os.path.exists('card_info_v3.db'):
            dbFileTemp = open('card_info_v3_temp.db','w')
            dbFileTemp.write(response)
            dbFileTemp.close()
            if os.path.getsize('card_info_v3_temp.db')>os.path.getsize('card_info_v3.db'):
                os.remove('card_info_v3.db')
                os.rename('card_info_v3_temp.db', 'card_info_v3.db')
                try:
                    os.remove('test.db')
                except WindowsError:
                    pass
            else:
                print 'no need change'
                os.remove('card_info_v3_temp.db')
        else:
            dbFileTemp = open('card_info_v3.db','w')
            dbFileTemp.write(response)
            dbFileTemp.close()
            try:
                os.remove('test.db')
            except WindowsError:
                pass
        self.database = carddatabase.CardDataBase(self.cur_file_dir())
        self.tipLabel.SetLabelText(u'更新完成，请登陆')



    def get_code(self):
        '''
        获取验证信息
        :return:
        '''
        getCodethread = myThread.GetCodePicThread(self,self.myHttpRequest,constant.USERNAME)
        getCodethread.start()

    #获取脚本文件的当前路径
    def cur_file_dir(self):
        path = sys.path[0]
        #判断为脚本文件还是py2exe编译后的文件，如果是脚本文件，则返回的是脚本的目录，如果是py2exe编译后的文件，则返回的是编译后的文件路径
        if os.path.isdir(path):
            return path+"\\"
        elif os.path.isfile(path):
            return os.path.dirname(path)+"\\"   
    
    #获取对应的url  
    def getUrl(self,url):
        skey = ''
        for ck in self.myHttpRequest.cj:
                if ck.name=='skey':
                    skey = ck.value
        base_url = url
        base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
        return base_url
                
app = wx.App(False)
frame = MyLogin(None, u"qq登陆器")
app.MainLoop()



