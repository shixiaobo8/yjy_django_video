#! /usr/bin/env python
# -*- coding:utf8 -*-
from __future__ import division
from django.http import HttpResponseRedirect
from django.core.mail import EmailMultiAlternatives
from django.template.context import RequestContext
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from video.forms import videoForm, LoginForm, registerForm, ImEditForm, NewForm, intersForm
from django.shortcuts import render_to_response
from django.core.paginator import Paginator, InvalidPage, EmptyPage, PageNotAnInteger
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from .models import Nav
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json, os, sys, xlwt, requests, time, calendar, random, shutil, simplejson
import MySQLdb as mdb
from django.http import StreamingHttpResponse
from collections import OrderedDict
import urllib
import logging,commands
from .tasks import sleep,cut_video
from ffmpeg import ffmpeg,Aes
import paramiko as pmk
import dns.resolver
from .video_update import updateDbTool

# navs = list(Nav.objects.all())

@csrf_exempt
def page_not_found(request):
    return render_to_response('404.html')


@csrf_exempt
def page_error(request):
    return render_to_response('500.html')


# Create your views here.
def addIm(request):
    form = videoForm(request.POST)
    return render(request, 'index.html', {'form': form})


def getChapterById(request):
    if request.method == 'GET':
        form = videoForm(request.GET)
        apptype = form.data['apptype']
        parentId = form.data['id']
        chapters1 = []
        chaps = getChapters(apptype, int(parentId))
        for i in range(0, len(chaps)):
            chapters1.append(chaps)
        return HttpResponse(json.dumps(chapters1[0]))


def getChapters(apptype, id):
    try:
        cursor = connection.cursor()
        chapters = []
        sql = "select `id`,`title` from %s.yjy_im_category where parent_id=%d" % (apptype, id)
        cursor.execute(sql)
        titles = cursor.fetchall()
        return titles
    except Exception, e:
        print e


def getappCategory(request):
    if request.method == 'GET':
        apptype = request.GET['apptype']
        res = []
        appCategorys = getCategorys(apptype)
        for i in range(0, len(appCategorys)):
            res.append(list(appCategorys[i]))
        return HttpResponse(json.dumps(res))


def getCategorys(apptype):
    try:
        cursor = connection.cursor()
        sql = "select `id`,`title` from `%s`.yjy_im_category where `parent_id`=0 and `is_del`=0 " % (apptype)
        cursor.execute(sql)
        appCategorys = cursor.fetchall()
        return appCategorys
    except Exception, e:
        print e


def add_Im(request):
    if request.method == 'POST':
        form = videoForm(request.POST)
        data = form.data
        json = dict()
        return HttpResponse(data.items())


def login(request):
    navs = list(Nav.objects.all())
    if request.method == 'POST':
        form = LoginForm(request.POST)
        data = form.data
        username = data['username']
        password = data['password']
        # login_mess = request.POST.get("login_mess","aaa")
        # captcha = request.POST.get("captcha","aaa")
        captcha_0 = data['captcha_0']
        if captcha_0 != '':
            print form.data
            print form.errors.as_data()
            if form.is_valid():
                human = True
                user = authenticate(username=username, password=password)
                if user is not None and user.is_active:
                    auth.login(request, user)
                    return redirect('usercenter.html')
                else:
                    login_mess = '用户名或者密码不正确'
                    return render(request, 'login.html', {'form': form, 'login_mess': login_mess})
            else:
                return HttpResponse({"DATA":"表单验证失败!"})
        else:
            login_mess = '验证码不能为空!'
            return render(request, 'login.html', {'form': form, 'login_mess': login_mess})
    else:
        login_mess = 'http method not allowed'
        return HttpResponse(login_mess)


def register(request):
    if request.method == 'POST':
        form = registerForm(request.POST)
        if form.is_valid():
            data = form.data
            if User.objects.filter(username=data['username']):
                reg_error = '用户名已存在!'
                return render(request, 'register.html', {'reg_error': reg_error, 'form': form})
            else:
                user = User()
                user.set_password(data['password'])
                user.username = data['username']
                user.email = data['email']
                user.save()
                try:
                    cursor = connection.cursor()
                    sql = "update auth_user set `apptype`='" + data['app_type'] + "',`department`='" + data['user_type'] + "' where username='" + data[
                        'username'] + "'"
                    cursor.execute(sql)
                    rs = cursor.fetchall()
                except Exception, e:
                    print e
                return HttpResponseRedirect('/im_list.html')
        else:
            message = "<b style='color:red;'>invalid</b> please keep slient and keep friendship and keep smile ^_^ and keep doing yourself and belive yourself ! "
            reg_error = form.errors
            return render(request, 'register.html', {'message': message, 'reg_error': reg_error, 'form': form})
    if request.method == 'GET':
        return HttpResponse(form.data)
        form = registerForm(request.POST)
        return HttpResponseRedirect(request, '/register.html', {'form': form})


def index(request):
    form = LoginForm(request.POST)
    navs = list(Nav.objects.all())
    return render(request, 'login.html', {'navs': navs, 'form': form})


def reg(request):
    form = registerForm(request.POST)
    return render(request, 'register.html', {'form': form})


def imList(request):
    navs = list(Nav.objects.all())
    return render(request, 'im_list.html', {'navs': navs})


def logout(request):
    auth.logout(request)
    # del request.session['c_user']
    return HttpResponseRedirect('/')


def pro_create(request):
    form = ImEditForm(request.POST)
    navs = list(Nav.objects.all())
    return render(request, 'projects_create.html', {'navs': navs, "form": form})


# def inters_count(date_table,top):
# 	"""
# 		date_table: 形如2017_05_13
# 		top: 查询的条数
# 	"""
# 	import  MySQLdb as mdb
# 	import datetime
# 	db_conn = mdb.connect('59.110.11.16','web_data','web_data@2017','all_web_data_history')
# 	cursor = db_conn.cursor()
# 	ret = ''
# 	try:
# 		cursor.execute("select * from (select `key`,`requests` from "+date_table+"_history_data limit "+top+") as top order by `requests`+0 desc limit "+top+";")
# 		datas = cursor.fetchall()
# 		ret = datas
# 	except mdb.Error,e:
# 		print e
# 	db_conn.close()
# 	# 内部调用数据返回
# 	return ret
# 	# 外部调用接口数据返回

def shareGame(request):
     if request.method == 'GET':
         roomid=request.GET.get('roomid','0')
         peoples=request.GET.get('peoples','0')
         status = 'ok'
         res = {"id": "penghu",
          'scheme_ios': "'yinjiapenghu://?mid=0&version=1.0.4&roomid=" + roomid + "&peoples=" + peoples + "&amp;timestamp=' + Date.parse(new Date())",
          'scheme_android': "'yinjiapenghu://com.yinjia.penghu?mid=0&version=1.0.4&roomid=" + roomid + "&peoples=" + peoples + "&amp;timestamp=' + Date.parse(new Date())",
          'ios_download': 'apk/YinJiaPengHu.apk',
          'android_download': 'apk/YinJiaPengHu.apk',
          'timeout': 1000};
         href = "yinjiapenghu://com.yinjia.penghu?mid=0&version=1.0.4&roomid=" + roomid + "&peoples=" + peoples
         res1 = """
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1"/>
                <title>银佳碰胡加入房间</title>
            </head>
            <body>
                <style type="text/css">
                *{margin:0; padding:0;}
                img{max-width: 100%; height: auto;}
                .test{height: 600px; max-width: 600px; font-size: 18px;}
                </style>
            <div class="test">
                <center><h4>银佳碰胡——欢迎你 </h4></center><h4><center> 房间号: """ + roomid +  """</h4></center><h4><center> 当前人数: """ + peoples +  """</h4></center><center><h4 onclick='startAPP()' style="color:red;border 1px solid green;"><b style='font-size:100px;'><img src='http://www.devops89.cn:56/jionRoomBtn.png' alt='加入房间'/> </b></h4></center>
                <br/><center>没有安装请点击下面的按钮下载</center><br/>
                <center><input type='image' src='http://www.devops89.cn:56/downloadBtn.png' onclick='downLoadApp()' alt='点击下载app'/></center>
                </div>
                <script>
                                function downLoadApp(){
                                    window.open("http://www.devops89.cn:56/apk/YinJiaPengHu.apk");
                                };
                                function startAPP(){
                                    window.location = '"""+ href+"""';
                                    }
                                </script>

                <script type="text/javascript">
                    function is_weixin() {
                        var ua = navigator.userAgent.toLowerCase();
                        if (ua.match(/MicroMessenger/i) == "micromessenger") {
                            return true;
                        } else {
                            return false;
                        }
                    }
                    var isWeixin = is_weixin();
                    var winHeight = typeof window.innerHeight != 'undefined' ? window.innerHeight : document.documentElement.clientHeight;
                    function loadHtml(){
                        var div = document.createElement('div');
                        div.id = 'weixin-tip';
                        div.innerHTML = '<p><img src="http://www.devops89.cn:56/live_weixin.png" alt="微信打开"/></p>';
                        document.body.appendChild(div);
                    }

                    function loadStyleText(cssText) {
                        var style = document.createElement('style');
                        style.rel = 'stylesheet';
                        style.type = 'text/css';
                        try {
                            style.appendChild(document.createTextNode(cssText));
                        } catch (e) {
                            style.styleSheet.cssText = cssText; //ie9以下
                        }
                        var head=document.getElementsByTagName("head")[0]; //head标签之间加上style样式
                        head.appendChild(style);
                    }
                    var cssText = "#weixin-tip{position: fixed; left:0; top:0; background: rgba(0,0,0,0.8); filter:alpha(opacity=80); width: 100%; height:100%; z-index: 100;} #weixin-tip p{text-align: center; margin-top: 10%; padding:0 5%;}";
                    if(isWeixin){
                        loadHtml();
                        loadStyleText(cssText);
                    }
                </script>
            </body>
            </html>
            """
         return HttpResponse(res1)


def test_inter(request):
    if request.method == 'GET' or request.method == 'POST':
        # A = dns.resolver.query(settings.SERVER_DOMAIN,'A')
        # ips = ''
        # for ip1 in A.response.answer:
        #     for ip in ip1.items:
        #         ips = ip.address
        return HttpResponse(json.dumps({'sharehaedURL':'https://mmbiz.qlogo.cn/mmbiz_png/YGE76YBu7064VpxGrEYzhfx2yLlwib2PgUQMQ6YkBaviawicFSpUpwfFZRP9jdMFWXJKhoRCck36CfY1YPYGqqknA/0?wx_fmt=png','Kefulist':'123456','Tipmsg':'欢迎大家','shareURL':'http://www.devops89.cn:81/share.html','version':'1.0.4','ip':'47.92.134.87','URL':'http://www.devops89.cn:56/yingjia.html','post':'7070'}))

