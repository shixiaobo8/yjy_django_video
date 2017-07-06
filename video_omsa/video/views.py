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
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from .models import Nav
import json,os,sys
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

def inters_count(date_table,top):
	"""
		date_table: 形如2017_05_13
		top: 查询的条数
	"""
	import  MySQLdb as mdb
	import datetime
	db_conn = mdb.connect('59.110.11.16','web_data','web_data@2017','all_web_data_history')
	cursor = db_conn.cursor()
	ret = ''
	try:
		cursor.execute("select * from (select `key`,`requests` from "+date_table+"_history_data limit "+top+") as top order by `requests`+0 desclimit "+top+";")
		datas = cursor.fetchall()
		ret = datas
		#return HttpResponse(ret)
		#data_js = dict()
		#for data in datas:
		#	data_js[data[0]] = data[1]
	except mdb.Error,e:
		print e
		#db_conn.close()
	db_conn.close()
	# 内部调用数据返回
	return ret
	# 外部调用接口数据返回
	#return render(request,'inters_count.html',{'data':datas})
	#return render(request,'inters_count.html',{'data':data_js})


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
			g_data = inters_count(d_date,top)
			return HttpResponse(f_data)
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
				return HttpResponse('页面正在开发中。。。')
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
				datas = inters_count(d_date,top)	
				#return HttpResponse(datas)
				if datas:
					return render(request,'inters_count.html',{'form':form,'data':datas})
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
	return HttpResponse('頁面正在開發中。。。')

def add(request):
	if request.method == 'GET':
		data = request.GET
		if data:
			return HttpResponse(int(data['a'])+int(data['b']))
		else:
			return render(request,'add.html')
