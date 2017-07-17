#!/usr/bin/env python
# -*- coding:utf8 -*-
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from captcha.fields import CaptchaStore
import json


# 刷新验证码
def refresh_captcha(request):
    """  Return json with new captcha for ajax refresh request """
    if not request.is_ajax(): # 只接受ajax提交
        raise Http404
    new_key = CaptchaStore.generate_key()
    to_json_response = {
        'key': new_key,
        'image_url': captcha_image_url(new_key),
    }
    return HttpResponse(json.dumps(to_json_response), content_type='application/json')

# ajax 验证码判断
def ajax_val(request):
    if  request.is_ajax():
        cs = CaptchaStore.objects.filter(response=request.GET['response'],
                                     hashkey=request.GET['hashkey'])
        if cs:
            json_data={'status':1}
        else:
            json_data = {'status':0}
        return JsonResponse(json_data)
    else:
        # raise Http404
        json_data = {'status':0}
        return JsonResponse(json_data) #需要导入  from django.http import JsonResponse