def inters_info(request):
    import types
    data = nginxData()
    total = data['total']
    detail = data['detail']
    # return HttpResponse(json.dumps(data))
    res = ''
    tmp1 = "<table class='table table-bordered table-striped'><caption style='color:green;font:40px;'>" + str(
        total[0]) + "</caption><colgroup><col class='col-xs-1'><col class='col-xs-3'></colgroup><thead><tr>"
    res += tmp1 + "<th>" + str(total[0]) + "</th><th>" + str(
        total[1]) + "</th></tr></thead><tbody></tbody></table><hr/>"
    for v in detail:
        tmp2 = "<table class='table table-bordered table-striped'><caption style='color:green;font:40px;'>" + str(
            v[0]) + "</caption><colgroup><col class='col-xs-1'><col class='col-xs-3'></colgroup><thead><tr>"
        if type(v) is types.ListType:
            tmp2 += "<th>域名/接口url</th><th>" + "访问量" + "</th></tr></thead><tbody>"
            for v1 in v[1]:
                tmp2 += "<tr><th scope='row'><code>" + str(v1[0]) + "</code></th><td>" + str(v1[1]) + "</td></tr>"
            tmp2 += "</tbody></table><hr/>"
        # elif type(v) is types.IntType:
        #    res += tmp + "<th>" + str(total[0]) + "</th><th>" + str(total[1]) + "</th></tr></thead><tbody></tbody></table><hr/>"
        res += tmp2
    return HttpResponse(res)


def History_inters(request):
    domains = ['tiku.letiku.net', 'tcmsq.letiku.net', 'tcms.letiku.net', 'www.letiku.net',
               'srcmock.letiku.net', 'zhongxiyijiehe.letiku.net', '123.57.185.38', 'api.yijiaoyuan.net',
               'kouqiangzonghe.letiku.net', 'kouqiangzyys.letiku.net', 'passport.letiku.net', 'political.letiku.net',
               'xiyizhiyeyishi.letiku.net', 'xiyizhulizyys.letiku.net', 'yijiaoyuan.letiku.net']
    if request.method == 'GET':
        f_data = request.GET
        his_month = f_data['data[history]']
        dates = getDates(his_month)
        data = dict()
        domain_data = []
        for do in domains:
            domain_datas = []
            do_data = dict()
            if do == '123.57.185.38':
                do_data['name'] = '总app访问量(123.57.185.38)'
            else:
                do_data['name'] = do
            for date in dates:
                redis_key = do + date + '_all_requests'
                reqs = read_from_cache(redis_key)
                if not reqs:
                    reqs = getHisData(date, do)
                    write_to_cache(redis_key, reqs)
                domain_datas.append(int(reqs))
            do_data['data'] = domain_datas
            domain_data.append(do_data)
    data['dates'] = dates
    data['domains_datas'] = domain_data
    data['months'] = his_month
    return HttpResponse(json.dumps(data))


def getcalendar(c_year, c_mon, month):
    res = dict()
    res['year'] = c_year
    res['month'] = int(month)
    if int(c_mon) == int(month):
        res['month'] = 12
        res['year'] = c_year - 1
    # 查询月份数小于当前月份数
    if int(c_mon) > int(month):
        res['month'] = int(c_mon) - int(month)
    # 查询月份数大于当前月份数
    if int(c_mon) < int(month):
        if int(month) / 12 > 0:
            res['year'] -= int(month) / 12
            res['month'] = int(c_mon) - int(month) % 12
        if int(month) / 12 == 0:
            res['month'] = 12 - (int(month) - int(c_mon))
            res['year'] -= 1
    # with open('/tmp/dates.log','ab+') as f:
    #	f.write(json.dumps(res))
    return res


def getDates(his_month):
    dates = []
    today = time.strftime('%Y_%m_%d', time.localtime(time.time()))
    c_year = int(today.split('_')[0])
    c_month = int(today.split('_')[1])
    start_month = int(getcalendar(c_year, c_month, his_month)['month'])
    start_year = int(getcalendar(c_year, c_month, his_month)['year'])
    for year in range(start_year, c_year + 1):
        if year == c_year and start_month > c_month:
            start_month = 1
            end_month = c_month
        if year == c_year and start_month < c_month:
            end_month = c_month + 1
        if year != c_year:
            end_month = 13
        if start_month < 0:
            start_month = 12 + start_month
            end_month = 13
        for mon in range(start_month, end_month):
            print mon
            m_days = ''
            if mon == c_month:
                m_days = int(today.split('_')[2])
            else:
                m_days = calendar.monthrange(year, mon)[1]
            for d in range(1, m_days):
                if d < 10:
                    if mon < 10:
                        date = str(year) + '_0' + str(mon) + '_0' + str(d)
                    else:
                        date = str(year) + '_' + str(mon) + '_0' + str(d)
                else:
                    if mon < 10:
                        date = str(year) + '_0' + str(mon) + '_' + str(d)
                    else:
                        date = str(year) + '_' + str(mon) + '_' + str(d)
                dates.append(date)
    # with open('/tmp/dates.log','ab+') as f:
    #	f.write(json.dumps(dates))
    return dates


def getHisData(date_table, domain):
    import MySQLdb as mdb
    data = ''
    db_conn = mdb.connect('59.110.11.16', 'web_data', 'web_data@2017', 'all_web_data_history')
    cursor = db_conn.cursor()
    try:
        sql = "select `requests` from " + date_table + "_history_data where `key`='" + domain + "' limit 1;"
        cursor.execute(sql)
        data = cursor.fetchall()
        if not data:
            data = ((('0',),))
    except mdb.Error, e:
        data = ((('0',),))
        print e
        db_conn.close()
    return data[0][0]


def nginxData():
    ng_url = 'http://api.letiku.net:888/yjy_req_status'
    r = requests.get(ng_url)
    data = r.text.split('\n')
    total_active = 0
    res = dict()
    max_actives = dict()
    top_actives = dict()
    # 当前最大并发值
    for d in data:
        if d != data[0]:
            d1 = d.split('\t')
            if len(d1) == 8:
                total_active += int(d1[6])
                max_actives[d1[1]] = int(d1[2])
                top_actives[d1[1]] = int(d1[6])
    maxs = sorted(max_actives.iteritems(), key=lambda d: d[1], reverse=True)
    active_tops = sorted(top_actives.iteritems(), key=lambda d: d[1], reverse=True)
    res['detail'] = []
    res['total'] = ['当前实时总并发值', total_active]
    res['detail'].append(['当前实时并发值前十接口', active_tops[:10]])
    res['detail'].append(['今日某一时刻(秒级)最大并发值前十接口', maxs[:10]])
    return res


def inters_count(date_table, top):
    """
        date_table: 形如2017_05_13
        top: 查询的条数
    """
    import MySQLdb as mdb
    import datetime
    db_conn = mdb.connect('59.110.11.16', 'web_data', 'web_data@2017', 'all_web_data_history')
    cursor = db_conn.cursor()
    res1 = ''
    try:
        cursor.execute("select * from " + date_table + "_history_data")
        data = cursor.fetchall()
        statics_files = ['jpg', 'png', 'html', 'js', 'css', 'ts', 'm3u8', 'txt', 'gif']
        statics = []
        res = dict()
        res[u'静态文件'] = 0
        data = [(d[2], int(d[6])) for d in data if d[1] == 'server_url']
        for d in data:
            if d[0].split('.')[-1] in statics_files:
                statics.append(d[0])
                res[u'静态文件'] += d[1]
            else:
                if len(d[0].split('/')) > 5:
                    key = ('/'.join(d[0].split('/')[:5])).lower()
                else:
                    key = d[0].lower()

                if res.has_key(key):
                    res[key] = res[key] + d[1]
                else:
                    res[key] = d[1]
        res1 = sorted(res.iteritems(), key=lambda d: d[1], reverse=True)
    except mdb.Error, e:
        print e
    db_conn.close()
    # return (top,'tttt')
    # 内部调用数据返回
    return res1[:int(top)]


# 外部调用接口数据返回
def upload(request):
    form = NewForm(request.GET)
    return render(request, 'upload.html')


@csrf_exempt
def change_touxiang(request):
    data = ''
    today = time.strftime('%Y_%m_%d', time.localtime(time.time()))
    os.chdir("./video/static/")
    image_dir = "Avatar" + os.sep + "uploads" + os.sep + today + os.sep
    random_file = request.user.username + '_' + time.strftime('%H_%M_%S', time.localtime(time.time()))
    if not os.path.exists(image_dir):
        os.makedirs(image_dir)
    if request.method == 'POST':
        files = request.FILES.get("touxiang", None)  # 获取上传的文件,如果没有文件,则默认为None
        if not files:
            return HttpResponse(json.dumps({'data': "没有上传数据"}))
        save_destination = open(os.path.join(image_dir, files.name), 'wb+')  # 打开特定的文件进行二进制写操作
        for chunk in files.chunks():
            save_destination.write(chunk)
        save_destination.close()
        save_file = image_dir + random_file + '.' + files.name.split('.')[-1]
        os.rename(image_dir + files.name, save_file)
        # 修改数据库配置
        try:
            cursor = connection.cursor()
            sql = "update auth_user set touxiang='" + save_file + "' where username='" + request.user.username + "';"
            sql = sql.replace('\\', '/')
            cursor.execute(sql)
            rs = cursor.fetchall()
            data = '头像修改成功'
            os.chdir("../../")
            return HttpResponse(json.dumps({'data': sql}))
        except Exception, e:
            os.rename(image_dir + files.name,
                      save_file.replace(request.user.username, request.user.username + '_fail_'))
            print e
            data = '头像修改失败'
            os.chdir("../../")
            return HttpResponse(json.dumps({'error': data}))


@login_required()
def chusername(request):
    res = '修改失败!'
    if request.method == "POST":
        new_username = request.POST.get("new_username")
        old_username = request.POST.get("old_username")
        try:
            cursor = connection.cursor()
            c_sql = "select `username` from auth_user where username='" + new_username + "';"
            cursor.execute(c_sql)
            user = cursor.fetchall()
            if user:
                res = "用户名已被占用!"
            else:
                i_sql = "update auth_user set username='" + new_username + "' where username='" + old_username + "';"
                cursor.execute(i_sql)
                data = cursor.fetchall()
                if not data:
                    res = "修改成功!"
        except Exception, e:
            print e
    return HttpResponse(json.dumps({"data": res}))


@login_required()
def chpwd(request):
    res = '修改失败!'
    i_sql = ''
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        old_username = request.POST.get("old_username")
        new_password = make_password(new_password, None, 'pbkdf2_sha256')
        try:
            cursor = connection.cursor()
            i_sql = "update auth_user set password='" + new_password + "' where username='" + old_username + "';"
            cursor.execute(i_sql)
            data = cursor.fetchall()
            if not data:
                res = "修改成功!"
        except Exception, e:
            print e
    return HttpResponse(json.dumps({"data": res}))


