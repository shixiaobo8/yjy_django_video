#! /usr/bin/env python
# -*- coding:utf8 -*-
""" 
    阿里云sdk调用ecs:
    安装步骤请参见官方文档：https://develop.aliyun.com/sdk/python?spm=5176.doc25699.2.2.seCDuq
"""
import json
from ali_client import ali_client
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest


class ecs(object):
    
    def __init__(self):
        client = ali_client()
        clt = client.getClient()
        ecs_req = DescribeInstancesRequest.DescribeInstancesRequest()
        ecs_req.set_accept_format('json')
        self.ecses = clt.do_action(ecs_req)
    
    def getEcses(self):
        return self.ecses

if __name__ == '__main__':
	ECS = ecs()
	print ECS.getEcses()

    
