#! /usr/bin/env python
# -*- coding:utf8 -*-
""" 
    阿里云sdk调用oss:
    安装步骤请参见官方文档：https://develop.aliyun.com/sdk/python?spm=5176.doc25699.2.2.seCDuq
"""
from __future__ import print_function
import oss2
import sys
from oss2 import auth

class oss():
    
    def __init__(self):
        self.endpoint = 'oss-cn-beijing.aliyuncs.com'
        self.auth = auth('LTAIYj7b9Fm1rrH2','6rWkgQX8yiIDrOY70vcy19EUuHvjW2');
        self.service = oss2.Service(auth,self.endpoint)
        
        
    def getBuckets(self):
        return oss2.BucketIterator(self.service)
        #return self.service.list_buckets()
    
    def newBucket(self,bucketname='',endpoint='oss-cn-beijing.aliyuncs.com'):
        # 在指定的endpoint上创建bucket 
        # param: endpoint ： 默认为华北2   
        # param：bucketname: 新建的 bucket名称 """
        bucket = oss2.Bucket(self.auth,endpoint,bucketname)
        bucket.create_bucket(oss2.models.BUCKET_ACL_PUBLIC_READ)
        
    def putFiles(self,onputfilename='',local_filename='',bucketname='',endpoint='oss-cn-beijing.aliyuncs.com'):
        bucket = oss2.Bucket(self.auth,endpoint,bucketname)
        bucket.put_object_from_file(onputfilename, local_filename,progress_callback='percentage')
        
    def percentage(self,consumed_bytes, total_bytes):
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            print('\r{0}% '.format(rate), end='')
            sys.stdout.flush()
    
    def download(self,endpoint,bucketname,remote_filename,local_filename):
        bucket = oss2.Bucket(self.auth,endpoint,bucketname)
        bucket.get_object_to_file(remote_filename, local_filename,progress_callback='percentage')
        
