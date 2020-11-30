from django.shortcuts import render,redirect
import ast
from django.http import HttpResponse,JsonResponse
# Create your views here.
from django.db.models import Count
from django.http import HttpResponse
from django.db import models
from .models import Server,Os,Cmanage,Doc

def dml(request):
    user_id = request.session['user_id']
    
    module={
            'Doc':Doc,
            'Os':Os,
            'Server':Server,
            'Cmanage':Cmanage,
        }
    illegal_data = {
                'code':1,
                'msg':'illegal request'
            }
    
    if request.method == 'GET':                 ###模型删除事件，提交方法为GET
        mod=request.GET.get('mod','x')
        if mod not in module:
            return JsonResponse(illegal_data)
        delete_list = request.GET.get('delete_list','')
        if delete_list:                         ###判断前端是否传的删除列表
            delete_list = delete_list.split(',')
            module[mod].objects.filter(id__in=delete_list).delete()

        id = request.GET.get('id')              ###单条目删除
        aa = module[mod].objects.filter(id=id).delete()
        return JsonResponse({'code':0,})


    data=request.POST.dict()                    ###模型新增和更新事件，提交方法为POST
    del data['csrfmiddlewaretoken']
    del data['mod']
    del data['id']

    mod=request.POST.get('mod','x')             ###判断前端提交的模型是否存在
    if mod not in module:
        return JsonResponse(illegal_data)
    
    _id = int(request.POST.get('id',0))
 
    if _id == 0:
        aa = module[mod].objects.create(**data)
        if aa.id:
            result = 1
        else:
            result = 0
    else:
        result = module[mod].objects.filter(id=_id).update(**data)
        
    if result == 1:                             ###新增或更新后返回json消息
        return JsonResponse({
                'code': 200,
                'msg': "提交成功",
            })
    elif result == 0:
        return JsonResponse({
            'code': 500,
            'msg':"提交失败",
        })
