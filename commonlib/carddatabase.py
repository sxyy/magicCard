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
            self.cu.execute("create table cardtheme (id integer primary key,pid integer,name text NULL,diff integer,type integer,gift text NULL)")
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
                self.cu.execute("insert into cardtheme(id,pid,name,diff,type,gift) values (NULL,'"+str(soup.theme['id'])+"','"+soup.theme['name']+"','"+str(soup.theme['diff'])+"','"+str(soup.theme['type'])+"','"+str(soup.theme['gift'])+"')")
            comblist = self.soup3.find_all('comb')
            for item in comblist:
                soup = BeautifulSoup(str(item))
                content = soup.comb['from'].split(',')
                self.cu.execute("insert into cardrelation(id,themeid,pid,content1,content2,content3,time) values (NULL,'"+str(soup.comb['theme_id'])+"','"+str(soup.comb['id'])+"','"+str(content[0])+"','"+str(content[1])+"','"+str(content[2])+"','"+str(soup.comb['time'])+"')")
            giftlist = self.soup3.find_all('gift')
            for item in giftlist:
                soup = BeautifulSoup(str(item))
                self.cu.execute("insert into gift(id,pid,showId,name)  values (NULL,'"+str(soup.gift['id'])+"','"+str(soup.gift['showid'])+"','"+soup.gift['name']+"')")
            print 'ok'
            self.cx.commit()
        else:
            self.cx = sqlite3.connect(path+constant.DATABASE,check_same_thread = False)
            self.cu= self.cx.cursor()
        
    #返回卡的id值
    def getCardId(self,cardName):
        self.cu.execute("select pid from cardinfo where name=?",(cardName,))
        result = self.cu.fetchone()
        return result[0]
    
    #返回卡的名字
    def getCardInfo(self,cardId):
        cardInfo = []
        self.cu.execute("select name,price,themeid from cardinfo where pid=?",(cardId,))
        result = self.cu.fetchone()
        cardInfo.append(result[0])
        self.cu.execute("select name from cardtheme where pid="+str(result[2])+"")
        cardInfo.append(self.cu.fetchone()[0])
        cardInfo.append(str(result[1]))
        return cardInfo
    
    #返回卡的id值
    def getCardThemeid(self,cardId):
        self.cu.execute("select themeid from cardinfo where pid=?",(int(cardId),))
        result = self.cu.fetchone()
        return result[0]


        
        