# -*-coding:utf-8-*-

__author__ = "mush (btyh17mxy@gmail.com)"

import re
import json
from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render_to_response

from models import WXWall, Msg, FakeUser 
from libs.weixin import WeixinPublic, WeixinNeedLoginError
from wxwall.settings import DEBUG

if DEBUG:
    site = 'http://localhost:8000'
    media_uri = 'media/wxuserimg'
else:
    site = 'http://wxwall.mubuys.com/'
    media_uri = '/www/wxwall/media/wxuserimg'

def index(request, wxwall_id):
    
    weixin, wxwall = get_wx_by_id(wxwall_id)
    if weixin == None:
        return HttpResponse('您请求的链接不存在%s'%wxwall_id)


    return render_to_response('index.html',{})

#@require_POST
#@csrf_exempt
def get_new_msg(request, wxwall_id):
    data = {'msg':[]}
    last_msg_id = 0
    def msg_key(s): 
       return s['id'] 

    g = re.search('[a-zA-z]*[^/]', wxwall_id)
    wxwall_id =  g.group(0)

    weixin, wxwall = get_wx_by_id(wxwall_id)
    if weixin == None:
        return HttpResponse('您请求的链接不存在%s'%wxwall_id)
    last_msg_id = wxwall.last_msg_id

    #从微信获取消息列表
    try :
        msgs = json.loads(weixin.get_msg_list())
    except WeixinNeedLoginError, e:
        weixin, wxwall = get_wx_by_id(wxwall_id, relogin = True)
        msgs = json.loads(weixin.get_msg_list())

    msg_items = msgs['msg_item'] 
    msg_items = sorted(msg_items, key = msg_key, reverse = False)
    for msg_item in msg_items:
        if msg_item['type'] == 1 and msg_item['id'] > last_msg_id:
            #weixin.get_user_icon(fakeid = int(msg_item['fakeid']), uri = 'media/wxuserimg')
            fu = get_user(weixin,wxwall, int(msg_item['fakeid']),msg_item['nick_name'])
            item = {
                    'nick_name':msg_item['nick_name'],
                    'content':msg_item['content'],
                    'msg_type':1,
                    'msg_id':msg_item['id'],
                    'icon':fu.icon
                    }
            data['msg'].append(item)
            wxwall.last_msg_id = msg_item['id']
            wxwall.msg_count = wxwall.msg_count + 1
            m = Msg()
            m.wxwall = wxwall
            m.msg_id = msg_item['id']
            m.fake_id = fu
            m.msg_type = 1
            m.date_time = msg_item['date_time']
            m.content = msg_item['content']
            m.save()

    wxwall.save()

    return render_to_response('msg_item.html',data)

#@require_POST
#@csrf_exempt
def get_msg_count(request, wxwall_id):
    
    g = re.search('[a-zA-z]*[^/]', wxwall_id)
    wxwall_id =  g.group(0)

    weixin, wxwall = get_wx_by_id(wxwall_id)
    if weixin == None:
        return HttpResponse('您请求的链接不存在')

    return HttpResponse(wxwall.msg_count)

def get_user(weixin, wxwall, fakeid, nick_name):
    try:
        fu = FakeUser.objects.get(fake_id = fakeid)
    except FakeUser.DoesNotExist, e:
        weixin.get_user_icon(fakeid = int(fakeid), uri = media_uri)
        fu = FakeUser()
        fu.fake_id = fakeid
        fu.nick_name = nick_name
        fu.icon = '%s/media/wxuserimg/%s.jpg'%(site,fakeid)
        fu.save()
    return fu



def get_wx_by_id(wxwall_id, relogin = False):
    #获取微信对象
    try: 
        wxwall = WXWall.objects.get(user_id = wxwall_id)
    except WXWall.DoesNotExist, e:
        return None, None 

    #登陆微信
    if relogin :
        weixin = WeixinPublic(wxwall.account, wxwall.pwd, ifencodepwd = True)
    else :
        weixin = WeixinPublic(wxwall.account, wxwall.pwd, wxwall.token, wxwall.cookies,ifencodepwd = True)
    #保存微信登陆状态
    wxwall.token = weixin.token
    wxwall.cookies = weixin.wx_cookies
    wxwall.save()
    return weixin, wxwall
