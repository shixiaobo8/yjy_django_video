#!/usr/bin/env python
# -*- coding:utf8 -*-
from django.shortcuts import render,redirect
from django.http import HttpResponse
from zabbix_api import ZabbixAPI
import json

# Create your views here.
def host_index(request):
    zapi = ZabbixAPI(server="http://yjy.zabbix.letiku.net:18989",user='admin',passwd='Yjy@yunwei123')
    zapi.login('admin','Yjy@yunwei123')
    host_param ={
        "output":["hostid","name"],
        "selectParentTemplates": [
            "templateid",
            "name"
        ],
        "filter":{"host":""}
    }
    json_obj = zapi.json_obj(method='host.get',params=host_param)
    r = zapi.do_request(json_obj=json_obj)
    rs = r['result']
    return  render(request,'hosts.html',{"host_info":rs})
