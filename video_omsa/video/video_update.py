#!/usr/bin/env /usr/bin/python2.6
# -*- coding:utf8 -*-
import MySQLdb as mdb
import os,sys,commands,time

class updateDbTool:
# 构造器
	def __init__(self,dbname):
		today = time.strftime('%Y_%m_%d',time.localtime(time.time()))
		self.dbname = dbname
		self.sandbox_host = '10.26.160.177'
		self.online_host = '10.24.203.239'
		self.user = 'video_40'
		self.password = 'abcxxx123'
		self.sqlstorepath = '/root/sqls/' + today + '/'
		if not os.path.exists(self.sqlstorepath):
			os.makedirs(self.sqlstorepath)
		self.tables = {
			'yjy_xiyizonghe':['yjy_im_chat','yjy_im_chat_aes','yjy_im_chat_aes_new'],
			'tcmsq':['yjy_im_chat','yjy_im_chat_aes'],
			'yjy_xiyizhiyeyishi':['yjy_im_chat','yjy_im_chat_aes'],
			'yjy_zhongyizonghe':['yjy_im_chat','yjy_im_chat_aes']
		}
		try:
			self.sandbox_conn = mdb.connect(self.sandbox_host,user=self.user,passwd=self.password,db=dbname,unix_socket='/tmp/mysql.sock')
			self.sandbox_cursor = self.sandbox_conn.cursor()
			self.online_conn = mdb.connect(self.online_host,user=self.user,passwd=self.password,db=dbname,unix_socket='/tmp/mysql.sock')
			self.online_cursor = self.online_conn.cursor()
		except mdb.Error,e:
			print e

# 析构器
	def __del__(self):
		self.sanbox_conn.close()
		self.online_conn.close()
		


# 同步线上的最新数据到沙盒数据库
	def update_to_online(self):
		# 先dump 保存sandbox和online各自的数据一份
		for table in self.tables[self.dbname]:
			c_time = time.strftime('%Y_%m_%d_%H%M%S',time.localtime(time.time()))
			sandbox_storesqlname = self.sqlstorepath + '/' + c_time + '_' + self.dbname + '_' + table + '.sql'
			online_storesqlname = self.sqlstorepath + '/' + c_time + '_' + self.dbname + '_' + table + '.sql'
			# 线上导出到40
			online_dump_cmd = 'mysqldump -h ' + self.online_host + ' -u' +self.user + ' -p' + self.password + ' --default-character-set=utf8 '+self.dbname + ' ' +table + ' > ' + online_storesqlname
			print online_dump_cmd
			online_rs = commands.getstatusoutput(online_dump_cmd)
			if online_rs[0] != 0:
				print "保存线上数据失败!"
				return "保存数据失败!" + online_dump_cmd
			# 预上线数据导出到40
			sandbox_dump_cmd = 'mysqldump -h ' + self.sandbox_host + ' -u' +self.user + ' -p' + self.password + ' --default-character-set=utf8 '+self.dbname + ' ' +table + ' > ' + sandbox_storesqlname
			print sandbox_dump_cmd
			sandbox_rs = commands.getstatusoutput(sandbox_dump_cmd)
			if sandbox_rs[0] != 0:
				print "保存沙盒数据失败!"
				return "保存数据失败!" + sandbox_dump_cmd
			# 从刚导出的table预上线数据导入到线上
			update_cmd = "mysql -u" + self.user + ' -h' + self.online_host +' -p' + self.password + ' < ' + sandbox_storesqlname
			print update_cmd
			update_rs = commands.getstatusoutput(update_cmd)
			if update_rs[0] != 0:
				print '导入数据失败!'
				return '导入数据失败!'+ update_cmd

		


if __name__ == '__main__':
	dbt = updateDbTool('yjy_xiyizhiyeyishi')
	dbt.update_to_online()
