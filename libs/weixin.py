#!/usr/bin/env python
# coding: UTF-8
import urllib2,cookielib
import json
import hashlib
from urllib import URLopener
from httplib2 import Http
import httplib2
from urllib import urlencode
import re
import random
#########################################################
import urllib2,cookielib,re
import json
import hashlib
from urllib import URLopener
#########################################################
import logging
DEBUG_LEVEL = logging.DEBUG
try:
    import colorizing_stream_handler
    root = logging.getLogger()
    root.setLevel(DEBUG_LEVEL)
    root.addHandler(colorizing_stream_handler.ColorizingStreamHandler())
except Exception, e:
    print 'loger initialize error'
    print e


'''
httplib2中修改这一行
content = zlib.decompress(content, -zlib.MAX_WBITS)

'''

'''base exception class.
'''
class WeixinPublicError(Exception):
    pass



'''raise when cookies expired.
'''
class WeixinNeedLoginError(WeixinPublicError):
    pass



'''rasie when unenable to login.
'''
class WeixinLoginError(WeixinPublicError):
    pass



class WeixinPublic(object):
    
    def __init__(self, account, pwd, token = None, cookies = None, ifencodepwd = False):
        self.account = account
        if ifencodepwd:
            self.pwd = pwd 
        else:
            self.pwd = hashlib.md5(pwd).hexdigest()
        self.wx_cookies = cookies
        self.lastmsgid = 0 
        self.token = token 
        self.base_headers =  {
                'Accept':'application/json, text/javascript, */*; q=0.01',
                'Accept-Encoding':'gzip,deflate,sdch',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
                'DNT':'1',
                'Host':'mp.weixin.qq.com',
                'Origin':'https://mp.weixin.qq.com',
                'Referer':'https://mp.weixin.qq.com/',
                'x-requested-with':'XMLHttpRequest',
                #'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like '
                #    +'Gecko) Chrome/33.0.1750.152 Safari/537.36',
                }

        if self.token == None or self.wx_cookies == None:
            self.token = ''
            self.wx_cookies = ''
            self.login_request()

    def get_user_icon_http(self, fakeid = 1155750780, uri = ''):
        http = Http()
        user_icon_url = "https://mp.weixin.qq.com/misc/getheadimg"
        user_icon_payload = {
                'token':self.token,
                'fakeid':fakeid,
                }
        user_icon_headers = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip,deflate,sdch',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Cache-Control':'no-cache',
                'Connection':'keep-alive',
                'cookie':self.wx_cookies,
                'DNT':'1',
                'Host':'mp.weixin.qq.com',
                'Pragma':'no-cache',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36 ',
                }

        r, s = http.request(user_icon_url, 'GET', body = urlencode(user_icon_payload), headers = user_icon_headers)

    def get_user_icon(self, fakeid = 1155750780, uri = ''):
        user_icon_url = "https://mp.weixin.qq.com/misc/getheadimg"
        user_icon_payload = {
                'token':self.token,
                'fakeid':fakeid,
                }
        user_icon_headers = {
                'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding':'gzip,deflate,sdch',
                'Accept-Language':'zh-CN,zh;q=0.8',
                'Cache-Control':'no-cache',
                'Connection':'keep-alive',
                'Cookie':self.wx_cookies,
                'DNT':'1',
                'Host':'mp.weixin.qq.com',
                'Pragma':'no-cache',
                'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.152 Safari/537.36 ',
                }

        cookies = cookielib.LWPCookieJar()
        cookie_support= urllib2.HTTPCookieProcessor(cookies)
        
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        
        req = urllib2.Request(url = user_icon_url, data = urlencode(user_icon_payload))
        
        req.add_header('cookie',self.wx_cookies)
        req.add_header("x-requested-with", "XMLHttpRequest")
        req.add_header("referer", "https://mp.weixin.qq.com/cgi-bin/message?t=message/list&count=20&day=7&token=%s&lang=zh_CN"%self.token)
        respond = opener.open(req).read()
        
        if uri == '':
            f = open('%d.jpg'%(fakeid),'wb+')
        else:
            f = open('%s/%d.jpg'%(uri, fakeid),'wb+')
        f.write(respond)
        f.close()

    def get_msg_list(self):
        http = Http()

        msg_list_url = "https://mp.weixin.qq.com/cgi-bin/message?t=message/list&token=%s&count=20&day=7"%self.token
        msg_list_payload = {
                't':'message/list',
                'token':self.token,
                'count':20,
                'day':7
                }
        msg_list_headers = self.base_headers
        msg_list_headers['Connection'] = 'keep-alive'
        msg_list_headers['Accept']='text/html, */*; q=0.01'
        msg_list_headers['Cookie'] = self.wx_cookies
        
        r, c = http.request(msg_list_url, 'GET', body = urlencode(msg_list_payload), headers = msg_list_headers)
        c = "".join(c.split())
        s =  re.search(r'list:\((.*)\).msg_item', c)
        if s == None:
            raise WeixinNeedLoginError('need re-login')
        else:
            return s.group(1)
        
    def get_new_msg_num_request(self):
        new_msg_url = "https://mp.weixin.qq.com/cgi-bin/getnewmsgnum"
        new_msg_payload = {
                'token':self.token,
                'lang':'zh_CN',
                'random':random.random(),
                'f':'json',
                'ajax':1,
                't':'ajax-getmsgnum',
                'lastmsgid':self.lastmsgid,
                }
        cookies = cookielib.LWPCookieJar()
        cookie_support= urllib2.HTTPCookieProcessor(cookies)
        
        # bulid a new opener
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        
        req = urllib2.Request(url = new_msg_url, data = urlencode(new_msg_payload))
        
        req.add_header('cookie',self.wx_cookies)
        req.add_header("x-requested-with", "XMLHttpRequest")
        req.add_header("referer", "https://mp.weixin.qq.com/cgi-bin/message?t=message/list&count=20&day=7&token=%s&lang=zh_CN"%self.token)
        respond = opener.open(req).read()
        
        
    '''login to weichat, get token and cookies.

    Raise:
        WeixinLoginError, when can not get token from respond.
    '''
    def login_request(self):
        cookies = cookielib.LWPCookieJar()
        cookie_support= urllib2.HTTPCookieProcessor(cookies)
        
        opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
        urllib2.install_opener(opener)
        
        req = urllib2.Request(url = 'https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN',
                              data = ('username=' + self.account + 
                              '&pwd=' + self.pwd + 
                              '&imgcode='
                              '&f=json'))
        
        req.add_header("x-requested-with", "XMLHttpRequest")
        req.add_header("referer", "https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN")
        respond = opener.open(req).read()
        logging.debug(respond)

        s = re.search(r'token=(\d+)', respond)
        
        if not s:
            logging.error('Login Error')
            raise WeixinLoginError("Login error.")
        
        self.token = s.group(1)
        
        for cookie in cookies:
            self.wx_cookies += cookie.name + '=' + cookie.value + ';'
        logging.debug('wx_cookies:\t%s'%self.wx_cookies)
        logging.debug('token:\t%s'%self.token)

    '''登陆公众平台
    '''
    def login_http(self):
        http = Http()

        login_url = 'https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN'
        login_payload = {
                'username':self.account,
                'pwd':self.pwd,
                'imgcode':'',
                'f':'json',
                }
        login_headers = self.base_headers
        login_headers['Referer'] = 'https://mp.weixin.qq.com/'

        r, c = http.request(login_url, 'POST', urlencode(login_payload),  headers = login_headers)

        #获取Token
        s = re.search(r'token=(\d+)', c)
        if not s:
            raise Exception("Login error.")
        self.token = int(s.group(1))
        
        #获取Cookies
        self.wx_cookies = self.wx_cookies + r['set-cookie']

    def home(self):
        http = Http()

        home_url = 'https://mp.weixin.qq.com/cgi-bin/home'
        home_payload = {
                't':'home/index',
                'lang':'zh_CN',
                'token':self.token,
                }
        home_headers = self.base_headers
        home_headers['Cookie'] = self.wx_cookies
        home_headers['Referer'] = 'https://mp.weixin.qq.com/'

        r, c = http.request(home_url, 'GET', urlencode(home_payload), headers = home_headers)

    def get_new_msg_num(self):
        http = Http()

        new_msg_url = "https://mp.weixin.qq.com/cgi-bin/getnewmsgnum"
        new_msg_payload = {
                'token':self.token,
                'lang':'zh_CN',
                'random':random.random(),
                'f':'json',
                'ajax':1,
                't':'ajax-getmsgnum',
                'lastmsgid':self.lastmsgid,
                }
        new_msg_headers = self.base_headers
        new_msg_headers['Connection'] = 'keep-alive'
        new_msg_headers['Accept']='text/html, */*; q=0.01'
        new_msg_headers['Referer'] = 'https://mp.weixin.qq.com/cgi-bin/message?t=message/list&count=20&day=7&token=%s&lang=zh_CN'%self.token
        new_msg_headers['Cookie'] = self.wx_cookies

        r, c = http.request(new_msg_url, 'POST', urlencode(new_msg_payload), headers = new_msg_headers)
        
if __name__ == '__main__':
    weixin = WeixinPublic("btyh17mxy@gmail.com","mushcode")
    #weixin.get_new_msg_num()
    weixin.get_user_icon_http()
