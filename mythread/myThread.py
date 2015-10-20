# -*- coding: utf-8 -*-
import threading;    
from commonlib import constant;
import commonlib.commons as commons;
import wx;
class GetCodePicThread(threading.Thread):
    def __init__(self,window,myHttpRequest,userName,key=0):
        threading.Thread.__init__(self,)  
        self.window = window
        self.myHttpRequest =myHttpRequest
        self.userName = str(userName)
        self.key = key
        # self.windows = windows;

    # Overwrite run() method, put what you want the thread do here
    def run(self):
        if self.getCode() == 1:
            self.getCodePic()
        else:
            wx.CallAfter(self.window.showTheCodePic, 0)
        
    def stop(self):  
        self.thread_stop = True  
    # 获取相应登陆的一些数据
    def getCode(self,):
        if self.key==0:
            base_url = constant.ISNEEDCODEURL2
        else:
            base_url = constant.ISNEEDCODEURL3
        randomNum = commons.getRandomNum(4)
        base_url = base_url.replace('UIN', self.userName)
        base_url = base_url.replace('RANDOM','0.'+randomNum)
        response = self.myHttpRequest .get_response(base_url)
        page_content = response.read().decode('utf-8')
        print page_content
        self.isNeedCode = int(page_content[13:-2].split(',')[0][1:-1])
        self.code = ''
        if self.isNeedCode==0:
            constant.CODE = page_content[13:-2].split(',')[1][1:-1]
            constant.SESSION = str(page_content[13:-2].split(',')[3][1:-1])
        else:
            self.cap_cd = str(page_content[13:-2].split(',')[1][1:-1])
            self.loginCode = str(page_content[13:-2].split(',')[2][1:-1])
        return self.isNeedCode
    
    # 获取验证码图片
    def getCodePic(self):
        if self.key==0:
            base_url = constant.CODEPIC2
        else:
            base_url = constant.CODEPIC3
        randomNum = commons.getRandomNum(4)
        base_url = base_url.replace('UIN', self.userName)
        base_url = base_url.replace('RANDOM', '0.'+randomNum)
        base_url = base_url.replace('CD', self.cap_cd)
        page_content = self.myHttpRequest.get_response(base_url)
        wx.CallAfter(self.window.showTheCodePic, page_content.read())
