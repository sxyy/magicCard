# -*- coding: utf-8 -*-
import threading
from commonlib import constant
from commonlib import commons
from bs4 import BeautifulSoup
import time
import wx
import commonlib.carddatabase as carddatabase
import random
import logging
import traceback,re


class MyThread(threading.Thread):
    def __init__(self,window,myHttpRequest,cardtheme,cardPrice,nodeItem,searchCardId,is_show_flash_card):
        threading.Thread.__init__(self,)
        self.window = window
        self.myHttpRequest =myHttpRequest
        self.cardtheme = cardtheme
        self.cardPrice = cardPrice
        self.nodeItem = nodeItem
        self.searchCardId = searchCardId
        self.thread_stop = False
        self.database = carddatabase.CardDataBase(self.window.path)
        self.hasFound = False
        self.is_show_flash_card = is_show_flash_card

    def run(self):
        # userList = []
        soup = BeautifulSoup(str(self.nodeItem))
        uinlist = soup.node['uin']
        uinList = uinlist.split('|')
        userList = [uin for uin in uinList]
        # for uin in uinList:
        #     userList.append(uin)
        for user in userList:
            self.hasFound = False

            if self.thread_stop:
                return
            try:
                print 'search user',user
                if user=='':
                    continue
                result = self.get_user_info(user)
                soup = BeautifulSoup(result)
                soup2 = BeautifulSoup(str(soup.changebox))
                self.exchang_box_info(soup2,user)
                if constant.ISSEARCHSTEALFRIEND==1:
                    try:
                        opuin = re.findall('opuin=\"(.*?)\" flag=',result,re.S)[0]
                    except:
                        opuin = '0'
                    try:
                        opuin2 = re.findall('opuin2=\"(.*?)\" id2=',result,re.S)[0]
                    except:
                        opuin2 = '0'
                    if opuin!=''and opuin!='0':
                        print 'search steal1',opuin
                        opuin_result = self.get_user_info(opuin)
                        soup2 = BeautifulSoup(str(BeautifulSoup(opuin_result).changebox))
                        self.exchang_box_info(soup2,opuin)

                    if opuin2!=''and opuin2!='0':
                        print 'search steal2',opuin2
                        opuin_result = self.get_user_info(opuin2)
                        soup2 = BeautifulSoup(str(BeautifulSoup(opuin_result).changebox))
                        self.exchang_box_info(soup2,opuin2)

            except:
                s = traceback.format_exc()
                logging.error(s)
    def stop(self):
        self.thread_stop = True



    def get_user_info(self,user):
        base_url = commons.getUrl(constant.CARDLOGINURL,self.myHttpRequest)
        postData = {
           'uin':constant.USERNAME,
           'opuin':user,
        }

        result = self.myHttpRequest.get_response(base_url,postData).read()
        return result


    def exchang_box_info(self,soup2,user):
        '''
        卡友交换箱中的信息
        '''
        self.hasFound = False
        try:
            collectThemelist = soup2.changebox['exch'].split(',')
        except:
            logging.info('error')
            logging.info(str(soup2))
            return
        exchStr,exchCardTheme,is_contain_flash_card = self.database.getCardFriendExchangTheme(collectThemelist)
        #print collectThemelist
        if self.is_show_flash_card and is_contain_flash_card:
            return
        cardlist = soup2.find_all('card')
        msg = ''
        for item in cardlist:

            if self.thread_stop:
                return
            soup3 = BeautifulSoup(str(item))
            pid = int(soup3.card['id'])
            if pid!=0 and pid!=-1:
                cardThemeId = self.database.getCardThemeid(pid)

                if cardThemeId==self.cardtheme:

                    if self.thread_stop:
                        return
                    if self.cardPrice==u'全部':
                        self.hasFound = True
                        card_info = self.database.getCardInfo(pid)
                        msg += ',['+card_info[0]+']('+str(card_info[2])+')'

                    else:
                        if self.database.getCardInfo(pid)[2]==self.cardPrice and (self.searchCardId==-1 or pid==self.searchCardId) :
                            self.hasFound = True

                            msg += ',['+self.database.getCardInfo(pid)[0]+']'

        if self.hasFound:
            wx.CallAfter(self.window.updateCardFriend,user,msg,exchCardTheme)
            msg = user+msg+','+exchStr
            wx.CallAfter(self.window.update_import_log,msg)
        if self.thread_stop:
            return
        # time.sleep(0.3)




