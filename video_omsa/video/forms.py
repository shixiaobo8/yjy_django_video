#!/usr/bin/env python
# -*- coding:utf8 -*-
from django import forms
from django.http import HttpResponse
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from django.forms.extras.widgets import SelectDateWidget
from django.db import connection, transaction
from captcha.fields import CaptchaField
from django.views.generic.edit import CreateView
from captcha.models import CaptchaStore
from captcha.helpers import captcha_image_url
from django.http import HttpResponse
import json, time
import re

YEARS_CHOICES = ('2016', '2017')
t_mon = int(time.strftime('%m', time.localtime(time.time())))
t_year = int(time.strftime('%Y', time.localtime(time.time())))
# 历史日期从2016年12月份11日开始有记录,即从2017的年份的倍数x12+当前月份的值+1
HISTORYS_CHOICES = tuple([(i, '近' + str(i) + '个月的访问历史趋势') for i in range(1, (t_year - 2017) * 12 + 1 + t_mon + 1)])
MONTHS_CHOICES = ('01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12')
DAYS_CHOICES = (
'01', '02', '03', '04', '05', '06', '07', '08', '09', '10', '11', '12', '13', '14', '15', '16', '17', '18', '19', '20',
'21', '22', '23', '24', '25', '26', '27', '28', '29', '30', '31')


def PhoneValidate(value):
    phone_re = re.compile(r'^(13[0-9]|15[012356789]|17[0678]|18[0-9]|14[57])[0-9]{8}$')
    if not phone_re.match(value):
        raise ValidationError('手机格式错误')


class videoForm(forms.Form):
    chapters = []
    PARENT_ID = []
    # PARENT_ID2 = [ (i,str(i) + "年真题") for i in range(1988,t_year + 1)]
    # PARENT_ID1 = PARENT_ID2.extend([(1,'直播'),(2,'精讲'),(3,'技能'),(4,'冲刺'),(5,'专题')])
    # PARENT_ID = tuple(PARENT_ID2)[::-1]
    STATUS_CHOICES = (
        (0, '关闭'),
        (1, '直播'),
    )
    SORT_CHOICES = (
        ('xiyao', '西药'),
        ('zhongyao', '中药'),
    )
    ZHUANGXUE_CHOICES = (
        ('zhuangsuo', '专硕'),
        ('xuesuo', '学硕'),
    )
    app_type = forms.ChoiceField(
        choices=[('yjy_xiyizonghe', '西医综合'), ('tcmsq', '中医执业医师'), ('yjy_zhongyizonghe', '中医综合'),
                 ('yjy_xiyizhiyeyishi', '西医执业医师')], label='app类型',
        widget=forms.Select(attrs={'class': 'form-control', 'onChange':'getCategorys(this.value)','required'
    :True}))
    room_id = forms.IntegerField(label='聊天室id',
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}))
    name = forms.CharField(label='视频名称', widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}))
    status = forms.ChoiceField(widget=forms.RadioSelect({'required': True}), choices=STATUS_CHOICES, required=True,
                               label='状态')
    sort = forms.ChoiceField(widget=forms.RadioSelect, choices=SORT_CHOICES, required=True, label='分类')
    zhuanorxue = forms.ChoiceField(widget=forms.CheckboxSelectMultiple(attrs={'required': True}),
                                   choices=ZHUANGXUE_CHOICES, label='专硕学硕')
    is_on_air = forms.ChoiceField(choices=[(0, '即将开始'), (1, '正在直播'), (2, '直播已结束')], label='直播状态',
                                  widget=forms.Select(attrs={'class': 'form-control', 'required': True}))
    goods_id = forms.IntegerField(label='商品id', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '请输入商品id', 'required': True}))
    service_id = forms.IntegerField(label='服务id', widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': '请输入服务id', 'required': True}))
    media_url = forms.URLField(label='加密地址', widget=forms.URLInput(attrs={'class': 'form-control', 'required': True}))
    download_url = forms.URLField(label='下载地址',
                                  widget=forms.URLInput(attrs={'size': 20, 'class': 'form-control', 'required': True}))
    duration = forms.DurationField(label='播放时长',
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}))
    sort = forms.IntegerField(label='排序', widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}))
    parent_id = forms.ChoiceField(choices=PARENT_ID, label='科目', widget=forms.Select(
        attrs={'class': 'form-control', 'onChange': 'getChapters(this.value)', 'required': True}))
    chapter_id = forms.ChoiceField(choices=chapters, label='章节名称',
                                   widget=forms.Select(attrs={'class': 'form-control', 'required': True}))
    file_size = forms.CharField(label='视频大小', widget=forms.TextInput(attrs={'class': 'form-control', 'required': True}))


