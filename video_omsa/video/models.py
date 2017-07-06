#! /usr/bin/env python
# -*- coding:utf8 -*-
from django.db import models

# Create your models here.
class Nav(models.Model):
        id = models.AutoField(primary_key=True)
        name = models.CharField(max_length=40,default="导航栏",blank=True,null=True)
        nnav = models.CharField(max_length=40,default="二级分类",blank=True,null=True)
        nnav_url = models.CharField(max_length=40,default="#",blank=True,null=True)
        nnav1 = models.CharField(max_length=40,default="二级分类1",blank=True,null=True)
        nnav_url1 = models.CharField(max_length=40,default="#",blank=True,null=True)
        nnav2 = models.CharField(max_length=40,default="二级分类2",blank=True,null=True)
        nnav_url2 = models.CharField(max_length=40,default="#",blank=True,null=True)

        def __unicode__(self):
                return self.name

class Video(models.Model):
	id = models.AutoField(primary_key=True)
	app_type = models.CharField(max_length=40,default="app类型",blank=False,null=False)
	project_name = models.CharField(max_length=40,default="项目类型",blank=False,null=False)
	marjor_name = models.CharField(max_length=40,default="科目类型",blank=False,null=False)
	marjor_teacher = models.CharField(max_length=40,default="授课老师",blank=False,null=False)
	is_shooting = models.CharField('拍摄情况',max_length=100,blank=True)
	cut_time = models.CharField('剪接情况',max_length=100,blank=True)
	to_m3u8_time = models.CharField('切片情况',max_length=100,blank=True)
	is_onsandbox = models.CharField('上沙盒情况',max_length=100,blank=True)
	content_test = models.CharField('内容测试情况',max_length=100,blank=True)
	qa_test = models.CharField('声画测试情况',max_length=100,blank=True)
	is_online = models.CharField('同步到线上',max_length=100,blank=False,null=False)