@csrf_exempt
def up_recive(request):
    if request.method == 'POST':
        files = request.FILES.get("up_file", None)  # 获取上传的文件,如果没有文件,则默认为None
        if not files:
            return HttpResponse(json.dumps({'data': "没有上传数据"}))
        save_destination = open(os.path.join("uploads", files.name), 'wb+')  # 打开特定的文件进行二进制写操作
        for chunk in files.chunks():
            save_destination.write(chunk)
        save_destination.close()
        return HttpResponse(json.dumps({'data': "上传完毕!"}))


def inters_data(request):
    d = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    err_mess = '对不起没有改时段的接口信息!'
    if request.method == 'GET':
        form = intersForm(request.GET)
        f_data = request.GET
        if f_data:
            d_date = f_data['data[d]']
            top = f_data['data[top]']
            cache_key = d_date + "_requests"
            if read_from_cache(cache_key) == None:
                datas = inters_count(d_date, top)
                write_to_cache(cache_key, datas)
            g_data = read_from_cache(cache_key)
            if f_data['action'] == 'pagination' and g_data:
                try:
                    page = int(request.GET.get('page', 1))
                    if page < 1:
                        page = 1
                except ValueError:
                    page = 1
                paginator = Paginator(g_data, 10)
                try:
                    page_data = paginator.page(page)
                except (EmptyPage, InvalidPage, PageNotAnInteger):
                    page_data = paginator.page(1)
                return render(request, 'inters_count.html',
                              {'form': form, 'data': page_data, 'page': page, 'd_date': d_date, 'top': top})
            # return render(request,'inters_count.html',{'form':form,'data':page_data,'page':page})
            if f_data['action'] == 'cvs' and g_data:
                # 自定义httpResponse流
                xls_name = 'd_date.xls'
                response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
                response['mimetype'] = 'application/vnd.ms-excel'
                response['Content-Disposition'] = 'attachment; filename=' + d_date + '.xls'
                # 创建工作簿
                workbook = xlwt.Workbook(encoding='utf-8')
                # 创建工作页
                sheet1 = workbook.add_sheet(d_date + u'访问情况')
                # 开始写入excel
                row0 = [u'访问url', u'访问次数']
                # for i in range(0,len(row0)):
                sheet1.write(0, 0, row0[0])
                sheet1.write(0, 1, row0[1])
                for i in range(1, len(g_data)):
                    sheet1.write(i, 0, g_data[i][0])
                    sheet1.write(i, 1, g_data[i][1])
                workbook.save(response)
                return response
            elif f_data['action'] == 'imge' and g_data:
                server_url = [data[0] for data in g_data]
                server_count = [int(data[1]) for data in g_data]
                da = json.dumps({'top': top, 'date': d_date, 'server_url': server_url, 'server_count': server_count})
                # da = [server_url,server_count]
                # return render(request,'inters_count.html',{'form':form,'server_url':server_url,'server_count':server_count,'date',d_date})
                return HttpResponse(da)
            else:
                return HttpResponse('检索的数据不存在')
        else:
            return render(request, 'inters_count.html', {'form': form})

    if request.method == 'POST':
        form = intersForm(request.POST)
        data = form.data
        date_year = data['date_year']
        date_month = data['date_month']
        date_day = data['date_day']
        d_date = date_year + date_month + date_day
        top = data['top']
        if d_date is None or top is None:
            return HttpResponse(err_mess)
            return render(request, 'inters_count.html', {'form': form, 'error_mess': err_mess})
        else:
            if d_date is not None and top is not None:
                if date_day in d:
                    date_day = '0' + date_day
                if date_month in d:
                    date_month = '0' + date_month
                d_date = date_year + '_' + date_month + '_' + date_day
                cache_key = d_date + "_requests"
                if read_from_cache(cache_key) == None:
                    datas = inters_count(d_date, top)
                    write_to_cache(cache_key, datas)
                datas = read_from_cache(cache_key)
                # return HttpResponse(datas)
                if datas:
                    paginator = Paginator(datas, 10)
                    try:
                        page = request.GET.get('page')
                    except:
                        page = 1
                    try:
                        page_data = paginator.page(page)
                    except PageNotAnInteger:
                        page_data = paginator.page(1)
                    except EmptyPage:
                        page_data = paginator.page(paginator.num_pages)

                    return render(request, 'inters_count.html',
                                  {'form': form, 'data': page_data, 'page': page, 'd_date': d_date, 'top': top})
                # return render('inters_count.html',{'form':form,'data':datas})
                else:
                    return render(request, 'inters_count.html', {'form': form, 'error_mess': err_mess})


def export_cvs(request):
    if request.method == 'GET':
        form = intersForm(request.GET)
        f_data = json.loads(request.GET.items()[0][1])
        if f_data:
            d_date = f_data['d']
            top = f_data['top']
            g_data = inters_count(d_date, top)
            if g_data:
                # 自定义httpResponse流
                # response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
                response = HttpResponse(content_type='application/octet-stream;charset=utf-8')
                response['mimetype'] = 'application/octet-stream'
                response['Content-Disposition'] = 'attachment; filename=' + d_date + '.xls'
                workbook = xlwt.Workbook(encoding='utf-8')
                # 创建工作页
                sheet1 = workbook.add_sheet(d_date + u'访问情况')
                # 开始写入excel
                row0 = [u'访问url', u'访问次数']
                sheet1.write(0, 0, row0[0])
                sheet1.write(0, 1, row0[1])
                for i in range(1, len(g_data)):
                    sheet1.write(i, 0, g_data[i][0])
                    sheet1.write(i, 1, g_data[i][1])
                workbook.save(response)
                url = request.get_full_path()
                return response
            # return HttpResponse([{'url':url,'response':response}])
            else:
                return HttpResponse('检索的信息不存在')


def get_imge(request):
    data = inters_count()
    return HttpResponse('頁面正在開發中。。。')


def add(request):
    if request.method == 'GET':
        data = request.GET
        if data:
            return HttpResponse(int(data['a']) + int(data['b']))
        else:
            return render(request, 'add.html')


# read cache
def read_from_cache(keys):
    value = cache.get(keys)
    if value == None:
        data = None
    else:
        data = json.loads(value)
    return data


# write cache
def write_to_cache(keys, value):
    cache.set(keys, json.dumps(value), timeout=None)


# 用户中心
@login_required(login_url='/')
def usercenter(request):
    navs = list(Nav.objects.all())
    data = ''
    try:
        cursor = connection.cursor()
        sql = "select `touxiang`,`apptype` from  auth_user where `username`='" + request.user.username + "';"
        cursor.execute(sql)
        data = cursor.fetchall()
    except Exception, e:
        print e
    touxiang = data[0][0]
    app_type = data[0][1]
    touxiang = getTouxiang(touxiang)
    # return HttpResponse(data)
    return render(request, 'usercenter.html', {'navs': navs, 'touxiang': touxiang, 'app_type': app_type},
                  context_instance=RequestContext(request))

def getTouxiang(touxiang):
    if 'default' in touxiang:
        touxiang = touxiang.replace('uploads/', '')
    touxiang = '/static/' + touxiang
    return touxiang

def tupleToStr(tuple):
    return tuple[0] + tuple[1] + '<br/>'


def getMp4Files(parent_dir, files):
    mp4files = []
    for file in files:
        file = parent_dir + '/' + file
        if os.path.isfile(file):
            file_t = (file, 'file')
            mp4files.append(tupleToStr(file_t))
        elif os.path.isdir(file):
            file_t = (file, 'dir')
            mp4files.append(tupleToStr(file_t))
            subdir = file
            subfiles = os.listdir(subdir)
            subfiles = getMp4Files(subdir, subfiles)
            mp4files.extend(subfiles)
        else:
            file_t = (file, 'otherfile')
            mp4files.append(tupleToStr(file_t))
    return mp4files


def categoryFile(files):
    res = []
    for file in files:
        if '.mp4' in file:
            res.append(file.replace('file', '').replace('<br/>', ''))
    return res


def categoryFile1(files):
    sqls = []
    for file in files:
        if '.mp4' in file:
            res = file.replace('file', '').replace('<br/>', '')
            sql = "insert into `django_video`.yjy_mp4(`original_sava_path`,`apptype`,`upload_save_time`) values('%s','yjy_xiyizonghe','57601')"%(res) + ";<br/>"
            sqls.append(sql)
    return sqls


def getMp4s(request):
    if request.method == 'GET':
        apptype = getApptypeName(getUserProperties(request.user.username)['apptype'])
        form = videoForm(request.GET)
        mp4ParentDirs = settings.MP4_SERVER_DIR
        files = os.listdir(mp4ParentDirs)
        mp4files = getMp4Files(mp4ParentDirs, files)
        # return HttpResponse(mp4files)
        res_files = categoryFile1(mp4files)
        return HttpResponse(res_files)


@login_required(login_url='/')
def video_list(request):
    if request.method == 'GET':
        apptype = getApptypeName(getUserProperties(request.user.username)['apptype'])
        form = videoForm(request.GET)
        mp4ParentDirs = settings.MP4_SERVER_DIR
        files = os.listdir(mp4ParentDirs)
        mp4files = getMp4Files(mp4ParentDirs, files)
        # return HttpResponse(mp4files)
        res_files = categoryFile(mp4files)
        paginator = Paginator(res_files, 10)
        try:
            page = request.GET.get('page')
        except:
            page = 1
        try:
            page_data = paginator.page(page)
        except PageNotAnInteger:
            page_data = paginator.page(1)
        except EmptyPage:
            page_data = paginator.page(paginator.num_pages)
        return render(request, 'mp4_list.html', {"mp4_file": page_data, 'form': form, "apptype": apptype})
        return HttpResponse(res_files)


@login_required(login_url='/')
def video_cut(request):
    pass


@login_required(login_url='/')
def video_toonline(request):
    pass


class dbUtil():
    reload(sys)
    sys.setdefaultencoding('utf8')
    import MySQLdb as mdb

    def __init__(self,host,port,user,passwd,dbname):
        try:
            self.dbname = dbname
            self.conn = mdb.connect(host=host, port=port, user=user, passwd=passwd, db=self.dbname,
                                    charset="utf8")
            self.cursor = self.conn.cursor()
        except Exception, e:
            print e

    def close(self):
        self.conn.close()


