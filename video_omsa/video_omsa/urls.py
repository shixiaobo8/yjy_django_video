#!/usr/bin/env python
# -*- coding:utf8 -*-
from django.conf.urls import include, url
from django.contrib import admin
from video import views as video_views
from aliyun import views as aliyun_views
#import xadmin
#xadmin.autodiscover()
#from xadmin.plugins import xversion
#xversion.registe_models()


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
    url(r'^addIm$', video_views.addIm),
    url(r'^add_Im$', video_views.add_Im),
    url(r'^im_list.html$', video_views.imList),
    url(r'^projects/create$', video_views.pro_create),
# 迁移过来的项目
    url(r'^ecs_list$', aliyun_views.ecs_list),
    url(r'^upload$', video_views.upload),
    url(r'^up_recive$', video_views.up_recive),
    url(r'^inters_data$', video_views.inters_data,name='inters'),
    url(r'^get_imge$', video_views.get_imge),
    url(r'^export_cvs$', video_views.export_cvs),
    url(r'^add', video_views.add),

]
