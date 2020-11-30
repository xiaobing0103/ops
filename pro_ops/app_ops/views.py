from django.shortcuts import render,redirect
import ast
from django.http import HttpResponse,JsonResponse
# Create your views here.
from django.db.models import Count
from django.http import HttpResponse
from django.db import models
from .models import Server,Os,Doc,Cmanage
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from functools import wraps
from django.contrib.auth.models import ContentType, Permission, User
from django.contrib.auth import authenticate, login, logout
from .check_login_views import check_login

def login_in(request):
    if request.method == 'GET':
        return render(request,'ops/login.html')
    else:
        ss_name = request.POST.get('user_name')
        ss_password = request.POST.get('user_password')
        
        user = authenticate(username=ss_name, password=ss_password)
        if user is not None and user.is_active:
            login(request,user)
            request.session['login'] = "success"
            request.session['username'] = user.username
            request.session['user_id'] = user.id
            request.session['fullname'] = user.first_name
            # request.session.set_expiry(60)
            msg = {
                'code': '200',
            }
            return JsonResponse(msg)
        else:
            msg = {
                'code': '400',
                'tips' :'用户不存在或密码错误',
            }
            return JsonResponse(msg)

def login_out(request):
    logout(request)
    return redirect('/ops/login/')

@check_login
def main(request):
    fullname = request.session['fullname']
    user_id = request.session['user_id']
    
    d1 = Server.objects.filter(data_center='总部6F').count()
    d2 = Server.objects.filter(data_center='总部7F').count()
    d3 = Server.objects.filter(data_center='新化').count()
    d4 = Server.objects.filter(data_center='日业').count()
    d5 = Server.objects.filter(data_center='鑫远').count()
    d6 = Server.objects.filter(data_center='公园道').count()
    dt = [d1,d2,d3,d4,d5,d6]

    o1 = Os.objects.filter(system_version__icontains='centos').count()
    o2 = Os.objects.filter(system_version__icontains='windows').count()
    o3 = Os.objects.filter(system_version__icontains='esxi').count()
    o4 = Os.objects.filter(system_version='').count()
    ot = {"Esxi":o3,"Linux":o1,"Windows":o2,"Others":o4}

    return render(request,'ops/main.html',{'fullname':fullname,'data':dt,'ot':ot,'user_id': user_id,})

