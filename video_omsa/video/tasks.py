#!/usr/bin/env python
# -*- coding:utf8 -*-
# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time,commands
from .ffmpeg import Aes,ffmpeg

@shared_task
def add(x, y):
    return x + y


@shared_task
def mul(x, y):
    return x * y


@shared_task
def xsum(numbers):
    return sum(numbers)

@shared_task
def sleep(s):
    time.sleep(s)
    return

@shared_task
def cut_video(task_id, video_id,mp4_path):
     fg = ffmpeg(task_id,video_id,mp4_path)
     res = fg.start_cut()
     return res

# #发送邮件
# @shared_task
# def send_Mail(task_id,video_id,status):
#     fg = ffmpeg(task_id,video_id,mp4_path)
#     res = fg.sendMail()
#     return res