def getSqls(request):
    res = []
    data = 'aaa'
    dbnames = ['yjy_xiyizonghe', 'yjy_xiyizhiyeyishi', 'yjy_zhongyizonghe', 'tcmsq']
    t_year = int(time.strftime('%Y', time.localtime(time.time())))
    PARENT_IDS = [(i, str(i) + '年真题') for i in range(1988, t_year + 1)]
    for dbname in dbnames:
        db = dbUtil(dbname)
        try:
            t_sql = "select distinct `title`,`app_type` from yjy_im_category where `parent_id` != 0 and `is_del` = 0;"
            db.cursor.execute(t_sql)
            titles = db.cursor.fetchall()
            for parent_id in PARENT_IDS:
                p_sql = "insert into `%s`.yjy_im_category(`id`,`title`,`parent_id`,`app_type`,`is_del`,`order`) values('%d','%s','0','','0','0');" % (
                    db.dbname, int(parent_id[0]), parent_id[1])
                res.append(p_sql)
                # db.cursor.execute(p_sql)
                for title in titles:
                    i_sql = "insert into `%s`.yjy_im_category(`title`,`parent_id`,`app_type`,`is_del`,`order`) values('%s','%s','%s','0','0');" % (
                        db.dbname, title[0], parent_id[0], title[1])
                    res.append(i_sql)
        except Exception, e:
            pass
    for r in res:
        with open("C:/Users/YJY/Desktop/add_chapter.sql", 'ab+') as f:
            f.write(str(r))
            f.write("\r")
    return HttpResponse(len(res))


# mp4视频同步上传处理
@csrf_exempt
def video_upload(request):
    res = dict()
    filenames = []
    upload_time = time.time()
    c_time = time.strftime('%Y_%m_%d_%H_%S_%M', time.localtime(upload_time))
    if request.method == 'POST':
        files = request.FILES.getlist("new-mp4")
        # 将操作写入数据库
        try:
            if files:
                for file in files:
                    filename = file.name
                    filenames.append(filename)
                    apptype = request.POST['apptype']
                    chapter_id = request.POST['chapter_id']
                    parentId = request.POST['parentId']
                    mp4_save_dir = getUploadDir(apptype, chapter_id, parentId)
                    save_filename = mp4_save_dir + '/' + request.user.username + '_' + c_time + '_' + filename
                    save_destination = open(save_filename, 'wb+')  # 打开特定的文件进行二进制写操作
                    for chunk in file.chunks():
                        save_destination.write(chunk)
                    save_destination.close()
                    sql = "insert into `yjy_mp4`(`original_sava_path`,`upload_save_time`,`chapter_id`,`apptype`,`parent_id`,`mp4_download_url`) values('%s','%s','%s','%s','%s','%s')" % (
                        save_filename, upload_time, chapter_id, apptype, parentId,
                        settings.SERVER_DOMAIN)
                    rs = executeSql(sql)
                res['data'] = "".join(filenames) + "上传成功!"
            else:
                res['error'] = "".join(filenames) + '上传文件失败！'
        except Exception, e:
            print e
        finally:
            return HttpResponse(json.dumps(res))


def getUploadDir(apptype, chapter_id, parent_id):
    today = time.strftime('%Y_%m_%d', time.localtime(time.time()))
    dir = settings.MP4_UPLOAD_DIR + '/' + apptype + '/' + parent_id + '/' + chapter_id + '/' + today + '/'
    if not os.path.exists(dir):
        os.makedirs(dir)
    return dir


def executeSql(sql):
    res = ''
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        res = data
    except Exception, e:
        print e
    return res


def getUserProperties(username):
    res = dict()
    sql = "select `id`,`password`,`last_login`,`is_superuser`,`username`,`first_name`,`last_name`,`email`,`is_staff`,`is_active`,`date_joined`,`apptype`,`touxiang`,`department` from auth_user where username='%s'" % (
        username)
    rs = executeSql(sql)
    if rs:
        res['id'] = rs[0][0]
        res['password'] = rs[0][1]
        res['last_login'] = rs[0][2]
        res['is_superuser'] = rs[0][3]
        res['username'] = rs[0][4]
        res['first_name'] = rs[0][5]
        res['last_name'] = rs[0][6]
        res['email'] = rs[0][7]
        res['is_staff'] = rs[0][8]
        res['is_active'] = rs[0][9]
        res['date_joined'] = rs[0][10]
        res['apptype'] = rs[0][11]
        res['touxiang'] = rs[0][12]
        res['department'] = rs[0][13]
    return res


