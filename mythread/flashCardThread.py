# -*- coding: utf-8 -*-
import threading
from commonlib import constant
import commonlib.commons as commons
import json
from bs4 import BeautifulSoup
import wx
import logging,traceback



###变卡逻辑  src_themeid  middle_theme_id des_theme_id scr_price middle_price des_price,flash_num

class FlashCardThread(threading.Thread):
    def __init__(self,window,myHttpRequest,card_theme_list,flash_num,card_price_list):
        threading.Thread.__init__(self,)  
        self.window = window
        self.src_theme_id = card_theme_list[0]
        self.mid_theme_id = card_theme_list[1]
        self.des_theme_id = card_theme_list[2]
        self.myHttpRequest =myHttpRequest
        self.flash_num = flash_num
        self.src_price = card_price_list[0]
        self.mid_price = card_price_list[1]
        self.des_price = card_price_list[2]
        self.exchange_box = []
        self.store_box = []

    # Overwrite run() method, put what you want the thread do here
    def run(self):


        try:
            self.main_page_info()
            self.receive_gift()
            self.main_page_info()
            print self.exchange_box
            print self.store_box
            if self.mid_theme_id==-1:
                self.transfer_card(self.des_theme_id,self.src_theme_id,self.des_price,self.src_price,False)
            else:
                self.transfer_card(self.mid_theme_id,self.src_theme_id,self.mid_price,self.src_price,False)
                self.transfer_card(self.des_theme_id,self.mid_theme_id,self.des_price,self.mid_price,True)
        except:
            s = traceback.format_exc()
            logging.error(s)
    def receive_gift(self):
        '''
        接收礼物
        :return:
        '''

        self.get_theme_card_num(self.src_theme_id,self.src_price)
        if self.card_num >=self.flash_num:
            return
        limit_receive_time = self.flash_num-self.card_num
        base_url = commons.getUrl(constant.GETGIFTLISTURL,self.myHttpRequest)
        base_url = base_url.replace('USERNAME',str(constant.USERNAME))
        page_content = self.myHttpRequest.get_response(base_url).read().decode("utf-8")
        # print page_content
        page_content = page_content[10:-4]
        gift_list = json.loads(page_content)['freegifts']
        base_url = commons.getUrl(constant.GIFTRECEIVE,self.myHttpRequest)
        for i,gift_dic in enumerate(gift_list):
            post_data = {
                'appid':365,
                'action':1,
                'index_id':gift_dic['index_id'],
                'uin':constant.USERNAME,
                'cb':1,
                'r':'0.4827874337788671',
                'qzreferrer':'http://qzs.qq.com/snsapp/app/free_gift/index.htm?appid=365&page=receive'
            }
            page_content = self.myHttpRequest.get_response(base_url,post_data).read().decode('utf-8')
            print page_content
            if u"系统繁忙" in page_content:
                wx.CallAfter(self.window.updateLog,u'卡箱已满')
                logging.info(u'卡箱已满')
            elif u'上限' in page_content:
                wx.CallAfter(self.window.updateLog,u'收卡上限')
                logging.info(u'卡箱已满')
                break
            else:
                logging.info(u'接收好友一个礼物')
                wx.CallAfter(self.window.updateLog,u'接收好友一个礼物')
            if i>=(limit_receive_time-1):
                break

    def transfer_card(self,des_card_theme,src_card_theme,des_price,src_price,is_flash_card,):
        '''
        变卡
        :return:
        '''
        base_url = commons.getUrl(constant.TRANSFER_CARD,self.myHttpRequest)
        for k in range(self.flash_num):
            src_card_id = -1
            slottype = -1
            slotid = -1
            for i,exchang_card_id in enumerate(self.exchange_box):
                if exchang_card_id!=0:
                    print exchang_card_id,self.window.database.getCardThemeid(exchang_card_id),self.window.database.getCardInfo(exchang_card_id)[2]
                    if int(self.window.database.getCardThemeid(exchang_card_id))==int(src_card_theme) and int(self.window.database.getCardInfo(exchang_card_id)[2])==int(src_price) :
                        slottype = 0
                        src_card_id = exchang_card_id
                        slotid = i
                        break

            if slotid ==-1:
                for i,store_card_id in enumerate(self.store_box):
                    if store_card_id!=0:
                        print store_card_id,self.window.database.getCardThemeid(store_card_id),self.window.database.getCardInfo(store_card_id)[2]
                        if int(self.window.database.getCardThemeid(store_card_id))==int(src_card_theme) and int(self.window.database.getCardInfo(store_card_id)[2])==int(src_price) :
                            slottype = 1
                            src_card_id = store_card_id
                            slotid = i
                            break
            if slotid==-1:
                break
            #是否变闪卡
            if is_flash_card:
                flash_card_str = u'（闪）'
                kind = 1
                types = 5
            else:
                flash_card_str = u''
                kind = 0
                types = 2
            des_card_id = self.get_random_flash_card_id(des_card_theme,des_price)
            post_data = {
                'dstid':des_card_id,
                'slottype':slottype,
                'kind':kind,
                'srcid':src_card_id,
                'uin':constant.USERNAME,
                'slotid':slotid,
                'type':types
            }

            page_content = self.myHttpRequest.get_response(base_url,post_data).read().decode('utf-8')
            logging.info(u'变卡结果'+page_content)
            if '-33087' in page_content:
                wx.CallAfter(self.window.updateLog,u'该普卡您还未收集齐')
                logging.info(u'该普卡您还未收集齐')
                break
            elif 'result=\"1\"' in  page_content:
                if slottype==0:
                    self.exchange_box[slotid] = des_card_id
                else:
                    self.store_box[slotid] = des_card_id
                wx.CallAfter(self.window.updateLog,u'变'+flash_card_str+self.window.database.getCardInfo(des_card_id)[0]+u'成功')
                logging.info(u'变'+flash_card_str+self.window.database.getCardInfo(des_card_id)[0]+u'成功')
            else:
                if slottype==0:
                    self.exchange_box[slotid] = 0
                else:
                    self.store_box[slotid] = 0
                wx.CallAfter(self.window.updateLog,u'变'+flash_card_str+self.window.database.getCardInfo(des_card_id)[0]+u'失败')
                logging.info(u'变'+flash_card_str+self.window.database.getCardInfo(des_card_id)[0]+u'失败')


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
        for cardId in  result :
            stealCardDict[cardId[0]] = self.exchange_box.count(cardId[0])+self.store_box.count(cardId[0])
        #对字典进行排序
        return sorted(stealCardDict.iteritems(),key=lambda asd:asd[1],reverse=False)[0][0]

    def get_theme_card_num(self,theme_id,price):
        '''
        获取卡箱对应主题的卡片个数
        :return:
        '''
        self.window.database.cu.execute("select pid from cardinfo where price=? and themeid=?",(price,theme_id))
        result = self.window.database.cu.fetchall()
        self.card_num = 0
        for card_id in result:
            self.card_num+=self.exchange_box.count(card_id[0])+self.store_box.count(card_id[0])
        print 'card_num',self.card_num