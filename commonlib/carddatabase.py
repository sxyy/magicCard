# -*- coding: utf-8 -*-
'''

@author: cvtpc
'''
import sqlite3,os
import commonlib.constant as constant
from bs4 import  BeautifulSoup


class CardDataBase(object):
    def __init__(self,path):
        
       
        if not os.path.exists(path+constant.DATABASE):
            self.cx = sqlite3.connect(path+constant.DATABASE,check_same_thread = False)
            self.cu= self.cx.cursor()
            self.cu.execute("create table cardinfo (id integer primary key,pid integer,themeid integer,name text NULL,price integer)")
            self.cu.execute("create table cardtheme (id integer primary key,pid integer,name text NULL,diff integer,type integer,gift text NULL,flashtheme integer)")
            self.cu.execute("create table cardrelation(id integer primary key,themeid integer,pid integer,content1 integer,content2 integer,content3 integer,time integer)")
            self.cu.execute("create table gift(id integer primary key,pid integer,showId integer,name text NULL)")
            f=file(path+"card_info_v3.db")
            self.soup3 = BeautifulSoup(f.read(),fromEncoding="gbk")
            cardlist = self.soup3.find_all('card')
            for item in cardlist:
                soup = BeautifulSoup(str(item))
                self.cu.execute("insert into cardinfo(id,pid,themeid,name,price) values (NULL,'"+str(soup.card['id'])+"','"+soup.card['theme_id']+"','"+soup.card['name']+"','"+str(soup.card['price'])+"')")
            themelist =self.soup3.find_all('theme')
            for item in themelist:
                soup = BeautifulSoup(str(item))# ,
                self.cu.execute("insert into cardtheme(id,pid,name,diff,type,gift,flashtheme) values (NULL,'"+str(soup.theme['id'])+"','"+soup.theme['name']+"','"+str(soup.theme['diff'])+"','"+str(soup.theme['type'])+"','"+str(soup.theme['gift'])+"','"+str(soup.theme['flashtheme'])+"')")
            comblist = self.soup3.find_all('comb')
            for item in comblist:
                soup = BeautifulSoup(str(item))
                content = soup.comb['from'].split(',')
                self.cu.execute("insert into cardrelation(id,themeid,pid,content1,content2,content3,time) values (NULL,'"+str(soup.comb['theme_id'])+"','"+str(soup.comb['id'])+"','"+str(content[0])+"','"+str(content[1])+"','"+str(content[2])+"','"+str(soup.comb['time'])+"')")
            giftlist = self.soup3.find_all('gift')
            for item in giftlist:
                soup = BeautifulSoup(str(item))
                self.cu.execute("insert into gift(id,pid,showId,name)  values (NULL,'"+str(soup.gift['id'])+"','"+str(soup.gift['showid'])+"','"+soup.gift['name']+"')")
            self.cx.commit()
        else:
            self.cx = sqlite3.connect(path+constant.DATABASE,check_same_thread = False)
            self.cu= self.cx.cursor()
        print 'ok'
        
    #返回卡的id值
    def getCardId(self,cardName):
        self.cu.execute("select pid from cardinfo where name=?",(cardName,))
        result = self.cu.fetchone()
        return result[0]
    
    #返回卡的名字 名字，主题，价格
    def getCardInfo(self,cardId):
        cardInfo = []
        self.cu.execute("select name,price,themeid from cardinfo where pid=?",(cardId,))
        result = self.cu.fetchone()
        cardInfo.append(result[0])
        self.cu.execute("select name from cardtheme where pid="+str(result[2])+"")
        cardInfo.append(self.cu.fetchone()[0])
        cardInfo.append(str(result[1]))
        return cardInfo

    '''获取卡片的主题名字
    '''

    def getCardThemeName(self, themeId):
        self.cu.execute("SELECT name FROM cardtheme WHERE pid=?", (int(themeId),))
        result = self.cu.fetchone()
        return result[0]
    #返回卡的主题id值
    def getCardThemeid(self,cardId):
        self.cu.execute("select themeid from cardinfo where pid=?",(int(cardId),))
        result = self.cu.fetchone()
        return result[0]


    def isOffCard(self,cardId):
        self.cu.execute("select themeid from cardinfo where pid=?",(int(cardId),))
        result = self.cu.fetchone()[0]
        self.cu.execute("SELECT type FROM cardtheme WHERE pid=?",(int(result),))
        result = self.cu.fetchone()[0]
        if int(result)!=0:
            return True
        else:
            return False

    def get_flash_card_list(self):
        '''
        返回闪卡列表
        :return:
        '''
        self.cu.execute("SELECT pid,name,flashTheme FROM cardtheme WHERE type=? ORDER BY diff",(9,))
        result = self.cu.fetchall()

        return result

    def get_grounding_card_list(self):
        '''
        获取未下架卡片以及非活动卡的列表
        :return:
        '''
        self.cu.execute("SELECT pid,name,diff FROM cardtheme WHERE type=? or type=? ORDER BY diff",(0,5))
        result = self.cu.fetchall()
        return result

    def getCardFriendExchangTheme(self,collectThemelist):
        '''
        获取卡友交换的主题
        :param collectThemelist:
        :return:
        '''
        exchStr = u'对方设置的交换主题:'
        exchCardTheme = ''
        hasSetExch = False
        is_contain_flash_card_theme = False
        collectThemelist = list(set(collectThemelist))
        # print collectThemelist
        for collectTheme in collectThemelist:
            if int(collectTheme)!=0:
                self.cu.execute("select type from cardtheme where pid=? ",(collectTheme,))
                result =self.cu.fetchone()
                if result[0]==9:
                    is_contain_flash_card_theme = True
                hasSetExch = True
                exchCardTheme +=self.getCardThemeName(int(collectTheme))+','
        exchStr +=exchCardTheme
        if not hasSetExch:
            exchStr = u'对方设置的交换主题:无'
            exchCardTheme = u'无'
        return exchStr,exchCardTheme,is_contain_flash_card_theme

    def getCardFromTheme(self,themeId):
        '''
        通过主题id查找卡片信息
        :param themeId:
        :return:
        '''
        self.cu.execute("SELECT pid,price,name FROM cardinfo WHERE themeid=?",(themeId,))
        result = self.cu.fetchall()
        return  result


    def canFlashCardTheme(self):
        '''
        获取可闪卡变闪卡的列表
        :return:
        '''
        self.cu.execute("SELECT pid FROM cardtheme WHERE diff>? AND type=?",(1,9))
        result = self.cu.fetchall()
        return result



        