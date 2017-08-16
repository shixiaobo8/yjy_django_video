#! /usr/bin/env python
# -*- coding:utf8 -*-
from django.http import HttpResponseRedirect
from django.shortcuts import render,redirect
from django.contrib import auth 
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.http import HttpResponse,JsonResponse
from video.forms import videoForm,LoginForm,registerForm,ImEditForm,NewForm,intersForm
from django.shortcuts import render_to_response
from django.core.paginator import Paginator,InvalidPage,EmptyPage,PageNotAnInteger
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from .models import Nav
import json,os,sys,xlwt,requests
#navs = list(Nav.objects.all())

@csrf_exempt
def page_not_found(request):
 	return render_to_response('404.html')

@csrf_exempt
def page_error(request):
	return render_to_response('500.html')

# Create your views here.
def addIm(request):
	form = videoForm(request.POST)
	return render(request,'index.html',{'form':form})

def getChapterById(request):
	if request.method == 'GET':
		form = videoForm(request.GET)
		apptype = form.data['apptype']
		parentId = form.data['id']
		chapters1 = []
		chaps = getChapters(apptype,int(parentId))
		for i in range(0,len(chaps)):
			chapters1.append(chaps[i][0])
		return HttpResponse(json.dumps(chapters1))

def getChapters(apptype,id):
	try:
		cursor = connection.cursor()
		chapters = []
		sql = "select title from %s.yjy_im_category where parent_id=%d"%(apptype,id)
		cursor.execute(sql)
		titles = cursor.fetchall()
		return titles
	except Exception,e:
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
                if form.is_valid():
			human = True
                        #return HttpResponse(data.items())
                        user = authenticate(username=username,password=password)
                        if user is not None and user.is_active:
                                auth.login(request,user)
                                #return render(request,'im_list.html',{'user':user,'navs':navs})
                                return redirect('im_list.html')
                        else:
                                login_mess = '用户名或者密码不正确'
                                return render(request,'login.html',{'form':form,'login_mess':login_mess})
        else:
                login_mess = 'http method not allowed'
                return HttpResponse(login_mess)

def register(request):
        if request.method == 'POST':
                form = registerForm(request.POST)
                if form.is_valid():
                        data = form.data
                        if  User.objects.filter(username=data['username']):
                                reg_error = '用户名已存在!'
                                return render(request,'register.html',{'reg_error':reg_error,'form':form})
                        else:
                                user = User()
                                user.set_password(data['password'])
                                user.username = data['username']
                                user.email = data['email']
                                user.apptype = data['app_type']
                                user.save()
				User.objects.filter(username=data['username']).update(apptype=data['app_type'])
                                return HttpResponseRedirect('/im_list.html')
                else:
                        message = "<b style='color:red;'>invalid</b> please keep slient and keep friendship and keep smile ^_^ and keep doing yourself and belive yourself ! "
                        reg_error = form.errors
                        return render(request,'register.html',{'message':message,'reg_error':reg_error,'form':form })
        if request.method == 'GET':
                return HttpResponse(form.data)
                form = registerForm(request.POST)
                return HttpResponseRedirect(request,'/register.html',{'form':form})

def index(request):
        form = LoginForm(request.POST)
        navs = list(Nav.objects.all())
        return render(request,'login.html',{'navs':navs,'form':form})

def reg(request):
        form = registerForm(request.POST)
        return render(request,'register.html',{'form':form})

def imList(request):
	navs = list(Nav.objects.all())
        return render(request,'im_list.html',{'navs':navs})

def logout(request):
	auth.logout(request)
        return HttpResponseRedirect('/')

def pro_create(request):
	form = ImEditForm(request.POST)
	navs = list(Nav.objects.all())
        return render(request,'projects_create.html',{'navs':navs,"form":form})

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

def inters_info(request):
	data = nginxData()
	#return HttpResponse("最大值")
	return HttpResponse(json.dumps(data.items()))

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
				max_actives[d1[1]] = d1[2]
				top_actives[d1[1]] = d1[6]
	maxs = sorted(max_actives.iteritems(),key = lambda d:d[1] ,reverse=True)
	active_tops = sorted(max_actives.iteritems(),key = lambda d:d[1] ,reverse=True)
	res['当前总并发值'] = total_active
	res['当前最大并发值前十接口'] = maxs[:10]
	res['当前并发值前十接口'] = active_tops[:10]
	return  res
	

def inters_count(date_table,top):
	"""
		date_table: 形如2017_05_13
		top: 查询的条数
	"""
	import  MySQLdb as mdb
	import datetime
	db_conn = mdb.connect('59.110.11.16','web_data','web_data@2017','all_web_data_history')
	cursor = db_conn.cursor()
	res1 = ''
	try:
		cursor.execute("select * from "+date_table+"_history_data")
		data = cursor.fetchall()
		statics_files = ['jpg','png','html','js','css','ts','m3u8','txt','gif']
                statics = []
                res = dict()
                res[u'静态文件'] = 0
                data = [ (d[2],int(d[6])) for d in data if d[1] == 'server_url' ]
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
                res1 = sorted(res.iteritems(),key = lambda d:d[1] ,reverse=True)
	except mdb.Error,e:
		print e
	db_conn.close()
	# return (top,'tttt')
	# 内部调用数据返回
	return res1[:int(top)]
	# 外部调用接口数据返回

def upload(request):
	#if request.method == 'GET':
	form = NewForm(request.GET)
	return render(request,'upload.html')

def up_recive(request):
	if request.method == 'POST':
		files = request.FILES.get("up_file",None) # 获取上传的文件,如果没有文件,则默认为None
		if not files:
			return HttpResponse("没有上传数据")
		save_destination = open(os.path.join("uploads",files.name),'wb+') # 打开特定的文件进行二进制写操作
		for chunk in files.chunks():
			save_destination.write(chunk)
		save_destination.close()
		return HttpResponse("上传完毕!")

