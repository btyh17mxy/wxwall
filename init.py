#!/usr/bin/env python
# -*-coding:utf-8-*-
from index.models import WXWall
import hashlib
w = WXWall()
w.account = 'btyh17mxy@gmail.com'
p = hashlib.md5('mushcode')
w.pwd = p.hexdigest()
w.user_id = 'mush'
w.save()
