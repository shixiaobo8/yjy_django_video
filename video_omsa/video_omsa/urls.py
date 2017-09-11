#!/usr/bin/env python
# -*- coding:utf8 -*-
from django.conf.urls import include, url
from django.contrib import admin
from video import views as video_views
from aliyun import views as aliyun_views
from zabbix import views as zabbix_views
from verifycode import views as vc_views

urlpatterns = [
    # Examples:
    # url(r'^$', 'video_omsa.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
 
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', video_views.index,name='index'),
    url(r'^register$', video_views.register),
    url(r'^login$', video_views.login),
    url(r'^logout$', video_views.logout),
    url(r'^reg$', video_views.reg),
    url(r'^getChapterById', video_views.getChapterById),
    url(r'^getCategorys', video_views.getappCategory),
    url(r'^getAppSections', video_views.getAppSections),
    url(r'^addIm$', video_views.addIm),
    url(r'^add_Im$', video_views.add_Im),
    url(r'^im_list.html$', video_views.imList),
    url(r'^projects/create$', video_views.pro_create),
    url(r'^ecs_list$', aliyun_views.ecs_list),
    url(r'^upload$', video_views.upload),
    url(r'^up_recive$', video_views.up_recive),
    url(r'^change_touxiang$', video_views.change_touxiang),
    url(r'^inters_data$', video_views.inters_data,name='inters'),
    url(r'^get_imge$', video_views.get_imge),
    url(r'^export_cvs$', video_views.export_cvs),
    url(r'^add', video_views.add),
    url(r'^monitor/zabbix', zabbix_views.host_index),
    url(r'^captcha/', include('captcha.urls')),
    url('^ajax_val', vc_views.ajax_val, name='ajax_val'),
    url(r'^refresh/$', vc_views.refresh_captcha, name='refresh_captcha'),
    url(r'^inters_info$', video_views.inters_info,name='CurInfo'),
    url(r'^Hisinters$', video_views.History_inters,name='Hisinters'),
    url(r'^usercenter.html$', video_views.usercenter,name='usercenter'),
    url(r'^chusername$', video_views.chusername,name='chusername'),
    url(r'^chpwd$', video_views.chpwd,name='chpwd'),
    url(r'^video/list.html$', video_views.video_list,name='video_list'),
    url(r'^video/cut$', video_views.video_cut,name='video_cut'),
    url(r'^video/upload$', video_views.video_upload,name='video_upload'),
    url(r'^video/toonline$', video_views.video_toonline,name='video_toonline'),
    url(r'^getSqls$', video_views.getSqls,name='getSqls'),
    url(r'^video/getMyAppMp4.html',video_views.getMyAppMp4,name='getMyAppMp4'),
    url(r'^video/mp4_file_download',video_views.mp4_file_download,name='mp4_file_download'),
    url(r'^video/chvideoname',video_views.chvideoname,name='chvideoname'),
    url(r'^video/CategoryMp4',video_views.CategoryMp4,name='CategoryMp4'),
    url(r'^getMp4s',video_views.getMp4s,name='getMp4s'),
]
handler404 = video_views.page_not_found
handler500 = video_views.page_error