def getAppMp4(apptype, where,search_key,search_time_range,sort):
    res = dict()
    checkMp4Status()
    # sql = "select `id`,`original_sava_path`,`upload_save_time`,`chapter_id`,`apptype`,`cut_staus`,`is_del`,`cut_id`,`video_name`,`mp4_download_url`,`section_id`,`is_named`,`is_category`,`chinese_name`,`parent_id` from yjy_mp4 where original_sava_path like '%" + apptype + "%'"
    sql = "select `id`,`original_sava_path`,`upload_save_time`,`chapter_id`,`apptype`,`cut_staus`,`is_del`,`cut_id`,`video_name`,`mp4_download_url`,`section_id`,`is_named`,`is_category`,`chinese_name`,`parent_id`,`task_id` from yjy_mp4 where apptype='" + apptype + "'"
    if where:
        for k, v in where.items():
            sql += " and " + k + "=" + v
    if search_key != 'None':
        sql += search_key
    if search_time_range != 'None':
        sql += search_time_range
    if sort:
        sql += sort
    rs = executeSql(sql)
    res['count'] = len(rs)
    res['list'] = []
    # return  rs
    for i in range(0, len(rs)):
        tmp = dict()
        tmp['id'] = rs[i][0]
        #tmp['original_save_path'] = rs[i][1].replace(settings.MP4_SERVER_DIR,'').split('/')[-1]
        tmp['original_save_path'] = rs[i][1].replace(settings.MP4_SERVER_DIR,'')
        tmp['upload_save_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rs[i][2]))
        tmp['chapter_id'] = {"id": rs[i][3], "name": getAppTitle(rs[i][4], rs[i][3])}
        tmp['apptype'] = getApptypeName(rs[i][4])
        tmp['cut_status'] = rs[i][5]
        tmp['is_del'] = rs[i][6]
        tmp['cut_id'] = rs[i][7]
        tmp['file_size'] = getMp4Size(rs[i][1])
        tmp['video_name'] = rs[i][8]
        tmp['mp4_download_url'] = rs[i][9]
        tmp['section_id'] = {"id":rs[i][10],"name":getAppSectionOneTitle(rs[i][4],rs[i][10])}
        tmp['is_named'] = rs[i][11]
        tmp['is_category'] = rs[i][12]
        tmp['chinese_name'] = rs[i][13]
        tmp['parent_id'] = {"id": rs[i][14], "name": getAppTitle(rs[i][4], rs[i][14])}
        tmp['task_id'] = {"id":rs[i][15],"name":getTaskName(rs[i][15])}
        res['list'].append(tmp)
    return res

# 获取任务名称
def getTaskName(task_id):
    sql = "select `task_name` from `yjy_mp4_cuttask` where id='%s'"%(task_id)
    rs = executeSql(sql)
    if not rs:
        return ''
    else:
        return rs[0][0]

# 获取文件大小
def getMp4Size(filename):
	if os.path.exists(filename):
		return str(round(os.path.getsize(filename)/1024/1024,2)) + 'M'
	else:
		return '文件可能已删除'


# 获取章节名称
def getAppTitle(apptype, id):
    sql = "select title from " + apptype + ".yjy_im_category where id='" + str(id) + "'"
    rs = executeSql(sql)
    if not rs:
        return ''
    else:
        return rs[0][0]


def getApptypeName(apptype):
    data = {
        "yjy_xiyizonghe": "西医综合",
        "xiyizonghe": "西医综合",
        "yjy_xiyizhiyeyishi": "西医执业医师",
        "tcmsq": "中医执业医师",
        "yjy_zhongyizonghe": "中医综合"
    }
    return data[apptype]


@login_required(login_url='/')
def getMyAppMp4(request):
    if request.method == 'GET':
        User = getUserProperties(request.user.username)
        department = User['department']
        where = dict()
        form = videoForm(request.GET)
        page_nums = request.GET.get('page_nums', '10')
        page = request.GET.get('page', 'None')
        chapter_id = request.GET.get('chapter_id', 'None')
        search_time_range = request.GET.get('search_time_range', 'None')
        search_time_sort = request.GET.get('search_time_sort', '0')
        search_app_type = request.GET.get('app_type', User['apptype'])
        search_key = request.GET.get('search_key', 'None')
        if chapter_id != 'None':
            where['chapter_id'] = chapter_id
        parent_id = request.GET.get('parent_id', 'None')
        if parent_id != 'None':
            where['parent_id'] = parent_id
        section_id = request.GET.get('section_id', 'None')
        if section_id != 'None':
            where['section_id'] = section_id
        if search_key != 'None':
            search_key.strip('\\*')
            search_key = " and `original_sava_path` like '%" + search_key + "%'"
        if search_time_range != 'None':
            search_time_range = ' and `upload_save_time` in ('+ search_time_range +')'
        if search_time_sort == '0':
            search_time_sort = ' order by `upload_save_time` desc'
        if search_time_sort == '1':
            search_time_sort = ' order by `upload_save_time` asc'
        t_MyVideos = getAppMp4(search_app_type, where,search_key,search_time_range,search_time_sort)
        c_url = getUniqUrl(request.get_full_path(), page)
        paginator = Paginator(t_MyVideos['list'], page_nums)
        try:
            page = request.GET.get('page')
        except:
            page = 1
        try:
            MyVideos = paginator.page(page)
        except PageNotAnInteger:
            MyVideos = paginator.page(1)
        except EmptyPage:
            MyVideos = paginator.page(paginator.num_pages)
        return render(request, 'MyAppMp4.html',
                      {'form': form, 'user1': User,'department':department ,'MyVideos': MyVideos, "count": t_MyVideos['count'],
                       "apptype": getApptypeName(search_app_type), "c_url": c_url,"page_nums":page_nums,"apptype_v":search_app_type,"user_apptype_v": getApptypeName(User['apptype'])})
    else:
        return HttpResponse(json.dumps({'code': '555', 'data': '参数错误'}))


def getUniqUrl(url, page_id):
    # if len(url.split('page')) > 1:
    url = url.replace("&page=" + page_id, '').replace("page=" + page_id + "?", '').replace("?page=" + page_id, '')
    # if len(url.split('?')) > 1:
    #     url = url.split('?')[0].replace("?","&") + "?" + url.split('?')[1]
    return urllib.unquote(url)

def getpageUrl(url,page_id):
    if  '?' not in url:
        url = url + '?'
    url.replace("&page=" + page_id, '').replace("page=" + page_id + "?", '').replace("?page=" + page_id, '')
    return urllib.unquote(url)

def mp4_file_download(request):
    if request.method == 'GET':
        id = request.GET['id']
        sql = "select original_sava_path from yjy_mp4 where id='%s'" % (id)
        file_name = executeSql(sql)[0][0]
        if id and file_name:
            def file_iterator(file_name):
                with open(file_name, 'rb') as f:
                    while True:
                        c = f.read()
                        if c:
                            yield c
                        else:
                            break
            response = StreamingHttpResponse(file_iterator(file_name))
            response['Content-Type'] = 'application/octet-stream'
            # response['Content-Type'] = 'video/x-mpg'
            response['Content-Disposition'] = 'attachment;filename="{0}"'.format("_".join(
                file_name.split('/')[-1].split('_')[-2:]))
            return response
        else:
            return HttpResponse(json.dumps({'code': '555', 'data': '参数错误'}))


@csrf_exempt
def chvideoname(request):
    data = dict()
    if request.method == 'POST':
        video_id = request.POST['video_id']
        new_videoname = request.POST['new_videoname']
        if video_id and new_videoname:
            sql = "update yjy_mp4 set chinese_name='%s' where id='%s'" % (new_videoname, video_id)
            rs = executeSql(sql)
            data['code'] = 200
            data['data'] = '视频名称修改成功'
        else:
            data['code'] = 555
            data['data'] = '参数错误'
        return HttpResponse(json.dumps(data))


@csrf_exempt
def p_chgoodsId(request):
    if request.method == 'POST':
        data = dict()
        video_id = request.POST['video_id']
        new_goodsId = request.POST['new_goodsId']
        apptype_v = request.POST['apptype'].encode('utf-8')
        if video_id and new_goodsId and apptype_v:
            apptype = getAppTypeKey(apptype_v)
            try:
                prepare_db = dbUtil(settings.PREPARE_SERVER_IP,3306,settings.PREPARE_DB_USER,settings.PREPARE_DB_PASSWD,apptype)
                sql = "update `%s`.`yjy_im_chat` set goods_id='%s' where id='%s'" % (apptype,new_goodsId, video_id)
                prepare_db.cursor.execute(sql)
                rs = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                sql1 = "update `%s`.`yjy_im_chat_aes` set goods_id='%s' where id='%s'" % (apptype,new_goodsId, video_id)
                prepare_db.cursor.execute(sql1)
                rs1 = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                if apptype == 'yjy_xiyizonghe':
                    sql2 = "update `%s`.`yjy_im_chat_aes_new` set goods_id='%s' where id='%s'" % (apptype,new_goodsId, video_id)
                    prepare_db.cursor.execute(sql2)
                    rs2 = prepare_db.cursor.fetchall()
                    prepare_db.conn.commit()
                data['code'] = 200
                data['data'] = '视频名称修改成功'
                # prepare_db.close()
            except Exception,e:
                data['code'] = 555
                data['data'] = e.message
            # finally:
            #     prepare_db.close()
        else:
            data['code'] = 555
            data['data'] = '参数错误'
        return HttpResponse(json.dumps(data))


@csrf_exempt
def p_chDuration(request):
    if request.method == 'POST':
        data = dict()
        video_id = request.POST['video_id']
        new_duration = request.POST['new_duration']
        apptype_v = request.POST['apptype'].encode('utf-8')
        if video_id and new_duration and apptype_v:
            apptype = getAppTypeKey(apptype_v)
            try:
                prepare_db = dbUtil(settings.PREPARE_SERVER_IP,3306,settings.PREPARE_DB_USER,settings.PREPARE_DB_PASSWD,apptype)
                sql = "update `%s`.`yjy_im_chat` set duration='%s' where id='%s'" % (apptype,new_duration, video_id)
                prepare_db.cursor.execute(sql)
                rs = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                sql1 = "update `%s`.`yjy_im_chat_aes` set duration='%s' where id='%s'" % (apptype,new_duration, video_id)
                prepare_db.cursor.execute(sql1)
                rs1 = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                if apptype == 'yjy_xiyizonghe':
                    sql2 = "update `%s`.`yjy_im_chat_aes_new` set duration='%s' where id='%s'" % (apptype,new_duration, video_id)
                    prepare_db.cursor.execute(sql2)
                    prepare_db.cursor.fetchall()
                    prepare_db.conn.commit()
                data['code'] = 200
                data['data'] = '视频时长修改成功'
            except Exception,e:
                data['code'] = 555
                data['data'] = e.message
            # finally:
            #     prepare_db.close()
        else:
            data['code'] = 555
            data['data'] = '参数错误'
        return HttpResponse(json.dumps(data))


@csrf_exempt
def p_chSort(request):
    if request.method == 'POST':
        data = dict()
        video_id = request.POST['video_id']
        new_sort = request.POST['new_sort']
        apptype_v = request.POST['apptype'].encode('utf-8')
        if video_id and new_sort and apptype_v:
            apptype = getAppTypeKey(apptype_v)
            print apptype
            try:
                prepare_db = dbUtil(settings.PREPARE_SERVER_IP,3306,settings.PREPARE_DB_USER,settings.PREPARE_DB_PASSWD,apptype)
                sql = "update `%s`.`yjy_im_chat` set sort='%s' where id='%s'" % (apptype,new_sort, video_id)
                prepare_db.cursor.execute(sql)
                rs = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                sql1 = "update `%s`.`yjy_im_chat_aes` set sort='%s' where id='%s'" % (apptype,new_sort, video_id)
                prepare_db.cursor.execute(sql1)
                rs1 = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                if apptype == 'yjy_xiyizonghe':
                    sql2 = "update `%s`.`yjy_im_chat_aes_new` set sort='%s' where id='%s'" % (apptype,new_sort, video_id)
                    prepare_db.cursor.execute(sql2)
                    prepare_db.cursor.fetchall()
                    prepare_db.conn.commit()
                data['code'] = 200
                data['data'] = '视频分类编号修改成功'
            except Exception,e:
                data['code'] = 555
                data['data'] = e.message
            # finally:
            #     prepare_db.close()
        else:
            data['code'] = 555
            data['data'] = '参数错误'
        return HttpResponse(json.dumps(data))


@csrf_exempt
def p_chFileSize(request):
    if request.method == 'POST':
        data = dict()
        video_id = request.POST['video_id']
        new_filesize = request.POST['new_filesize']
        apptype_v = request.POST['apptype'].encode('utf-8')
        if video_id and new_filesize and apptype_v:
            apptype = getAppTypeKey(apptype_v)
            prepare_db = dbUtil(settings.PREPARE_SERVER_IP,3306,settings.PREPARE_DB_USER,settings.PREPARE_DB_PASSWD,apptype)
            try:
                sql1 = "update `%s`.`yjy_im_chat_aes` set file_size='%s' where id='%s'" % (apptype,new_filesize, video_id)
                prepare_db.cursor.execute(sql1)
                rs1 = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                if apptype == 'yjy_xiyizonghe':
                    sql2 = "update `%s`.`yjy_im_chat_aes_new` set file_size='%s' where id='%s'" % (apptype,new_filesize, video_id)
                    prepare_db.cursor.execute(sql2)
                    prepare_db.cursor.fetchall()
                    prepare_db.conn.commit()
                data['code'] = 200
                data['data'] = '切片下载文件大小修改成功'
            except Exception,e:
                data['code'] = 555
                data['data'] = e.message
            # finally:
            #     prepare_db.close()
        else:
            data['code'] = 555
            data['data'] = '参数错误'
        return HttpResponse(json.dumps(data))


@csrf_exempt
def p_chserviceId(request):
    if request.method == 'POST':
        data = dict()
        video_id = request.POST['video_id']
        new_serviceId = request.POST['new_serviceId']
        apptype_v = request.POST['apptype'].encode('utf-8')
        if video_id and new_serviceId and apptype_v:
            apptype = getAppTypeKey(apptype_v)
            try:
                prepare_db = dbUtil(settings.PREPARE_SERVER_IP,3306,settings.PREPARE_DB_USER,settings.PREPARE_DB_PASSWD,apptype)
                sql = "update `%s`.`yjy_im_chat` set service_id='%s' where id='%s'" % (apptype,new_serviceId, video_id)
                prepare_db.cursor.execute(sql)
                rs = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                sql1 = "update `%s`.`yjy_im_chat_aes` set service_id='%s' where id='%s'" % (apptype,new_serviceId, video_id)
                prepare_db.cursor.execute(sql1)
                rs1 = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                if apptype == 'yjy_xiyizonghe':
                    sql2 = "update `%s`.`yjy_im_chat_aes_new` set service_id='%s' where id='%s'" % (apptype,new_serviceId, video_id)
                    prepare_db.cursor.execute(sql2)
                    prepare_db.cursor.fetchall()
                    prepare_db.conn.commit()
                data['code'] = 200
                data['data'] = '商品服务id修改成功'
            except Exception,e:
                data['code'] = 555
                data['data'] = e.message
            # finally:
            #     prepare_db.close()
        else:
            data['code'] = 555
            data['data'] = '参数错误'
        return HttpResponse(json.dumps(data))


@csrf_exempt
def p_chvideoname(request):
    if request.method == 'POST':
        data = dict()
        video_id = request.POST['video_id']
        new_videoname = request.POST['new_videoname']
        apptype_v = request.POST['apptype'].encode('utf-8')
        if video_id and new_videoname and apptype_v:
            apptype = getAppTypeKey(apptype_v)
            prepare_db = dbUtil(settings.PREPARE_SERVER_IP,3306,settings.PREPARE_DB_USER,settings.PREPARE_DB_PASSWD,apptype)
            try:
                sql = "update `%s`.`yjy_im_chat` set name='%s' where id='%s'" % (apptype,new_videoname, video_id)
                prepare_db.cursor.execute(sql)
                prepare_db.conn.commit()
                sql1 = "update `%s`.`yjy_im_chat_aes` set name='%s' where id='%s'" % (apptype,new_videoname, video_id)
                prepare_db.cursor.execute(sql1)
                rs1 = prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                if apptype == 'yjy_xiyizonghe':
                    sql2 = "update `%s`.`yjy_im_chat_aes_new` set name='%s' where id='%s'" % (apptype,new_videoname, video_id)
                    prepare_db.cursor.execute(sql2)
                    rs2 = prepare_db.cursor.fetchall()
                    prepare_db.conn.commit()
                data['code'] = 200
                data['data'] = '切片中文名称修改成功'
            except Exception,e:
                data['code'] = 555
                data['data'] = e.message
            # finally:
            #     prepare_db.close()
        else:
            data['code'] = 555
            data['data'] = '参数错误'
        return HttpResponse(json.dumps(data))


def getAppTypeKey(apptype_v):
    data = {
        "西医综合":"yjy_xiyizonghe",
        "西医执业医师":"yjy_xiyizhiyeyishi",
        "中医执业医师":"tcmsq",
         "中医综合":"yjy_zhongyizonghe"
    }
    return data[apptype_v]

@csrf_exempt
def CategoryMp4(request):
    data = dict()
    if request.method == 'GET':
        apptype = request.GET.get('app_type', None)
        parent_id = request.GET.get('parent_id', None)
        chapter_id = request.GET.get('chapter_id', None)
        section_id = request.GET.get('section_id', '0')
        id = request.GET.get('id', None)
        name = request.GET.get('name', None)
        if apptype and parent_id and chapter_id and section_id and name and id:
            sql = "update yjy_mp4 set chinese_name='%s',apptype='%s',parent_id='%s',chapter_id='%s',section_id='%s' where id='%s'" % (name, apptype,parent_id,chapter_id,section_id,id)
            try:
                rs = executeSql(sql)
                data['code'] = 200
                data['data'] = '视频名称修改成功'
            except Exception,e:
                data['code'] = 554
                data['data'] = sql
        else:
            data['code'] = 555
            data['data'] = '参数错误'
        return HttpResponse(json.dumps(data))


@csrf_exempt
def getAppSections(request):
    if request.method == 'GET':
        apptype = request.GET.get('apptype', None)
        chapter_id = request.GET.get('chapter_id', None)
        if apptype and chapter_id:
            res = []
            sections = getAppSectionTitle(apptype, chapter_id)
            for i in range(0, len(sections)):
                res.append(list(sections[i]))
            return HttpResponse(json.dumps(res))
        else:
            data = dict()
            data['code'] = 555
            data['data'] = '参数错误'
            return HttpResponse(json.dumps(data))


def getAppSectionTitle(apptype, chapter_id):
    sql = "select `id`,`title` from `%s`.yjy_im_chapter where category_id='%s'" % (apptype, chapter_id)
    rs = executeSql(sql)
    return rs

def getAppSectionOneTitle(apptype, section_id):
    sql = "select `id`,`title` from `%s`.yjy_im_chapter where id='%s'" % (apptype, section_id)
    try:
        rs = executeSql(sql)
        return rs[0][1]
    except Exception,e:
        return 'None'

@csrf_exempt
def p_show_video(request):
    res = dict()
    res['code'] = '555'
    res['data'] = '参数错误'
    if request.method == 'POST':
        id = request.POST.get('video_id',None)
        apptype_v = request.POST['apptype'].encode('utf-8')
        apptype = getAppTypeKey(apptype_v)
        prepare_db = dbUtil(settings.PREPARE_SERVER_IP,3306,settings.PREPARE_DB_USER,settings.PREPARE_DB_PASSWD,apptype)
        if id and apptype:
            try:
                sql = "update `%s`.`yjy_im_chat` set `status`=1 where id='%s'"%(apptype,str(id))
                prepare_db.cursor.execute(sql)
                prepare_db.cursor.fetchall()
                prepare_db.conn.commit()

                sql1 = "update `%s`.`yjy_im_chat_aes` set `status`=1 where id='%s'"%(apptype,str(id))
                prepare_db.cursor.execute(sql1)
                prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                if apptype == 'yjy_xiyizonghe':
                    sql2 = "update `%s`.`yjy_im_chat_aes_new` set `status`=1 where id='%s'"%(apptype,str(id))
                    prepare_db.cursor.execute(sql2)
                    prepare_db.cursor.fetchall()
                    prepare_db.conn.commit()
                res['code'] = '200'
                res['data'] = 'ok'
            except Exception,e:
                res['code'] = '555'
                res['data'] = json.dumps(e)
        return HttpResponse(json.dumps(res))


@csrf_exempt
def p_hide_video(request):
    res = dict()
    res['code'] = '555'
    res['data'] = '参数错误'
    if request.method == 'POST':
        id = request.POST.get('video_id',None)
        apptype_v = request.POST['apptype'].encode('utf-8')
        apptype = getAppTypeKey(apptype_v)
        prepare_db = dbUtil(settings.PREPARE_SERVER_IP,3306,settings.PREPARE_DB_USER,settings.PREPARE_DB_PASSWD,apptype)
        if id and apptype:
            try:
                sql = "update `%s`.`yjy_im_chat` set `status`=0 where id='%s'"%(apptype,str(id))
                prepare_db.cursor.execute(sql)
                prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                sql1 = "update `%s`.`yjy_im_chat_aes` set `status`=0 where id='%s'"%(apptype,str(id))
                prepare_db.cursor.execute(sql1)
                prepare_db.cursor.fetchall()
                prepare_db.conn.commit()
                if apptype == 'yjy_xiyizonghe':
                    sql2 = "update `%s`.`yjy_im_chat_aes_new` set `status`=0 where id='%s'"%(apptype,str(id))
                    prepare_db.cursor.execute(sql2)
                    prepare_db.cursor.fetchall()
                    prepare_db.conn.commit()
                res['code'] = '200'
                res['data'] = 'ok'
            except Exception,e:
                res['code'] = '555'
                res['data'] = json.dumps(e)
        return HttpResponse(json.dumps(res))


@csrf_exempt
def p_chapptype(request):
    res = dict()
    res['code'] = '555'
    res['data'] = '参数错误'
    if request.method == 'POST':
        id = request.POST.get('video_id',None)
        apptype_v = request.POST['apptype'].encode('utf-8')
        apptype = getAppTypeKey(apptype_v)
        new_apptype = request.POST.get('new_apptype',None)
        if id and apptype and new_apptype:
            try:
                sql = "update `%s`.`yjy_im_chat` set `app_type`='%s' where id='%s'"%(apptype,new_apptype,str(id))
                rs = executeSql(sql)
                sql1 = "update `%s`.`yjy_im_chat_aes` set `app_type`='%s' where id='%s'"%(apptype,new_apptype,str(id))
                rs = executeSql(sql1)
                if apptype == 'yjy_xiyizonghe':
                    sql2 = "update `%s`.`yjy_im_chat_aes_new` set `app_type`='%s' where id='%s'"%(apptype,new_apptype,str(id))
                    rs = executeSql(sql2)
                res['code'] = '200'
                res['data'] = 'ok'
            except Exception,e:
                res['code'] = '555'
                res['data'] = e
        return HttpResponse(json.dumps(res))


@csrf_exempt
def delete_video(request):
    res = dict()
    res['code'] = '555'
    res['data'] = '参数错误'
    if request.method == 'GET':
        id = request.GET.get('id',None)
        if id:
            try:
                sql = "update yjy_mp4 set is_del=1 where id='%s'"%(str(id))
                rs = executeSql(sql)
                res['code'] = '200'
                res['data'] = 'ok'
            except Exception,e:
                res['code'] = '555'
                res['data'] = '参数错误'
        return HttpResponse(json.dumps(res))

def recovery_video(request):
    res = dict()
    res['code'] = '555'
    res['data'] = '参数错误'
    if request.method == 'GET':
        id = request.GET.get('id',None)
        if id:
            try:
                sql = "update yjy_mp4 set is_del=0 where id='%s'"%(str(id))
                rs = executeSql(sql)
                res['code'] = '200'
                res['data'] = 'ok'
            except Exception,e:
                res['code'] = '555'
                res['data'] = '参数错误'
        return HttpResponse(json.dumps(res))

def chVideoSection(request):
    res = dict()
    res['code'] = '555'
    res['data'] = '参数错误'
    if request.method == 'POST':
        new_section_id = request.POST.get('new_section_id',None)
        video_id = request.POST.get('video_id',None)
        if video_id and new_section_id:
            try:
                sql = "update yjy_mp4 set section_id='%s' where id='%s'"%(str(new_section_id),str(video_id))
                rs = executeSql(sql)
                res['code'] = '200'
                res['data'] = 'ok'
            except Exception,e:
                res['code'] = '500'
                res['data'] = '修改失败'
        else:
            res['code'] = '555'
            res['data'] = '参数错误'
        return HttpResponse(json.dumps(res))

@login_required(login_url="/")
@csrf_exempt
def VideoCenter(request):
    User = getUserProperties(request.user.username)
    if request.method == 'POST':
        tasks = getTasks(User['username'])
        return HttpResponse(json.dumps(tasks))
    elif request.method == 'GET':
        tasks = getTasks(User['username'])
        return render(request,"videoCenter_listCut.html",{'user1':User,'touxiang':getTouxiang(User['touxiang']),'tasks':tasks})

def TimeFormat(timestamp):
    return time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(timestamp))


