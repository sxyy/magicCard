# -*- coding: utf-8 -*-
'''
Created on 2015��5��28��

@author: cvtpc
'''
import random
import Tea
import constant,logging
import socket
import struct
import time
import win32api

from bs4 import BeautifulSoup

TimeServer = 'cn.pool.ntp.org' #国家授时中心ip
Port = 123

def getRandomNum(num):
    strNum = ''
    for i in range(num):
        strNum += str(random.randint(0,9))
    return strNum

#获取对应的url
def getUrl(url,myHttpRequest):
    skey = ''
    for ck in myHttpRequest.cj:
            if ck.name=='skey':
                skey = ck.value
    base_url = url
    base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
    return base_url

def drawCard(myhttpRequest,types,fetchnum):
    base_url = getUrl(constant.DRAWCARDURL,myhttpRequest)
    post_data ={
        'type':types,
        'fetchnum':fetchnum,
    }
    print myhttpRequest.get_response(base_url,post_data).read().decode('utf-8')

def buyCard(myhttpRequest,card_id,card_theme):
    '''
    购买卡片
    :param myhttpRequest:
    :param card_id:
    :param card_theme:
    :return:
    '''
    base_url = getUrl(constant.BUYCARDURL,myhttpRequest)
    post_data ={
        'card_id':card_id,
        'theme_id':card_theme,
    }
    print myhttpRequest.get_response(base_url,post_data).read().decode('utf-8')

def sellCard(myhttpRequest,account,slot_no,cardid,types):
    '''
    出售卡片
    :param myhttpRequest:
    :param account:
    :param slot_no:
    :param cardid:
    :param types:
    :return:
    '''
    base_url = getUrl(constant.SALECARD,myhttpRequest)
    post_data ={
        'slot_no':slot_no,
        'cardid':cardid,
        'type':types,
        'uin':account
    }
    print myhttpRequest.get_response(base_url,post_data).read().decode('utf-8')

def cardExchange(myhttpReuqest,account,src,dest,types):
    '''
    卡片交换
    :param myhttpReuqest:
    :param account:
    :param src:
    :param dest:
    :param types:
    :return:
    '''
    base_url = getUrl(constant.CARDINPUTSTOREBOX,myhttpReuqest)
    post_data ={
        'dest':dest,
        'src':src,
        'type':types,
        'uin':account
    }
    logging.info(myhttpReuqest.get_response(base_url,post_data).read().decode('utf-8'))

def completeMission(myhttpRequest,curmiss,tid=None):
    '''
    完成任务
    :param myhttpRequest:
    :param curmiss:
    :return:
    '''
    base_url = getUrl(constant.MAGICCOMMLETEMISSION,myhttpRequest)
    if tid is None:
        post_data = {
            'curmiss':curmiss
        }
    else:
        post_data = {
            'curmiss':curmiss,
            'tid':tid
        }

    pagecontent = myhttpRequest.get_response(base_url,post_data).read().decode('utf-8')
    logging.info(pagecontent)
    return pagecontent

def magicCardGuide(myhttpRequest,account,mid,stp):
    '''
    引导
    :param myhttpRequest:
    :return:
    '''
    base_url = getUrl(constant.MAGICCARDGUIDE,myhttpRequest)
    post_data = {
        'uin':account,
        'mid':mid,
        'stp':stp
    }
    myhttpRequest.get_response(base_url,post_data)



def registerMagic(myhttpRequest):
    '''
    注册魔卡
    :param myhttpRequest:
    :return:
    '''
    base_url = getUrl(constant.REGISTERMAGICCARD,myhttpRequest)
    page_content = myhttpRequest.get_response(base_url).read().decode('utf-8')
    logging.info(page_content)
#获取魔卡信息
def getMagicInfo(myhttpRequest,account):
    skey = ''
    for ck in myhttpRequest.cj:
            if ck.name=='skey':
                skey = ck.value
    postData = {
                    'code':'',
                    'uin':account

    }
    base_url = constant.CARDLOGINURL
    base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
    page_content = myhttpRequest.get_response(base_url,postData).read().decode('utf-8')
    return   page_content


