# -*- coding: utf-8 -*-

import threading
from commonlib import commons,constant
import wx
import accountManage
class AccountSupportThread(threading.Thread):
    def __init__(self,window,myHttpRequest,cardtheme,cardPrice,cardDetail):
        threading.Thread.__init__(self,)
        self.window = window
        self.myHttpRequest = myHttpRequest
        self.cardtheme = cardtheme
        self.cardPrice = cardPrice
        self.cardDetail = cardDetail
        self.thread_stop = False

    # Overwrite run() method, put what you want the thread do here
    def run(self):
        user_card_info = commons.getMagicInfo(self.myHttpRequest,constant.USERNAME)
        self.user_exchange_box = commons.get_type_info(constant.EXCHANGEBOX,user_card_info)


        card_exchange_dic = {}
        for i,card_id in enumerate(self.user_exchange_box):
            if self.thread_stop:
                break
            if int(card_id) != 0 :
                card_info = self.window.database.getCardInfo2(card_id)
                if self.cardPrice != u'全部':
                    if card_info[2] != self.cardtheme and card_info[1] == self.cardPrice:
                        card_exchange_dic[i] = card_id
                    else:
                        continue
                elif card_info[2] != self.cardtheme:
                    card_exchange_dic[i] = card_id
                else:
                    continue

        print card_exchange_dic


                # card_info = commons.getMagicInfo2(self.myHttpRequest,constant.USERNAME)
                # exchange_box = commons.get_type_info(constant.EXCHANGEBOX,card_info)
                # store_box = commons.get_type_info(constant.STOREBOX,card_info)

        wx.CallAfter(self.window.updateLog,u'换卡完成')
        pass


    def exchange_card(self,card_exchange_dic):
        '''
        卡片交换
        :param position:
        :param card_id:
        :param card_price:
        :param account:
        :param type:
        :return:
        '''



        for key,value in card_exchange_dic.item():
            for account,httpRequest in accountManage.AccountManage.account_http_dic.items():
                account = account.replace("\n","")

                if int(account) == int(constant.USERNAME):
                    continue

                if self.thread_stop:
                    break

                if account.strip() != '':
                    user_card_info = commons.getMagicInfo(value,key)
                    exchange_box = commons.get_type_info(constant.EXCHANGEBOX,user_card_info)
                    store_box = commons.get_type_info(constant.STOREBOX,user_card_info)

                    for i,card_id in enumerate(exchange_box):
                        if int(card_id) != 0:
                            card_info = self.window.database.getCardInfo2(card_id)
                            if card_info[2] == self.cardtheme and card_info[1] == self.cardPrice:
                                src_card_name = card_info[0]
                                src_card_id = card_id
                                src_type = 0
                                src_position = i
                                break


        # base_url = commons.getUrl(constant.EXCHANGECARD,self.myHttpRequest)
        # src_card_id = -1
        # src_type = -1
        # src_position = -1
        # src_card_name = ''
        # for i,card_id in enumerate(self.user_exchange_box):
        #     if int(card_id) != 0:
        #         card_info = self.window.database.getCardInfo2(card_id)
        #         if not self.window.database.isOffCard(card_id) and card_info[2] != self.cardtheme and card_info[1] == card_price:
        #             src_card_name = card_info[0]
        #             src_card_id = card_id
        #             src_type = 0
        #             src_position = i
        #             break
        #
        # if src_card_id == -1:
        #     for i,card_id in enumerate(self.user_store_box):
        #         if int(card_id) != 0:
        #             card_info = self.window.database.getCardInfo2(card_id)
        #             if not self.window.database.isOffCard(card_id) and card_info[2] != self.cardtheme and card_info[1] == card_price:
        #                 src_card_name = card_info[0]
        #                 src_card_id = card_id
        #                 src_type = 1
        #                 src_position = i
        #                 break
        #
        # if src_card_id != -1:
        #     src = str(src_card_id)+"_"+str(src_position)+"_"+str(src_type)
        #     dst = str(dst_card_id)+"_"+str(position)+"_"+str(types)
        #     post_data ={
        #         'cmd':1,
        #         'isFriend':1,
        #         'frnd':str(account),
        #         'uin':str(constant.USERNAME),
        #         'dst':dst,
        #         'src':src
        #     }
        #     print post_data
        #     page_content = self.myHttpRequest.get_response(base_url,post_data).read().decode('utf-8')
        #     print page_content
        #     if 'code="0"' in page_content:
        #         wx.CallAfter(self.window.updateLog,u'与卡友'+str(account)+u'交换卡片'+src_card_name+'->'+card_name)
        #         if src_type == 0:
        #             self.user_exchange_box[src_position] = dst_card_id
        #         else :
        #             self.user_store_box[src_position] = dst_card_id
        #     else:
        #         wx.CallAfter(self.window.updateLog,u'与卡友'+str(account)+u'交换卡片失败')
        #
        #     return  page_content
        # else:
        #     return -1
        #
        # pass

    def stop(self):
        self.thread_stop = True


