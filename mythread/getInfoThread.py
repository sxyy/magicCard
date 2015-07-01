# -*- coding: utf-8 -*-
import threading
from bs4 import BeautifulSoup
import commonlib.constant as constant
import wx,re,sqlite3,time
import collectcard

'''
Created on 2015��5��31��

@author: Administrator
'''

class GetInfoThread(threading.Thread):

    def __init__(self, magicCardInfo,flag,windows,myHttpRequest):

        threading.Thread.__init__(self,)
        self.soup = BeautifulSoup(magicCardInfo)
        self.flag = flag
        self.windows = windows
        self.cardNamePatter = re.compile(r'name="(.*?)"')
        cx = sqlite3.connect(constant.DATABASE,check_same_thread = False)
        self.cu = cx.cursor()
        self.isStartTBCardThread = False
        self.myHttpRequest = myHttpRequest
    
    
    
    def getSlove2Info(self,StealFriend):
        base_url = self.windows.getUrl(constant.CARDLOGINURL)
        postData = {
                    'stoveinfo':1,
                    'code':'',
                    'uin':constant.USERNAME,
                    'opuin':StealFriend,
                    'stageuin':constant.USERNAME
        }
        page_content = self.windows.myHttpRequest.get_response(base_url,postData).read()
        print u'偷炉2',page_content
        soup = BeautifulSoup(page_content)
        self.windows.stoveBox[-2]=int(soup.card['id'])
        endtime = int(soup.card['btime'])+int(soup.card['locktime'])
        x = time.localtime(endtime)
        self.timelist.insert(-1, time.strftime('%Y-%m-%d %H:%M:%S',x))
        if int(soup.card['flag'])==2:
            self.cardcomplete.insert(-1, 1)
        else:
            self.cardcomplete.insert(-1, 0)
        print u'插入后的卡炉信息',self.windows.stoveBox
        
       
    def run(self):
        self.timelist = []
        self.cardcomplete = []
        self.userInfo = []
        self.windows.stealFriend = []
        if self.flag==constant.EXCHANGEBOX:
            self.childlist = self.soup.changebox.children
            constant.EXCHANGEBOXNUM = int(self.soup.changebox['cur'])
            self.windows.exchangeBox = [0]*constant.EXCHANGEBOXNUM
            constant.RANDCHANCE = int(self.soup.user['randchance'])
            constant.ISRED = int(self.soup.user['redvip'])
            self.userInfo.append(self.soup.user['nick'])
            self.userInfo.append(self.soup.user['lv'])
            self.userInfo.append(self.soup.user['money'])
            self.userInfo.append(self.soup.user['mana'])
        elif self.flag==constant.STOREBOX:
            self.childlist = self.soup.storebox.children
            constant.STOREBOXNUM = int(self.soup.storebox['cur'])
            self.windows.storeBox = [0]*constant.STOREBOXNUM
        elif self.flag==constant.STOVEBOX:
            if constant.ISRED==0:
                constant.SLOVENUM = int(self.soup.stovebox['cur'])-1
            else:
                constant.SLOVENUM = int(self.soup.stovebox['cur'])
            self.windows.stoveBox = [0]*constant.SLOVENUM
            self.childlist = self.soup.stovebox.children
        for item in self.childlist:
            if item != u'\n':
                soup2 = BeautifulSoup(str(item))
                pid = int(soup2.card['id'])
                
                
                if self.flag==constant.EXCHANGEBOX:
                    if pid==-1:
                        self.windows.exchangeBox[int(soup2.card['slot'])] = 0
                    else:
                        self.windows.exchangeBox[int(soup2.card['slot'])] = pid
                elif self.flag==constant.STOREBOX:
                    self.windows.storeBox[int(soup2.card['slot'])] = pid
                else:
                    if int(soup2.card['flag'])==2:
                        self.cardcomplete.append(1)
                    else:
                        self.cardcomplete.append(0)
                    if pid!=0:
                        endtime = int(soup2.card['btime'])+int(soup2.card['locktime'])
                        x = time.localtime(endtime)
                        self.timelist.append(time.strftime('%Y-%m-%d %H:%M:%S',x) )
                    else:
                        self.timelist.append('')
                    if int(soup2.card['slot'])!=6:
                        self.windows.stoveBox[int(soup2.card['slot'])] = pid
                    else:
                        if pid!=0:
                            self.windows.stealFriend.append(int(soup2.card['opuin']))
                        self.windows.stoveBox[-1] = int(pid)
                        if constant.ISRED==1 and int(soup2.card['opuin2'])!=0:
                            self.windows.stealFriend.append(int(soup2.card['opuin2']))
                            self.getSlove2Info(int(soup2.card['opuin2']))
                        elif constant.ISRED==1:
                            self.windows.stoveBox[-2] = 0
                            self.timelist.insert(-1, "")
                            self.cardcomplete.append(0)
                        else:
                            pass
#                             
        
        wx.CallAfter(self.windows.updateInfo,self.flag,self.timelist,self.userInfo)
        if ((1 in self.cardcomplete) or (0 in self.windows.stoveBox) or (constant.RANDCHANCE>=10)) and constant.COLLECTTHEMEID!=-1 and  self.flag==constant.STOVEBOX :
            print '偷炉1',constant.STEALFRIEND,'偷炉2',constant.STEALFRIEND2
            time.sleep(10)
            collectCardThread = collectcard.MyCollectCard(self.windows,self.cardcomplete)
            collectCardThread.start()
            
            
   