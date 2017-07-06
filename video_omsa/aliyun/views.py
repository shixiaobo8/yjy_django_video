# !/usr/bin/env python
# -*- coding:utf8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from .models import ecs
from .ecs import ecs
import json

# Create your views here.
def ecs_list(request):
    ECS = ecs()
    #ecses = ECS.getEcses()
    ecses = json.loads(ECS.getEcses())['Instances'].values()[0]
    #return render(request,'ecs_list.html',{'ecses':json.loads(ecses)})
    return render(request,'ecs_list.html',{'ecses':ecses})
#    return HttpResponse(ecses) # 返回json格式
