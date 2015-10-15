# -*- coding: utf-8 -*-
import threading
from commonlib import constant
import commonlib.commons as commons
import json
from bs4 import BeautifulSoup
import wx
import logging,traceback



###变卡逻辑  src_themeid  middle_theme_id des_theme_id scr_price middle_price des_price,flash_num

class FlashCardToFlashCardThread(threading.Thread):
    def __init__(self,window,myHttpRequest,src_price,des_price,types=0):
        threading.Thread.__init__(self,)  
        self.window = window
        self.myHttpRequest = myHttpRequest
        self.src_price = src_price
        self.des_price = des_price
        self.exchange_box = []
        self.store_box = []
        self.types = types

    # Overwrite run() method, put what you want the thread do here
    def run(self):


        try:
            self.main_page_info()
            print self.exchange_box
            print self.store_box
            self.transfer_card(self.des_price,self.src_price)
        except:
            s = traceback.format_exc()
            logging.error(s)


    def transfer_card(self,des_price,src_price):
        '''
        变卡
        :return:
        '''
        normal_flash_dict = {}
        if self.types==0:
            theme_list = self.window.database.canFlashCardTheme()
            flash_theme_list = []
            for theme_id in theme_list:
                flash_theme_list.append(theme_id[0])
        else:
            theme_list = self.window.database.get_flash_card_list()
            flash_theme_list = []
            for theme_id in theme_list:
                flash_theme_list.append(theme_id[2])
                normal_flash_dict[theme_id[2]] = theme_id[0]
        base_url = commons.getUrl(constant.TRANSFER_CARD,self.myHttpRequest)
        for i,card_id in enumerate(self.exchange_box):
            if card_id!=0:
                card_info = self.window.database.getCardInfo(card_id)
                card_theme = self.window.database.getCardThemeid(card_id)
                if card_theme in flash_theme_list and int(card_info[2])==src_price:
                    if self.types==0:
                        des_theme = card_theme
                    else:
                        des_theme =normal_flash_dict[card_theme]
                    des_card_id = self.get_random_flash_card_id(des_theme,des_price)
                    if des_card_id is not False:
                        self.flashCard(base_url,card_id,des_card_id,0,i,card_info[0])

        for i,card_id in enumerate(self.store_box):
            if card_id!=0:
                card_info = self.window.database.getCardInfo(card_id)
                card_theme = self.window.database.getCardThemeid(card_id)
                if card_theme in flash_theme_list and int(card_info[2])==src_price:
                    if self.types==0:
                        des_theme = card_theme
                    else:
                        des_theme =normal_flash_dict[card_theme]
                    des_card_id = self.get_random_flash_card_id(des_theme,des_price)
                    if des_card_id is not False:
                        self.flashCard(base_url,card_id,des_card_id,1,i,card_info[0])

        wx.CallAfter(self.window.updateLog,u'变卡结束')

    def flashCard(self,base_url,card_id,des_card_id,slottype,slotid,card_name):
        post_data = {
                    'dstid':des_card_id,
                    'slottype':slottype,
                    'kind':1,
                    'srcid':card_id,
                    'uin':constant.USERNAME,
                    'slotid':slotid,
                    'type':5
                }

        page_content = self.myHttpRequest.get_response(base_url,post_data).read().decode('utf-8')
        if self.types==0:
            m_str = u'(闪)'
        else:
            m_str = ''
        if 'result=\"1\"' in  page_content:
                if slottype==0:
                    self.exchange_box[slotid] = des_card_id
                else:
                    self.store_box[slotid] = des_card_id
                wx.CallAfter(self.window.updateLog,m_str+card_name+u'变(闪)'+self.window.database.getCardInfo(des_card_id)[0]+u'成功')
                logging.info(m_str+card_name+u'变(闪)'+self.window.database.getCardInfo(des_card_id)[0]+u'成功')
        else:
            if slottype==0:
                self.exchange_box[slotid] = 0
            else:
                self.store_box[slotid] = 0
            wx.CallAfter(self.window.updateLog,m_str+card_name+u'变(闪)'+self.window.database.getCardInfo(des_card_id)[0]+u'失败')
            logging.info(m_str+card_name+u'变(闪)'+self.window.database.getCardInfo(des_card_id)[0]+u'失败')

    def main_page_info(self):
        postData = {
                            'code':'',
                            'uin':constant.USERNAME

        }
        base_url =  commons.getUrl(constant.CARDLOGINURL,self.myHttpRequest)
        page_content = self.myHttpRequest.get_response(base_url,postData)
        magicCardInfo= page_content.read().decode('utf-8')
        self.get_type_info(constant.STOREBOX,magicCardInfo)
        self.get_type_info(constant.EXCHANGEBOX,magicCardInfo)

        pass


    def get_type_info(self,flag,magicCardInfo):
        '''
        获取卡片信息
        :param flag:
        :param magicCardInfo:
        :return:
        '''
        self.timelist = []
        self.cardcomplete = []
        self.userInfo = []
        soup = BeautifulSoup(magicCardInfo)
        if flag==constant.EXCHANGEBOX:
            self.childlist = soup.changebox.children
            constant.EXCHANGEBOXNUM = int(soup.changebox['cur'])
            self.exchange_box = [0]*constant.EXCHANGEBOXNUM
        elif flag==constant.STOREBOX:
            self.childlist = soup.storebox.children
            constant.STOREBOXNUM = int(soup.storebox['cur'])
            self.store_box = [0]*constant.STOREBOXNUM

        for item in self.childlist:
            if item != u'\n':
                soup2 = BeautifulSoup(str(item))
                pid = int(soup2.card['id'])

                if flag==constant.EXCHANGEBOX:
                    if pid==-1:
                        self.exchange_box[int(soup2.card['slot'])] = 0
                    else:
                        self.exchange_box[int(soup2.card['slot'])] = pid
                elif flag==constant.STOREBOX:
                    self.store_box[int(soup2.card['slot'])] = pid




    def get_random_flash_card_id(self,des_card_theme,price):
        '''
        获取随机的变卡的id
        :return:
        '''
        self.window.database.cu.execute("select pid from cardinfo where price=? and themeid=?",(price,des_card_theme))

        stealCardDict = {}
        result = self.window.database.cu.fetchall()

        if len(result)==0:
            return False
        for cardId in  result :
            stealCardDict[cardId[0]] = self.exchange_box.count(cardId[0])+self.store_box.count(cardId[0])
        #对字典进行排序
        return sorted(stealCardDict.iteritems(),key=lambda asd:asd[1],reverse=False)[0][0]

