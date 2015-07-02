# -*- coding: utf-8 -*-
'''
Created on 2015��5��28��

@author: cvtpc
'''
import random
import Tea



def getRandomNum(num):
    strNum = '';
    for i in range(num):
        strNum += str(random.randint(0,9));
    return strNum;

#获取对应的url
def getUrl(url,myHttpRequest):
    skey = ''
    for ck in myHttpRequest.cj:
            if ck.name=='skey':
                skey = ck.value
    base_url = url
    base_url = base_url.replace('GTK', str(Tea.getGTK(skey)))
    return base_url


        