def inters_data(request):
	d = ['1','2','3','4','5','6','7','8','9']
	err_mess = '对不起没有改时段的接口信息!'
	if request.method == 'GET':
		form = intersForm(request.GET)
		f_data = request.GET
		if f_data:
			d_date = f_data['data[d]']
			top = f_data['data[top]']
			cache_key = d_date + "_requests"
			if read_from_cache(cache_key) == None:
					datas = inters_count(d_date,top)
					write_to_cache(cache_key,datas)
			g_data = read_from_cache(cache_key)
			if f_data['action'] == 'pagination' and g_data:
				try:
					page = int(request.GET.get('page',1))
					if page < 1:
						page = 1
				except ValueError:
					page =1
				paginator = Paginator(g_data,10)
				try:
					page_data = paginator.page(page)
				except (EmptyPage,InvalidPage,PageNotAnInteger):
					page_data = paginator.page(1)
				return render(request,'inters_count.html',{'form':form,'data':page_data,'page':page,'d_date':d_date,'top':top})
				# return render(request,'inters_count.html',{'form':form,'data':page_data,'page':page})
			if f_data['action'] == 'cvs' and g_data:
				# 自定义httpResponse流
				xls_name = 'd_date.xls'
				response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
				response['mimetype']='application/vnd.ms-excel'
				response['Content-Disposition'] = 'attachment; filename=' + d_date + '.xls'
				# 创建工作簿
				workbook = xlwt.Workbook(encoding='utf-8')
				# 创建工作页
				sheet1 = workbook.add_sheet(d_date+u'访问情况')
				# 开始写入excel
				row0 = [u'访问url',u'访问次数']
				#for i in range(0,len(row0)):
				sheet1.write(0,0,row0[0])
				sheet1.write(0,1,row0[1])
				for i in range(1,len(g_data)):
					sheet1.write(i,0,g_data[i][0])
					sheet1.write(i,1,g_data[i][1])
				workbook.save(response)
				return response
			elif f_data['action'] == 'imge' and g_data:
				server_url = [ data[0] for data in g_data ]
				server_count = [ int(data[1]) for data in g_data ]
				da = json.dumps({'top':top,'date':d_date,'server_url':server_url,'server_count':server_count})
				# da = [server_url,server_count]
				# return render(request,'inters_count.html',{'form':form,'server_url':server_url,'server_count':server_count,'date',d_date})
				return HttpResponse(da)
			else:
				return HttpResponse('检索的数据不存在')
		else:
			return render(request,'inters_count.html',{'form':form})

	if request.method == 'POST':
		form = intersForm(request.POST)
		data = form.data
		date_year = data['date_year']
		date_month = data['date_month']
		date_day = data['date_day']
		d_date = date_year + date_month + date_day
		top  = data['top']
		if  d_date is None or top is None:
			return HttpResponse(err_mess)
			return render(request,'inters_count.html',{'form':form,'error_mess':err_mess })
		else:
			if d_date is not None and top is not None:
				if date_day in d:
					date_day = '0' + date_day
				if date_month in d:
					date_month = '0' + date_month
				d_date = date_year + '_' + date_month + '_' + date_day
				cache_key = d_date + "_requests"
				if read_from_cache(cache_key) == None:
					datas = inters_count(d_date,top)
					write_to_cache(cache_key,datas)
				datas = read_from_cache(cache_key)
				# return HttpResponse(datas)
				if datas:
					paginator = Paginator(datas,10)
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

					return render(request,'inters_count.html',{'form':form,'data':page_data,'page':page,'d_date':d_date,'top':top})
						# return render('inters_count.html',{'form':form,'data':datas})
				else:
					return render(request,'inters_count.html',{'form':form,'error_mess':err_mess })

def export_cvs(request):
	if request.method == 'GET':
		form = intersForm(request.GET)
		f_data = json.loads(request.GET.items()[0][1])
		if f_data:
			d_date = f_data['d']
			top = f_data['top']
			g_data = inters_count(d_date,top)
			if  g_data:
				# 自定义httpResponse流
				# response = HttpResponse(content_type='application/vnd.ms-excel;charset=utf-8')
				response = HttpResponse(content_type='application/octet-stream;charset=utf-8')
				response['mimetype']='application/octet-stream'
				response['Content-Disposition'] = 'attachment; filename=' + d_date + '.xls'
				workbook = xlwt.Workbook(encoding='utf-8')
				# 创建工作页
				sheet1 = workbook.add_sheet(d_date+u'访问情况')
				# 开始写入excel
				row0 = [u'访问url',u'访问次数']
				sheet1.write(0,0,row0[0])
				sheet1.write(0,1,row0[1])
				for i in range(1,len(g_data)):
					sheet1.write(i,0,g_data[i][0])
					sheet1.write(i,1,g_data[i][1])
				workbook.save(response)
				url = request.get_full_path()
				return response
				#return HttpResponse([{'url':url,'response':response}])
			else:
				return HttpResponse('检索的信息不存在')

def get_imge(request):
	data = inters_count()
	return HttpResponse('頁面正在開發中。。。')

def add(request):
	if request.method == 'GET':
		data = request.GET
		if data:
			return HttpResponse(int(data['a'])+int(data['b']))
		else:
			return render(request,'add.html')

# read cache
def read_from_cache(keys):
    value = cache.get(keys)
    if value == None:
        data = None
    else:
        data = json.loads(value)
    return data

#write cache
def write_to_cache(keys,value):
    cache.set(keys, json.dumps(value), timeout=None)
