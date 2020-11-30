from django.shortcuts import render,redirect
import ast
from django.http import HttpResponse,JsonResponse
# Create your views here.
from django.db.models import Count
from django.http import HttpResponse
from django.db import models
from .models import Os
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .check_login_views import check_login
from django.contrib.auth.models import ContentType, Permission, User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password

@check_login
def user_list(request):
    info = User.objects.all()
    fullname = request.session['fullname']
    user_id = request.session['user_id']
    content = {
        'info': info,
        'fullname': fullname,
        'user_id': user_id,
    }
    return render(request, 'ops/user.html', context=content)

def user_detail(request,id):
    all_models = {'server': (['服务器',]),
        'os': (['操作系统',]),
        'doc': (['文档',]),
        'cmanage': (['变更',]),
    }
    fullname = request.session['fullname']
    user_id = request.session['user_id']
    
    if id == '0':
        username = ''
    elif id == '1':
        all_models = {'server': (['服务器','view','add','change','delete']),
            'os': (['操作系统','view','add','change','delete']),
            'doc': (['文档','view','add','change','delete']),
            'cmanage': (['变更','view','add','change','delete']),
        }
        user = User.objects.get(id=id)
        username = user.username
    else:
        user = User.objects.get(id=id)
        username = user.username
        all_perms = user.get_all_permissions()

        for i in all_perms:
            x = i.split('.')[1]
            perms_type = x.split('_')[0]
            perms_model = x.split('_')[1]
            all_models[perms_model].append(perms_type)

    
    content = {
        'info': all_models,
        'fullname': fullname,
        'id': id,
        'username': username,
        'user_id': user_id,
    }
    return render(request, 'ops/add_or_edit_user.html', context=content)

def change_pd_or_perm(request,id):
    username = request.GET.get('username')
    user_id = request.session['user_id']
    new_password = make_password(request.GET.get('new_password'))
    if username:
        if id == '0':
            first_name = request.GET.get('first_name')
            email = 'ops@ops.com'
            User.objects.create(username=username, email=email, password=new_password, first_name=first_name)
            newuser = User.objects.get(username=username)

            id = newuser.id
            msg = {'tips':'创建成功', 'id': id}
            return JsonResponse(msg)
        else:
            if user_id == 1:
                User.objects.filter(id=id).update(password=new_password)
                msg = {'tips': '密码更改成功','id': id}
                return JsonResponse(msg)
            else:
                old_password = request.GET.get('old_password')
                us = authenticate(username=username, password=old_password)
                print(us)
                if us is not None and us.is_active:
                    us.set_password(request.GET.get('new_password'))
                    us.save()
                    msg = {'tips': '密码更改成功','id': id}
                    return JsonResponse(msg)
                else:
                    msg = {'tips': '密码更改失败', 'id': id}
                    return JsonResponse(msg)
    else:
        user = User.objects.get(id=id)
        perm = request.GET.get("perm")
        flag = request.GET.get("flag")

        msg = {'tips':'权限更改生效'}

        perm_id = Permission.objects.get(codename=perm)
        if flag == "add_perm":
            user.user_permissions.add(perm_id)
        else:
            user.user_permissions.remove(perm_id)

        return JsonResponse(msg)

def del_user(request,id):
    res = User.objects.get(id=id).delete()
    if res:
        msg = {'tips':'用户删除成功'}
    else:
        msg = {'tips':'用户删除失败'}
    return JsonResponse(msg)