class ImEditForm(forms.Form):
    EDITSTATUS = (
        (0, '已完成'),
        (1, '待完成'),
    )
    video = forms.ChoiceField(widget=forms.RadioSelect, choices=EDITSTATUS, required=True, label='视频拍摄完成状态')
    cut = forms.ChoiceField(widget=forms.RadioSelect, choices=EDITSTATUS, required=True, label='视频剪接状态')
    tom3u8 = forms.ChoiceField(widget=forms.RadioSelect, choices=EDITSTATUS, required=True, label='切片状态')
    tobackend = forms.ChoiceField(widget=forms.RadioSelect, choices=EDITSTATUS, required=True, label='上传到后台')
    contenttest = forms.ChoiceField(widget=forms.RadioSelect, choices=EDITSTATUS, required=True, label='内容测试')
    qatest = forms.ChoiceField(widget=forms.RadioSelect, choices=EDITSTATUS, required=True, label='视频质量测试')
    lasttest = forms.ChoiceField(widget=forms.RadioSelect, choices=EDITSTATUS, required=True, label='最终测试')
    is_online = forms.ChoiceField(widget=forms.RadioSelect, choices=EDITSTATUS, required=True, label='是否上线')
    is_onsandbox = forms.ChoiceField(widget=forms.RadioSelect, choices=EDITSTATUS, required=True, label='是否上沙盒')
    app_type = forms.ChoiceField(
        choices=[('yjy_xiyizonghe', '西医综合'), ('tcmsq', '中医执业医师'), ('yjy_zhongyizonghe', '中医综合'),
                 ('yjy_xiyizhiyeyishi', '西医执业医师')], label='app类型',
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}))


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=16,
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}, ), )
    password = forms.CharField(max_length=100,
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}, ), )
    captcha = CaptchaField(label='验证码', error_messages={"invalid": u"验证码错误"})


class registerForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=16, error_messages={'required': "用户名不能为空"},
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}, ), )
    password = forms.CharField(max_length=100, error_messages={'required': "密码不能为空"},
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}, ), )
    email = forms.EmailField(required=True, label='电子邮箱', max_length=100, error_messages={'required': '邮箱不能为空!'},
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}, ))
    app_type = forms.ChoiceField(
        choices=[('yjy_xiyizonghe', '西医综合'), ('tcmsq', '中医执业医师'), ('yjy_zhongyizonghe', '中医综合'),
                 ('yjy_xiyizhiyeyishi', '西医执业医师')], label='app类型',
        widget=forms.Select(attrs={'class': 'form-control', 'required': True}))


class intersForm(forms.Form):
    date = forms.DateField(label='请选择日期', widget=SelectDateWidget(years=YEARS_CHOICES))
    top = forms.CharField(label='请填写查询的top条数', max_length=160, widget=forms.TextInput, )
    history = forms.ChoiceField(choices=HISTORYS_CHOICES, label='请选择历史趋势时间', widget=forms.Select, )


class NewForm(forms.Form):
    username = forms.CharField(label='用户名', max_length=16, error_messages={'required': "用户名不能为空"},
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '用户名'}, ), )
    password = forms.CharField(max_length=100, error_messages={'required': "密码不能为空"},
                               widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '密码'}, ), )
    phone = forms.CharField(validators=[PhoneValidate, ], error_messages={'required': '手机号码不能为空'},
                            widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '手机号'}, ), )
    email = forms.EmailField(required=True, label='电子邮箱', max_length=100, error_messages={'required': '邮箱不>能为空!'},
                             widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'email'}, ))