class SearchCardThread(threading.Thread):
    def __init__(self,window,myHttpRequest,cardtheme,cardPrice,cardDetail,search_range_theme_id,is_show_flash_card):
        threading.Thread.__init__(self,)  
        self.window = window
        self.myHttpRequest =myHttpRequest
        self.cardtheme = cardtheme
        self.cardPrice = cardPrice
        if cardDetail!=-1 :
            self.searchCardId = self.window.database.getCardId(cardDetail)
        else:
            self.searchCardId = -1
        self.search_range_theme_id = search_range_theme_id
        self.thread_stop = False
        self.threadList = []
        self.is_show_flash_card = is_show_flash_card

   
    def run(self):
        self.window.database.cu.execute("select * from cardtheme where type=? or type=? or type=? or type=? or type=?",(0,9,5,1,2))
        result =self.window.database.cu.fetchall()
        #创建搜索的excel表
        result_list = dict.fromkeys(result,True)
        len1 = len(result)
        for i in xrange(len1):

            if i==0 or self.search_range_theme_id!=-1:
                if self.search_range_theme_id==-1:
                    self.window.database.cu.execute("select * from cardtheme where pid=?",(self.cardtheme,))
                else:
                    self.window.database.cu.execute("select * from cardtheme where pid=?",(self.search_range_theme_id,))
                searchResult =self.window.database.cu.fetchall()
                themeItem = searchResult[0]
                if themeItem not  in result_list:
                    themeItem = random.choice(result)
                    result.remove(themeItem)
                    del result_list[themeItem]
            else:
                themeItem = random.choice(result)
                result.remove(themeItem)
                del result_list[themeItem]
            if self.thread_stop:
                break
            base_url = commons.getUrl(constant.THEMELISTURL,self.myHttpRequest)
            print base_url
            postData = {
                   'uin':constant.USERNAME,

                   'tid':int(themeItem[1])
            }
            print 'themeItem',themeItem[1]
            wx.CallAfter(self.window.updateLog,u'搜索正在炼制'+themeItem[2]+u'套卡的卡友')
            try:
                searchCardUserNum = 0
                searchCardNum = int(constant.CARDUSERNUM)
                while searchCardUserNum<searchCardNum:
                    # wx.CallAfter(self.window.update_search_progress,searchCardUserNum)
                    if self.thread_stop:
                        break
                    results = self.myHttpRequest.get_response(base_url,postData).read()
                    soup = BeautifulSoup(results)
                    nodeList = soup.find_all('node')
                    if len(nodeList)==0:
                        break
                    #print u'线程个数',len(nodeList)
                    searchCardUserNum +=10*len(nodeList)
                    #wx.CallAfter(self.window.updateLog,u'共有'+str(10*len(nodeList))+u'卡友')
                    len2 = len(nodeList)
                    for i in xrange(len2):

                        mythread = MyThread(self.window,self.myHttpRequest,self.cardtheme,self.cardPrice,nodeList[i],self.searchCardId,self.is_show_flash_card)
                        mythread.start()
                        self.threadList.append(mythread)

                    for mythread in self.threadList:
                        mythread.join(30)
                    print searchCardUserNum
                    wx.CallAfter(self.window.update_search_progress,searchCardUserNum)
                    self.threadList = []
            except :
                s = traceback.format_exc()
                logging.error(s)
                continue
        print 'stop'
        wx.CallAfter(self.window.searchComplete)
    def stop(self):
        self.thread_stop = True
        print u'目前线程长度'+str(len(self.threadList))
        for mythread in self.threadList:

            mythread.thread_stop = True


        