def checkTaskStauts():
    sql = "select `id`,`created_time`,`expired_time` from `yjy_mp4_cuttask` where `status`=0"
    # logger = logging.getLogger('django')
    # logger = logging.getLogger('django.request')
    rs = executeSql(sql)
    if len(rs) > 0:
        for r in rs:
            logging.debug(abs(int(time.time()) - int(r[2])))
            if int(r[2]) - int(time.time()) < 0:
                sql1 = "update yjy_mp4_cuttask set status=1 where id='%s'"%(r[0])
                rs1 = executeSql(sql1)
            if abs(int(time.time()) - int(r[2])) > 86400:
                sql2 = "update yjy_mp4_cuttask set is_del=1 where id='%s'"%(r[0])
                rs2 =  executeSql(sql2)

# 获取用户的切片任务队
def getTasks(tasker):
    tasks = dict()
    # 先扫描并标记过期的任务队列
    checkTaskStauts()
    sql = "select `id`,`tasker`,`task_name`,`created_time`,`expired_time`,`others`,`status`  from `yjy_mp4_cuttask` where `is_del`='0' order by status"
    try:
        rs = executeSql(sql)
        t = []
        m = []
        for r in rs:
            if r[6] == 0:
                t1 = dict()
                t1['id'] = r[0]
                t1['tasker'] = r[1]
                t1['task_name'] = r[2]
                t1['created_time'] = TimeFormat(int(r[3]))
                t1['expired_time'] = TimeFormat(int(r[4]))
                t1['others'] = r[5]
                t.append(t1)
            if r[6] == 1:
                t1 = dict()
                t1['id'] = r[0]
                t1['tasker'] = r[1]
                t1['task_name'] = r[2]
                t1['created_time'] = TimeFormat(int(r[3]))
                t1['expired_time'] = TimeFormat(int(r[4]))
                t1['others'] = r[5]
                m.append(t1)
        tasks['count'] = len(rs)
        tasks['list_able'] = t
        tasks['list_disable'] = m
    except Exception,e:
        tasks['list'] = 'None'
        tasks['count'] = 0
    return tasks

@csrf_exempt
def cutCenterList(request):
    if request.method == 'POST':
        User = getUserProperties(request.user.username)
        tasks = getTasks(User['username'])
        return HttpResponse(json.dumps(tasks))

@csrf_exempt
@login_required(login_url="/")
def checkTaskName(request):
    res = dict()
    if request.method == 'GET':
        new_task_name = request.GET.get('new_task_name',None)
        if new_task_name:
            try:
                sql = "select task_name from `yjy_mp4_cuttask` where task_name='%s'"%(new_task_name)
                rs = executeSql(sql)
                if len(rs) > 1:
                    res['code'] = '202'
                    res['data'] = '任务名已存在'
                else:
                    res['code'] = '200'
                    res['data'] = '任务名不存在'
                return  HttpResponse(json.dumps(res))
            except:
                res['code'] = '555'
                res['data'] = new_task_name
                return  HttpResponse(json.dumps(res))

