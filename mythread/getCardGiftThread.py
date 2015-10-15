# -*- coding: utf-8 -*-
import threading
from commonlib import constant,myhttp
import wx,re
import logging,time
class GetCardThread(threading.Thread):
    def __init__(self,window,account_dict):
        threading.Thread.__init__(self,)
        self.window = window
        self.account_dict =account_dict
        self.account_sid_dict = {}


     # Overwrite run() method, put what you want the thread do here
    def run(self):


        for key,value in self.account_dict.items():

            self.get_sid(key,value)
            if self.account_sid_dict[key]=='-1':
               wx.CallAfter(self.window.updateLog,u'无法获取到用户'+key+u'的sid')
            else:
                myhttps = myhttp.MyHttpRequest()
                base_url = constant.GETCARD
                post_data = {
                    'sid':self.account_sid_dict[key],
                    'loginuin':key,
                    'actid':3006,
                    'appid':200,
                    'packid':612
                }
                pagecontent = myhttps.get_response(base_url,post_data).read().decode('utf-8')
                print pagecontent



    def stop(self):
        self.thread_stop = True

    # 获取相应登陆的一些数据
    def get_sid(self,key,value):
        myHttpRequest = myhttp.MyHttpRequest()
        base_url = constant.MAINPAGE
        myHttpRequest.get_response(base_url)
        base_url = constant.GETSID
        post_data = {
            'qq':key,
            'pwd':value,
            'sidtype':'1',
            'nopre':'0',
            'loginTitle':u'手机腾讯网'.encode('utf-8'),
            'q_from':'',
            'bid':'0',
            'loginType':'3',
            'loginsubmit':u'登录'.encode('utf-8'),
            "login_url":"http://pt.3g.qq.com/s?aid=nLogin&sid=AfYLxNl-zrRwzRvmKiZc5aV8"
        }
        sid = []
        i = 0
        while len(sid)==0:
            if i>50:
                break
            page_content = myHttpRequest.get_response(base_url,post_data).read().decode('utf-8')
            if u'验证' in page_content:
                print page_content
                image_code  = re.findall('img src=\"(.*?)\" alt=',page_content,re.S)
                page_content2 = myHttpRequest.get_response(image_code[0]).read()
                mysid = re.findall('name=\"sid\" value=\"(.*?)\"/>',page_content,re.S)
                r = re.findall('name=\"r\" value=\"(.*?)\"/>',page_content,re.S)
                extend = re.findall('name=\"extend\" value=\"(.*?)\"/>',page_content,re.S)
                r_sid = re.findall('name=\"r_sid\" value=\"(.*?)\"/>',page_content,re.S)
                rip = re.findall('name=\"rip\" value=\"(.*?)\"/>',page_content,re.S)
                login_url =  re.findall('name=\"login_url\" value=\"(.*?)\"/>',page_content,re.S)
                hexpwd =  re.findall('name=\"hexpwd\" value=\"(.*?)\"/>',page_content,re.S)
                wx.CallAfter(self.window.show_image_code,page_content2)
                print image_code
                while constant.NEWCODE=='':
                    time.sleep(1)
                print constant.NEWCODE
                my_post_data = {
                    'qq':str(key),
                    'u_token':str(key),
                    'hexpwd':hexpwd[0],
                    'hexp':'true',
                    'sid':mysid[0],
                    'auto':'0',
                    'loginTitle':u'手机腾讯网'.encode('utf-8'),
                    'qfrom':'',
                    'q_status':'20',
                    'r':r[0],
                    'loginType':'3',
                    'bid_code':'qqchatLogin',
                    'extend':extend[0],
                    'r_sid':r_sid[0],
                    'rip':rip[0],
                    'modifySKey':'0',
                    'bid':'0',
                    'login_url':login_url[0],
                    'verify':constant.NEWCODE,
                    'submitlogin':u'马上登录'.encode('utf-8')
                }
                page_content = myHttpRequest.get_response(constant.GETSID,my_post_data).read().decode('utf-8')
                print page_content
                constant.NEWCODE = ''
            sid = re.findall('ontimer=\"http://info\.3g\.qq\.com/g/s\?sid=(.*?)&amp',page_content,re.S)
            logging.info('sid'+'.'.join(sid))
            print sid
            i += 1
        try:
            self.account_sid_dict[key] =  sid[0]
        except IndexError:
            self.account_sid_dict[key] = '-1'