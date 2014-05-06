#!/usr/bin/env python
# -*-coding:utf-8-*-

__version__ = '0.1'
__author__ = 'Mush (btyh17mxy@gmail.com)'

from django.db import models

class WXWall(models.Model):
    user_id = models.CharField(max_length = 24, unique = True)
    account = models.CharField(max_length = 60, unique = True)
    pwd = models.CharField(max_length = 120)
    token = models.IntegerField(null = True,blank = True)
    cookies = models.CharField(max_length = 500,null = True, blank = True)
    last_msg_id = models.IntegerField(default = 0)
    msg_count = models.IntegerField(default = 0)

class Msg(models.Model):
    wxwall = models.ForeignKey('WXWall')
    msg_id = models.IntegerField(unique = True)
    msg_type = models.IntegerField()
    fake_id = models.ForeignKey('FakeUser')
    date_time = models.IntegerField()
    content = models.CharField(max_length = 1000)


class FakeUser(models.Model):
    fake_id = models.IntegerField(primary_key = True)
    icon = models.CharField(max_length = 120, blank = True)
    nick_name = models.CharField(max_length = 120)
    pup_date = models.DateTimeField(auto_now = True)
    male = models.BooleanField(default = True)
    location = models.CharField(max_length = 140, default = 'unknown')

class MsgCount(models.Model):
    wxwall = models.ForeignKey('WXWall')
    msg_count = models.IntegerField()