@csrf_exempt
@login_required(login_url="/")
def task_add(request):
    if request.method == 'POST':
        sql =''
        task_name = request.POST.get("task_name",None)
        task_expired_time = request.POST.get("task_expired_time",None)
        task_input_infos = request.POST.get("task_input_infos",None)
        if task_name and task_expired_time and task_input_infos:
            try:
                sql = "insert into `yjy_mp4_cuttask`(`tasker`,`task_name`,`created_time`,`expired_time`,`others`,`is_del`) values('%s','%s','%s','%s','%s','0')"%(request.user.username,task_name,str(int(time.time())),str((int(time.time())+int(task_expired_time)*86400)),task_input_infos)
                rs = executeSql(sql)
                if not rs:
                    return HttpResponse(json.dumps({'data':"ok","code":"200"}))
                else:
                    return HttpResponse(json.dumps({'data':sql,"code":"500"}))
            except Exception,e:
                print e
                return HttpResponse(json.dumps({'data':sql,"code":"500"}))
        else:
            return HttpResponse(json.dumps({'data':"not ok","code":"502"}))


def addMp4ToCut(request):
    res = dict()
    if request.method == 'POST':
        video_id = request.POST.get('video_id',None)
        task_id = request.POST.get('task_id',None)
        if video_id and task_id:
            sql = "update `yjy_mp4` set `task_id`='%s',cut_staus=1 where id='%s'"%(task_id,video_id)
            try:
                rs = executeSql(sql)
                res['code'] = '200'
                res['data'] = 'ok'
            except Exception,e:
                print e
                res['code'] = '500'
                res['data'] = e
            finally:
                return HttpResponse(json.dumps(res))
        else:
            res['code'] = '555'
            res['data'] = '参数错误'
            return HttpResponse(json.dumps(res))

# 任务队列详情
def task_detail(request):
    res = ''
    if request.method == 'GET':
        checkMp4Status()
        task_id = request.GET.get('id',None)
        task_name = getTaskName(task_id)
        checkMp4Status()
        sql = "select `apptype`,`chapter_id`,`parent_id`,`section_id`,`chinese_name`,`cut_staus`,`cut_id`,`id`,`original_sava_path` from `yjy_mp4` where task_id='%s' and `cut_staus`=1 order by `apptype`"%(task_id)
        rs = executeSql(sql)
        tmp = []
        for r in rs:
            tmp1 = dict()
            tmp1['app_type'] = getApptypeName(r[0])
            tmp1['cut_id'] = r[6]
            tmp1['parent_id'] = getAppTitle(r[0],r[1])
            tmp1['chapter_id'] = getAppTitle(r[0],r[2])
            tmp1['section_id'] =  getAppSectionOneTitle(r[0],r[3])
            tmp1['chinese_name'] = r[4]
            tmp1['cut_status'] = r[5]
            tmp1['id'] = r[7]
            tmp1['original_sava_path'] = r[8].split('/')[-1]
            tmp.append(tmp1)
        paginator = Paginator(tmp, 15)
        try:
            page = request.GET.get('page')
        except:
            page = 1
        try:
            task_videos = paginator.page(page)
        except PageNotAnInteger:
            task_videos = paginator.page(1)
        except EmptyPage:
            task_videos = paginator.page(paginator.num_pages)

        return render(request,'task_detail.html',{'task_videos':task_videos,'task_name':task_name,'task_id':task_id,"videos_nums":len(tmp),"videos":json.dumps(tmp)})


# 检查MP4状态
@csrf_exempt
def checkMp4Status():
    sql = "select `id`,`cut_id` from yjy_mp4 where `cut_staus`='2';"
    print sql
    rs = executeSql(sql)
    print rs
    for r in rs:
        if r[1] and r[0]:
            sql1 = "select `result` from `django_celery_results_taskresult` where `task_id`='%s'"%(r[1])
            result = executeSql(sql1)
            print result
            print sql1,result
            if result != '切片顺利完成!' and result:
                sql2 = "update `yjy_mp4` set `cut_staus`='7' where id='%s'"%(r[0])
                print sql2
                executeSql(sql2)


# 批量任务切片
@csrf_exempt
def start_task(request):
    if request.method == 'POST':
        task_id = request.POST.get('task_id',None)
        task_name = getTaskName(task_id)
        sql = "select `id`,`original_sava_path`,`cut_staus` from yjy_mp4 where task_id='%s'"%(task_id)
        videos = executeSql(sql)
        for video in videos:
            if int(video[2]) == 1:
                res = cut_video.delay(task_id,video[0],video[1])
                res_id = res.id
                sql1 = "update yjy_mp4 set `cut_id`='%s',`cut_staus`='2' where id='%s' and `cut_staus`='1'"%(res_id,video[0])
                executeSql(sql1)
            # 一次task 只能用一次
            # sql2 = "update `yjy_mp4_cuttask` set `is_del`=1 where `id`='%s'"%(task_id)
            # executeSql(sql2)
        return HttpResponse(json.dumps({"code":"200","videos":videos}))

# 删除任务切片MP4
@csrf_exempt
def DelteMp4ToCut(request):
    if request.method == 'POST':
        video_id = request.POST.get('video_id',None)
        sql = "update yjy_mp4 set task_id='0',cut_staus='0' where id='%s'"%(video_id)
        try:
            rs = executeSql(sql)
            return HttpResponse(json.dumps({"code":"200","mess":"ok"}))
        except Exception,e:
            return HttpResponse(json.dumps({"code":"500","mess":e}))

# 查看MP4切片后的记录
@csrf_exempt
def mp4AferCut(request):
    reload(sys)
    sys.setdefaultencoding('utf-8')
    if request.method == 'GET':
        res = dict()
        video_id = request.GET.get('id',None)
        sql = "select `id`,`video_id`,`thumb_url`,`resolution`,`duration`,`m3u8_serverPath`,`aes_m3u8_serverPath`,`file_size`,`cut_time`,`status` from `mp4_cut_recoder` where `video_id`='%s'"%(video_id)
        rs = executeSql(sql)
        appinfos = getApptypes(video_id)[0]
        apptype_v = getApptypeName(appinfos[0])
        parent = {'id':int(appinfos[1]),'name':getAppTitle(appinfos[0],appinfos[1])}
        chapter = {'id':int(appinfos[2]),'name':getAppTitle(appinfos[0],appinfos[2])}
        section = {'id':appinfos[3],'name':getAppSectionOneTitle(appinfos[0],appinfos[3])}
        chinese_name = getApptypes(video_id)[0][4]
        tmp = []
        for r in rs:
            tmp1 = dict()
            tmp1['id'] = r[0]
            tmp1['video_id'] = r[1]
            tmp1['thumb_url'] = r[2].replace('/data/hls/','http://m1.letiku.net/')
            tmp1['resolution'] = r[3]
            tmp1['duration'] = r[4]
            tmp1['m3u8_serverPath'] = r[5].replace('/data/hls/','http://m1.letiku.net/')
            tmp1['aes_m3u8_serverPath'] = r[6].replace('/data/hls/','http://m1.letiku.net/')
            tmp1['file_size'] = r[7]
            tmp1['cut_time'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(float(r[8])))
            tmp1['status'] = r[9]
            tmp1['apptype'] = apptype_v
            tmp1['parent_id'] = parent
            tmp1['chapter_id'] = chapter
            tmp1['section_id'] = section
            tmp1['chinese_name'] = chinese_name
            tmp.append(tmp1)
        res['list'] = tmp
        return render(request,'cut_info.html',{'video_id':video_id,'videos':res})
        return HttpResponse(json.dumps(res))

# 根据id获取信息
def getApptypes(video_id):
    sql = "select `apptype`,`parent_id`,`chapter_id`,`section_id`,`chinese_name` from yjy_mp4 where id='%s'"%(video_id)
    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        data = cursor.fetchall()
        res = data
        return res
    except Exception, e:
        print e

# 单个MP4上到预上线
@csrf_exempt
def OneToPrepare(request):
    import MySQLdb as mdb
    if request.method == 'POST':
        recoder_id = request.POST.get('recoder_id',None)
        apptypeset = request.POST.get('apptypeset',None)
        if recoder_id:
            sql = "select `id`,`video_id`,`thumb_url`,`resolution`,`duration`,`m3u8_serverPath`,`aes_m3u8_serverPath`,`file_size`,`status` from `mp4_cut_recoder` where id='%s'"%(recoder_id)
            recoders = executeSql(sql)[0]
            appinfos = getApptypes(recoders[1])[0]
            app_type = appinfos[0]
            parent_id = int(appinfos[1])
            chapter_id = int(appinfos[2])
            if appinfos[3]:
                section_id = int(appinfos[3])
            else:
                section_id = 'None'
            video_name = appinfos[4]
            if int(parent_id) > 1995:
                return HttpResponse(json.dumps({"code":200,"message":"真题视频暂不支持上线!"}))
            else:
                print app_type,parent_id,chapter_id,section_id,video_name
                goods_id = getServiceGoodsId(app_type,parent_id,'goods_id')
                service_id = getServiceGoodsId(app_type,parent_id,'service_id')
                sort = 0
                db_conn = mdb.connect(settings.PREPARE_SERVER_IP, 'django', 'django@2017', app_type)
                cursor = db_conn.cursor()
                db_conn.set_character_set('utf8')
                cursor.execute('SET NAMES utf8;')
                cursor.execute('SET character_set_connection=utf8;')
                data = ''
                try:
                    download_url = recoders[6].replace('/data/hls','http://m1.letiku.net')
                    media_url = download_url
                    prepare_thumb_path = syncThumbToPrepare(app_type,settings.PREPARE_SERVER_IP,recoders[2].replace('http://m1.letiku.net/','/data/hls/'))
                    sql1 = "insert into `yjy_im_chat`(`name`,`thumb`,`status`,`started`,`ended`,`created`,`service_id`,`goods_id`,`media_url`,`chapter_id`,`duration`,`sort`,`app_type`) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(video_name,prepare_thumb_path,1,int(time.time()),int(time.time()),int(time.time()),service_id,goods_id,media_url,chapter_id,recoders[4],sort,apptypeset)
                    print sql1
                    cursor.execute(sql1)
                    db_conn.commit()
                    sql2 = "insert into `yjy_im_chat_aes`(`name`,`thumb`,`status`,`started`,`ended`,`created`,`service_id`,`goods_id`,`media_url`,`chapter_id`,`duration`,`sort`,`file_size`,`app_type`) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(video_name,prepare_thumb_path,1,int(time.time()),int(time.time()),int(time.time()),service_id,goods_id,media_url,chapter_id,recoders[4],sort,recoders[7].replace('M',''),apptypeset)
                    cursor.execute(sql2)
                    print sql2
                    db_conn.commit()
                    if 'xiyizonghe' in app_type:
                        sql3 = "insert into `yjy_im_chat_aes_new`(`name`,`thumb`,`status`,`started`,`ended`,`created`,`service_id`,`goods_id`,`media_url`,`is_del`,`chapter_id`,`duration`,`sort`,`download_url`,`file_size`,`app_type`,`category_id`) values('%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(video_name,prepare_thumb_path,1,int(time.time()),int(time.time()),int(time.time()),service_id,goods_id,media_url,0,section_id,recoders[4],sort,download_url,recoders[7].replace('M',''),apptypeset,chapter_id)
                        cursor.execute(sql3)
                        print sql3
                        db_conn.commit()
                    # 更改MP4状态
                    sql4 = "update yjy_mp4 set `cut_staus`=4 where id='%s'"%(recoders[1])
                    print sql4
                    executeSql(sql4)
                    # 更改切片记录状态
                    sql5= "update `mp4_cut_recoder` set `status`=1 where id='%s'"%(recoders[0])
                    executeSql(sql5)
                    print sql5
                    return HttpResponse(json.dumps({'code':200,'message':"已成功上到预上线!"}))
                except mdb.Error, e:
                    print e
                    return HttpResponse(json.dumps({'code':500,'message':e}))
                    db_conn.close()
        else:
            return HttpResponse(json.dumps({'code':500,'message':'参数错误'}))


