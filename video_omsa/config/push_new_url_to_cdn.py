#!/usr/bin/env python
#-*- coding:utf8 -*-
# 暂由shell调用改脚本，约定一个ts列表的配置文件
from __future__ import print_function
import os,sys,commands,requests
import oss2


# 新上线的ts链接地址列表
UrlList = []
# 初始化oss登录验证
auth = oss2.Auth('LTAIYj7b9Fm1rrH2', '6rWkgQX8yiIDrOY70vcy19EUuHvjW2')

prefix_url = 'http://yjy-media.oss-cn-beijing.aliyuncs.com'
# 所有ts视频bucket
videos_bucket = oss2.Bucket(auth, 'oss-cn-beijing-internal.aliyuncs.com',' yjy-media')


# 预热这些url到cdn
def callback():
	for url in UrlList:
		cmd = 'python /root/scripts/cdn.py Action=PushObjectCache ObjectPath='+url+' ObjectType=File'
                pushCacheUrl = commands.getstatusoutput(cmd)[1]
		print(pushCacheUrl)
                r = requests.get(pushCacheUrl)
                print(r.text)
	

def upload_to_oss():
	for url in UrlList:
		n_url = url.replace('http://m1.letiku.net',prefix_url).replace('http://media.yijiaoyuan.net:9999',prefix_url).replace('//','/')
		local_path = url.replace('http://m1.letiku.net','/data/hls').replace('http://media.yijiaoyuan.net:9999','/data/hls').replace('//','/').replace('\n','')
		print(local_path)
		remote_key = url.replace('http://m1.letiku.net/','').replace('http://media.yijiaoyuan.net:9999/','').replace('//','/').replace('\n','')
		print(remote_key)
		result = videos_bucket.put_object_from_file(remote_key,local_path,progress_callback=percentage)
                print(remote_key)
		print(result)

# 进度条功能
def percentage(consumed_bytes, total_bytes):
        if total_bytes:
                rate = int(100* (float(consumed_bytes)) / (float(total_bytes)))
                print('\r{0}%'.format(rate),end='')
                sys.stdout.flush()


if __name__ == '__main__':
# 判断传入的ts_file文件参数
	if len(sys.argv) == 2:
		try:
			ts_file = sys.argv[1]
			with open(ts_file) as f:
				UrlList = [ url for url in f.readlines() if url !='\n' and 'data/hls' not in url ]
		except Exception,e:
			print(e)
		callback()
		upload_to_oss()
	else:
		print("预热上传脚本错误!!")
		sys.exit(1)
		
