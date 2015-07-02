# -*- coding: utf-8 -*-
'''
Created on 2015��6��2��

@author: cvtpc
'''

import threading
import time,wx,random
from bs4 import BeautifulSoup
import commonlib.constant as constant
import  commonlib.commons as commons

class MyCollectCard(threading.Thread):



    def __init__(self, windows,slovelist):
        threading.Thread.__init__(self,)
        self.windows = windows
        self.slovelist = slovelist
        #用来炼卡后跳出递归循环
        self.flag = False
        self.cardInSlove = False
        self.cardInSloveList =[]
        #self.windows.zcgInfoDic
        print u'偷炉信息',self.windows.stealFriend
    
    def run(self):
        self.emptySlove = 0
        
        self.getRefineCard()

        
        if constant.RANDCHANCE>=10:
            for i in  range(5):
                wx.CallAfter(self.windows.drawCard)
                time.sleep(1)

        '''这里进行珍藏阁炼卡
        '''
        self.refineCardInZCG()

        '''收拾交换箱将面值超过10或者为需要炼制卡的主题放入储物箱将面值<=10的出售
        '''
        for i,cardId in enumerate(self.windows.exchangeBox):
            if cardId!=0 and cardId!=-1:
                self.windows.database.cu.execute("select themeid,price from cardinfo where pid=?",(cardId,))
                result = self.windows.database.cu.fetchone()
                themeId = result[0]
                price = result[1]
                '''增加判断放置保险箱已满出现异常
                '''
                if int(price)==10 and themeId!=constant.COLLECTTHEMEID :
                    wx.CallAfter(self.windows.saleCard,cardId,i)
                elif  0 in self.windows.storeBox: 
                    wx.CallAfter(self.windows.card_user_storage_exchange,0,i,cardId)
                time.sleep(1)
        '''获取到需要炼制的主题的卡片，从最高面值开始往下进行遍历。
        ''' 
        self.windows.database.cu.execute("select pid from cardinfo where themeid=? order by price DESC",(constant.COLLECTTHEMEID,))
        collectCardList =  self.windows.database.cu.fetchall()
        '''这里进行炼卡
        '''  
        
        nowtime = time.localtime(time.time())
        if 8<=int(time.strftime('%H',nowtime))<22:
            if constant.ISRED==1:
                self.stealSlove(-2)
            self.stealSlove(-1)
            
        maxEmptySlove = 2
        '''这里不仅要判断时间并且防止另外一种情况当偷炉卡未没收回，但是有一个炉子已经空了的情况。
        '''
        if (8<=int(time.strftime('%H',nowtime))<22) or self.windows.stoveBox[-1]!=0 :
            maxEmptySlove -= 1
        if constant.ISRED==1 and ((8<=int(time.strftime('%H',nowtime))<22) or self.windows.stoveBox[-2]!=0) :
            maxEmptySlove -= 1
        elif constant.ISRED!=1:
            maxEmptySlove -= 1
        
        print self.emptySlove,'  ',maxEmptySlove
        self.cardInSlove = False
        self.cardInSloveList =[]
        while self.emptySlove>maxEmptySlove and constant.COLLECTTHEMEID!=-1:
            self.flag = False
            collectCardNum = 0
            for cardItem in collectCardList:
                collectCardNum+=1
                cardId = cardItem[0]
                if self.cardExist(0,cardId):
                    continue
                elif self.windows.database.getCardInfo(cardId)[2]=='10':
                    '''进行买卡 
                    '''
                    wx.CallAfter(self.windows.buyCard,cardId)
                    time.sleep(1)
                    continue
                else:
                    
                    self.windows.database.cu.execute("select content1,content2,content3 from cardrelation where pid=? ",(cardId,))
                    cardcontentlist = self.windows.database.cu.fetchone()
                    self.searchCard(cardcontentlist,cardId)
                    if self.flag:
                        break
            if collectCardNum==len(collectCardList) :
                if self.cardInSlove:
                    break
                base_url = self.windows.getUrl(constant.COLLECTADD)
                self.windows.database.cu.execute("select pid from gift where showId=?",(constant.QQSHOWID,))
                sqlresult = self.windows.database.cu.fetchone()
                postData = {
                            'themetype':0,
                            'giftid':sqlresult[0],
                            'cardtype':1,
                            'theme':constant.COLLECTTHEMEID
                }
                content_page = self.windows.myHttpRequest.get_response(base_url,postData)
                result = content_page.read()
                print result
                self.saveConfig()


