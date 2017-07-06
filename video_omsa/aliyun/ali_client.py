#! /usr/bin/env python
# -*- coding:utf8 -*-

"""
    阿里云sdk client 类
"""
from aliyunsdkcore import client

class ali_client(object):    
      
    def __init__(self):
        self.config = ('LTAIYj7b9Fm1rrH2','6rWkgQX8yiIDrOY70vcy19EUuHvjW2','cn-beijing')
        self.alt = client.AcsClient(self.config[0],self.config[1],self.config[2])
        
    def getClient(self):
        return self.alt
