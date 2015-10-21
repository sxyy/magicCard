# -*- coding: utf-8 -*-
import threading
from bs4 import BeautifulSoup
import commonlib.constant as constant
import wx,re,sqlite3,time
import collectcard
import commonlib.commons as commons
import json
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
            self.cardcomplete[-2] = 1
        else:
            self.cardcomplete[-2] = 0
        print u'插入后的卡炉信息',self.windows.stoveBox


    '''获取珍藏阁信息
    '''
    def getZCGInfo(self):
        base_url = commons.getUrl(constant.ZCGINFOURL,self.myHttpRequest)
        postData = {
           'opuin':constant.USERNAME,
            'act':1
        }
        return self.myHttpRequest.get_response(base_url,postData).read()

        
       
    def run(self):
        self.timelist = []
        self.cardcomplete = []
        self.userInfo = []

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
                self.windows.stealFriend = [0]
            else:
                constant.SLOVENUM = int(self.soup.stovebox['cur'])
                self.windows.stealFriend = [0, 0]
            self.windows.stoveBox = [0]*constant.SLOVENUM
            self.cardcomplete = [0] * constant.SLOVENUM
            self.childlist = self.soup.stovebox.children
        elif self.flag==constant.ZCG:
            self.windows.zcgInfoDic = []
            self.windows.czgComplete = []
            resultInfo = self.getZCGInfo()
            zcgInfos = json.loads(resultInfo)['puzi']
            print u'珍藏阁信息', zcgInfos
            for i,zcgInfo in enumerate(zcgInfos):
                try:
                    endpuzi =  int(zcgInfo['end'])
                except KeyError:
                    endpuzi = 9436421308
                if int(time.time())<= endpuzi:
                    if zcgInfo['card_id']!=0:
                        endtime = int(zcgInfo['begin'])+int(zcgInfo['smelt_time'])
                        if int(time.time())-endtime>10:
                            self.windows.czgComplete.append(1)
                        else:
                            self.windows.czgComplete.append(0)
                        x = time.localtime(endtime)
                        self.timelist.append(time.strftime('%Y-%m-%d %H:%M:%S',x) )
                    else:
                        self.windows.czgComplete.append(-1)
                    self.windows.zcgInfoDic.append(zcgInfo['id'])

            print u'空珍藏阁信息',self.windows.zcgInfoDic
            print
        if self.flag!=constant.ZCG:
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
                    elif self.flag==constant.STOVEBOX:

                        if pid!=0:
                            endtime = int(soup2.card['btime'])+int(soup2.card['locktime'])
                            x = time.localtime(endtime)
                            self.timelist.append(time.strftime('%Y-%m-%d %H:%M:%S',x) )
                        else:
                            self.timelist.append('')
                        if int(soup2.card['slot'])!=6:
                            '''卡片的完成情况
                            '''
                            self.windows.stoveBox[int(soup2.card['slot'])] = pid
                            if int(soup2.card['flag']) == 2:
                                self.cardcomplete[int(soup2.card['slot'])] = 1
                            else:
                                self.cardcomplete[int(soup2.card['slot'])] = 0
                        else:

                            if int(soup2.card['flag']) == 2:
                                self.cardcomplete[-1] = 1
                            else:
                                self.cardcomplete[-1] = 0

                            if pid!=0:
                                self.windows.stealFriend[-1] = int(soup2.card['opuin'])
                            else:
                                self.windows.stealFriend[-1] = 0
                            self.windows.stoveBox[-1] = int(pid)
                            if constant.ISRED==1 and int(soup2.card['opuin2'])!=0:
                                self.windows.stealFriend[-2] = int(soup2.card['opuin2'])
                                self.getSlove2Info(int(soup2.card['opuin2']))
                            elif constant.ISRED==1:
                                self.windows.stoveBox[-2] = 0
                                self.timelist.insert(-1, "")
                                self.cardcomplete[-2] = 0
                                self.windows.stealFriend[-2] = 0

#                             
        
        wx.CallAfter(self.windows.updateInfo,self.flag,self.timelist,self.userInfo)
        if constant.RUNSTATE:
            if ((1 in self.cardcomplete) or (0 in self.windows.stoveBox) or (constant.RANDCHANCE >= 10) or (
                -1 in self.windows.czgComplete) or (
                1 in self.windows.czgComplete)) and constant.COLLECTTHEMEID != -1 and (self.flag == constant.STOVEBOX):
                print u'偷炉信息', self.windows.stealFriend
                time.sleep(10)
                collectCardThread = collectcard.MyCollectCard(self.windows, self.cardcomplete)
                collectCardThread.start()