def getStoveBoxInfo(page_content):
    '''
    获取炉子的信息
    :param page_content:
    :return:
    '''
    soup = BeautifulSoup(page_content)
    slove_num = int(soup.stovebox['cur'])-1
    cardcomplete = [0] * slove_num
    childlist = soup.stovebox.children
    for item in childlist:
        if item != u'\n':
            soup2 = BeautifulSoup(str(item))
            if int(soup2.card['slot'])!=6:
                '''卡片的完成情况
                '''
                if int(soup2.card['flag']) == 2:
                    cardcomplete[int(soup2.card['slot'])] = 1
                else:
                    cardcomplete[int(soup2.card['slot'])] = 0
            else:

                if int(soup2.card['flag']) == 2:
                    cardcomplete[-1] = 1
                else:
                    cardcomplete[-1] = 0
    return cardcomplete

def fanpai(myhttpRequest):
    base_url = getUrl(constant.FANPAIURL,myhttpRequest)
    postData = {
                'type':1,
    }
    page_content = myhttpRequest.get_response(base_url,postData).read().decode('utf-8')
    print u'翻牌结果',page_content
    logging.info(u'翻牌结果'+page_content)


def get_type_info(flag,magicCardInfo):
    '''
    获取卡片信息
    :param flag:
    :param magicCardInfo:
    :return:
    '''
    childlist = []
    store_box = []
    exchange_box = []
    soup = BeautifulSoup(magicCardInfo)
    if flag==constant.EXCHANGEBOX:
        childlist = soup.changebox.children
        constant.EXCHANGEBOXNUM = int(soup.changebox['cur'])
        exchange_box = [0]*constant.EXCHANGEBOXNUM
    elif flag==constant.STOREBOX:
        childlist = soup.storebox.children
        constant.STOREBOXNUM = int(soup.storebox['cur'])
        store_box = [0]*constant.STOREBOXNUM

    for item in childlist:
        if item != u'\n':
            soup2 = BeautifulSoup(str(item))
            pid = int(soup2.card['id'])

            if flag==constant.EXCHANGEBOX:
                if pid==-1:
                    exchange_box[int(soup2.card['slot'])] = 0
                else:
                    exchange_box[int(soup2.card['slot'])] = pid
            elif flag==constant.STOREBOX:
                store_box[int(soup2.card['slot'])] = pid

    if flag==constant.EXCHANGEBOX:
        return exchange_box
    else:
        return store_box


def getCode(myHttpRequest,username):
    base_url = constant.ISNEEDCODEURL2
    randomNum = getRandomNum(4)
    base_url = base_url.replace('UIN', str(username))
    base_url = base_url.replace('RANDOM','0.'+randomNum)
    response = myHttpRequest.get_response(base_url)
    page_content = response.read().decode('utf-8')
    print page_content
    isNeedCode = int(page_content[13:-2].split(',')[0][1:-1])
    code = ''
    if isNeedCode==0:
        constant.CODE = page_content[13:-2].split(',')[1][1:-1]
        constant.SESSION = str(page_content[13:-2].split(',')[3][1:-1])
    else:
        cap_cd = str(page_content[13:-2].split(',')[1][1:-1])
        loginCode = str(page_content[13:-2].split(',')[2][1:-1])
    return isNeedCode


def getTime():
    TIME_1970 = 2208988800L
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    socket.timeout(5)
    data = '\x1b' + 47 * '\0'
    client.sendto(data, (TimeServer, Port))
    data, address = client.recvfrom(1024)
    data_result = struct.unpack('!12I', data)[10]
    data_result -= TIME_1970
    return data_result

def setSystemTime():
    tm_year, tm_mon, tm_mday, tm_hour, tm_min, tm_sec, tm_wday, tm_yday, tm_isdst = time.gmtime(getTime())
    win32api.SetSystemTime(tm_year, tm_mon, tm_wday, tm_mday, tm_hour, tm_min, tm_sec, 0)

import re

def getPrizeInfo(page_content):
    result = ''
    card_list =  re.findall('(\d+)_(.*?)_(\d+)',page_content,re.S)
    for list_item in card_list:
        if list_item[0] in constant.GIFTDICT:
            result += constant.GIFTDICT[list_item[0]]+'*'+list_item[2]
        elif list_item[0] =='48':
            if list_item[1]=='19':
                result+=u'积分'+'*'+list_item[2]
            elif list_item[1]=='14':
                result+= u'7天租铺卡'+'*'+list_item[2]
            elif list_item[1]=='8':
                result+= u'3天累计卡'+'*'+list_item[2]
            elif list_item[1]=='17':
                result+= u'3天经验卡'+'*'+list_item[2]
            elif list_item[1]=='18':
                result+= u'7天经验卡'+'*'+list_item[2]
            else:
                result+= u'未知',list_item
        result+=','
    return result

