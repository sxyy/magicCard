# -*- coding: utf-8 -*-
import urllib
import urllib2
import cookielib

class MyHttpRequest(object):
    def __init__(self):
        self.operate = ''  
        self.formhash = '' 
        
        self.cj = cookielib.CookieJar()
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(self.cj))
        urllib2.install_opener(self.opener)
    

    def get_response(self, url, data = None,customCookies=None):
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'

        #headers = { 'User-Agent' :user_agent,'Accept-Encoding':'*'}

        if data is not None:
            req = urllib2.Request(url, urllib.urlencode(data))
        else:
            req = urllib2.Request(url)
        req.add_header('User-Agent', user_agent)
        req.add_header('Accept-Encoding', '*')
        if customCookies is not None:
            req.add_header("Cookie", customCookies)
        response = self.opener.open(req)
        return response

    