# 将视频服务器上的切片略缩图图片传送给预上线或者线上
def syncThumbToPrepare(app_type,server,client_thumb_path):
    today = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    ssh = pmk.SSHClient()
    ssh.set_missing_host_key_policy(pmk.AutoAddPolicy())
    ssh.connect(server,2282,'root')
    thumb_path =''
    if 'xiyizonghe' in app_type:
        thumb_path = '/www/pre_social_web/sandbox.xiyizonghe.letiku.net/Uploads/Admin/' + today + os.sep
    else:
        if app_type == 'tcmsq':
            thumb_path = '/www/pre_social_web/sandbox.social/tcmsq/Uploads/Admin/' + today + os.sep
        if app_type == 'tcms':
            thumb_path = '/www/pre_social_web/sandbox.social/zhongyizonghe_new/Uploads/Admin/' + today + os.sep
        if 'xiyizhiyeyishi' in app_type:
            thumb_path = '/www/pre_social_web/sandbox.social/xiyizhiyeyishi/Uploads/Admin/' + today + os.sep
    cmd = 'mkdir -p ' + thumb_path
    stdin,stdout,stderr = ssh.exec_command(cmd)
    cmd1 = 'scp -rp -P2282 '+ client_thumb_path +' root@' + server + ':' + thumb_path
    print cmd1
    write_test(cmd1)
    rs1 = commands.getstatusoutput(cmd1)
    server_thumb_path = today + os.sep + client_thumb_path.split('/')[-1]
    return server_thumb_path

def write_test(mess):
    today = time.strftime('%Y_%m_%d',time.localtime(time.time()))
    file='/tmp/log_'+today + '.log'
    with open(file,"a+") as f:
        f.write(mess)

# 获取视频的service_id  goods_id   res_type 分为两种类型 goods_id 和sevices_id
def getServiceGoodsId(apptype,parent_id,res_type):
    return settings.APP_GOOD_SERVICE_IDS[apptype][res_type][str(parent_id)]


def video_online(request):
    return  render(request,'video_preare.html',{})

def getPrepareList(apptype, where,search_key,search_time_range,sort):
    res = dict()
    prepare_db = dbUtil(settings.PREPARE_SERVER_IP,3306,settings.PREPARE_DB_USER,settings.PREPARE_DB_PASSWD,apptype)
    sql = "select `id`,`name`,`thumb`,`status`,`created`,`service_id`,`goods_id`," \
                  "`app_type`,`media_url`,`is_del`,`chapter_id`,`duration`,`sort`,`file_size` from "\
                  + apptype + ".yjy_im_chat_aes where `is_del`=0"
    if apptype == 'yjy_xiyizonghe':
        sql = "select `id`,`name`,`thumb`,`status`,`created`,`service_id`,`goods_id`," \
                  "`app_type`,`media_url`,`is_del`,`chapter_id`,`duration`,`sort`,`file_size` from "\
                  + apptype + ".yjy_im_chat_aes_new where `is_del`=0"
    if where:
        for k, v in where.items():
            sql += " and " + k + "=" + v
    if search_key != 'None':
        sql += search_key
    if search_time_range != 'None':
        sql += search_time_range
    sql += sort
    prepare_db.cursor.execute(sql)
    print sql
    res = prepare_db.cursor.fetchall()
    # prepare_db.close()
    return res

def video_prepare(request):
    if request.method == 'GET':
        apptype = request.GET.get('app_type',None)
        User = getUserProperties(request.user.username)
        if not apptype:
            apptype = User['apptype']
        apptype_v = getApptypeName(apptype)
        department = User['department']
        page_nums = request.GET.get('page_nums', '15')
        page = request.GET.get('page', 'None')
        chapter_id = request.GET.get('chapter_id', 'None')
        search_time_range = request.GET.get('search_time_range', 'None')
        # search_app_type = request.GET.get('app_type', User['apptype'])
        search_key = request.GET.get('search_key', 'None')
        sort = request.GET.get('sort','0')
        where = dict()
        parent = ''
        chapter = ''
        section = ''
        if chapter_id != 'None':
            chapter = getAppTitle(apptype,chapter_id)
            if apptype == 'yjy_xiyizonghe':
                where['category_id'] = chapter_id
            else:
                where['chapter_id'] = chapter_id
        parent_id = request.GET.get('parent_id', 'None')
        if parent_id != 'None':
            parent = getAppTitle(apptype,parent_id)
        section_id = request.GET.get('section_id', 'None')
        if section_id != 'None':
            section = getAppTitle(apptype,section_id)
            if apptype == 'yjy_xiyizonghe':
                where['chapter_id'] = section_id
                del where['category_id']
        if sort == '0':
            sort = ' order by `sort` asc'
        if sort == '1':
            sort = ' order by `sort` desc'
        if search_key != 'None':
            search_key.strip('\\*')
            search_key = " and `name` like '%" + search_key + "%'"
        MyVideos = ''
        tmp = getPrepareList(apptype,where,search_key,search_time_range,sort)
        videos = []
        for t in tmp:
            t1 = dict()
            t1['id'] = t[0]
            t1['name'] = t[1]
            t1['thumb'] = t[2]
            t1['status'] = t[3]
            t1['created'] = TimeFormat(t[4])
            t1['service_id'] = t[5]
            t1['goods_id'] = t[6]
            t1['app_type'] = t[7]
            t1['media_url'] = {'m3u8':t[8].replace('aes_','').replace('_aes',''),'value':(t[8].split('/')[-1])}
            t1['chapter_id'] = t[9]
            t1['duration'] = t[11]
            t1['sort'] = t[12]
            t1['file_size'] = t[13]
            # t1['parent'] = getAppTitle(t[7],)
            videos.append(t1)
        paginator = Paginator(videos, page_nums)
        page_list = [ i for i in range(1,paginator.num_pages+1)]
        c_url = getpageUrl(request.get_full_path(), page)
        page_list = []
        try:
            page = request.GET.get('page')
            page_list = [ i for i in range(1,paginator.num_pages+1)]
            p_pages = [ i for i in range(1,int(len(page_list)/10)+1)]
        except:
            page = 1
        try:
            MyVideos = paginator.page(page)
        except PageNotAnInteger:
            MyVideos = paginator.page(1)
        except EmptyPage:
            MyVideos = paginator.page(paginator.num_pages)
        return  render(request,'video_prepare.html',{'chapter':chapter,'parent':parent,'section':section,'page_nums':page_nums,'p_pages':p_pages,"videos":MyVideos,'c_url':c_url,'count':len(videos),'department':department,'apptype':apptype_v,'apptype_v':apptype,'page_list':page_list})

# 发送邮件(含任务失败和成功邮件)
def sendMail(task_id,video_id,stauts='ok'):
    videoInfos = getApptypes(video_id)
    video_name = videoInfos[4]
    apptype_v = getApptypeName(videoInfos[0])
    parent = getAppTitle(videoInfos[0],int(videoInfos[1]))
    chapter = getAppTitle(videoInfos[0],int(videoInfos[2]))
    section = getAppSectionOneTitle(videoInfos[0],videoInfos[3])
    sql = "select `email` from `auth_user` where apptype='%s'"%(videoInfos[0])
    # 给app部门组发送邮件
    apptypeEmails = [ r[0] for r in executeSql(sql)]
    userEmail = getUserProperties(username)
    now = time.strftime('%Y年%m月%d日 %H:%M:%S',time.localtime(time.time()))
    if type == 'ok':
        subject = now + ":医教园视频切片进度提醒"
        text_content = now + ':切片视频:' + apptype_v + '--' + parent + '--' + chapter
        if section:
            text_content += '--' + section
        text_content += video_name
        html_content = '<h3><'+apptype_v+'组的成员们:以下视频已切片成功:'+'</h3><p><h2>'+text_content+'</h2></p><p><a href="http://101.201.31.40:88/video/mp4AferCut?id='+ video_id +'">点击这里可以查看切片详情并上传到<strong>预上线<strong></a></p><ul><li>注1.上到预上线后可直接通过测试app测试</li><li>2.测试环境通过后请通知后台人员上线</li></ul>'
        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM, apptypeEmails)
        msg.attach_alternative(html_content, "text/html")
        res = msg.send()
        if res >=1 :
            return json.dumps({"date":now,"code":200,'mess':"给"+userEmail+"发送邮件成功"})
        else:
            return json.dumps({"date":now,"code":200,'mess':"给"+userEmail+"发送邮件失败"})
    else:
        subject = now + ":医教园视频切片失败提醒"
        text_content = now + ':切片视频:' + apptype_v + '--' + parent + '--' + chapter
        if section:
            text_content += '--' + section
        text_content += video_name
        html_content = '<h3><'+apptype_v+'切片失败了:'+'</h3><p><h2>'+text_content+'</h2></p><p><a href="http://101.201.31.40:88/video/mp4AferCut?id='+ video_id +'"></a></p>'
        msg = EmailMultiAlternatives(subject, text_content, settings.EMAIL_FROM,['769079707@qq.com'])
        msg.attach_alternative(html_content, "text/html")
        res = msg.send()
        if res >=1 :
            return json.dumps({"date":now,"code":200,'mess':"给运维负责人发送邮件成功"})
        else:
            return json.dumps({"date":now,"code":200,'mess':"给运维负责人发送邮件失败"})

def p_toonline(request):
    if request.method == 'POST':
        res = dict()
        apptype = request.POST.get('apptype','None')
        if apptype:
            udb = updateDbTool(apptype)
            mess = udb.update_to_online()
            res['code'] = 200
            res['data'] = mess
        else:
            res['code'] = 555
            res['data'] = '参数错误!'
        return HttpResponse(json.dumps(res))
