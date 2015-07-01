# -*- coding: utf-8 -*-
'''
Created on 2015��5��28��

@author: cvtpc
'''
import random



def getRandomNum(num):
    strNum = '';
    for i in range(num):
        strNum += str(random.randint(0,9));
    return strNum; 
        