#                 soup = BeautifulSoup(result)
#                 wx.CallAfter(self.windows.updateUserinfo,2,soup.qqhome['money'])
#                 wx.CallAfter(self.windows.updateUserinfo,1,soup.qqhome['lv'])

                wx.CallAfter(self.windows.freshRightNow)
                break
                
        #while emptySlove!=0:


    '''珍藏阁炼卡
    '''
    def refineCardInZCG(self):
        for k,czgComplete in enumerate(self.windows.czgComplete):
            if czgComplete==-1:
                cardIdTemp = 0
                cardPos = -1
                for i,cardId in enumerate(self.windows.exchangeBox):
                    if cardId==0:
                        continue
                    if self.windows.database.getCardInfo(cardId)[2]==10:
                        cardIdTemp = cardId
                        cardPos = i
                        break
                if cardIdTemp==0:
                    wx.CallAfter(self.windows.buyCard,constant.DEFAULTBYCARDID)
                    time.sleep(0.5)
                    cardIdTemp = constant.DEFAULTBYCARDID
                    cardPos = self.windows.exchangeBox.index(constant.DEFAULTBYCARDID)

                base_url =commons.getUrl(constant.ZCGINFOURL,self.windows.myHttpRequest)
                postData = {
                    'puzi_id':self.windows.zcgInfoDic[k],
                    'slot_id':cardPos,
                    'card_id':cardIdTemp,
                    'act':2
                }
                content_page = self.windows.myHttpRequest.get_response(base_url,postData)
                self.windows.exchangeBox[cardPos] = 0
                print content_page.read()


    '''保存配置文件
    '''
    def saveConfig(self):
        themeTemp = constant.COLLECTTHEMEID
        constant.COLLECTTHEMEID = constant.COLLECTTHEMEID2
        constant.COLLECTTHEMEID2 = themeTemp
        qqshowTemp = constant.QQSHOWSELECT
        constant.QQSHOWSELECT = constant.QQSHOWSELECT2
        constant.QQSHOWSELECT2 = qqshowTemp
        qqshowId = constant.QQSHOWID
        constant.QQSHOWID = constant.QQSHOWID2
        constant.QQSHOWID2 = qqshowId
        configFile = open('Mfkp_config.ini','w')
        configFile.write('['+str(constant.USERNAME)+']'+'\n')
        configFile.write('themeid='+str(constant.COLLECTTHEMEID)+'\n')
        configFile.write('themeid2=' + str(constant.COLLECTTHEMEID2) + '\n')
        configFile.write('friendid='+str(constant.STEALFRIEND)+'\n')
        configFile.write('qqshow='+str(constant.QQSHOWSELECT)+'\n')
        configFile.write('qqshowid='+str(constant.QQSHOWID)+'\n')
        configFile.write('qqshow=' + str(constant.QQSHOWSELECT2) + '\n')
        configFile.write('qqshowid=' + str(constant.QQSHOWID2) + '\n')
        configFile.write('friendid2='+str(constant.STEALFRIEND2)+'\n')
        configFile.close()
    
    
    '''收获卡片
    '''
    def getRefineCard(self):
        
        print u'卡炉卡片完成情况',self.slovelist
        print u'偷炉信息',self.windows.stealFriend
        base_url = ''

        #这里需要增加收获czg的卡片

        for i, czg in enumerate(self.windows.czgComplete):
            if czg == 1:
                base_url = commons.getUrl(constant.ZCGINFOURL, self.windows.myHttpRequest)
                postData = {
                    'act': 5,
                    'puzi_id': self.windows.zcgInfoDic[i]
                }
                result = self.windows.myHttpRequest.get_response(base_url, postData).read()
                print result
                self.windows.czgComplete[i] = -1



        for i,cardId in enumerate(self.windows.stoveBox):
            if cardId==0:
                self.emptySlove +=1
                #myslovelist.append(0)
            elif self.slovelist[i]==1:
                if i==(len(self.slovelist)-1):
                    self.postData = {
                            'ver':1,
                            'slotid':i,
                            'code':'',
                            'slottype':1,
                            'uin':constant.USERNAME,
                            'opuin':self.windows.stealFriend[0]
                    }
                    base_url = self.windows.getUrl(constant.GETSTEALCARD)
                    del self.windows.stealFriend[0]
                elif constant.ISRED==1 and i==(len(self.slovelist)-2):
                    self.postData = {
                            'ver':1,
                            'slotid':i,
                            'code':'',
                            'slottype':1,
                            'uin':constant.USERNAME,
                            'opuin':self.windows.stealFriend[1]
                    }
                    base_url = self.windows.getUrl(constant.GETSTEALCARD)
                    del self.windows.stealFriend[1]
                else:
                    self.postData = {
                            'ver':1,
                            'slotid':i,
                            'code':'',
                            'slottype':1,
                            'uin':constant.USERNAME
                    }
                    base_url = self.windows.getUrl(constant.REFINEDCARD)
                          
                print self.postData
                page_content = self.windows.myHttpRequest.get_response(base_url,self.postData)
                result = page_content.read()
                print u'收获卡片返回信息',result
                if i!=(len(self.slovelist)-1):
                    self.fanpai()
                soup = BeautifulSoup(result)
                #wx.CallAfter(self.windows.updateUserinfo,2,soup.qqhome['money'])
                #wx.CallAfter(self.windows.updateUserinfo,1,soup.qqhome['lv'])
                wx.CallAfter(self.windows.operateLogUpdate,u'收获卡片 :'+self.windows.database.getCardInfo(soup.card['id'])[0])
                self.windows.stoveBox[i] = 0
                self.windows.storeBox[int(soup.card['slot'])] = int(soup.card['id'])
                wx.CallAfter(self.windows.updateStoreBox,soup.card['id'],soup.card['slot'],i)
                time.sleep(2)
                self.emptySlove+=1
                

    
    '''slot 表示卡炉的位置
    '''
    def stealSlove(self,slot):
        print u'进行偷炉'
        stealfriend = 0
        if slot == -2:
            stealfriend = constant.STEALFRIEND2
        else:
            stealfriend = constant.STEALFRIEND
        print u'卡炉信息',self.windows.stoveBox
        print u'偷炉信息',self.windows.stealFriend
        if self.windows.stoveBox[slot]==0:
            stealCardId = self.getRandomStealCardId()
            print 'stealCardId',stealCardId
            if stealCardId!=-1:
                self.windows.database.cu.execute("select content1,content2,content3 from cardrelation where pid=? ",(stealCardId,))
                cardlist = self.windows.database.cu.fetchone()
                for cardId in cardlist:
                    if not (cardId in self.windows.storeBox or cardId in self.windows.exchangeBox):
                        wx.CallAfter(self.windows.buyCard,cardId)
                    time.sleep(1)
                slotlist = self.findCardPosition(cardlist)
                
                if constant.STEALFRIEND in self.windows.stealFriend:
                    stealfriend = constant.STEALFRIEND2
                else:
                    stealfriend = constant.STEALFRIEND
                
                postData = {
                'targetid':stealCardId,
                'slot1':slotlist[0],
                'slottype1':slotlist[1],
                'slot2':slotlist[2],
                'slottype2':slotlist[3],
                'slot3':slotlist[4],
                'slottype3':slotlist[5],
                'bflash':0,
                'ver':1,
                'targettype':1,
                'themeid':constant.COLLECTTHEMEID,
                'slottype':1,
                'opuin':stealfriend,
                }
                self.windows.stealFriend.append(stealfriend)
                self.refineCard(stealCardId, self.findCardPosition(cardlist), cardlist,constant.STEALCARD,postData)
            else:
                self.emptySlove -=1
                self.windows.stoveBox[-1] =stealCardId
    
    
    #获取随机的偸炉卡的id
    def getRandomStealCardId(self):
        self.windows.database.cu.execute("select pid from cardinfo where price=? and themeid=?",(40,constant.COLLECTTHEMEID))
      
        stealCardDict = {}
        result = self.windows.database.cu.fetchall()
        for cardId in  result :

            stealCardDict[cardId[0]] = self.windows.exchangeBox.count(cardId[0])+self.windows.storeBox.count(cardId[0])+self.windows.stoveBox.count(cardId[0])
        #对字典进行排序
        return sorted(stealCardDict.iteritems(),key=lambda asd:asd[1],reverse=False)[0][0]
        #except Exception:
            #return -1
        
    
            
    #搜索卡片    
    def searchCard(self,cardlist,cardId1):
        
        for cardId in cardlist:
            if self.emptySlove<=0:
                break
            elif self.cardExist(1,cardId):
                continue
            elif self.windows.database.getCardInfo(cardId)[2]=='10':
                '''进行买卡
                '''
                if self.cardExist(1,cardId):
                    continue
                wx.CallAfter(self.windows.buyCard,cardId)
                time.sleep(1)
                continue
            else:
                self.windows.database.cu.execute("select content1,content2,content3 from cardrelation where pid=? ",(cardId,))
                cardcontentlist = self.windows.database.cu.fetchone()
                self.searchCard(cardcontentlist,cardId)
        if self.flag:
            return
