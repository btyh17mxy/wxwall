#!/usr/bin/env python
# coding: UTF-8
import json
import hashlib
import re
import random
import json
import requests
import logging
DEBUG_LEVEL = logging.DEBUG
try:
    import colorizing_stream_handler
    root = logging.getLogger()
    root.setLevel(DEBUG_LEVEL)
    root.addHandler(colorizing_stream_handler.ColorizingStreamHandler())
except Exception, e:
    print 'can not import colorizing_stream_handler, using logging.StreamHandler()'
    root = logging.getLogger()
    root.setLevel(DEBUG_LEVEL)
    root.addHandler(logging.StreamHandler())



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
        self.wx_cookies = cookies
        self.token = token 

        if ifencodepwd:
            self.pwd = pwd 
        else:
            self.pwd = hashlib.md5(pwd).hexdigest()

        if self.token == None or self.wx_cookies == None:
            self.token = ''
            self.wx_cookies = ''
            self.login()

    '''login to weichat, get token and cookies.

    Raise:
        WeixinLoginError, when can not get token from respond.
    '''
    def login(self):
        url = 'https://mp.weixin.qq.com/cgi-bin/login?lang=zh_CN'
        payload = {
                'username' : self.account,
                'imgcode' : '',
                'f' : 'json',
                'pwd' : self.pwd,
                }
        headers = {
                'x-requested-with' : 'XMLHttpRequest',
                'referer' : 'https://mp.weixin.qq.com/cgi-bin/loginpage?t=wxm2-login&lang=zh_CN',
                }

        r = requests.post(url, data = payload, headers = headers)
        
        logging.info('------login------')
        logging.debug("respond:\t%s"%r.text)

        s = re.search(r'token=(\d+)', r.text)
        if not s:
            logging.error('Login Error!!!')
            raise WeixinLoginError("Login error.")
        self.token = int(s.group(1))
        logging.debug('token:\t%d'%self.token)
        
        self.wx_cookies = ''
        for cookie in r.cookies:
            self.wx_cookies += cookie.name + '=' + cookie.value + ';'
        logging.debug('cookies:\t%s'%self.wx_cookies)
        logging.info('------end login------')

    '''get message list.

    Get a list of message after date_time or lastmsgid.

    Args:
        date_time
        lastmsgid

    Raise :
        WeixinNeedLoginError, when need re-login.

    Returns :
        messages in dict.
    '''
    def get_msg_list(self, date_time = 0, lastmsgid = 0):
        logging.info('------get_msg_list------')
        url = 'https://mp.weixin.qq.com/cgi-bin/message'
        payload = {
                't':'message/list',
                'token':self.token,
                'count':20,
                'day':7,
                }
        headers = {
                'Referer':'https://mp.weixin.qq.com/cgi-bin/message',
                'cookie' : self.wx_cookies,
                }
        msg_list = []
        total_count = -1

        while True:
            r = requests.get(url, params = payload, headers = headers)

            c = "".join(r.text.split())
            s =  re.search(r'list:\((.*)\).msg_item', c)
            if s == None:
                logging.error('need re-login')
                raise WeixinNeedLoginError('need re-login')
            else:
                s =  s.group(1)

            msg_list += json.loads(s)['msg_item']
            logging.debug('msg_list_len:%d'%len(msg_list))

            if total_count < 0:
                total_count =  re.search(r'total_count:(.*),la', c)
                total_count = int(total_count.group(1))
                logging.debug('total_count:\t%d'%total_count)
                if (len(msg_list) == 0):
                    return msg_list
                else:
                    frommsgid = msg_list[0]['id']

            msg_list = sorted(msg_list, key = lambda i: i['id'] , reverse = False)
            i = 0
            while i < len(msg_list):
                if not date_time < msg_list[i]['date_time'] or not lastmsgid < msg_list[i]['id']:
                    del msg_list[i:len(msg_list)-1]
                    return msg_list
                    
                i+=1
            if total_count == len(msg_list):
                break

            payload = {
                        't':'message/list',
                        'action':'',
                        'keyword':'',
                        'frommsgid':frommsgid,
                        'offset':20,
                        'count':20,
                        'day':7,
                        'filterivrmsg':1,
                        'token':self.token,
                        'lang':'zh_CN',
                    }

        return msg_list
 
    '''get user icon.

    Args:
        fakeid.
        uri, local uri to store this img.
    '''
    def get_user_icon(self, fakeid = 1155750780, uri = ''):
        logging.info('------get_user_icon------')
        url = "https://mp.weixin.qq.com/misc/getheadimg"
        payload = {
                'token':self.token,
                'fakeid':fakeid,
                }
        headers = {
                'Cookie':self.wx_cookies,
                }
        
        r = requests.get(url, params = payload, headers = headers)
        respond_headers = r.headers 
        if 'content-type' in respond_headers.keys() and not respond_headers['content-type'] == 'image/jpeg':
            logging.error('download user icon error, need re-login.')
            raise WeixinNeedLoginError('download user icon error, need re-login.')

        if uri == '':
            f = open('%d.jpg'%(fakeid),'wb+')
        else:
            f = open('%s/%d.jpg'%(uri, fakeid),'wb+')
        f.write(r.content)
        f.close()
        logging.info('------end get_user_icon------')

    '''get user info.

    Args:
        fakeid

    Raise:
        WeixinPublicError, when can not get user info

    Returns:
        userinfo in dict.
    '''
    def get_user_info(self, fakeid = 1155750780):
        logging.info('------get_user_info------')
        url = 'https://mp.weixin.qq.com/cgi-bin/getcontactinfo'
        payload = {
                'token':self.token,
                'lang':'zh_CN',
                'random':random.random(),
                'f':'json',
                'ajax':'1',
                't':'ajax-getcontactinfo',
                'fakeid':fakeid,
                }
        headers = {
                'cookie':self.wx_cookies,
                'Referer':'https://mp.weixin.qq.com/cgi-bin/contactmanage?t=user/index&token=%d&lang=zh_CN'%self.token,
                'X-Requested-With':'XMLHttpRequest',
                }

        r = requests.post(url, data = payload, headers = headers)
        logging.info(r.text)
        r = json.loads(r.text)
        if not r['base_resp']['err_msg'] == 'ok':
            logging.error('get_user_info error !!!\t%s'%r['base_resp']['err_msg'])
            raise WeixinPublicError(r['base_resp']['err_msg'] )

        userinfo = r['contact_info']
        logging.debug(userinfo)
        logging.info('------end get_user_info------')
        return userinfo

    '''push msg to all users.

    Args:
        content, this content of message.

    Raise:
        WeixinPublicError

    Returns:
        True if success.
    '''
    #TODO:提供发送图片和向指定分组推送消息的选项
    def msg_push(self, content):
        url = 'https://mp.weixin.qq.com/cgi-bin/masssend'
        payload = {
            'type':'1',
            'content':content,
            'sex':'0',
            'groupid':'-1',
            'synctxweibo':'0',
            'synctxnews':'0',
            'country':'',
            'province':'',
            'city':'',
            'imgcode':'',
            'token':self.token,
            'lang':'zh_CN',
            'random':random.random(),
            'f':'json',
            'ajax':'1',
            't':'ajax-response',
            }
        headers = {
                'cookie':self.wx_cookies,
                'Referer':'https://mp.weixin.qq.com/cgi-bin/contactmanage?t=user/index&token=%d&lang=zh_CN'%self.token,
                'X-Requested-With':'XMLHttpRequest',
                    }

        r = requests.post(url, data = payload, headers = headers)
        logging.debug(r.text)
        r = json.loads(r.text)
        if (r['msg'] == 'ok'):
            return True
        else:
            logging.error(r['msg'])
            raise WeixinPublicError(r['msg'])

    '''send a message to reply a specific message.

    Args:
        content.
        tofakeid, to which user.
        quickreplyid, reply which message send by this user.

    Raise:
        WeixinPublicError

    Returns:
        True if success.
    '''
    def msg_send(self, content, tofakeid = 1155750780, quickreplyid = 200229775):
        url = 'https://mp.weixin.qq.com/cgi-bin/singlesend'
        payload = {
                'mask':'false',
                'tofakeid':tofakeid,
                'imgcode':'',
                'type':1,
                'content':content,
                'quickreplyid':quickreplyid,
                'token':self.token,
                'lang':'zh_CN',
                'random':random.random(),
                'f':'json',
                'ajax':1,
                't':'ajax-response',
                }
        headers = {
                'cookie':self.wx_cookies,
                'Referer':'https://mp.weixin.qq.com/cgi-bin/contactmanage?t=user/index&token=%d&lang=zh_CN'%self.token,
                'X-Requested-With':'XMLHttpRequest',
                    }

        r = requests.post(url, data = payload, headers = headers)
        logging.debug(r.text)
        r = json.loads(r.text)
        if (r['msg'] == 'ok'):
            return True
        else:
            logging.error(r['msg'])
            raise WeixinPublicError(r['msg'])

if __name__ == '__main__':
    weixin = WeixinPublic("btyh17mxy@gmail.com","4f65517f1bd05369567631bb2d34553e", ifencodepwd = True)
    print weixin.get_msg_list(lastmsgid = 200229775)
    #weixin.get_user_icon()
    #weixin.get_user_info(508305040)
    #weixin.msg_push("推送消息测试")
    #weixin.msg_send("测试")
    #for msg in weixin.get_msg():
    #    print msg
