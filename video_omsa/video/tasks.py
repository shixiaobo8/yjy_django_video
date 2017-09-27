#!/usr/bin/env python
# -*- coding:utf8 -*-
# Create your tasks here
from __future__ import absolute_import, unicode_literals
from celery import shared_task
import time

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
    return 'ok'