#         print cardlist
#         print self.windows.exchangeBox
#         print  self.windows.storeBox
#         print self.windows.stoveBox
        
        slotlist = self.findCardPosition(cardlist)
                    
#         print slotlist
        if len(slotlist)!=6:
            return
        
        
#         if int(self.windows.database.getCardInfo()[2])==40 and self.windows.tabOne.sloveBoxList.GetItemText(5,1)!='':
#             self.userName = 543004046
#         else:
#             self.userName = constant.USERNAME
        
        
        postData = {
            'targetid':cardId1,
            'slot1':slotlist[0],
            'slottype1':slotlist[1],
            'slot2':slotlist[2],
            'slottype2':slotlist[3],
            'slot3':slotlist[4],
            'slottype3':slotlist[5],
            'bflash':0,
            'ver':1,
            'targettype':1,
            'themeid':constant.COLLECTTHEMEID,
            'code':'',
            'slottype':1,
            'opuin':constant.USERNAME,
        }  
        
        self.refineCard(cardId1,slotlist,cardlist,constant.STOVEREFINEURL,postData)
    
    
    #查找卡片所在的具体位置, cardlist 炼制的3张卡列表
    def findCardPosition(self,cardlist):
        slotlist = []
        for cardcontent in cardlist: 
           
            if cardcontent in self.windows.exchangeBox:
                cardName = self.windows.database.getCardInfo(cardcontent)[0]
                for i in range(constant.EXCHANGEBOXNUM):
                    if self.windows.exchangeBoxlist.GetItemText(i,1)==cardName:
                        slotlist.append(i)
                        print 'find exchangbox cardid'
                        slotlist.append(0)
                        break
            elif cardcontent in self.windows.storeBox:
                cardName = self.windows.database.getCardInfo(cardcontent)[0]
                for i in range(constant.STOREBOXNUM):
                    if self.windows.safeBoxlist.GetItemText(i,1)==cardName:
                        slotlist.append(i)
                        print 'find storeBox cardid'
                        slotlist.append(1)
                        break
            elif cardcontent in self.windows.stoveBox:
                return slotlist
        print slotlist
        return slotlist
    
    #提炼卡片 cardId1, 炼制的卡的id ,炼制卡片所需的卡的位置列表,card的id列表
    def refineCard(self,cardId1,slotlist,cardlist,cardUrl,postData):
        
        base_url = self.windows.getUrl(cardUrl)
        
        print base_url
        print postData
        
        
        page_content = self.windows.myHttpRequest.get_response(base_url,postData)
        response = page_content.read()
        print response
        soup = BeautifulSoup(response)
        soup2 = BeautifulSoup(str(soup.find_all('card')[0]))
        sloveInfo = []
        cardInfo = self.windows.database.getCardInfo(cardId1)
        wx.CallAfter(self.windows.operateLogUpdate,u'炼制卡片 :'+cardInfo[0])
        sloveInfo.append(cardInfo[0])
        sloveInfo.append(cardInfo[1])
        endtime = int(soup2.card['btime'])+int(soup2.card['times'])
        x = time.localtime(endtime)
        sloveInfo.append(time.strftime('%Y-%m-%d %H:%M:%S',x))
        if not int(soup2.card['slotid'])>=len(self.windows.stoveBox):
            if int(soup2.card['slotid'])== 5 and self.windows.stoveBox[5]!=0:
                self.windows.stoveBox[-1] = int(soup2.card['id'])
            else:
                self.windows.stoveBox[int(soup2.card['slotid'])] = int(soup2.card['id'])
        else:
            self.windows.stoveBox[-1] = int(soup2.card['id'])
        self.emptySlove -= 1
        
        if postData['slottype1']==0:
            self.windows.exchangeBox[postData['slot1']] = 0
        else:
            self.windows.storeBox[postData['slot1']] = 0
            
        if postData['slottype2']==0:
            self.windows.exchangeBox[postData['slot2']] = 0
        else:
            self.windows.storeBox[postData['slot2']] = 0
            
        if postData['slottype3']==0:
            self.windows.exchangeBox[postData['slot3']] = 0
        else:
            self.windows.storeBox[postData['slot3']] = 0
        
        wx.CallAfter(self.windows.updateSlove,slotlist,int(soup2.card['slotid']),sloveInfo)
        time.sleep(2)
        self.flag = True
    
    
    '''进行翻牌操作
    '''
    def fanpai(self):
        base_url = self.windows.getUrl(constant.FANPAIURL)
        postData = {
                    'type':1,
        }
        page_content = self.windows.myHttpRequest.get_response(base_url,postData).read()
        print u'翻牌结果',page_content


    #判断卡片是否存在
    def cardExist(self,flag,cardId):
        print u'检查卡箱是否存在该卡片',cardId
        print  u'交换箱',self.windows.exchangeBox,u'保险箱',self.windows.storeBox
        if cardId in self.windows.exchangeBox or cardId in self.windows.storeBox  :
            return True
        elif cardId in self.windows.stoveBox:
            if cardId in self.cardInSloveList and self.cardInSloveList.count(cardId)==self.windows.stoveBox.count(cardId):
                return False
            else:
                self.cardInSloveList.append(cardId)
                self.cardInSlove = True
                return True
        else:
            return False
        
