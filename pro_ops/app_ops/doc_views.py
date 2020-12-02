from django.shortcuts import render,redirect
import ast, io, os, time, datetime
from django.http import HttpResponse,JsonResponse
# Create your views here.
from django.db.models import Count
from django.http import HttpResponse
from django.db import models
from .models import Doc, Directory, Document, Properm, Progroup, Personal, Usergroup
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .check_login_views import check_login
from django.contrib.auth.models import ContentType, Permission, User


@check_login
def doc(request,doc_id=''):
    # query = request.GET.get('na_query')
    # if query:
    #     document = Doc.objects.filter(title__icontains=query).order_by()
    # else:
    #     query = ''
    #     document = Doc.objects.all().order_by()
    
    group = Usergroup.objects.filter(user=request.user).values_list('group',flat=True)
    pro_list = Properm.objects.filter(group__in=group).values_list('project').distinct()
    pros = Directory.objects.filter(id__in=pro_list)
    # pros = Directory.objects.filter(id__in=pr)
    pri = Personal.objects.filter(user=request.user).values_list('project',flat=True)
    private = Directory.objects.filter(id__in=pri)

    if not doc_id:
        filename = 'documents/main.wt'
        with open(filename,encoding='utf-8') as file_obj:
            main_html = file_obj.read()
        content = {
        'pros': pros,
        'private': private,
        'main_html': main_html,
        'doc_id': doc_id,
        'doc_name':'主页',
        'doc_author': 'xiao.bingbing',
        'doc_createtime': '2020-11-20 11:11:11',
        'doc_editortime': '2020-11-30 12:12:12',
        }
        return render(request,'ops/doc.html',context=content)
    else:
        doc_data = Document.objects.get(id=doc_id)
        with open(doc_data.filepath,encoding='utf-8') as file_obj:
            doc_content = file_obj.read()
        return JsonResponse({
        'code': 0,
        'doc_content': doc_content,
        'doc_id': doc_id,
        'doc_name': doc_data.filename,
        'doc_author': doc_data.author.username,
        'doc_createtime': doc_data.createtime,
        'doc_editortime': doc_data.editortime,
        })
    
@check_login
def add_or_edit(request,doc_id):
    if doc_id == '0':
        doc_data = request.POST.dict()
        doc_date = str(datetime.date.today())
        doc_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) 
        timestamp = str(int(round(time.time() * 1000)))
        doc_path = 'documents/'+doc_date+'/'+request.user.username
        filepath = doc_path+'/'+doc_data['filename']+'_'+timestamp+'.wt'
        isExists=os.path.exists(doc_path)
        if isExists:
            pass
        else:
            os.makedirs(doc_path)
        with open(filepath,'w+',encoding='utf-8') as f:
            f.write('')
        del doc_data['csrfmiddlewaretoken']
        doc_data['filepath'] = filepath
        doc_data['author'] = request.user
        doc_data['directory'] = Directory.objects.get(id=doc_data['directory'])
        doc_data['createtime'] = doc_time
        add_doc = Document.objects.create(**doc_data)
        return JsonResponse({'doc_id': add_doc.id, 'code': 0})
    else:
        doc_id = int(doc_id)
        content = request.POST.get('content','')
        option = request.GET.get('option','')
        if content:
            doc_data = Document.objects.get(id=doc_id)
            filename = doc_data.filepath
            with open(filename,'w',encoding='utf-8') as file_object:
                file_object.write(content)
            return JsonResponse({'code': 0,})
        elif option:
            doc_data = Document.objects.get(id=doc_id)
            with open(doc_data.filepath,encoding='utf-8') as file_object:
                doc_content = file_object.read()
            return render(request,'ops/add_or_edit_doc.html',{'doc_id': doc_id, 'doc_content':doc_content})
        else:
            return render(request,'ops/add_or_edit_doc.html',{'doc_id': doc_id,})

@check_login
def create_project(request):
    project = request.POST.dict()
    label = project['label']
    del project['label']
    del project['id']
    del project['csrfmiddlewaretoken']

    newproject = Directory.objects.create(**project)
    if label == 'public':
        newgroup = Progroup.objects.create(group='owner_'+str(newproject.id))
        newperm = Properm.objects.create(project=newproject,group=newgroup,perm='owner')
        newusergroup = Usergroup.objects.create(user=request.user,group=newgroup,label=1)
    else:
        private = Personal.objects.create(project=newproject,user=request.user)
    
    return JsonResponse({'code': 200,'msg': '提交成功','id':newproject.id,'grade':newproject.grade})

@check_login
def create_dir(request):
    directory = request.POST.dict()
    del directory['id']
    del directory['csrfmiddlewaretoken']

    new_dir = Directory.objects.create(**directory)

    return JsonResponse({'code': 200,'msg': '提交成功','id':new_dir.id})

@check_login
def list_dir(request):
    id = request.POST.get('id')
    data = {}
    data2 = {}
    directory = Directory.objects.filter(parentid=id).values()
    docs = Document.objects.filter(directory=id).values()
    data = list(directory)
    data2 = list(docs)
    return JsonResponse({'code': 200,'msg': '提交成功', 'directory':data, 'docs':data2})

@check_login
def rename(request):
    data = request.POST.dict()
    del data['csrfmiddlewaretoken']
    if data['type'] == '0':
        rename = Directory.objects.filter(id=data['id']).update(dirname=data['new_name'])
    else:
        rename = Document.objects.filter(id=data['id']).update(filename=data['new_name'])

    return JsonResponse({'code': 200,'msg': '提交成功'})

@check_login
def del_dir_or_file(request):
    data = request.POST.dict()
    del data['csrfmiddlewaretoken']
    if data['type'] == '0':
        operation = Directory.objects.filter(id=data['id']).delete()
        doc_del_list = Document.objects.filter(directory=data['id'])
        for n in doc_del_list:
            os.remove(n.filepath)
            n.delete()
        child = Directory.objects.filter(parentid=data['id'])
        while child:
            for x in child:
                child = Directory.objects.filter(parentid=x.id)
                x.delete()
                doc_data = Document.objects.filter(directory=x.id)
                for i in doc_data:
                    os.remove(i.filepath)
                    i.delete()

    else:
        doc_data = Document.objects.get(id=data['id'])
        if os.path.exists(doc_data.filepath):
            os.remove(doc_data.filepath)
            doc_data.delete()
        else:
            pass
    return JsonResponse({'code': 200,'msg': '提交成功'})

@check_login
def perms(request):
    groups = Usergroup.objects.filter(user=request.user).values_list('group',flat=True)
    projects = Properm.objects.filter(group__in=groups,perm='owner').values_list('project',flat=True)
    all_groups = Properm.objects.filter(project__in=projects)
    return render(request,'ops/progroup.html',{'group_list': all_groups})

@check_login
def add_or_edit_group(request,group_id):
    if group_id == '0':
        all_group = Usergroup.objects.filter(user=request.user).values_list('group',flat=True)
        all_project = Properm.objects.filter(group__in=all_group,perm='owner')
        content = {
            'project_list': all_project,
            'group_id': group_id,
        }
    else:
        group = Progroup.objects.get(id=group_id)
        properm = Properm.objects.get(group=group)
        project = properm.project
        user_list = Usergroup.objects.filter(group=group)
        all_user = User.objects.all()
        
        content = {
            'project': project,
            'properm': properm,
            'user_list': user_list,
            'all_user': all_user,
            'group_id': group_id,
            'group': group.group,
            'perm_id': properm.id,
        }
    return render(request,'ops/add_or_edit_group.html',context=content)

@check_login
def update_group(request):
    option = request.GET.get("option")
    group_id = request.GET.get("group_id")
    username = request.GET.get("username")
    ## 1为新增用户组成员
    if option == '1':
        group = Progroup.objects.get(id=group_id)
        try:
            user = User.objects.get(username=username)
        except:
            user = None
        try:
            rs = Usergroup.objects.get(user=user,group=group_id)
        except:
            rs = None
        if user and not rs:
            newgroup = Usergroup.objects.create(user=user,group=group,label=0)
            return JsonResponse({'code': 0,'msg': '提交成功','group_id':newgroup.id})
        else:
            return JsonResponse({'code': 500,'msg': '用户不存在或权限已存在'})
    ## 2为删除用户组成员
    elif option == '2':
        dt = Usergroup.objects.get(id=group_id)
        perm_info = Properm.objects.get(group=dt.group)
        if dt.label == 0:
            dt.delete()
            return JsonResponse({'code': 0,'msg': '删除成功'})
        elif dt.label == 1 and perm_info.perm != 'owner':
            dt.delete()
            return JsonResponse({'code': 0,'msg': '删除成功'})
        else:
            return JsonResponse({'code': 500,'msg': '默认权限组不允许删除'})
    elif option == '3':
        Progroup.objects.get(id=group_id).delete()
        return JsonResponse({'code': 0,'msg': '删除成功'})

@check_login
def update_perm(request):
    update_data = request.POST.dict()
    try:
        group_name = update_data['group']
        del update_data['group']
    except:
        group_name = None
    perm_id = update_data['perm_id']
    group_id = update_data['group_id']
    del update_data['csrfmiddlewaretoken']
    del update_data['group_id']
    del update_data['perm_id']
    if group_name:                                                                          ## 判断是否有用户组信息更新
        if group_id == '0':                                                                 ## 0代表新增，非0为更新
            add_group = Progroup.objects.create(group=group_name)                           ## 新增用户组及权限表项目
            add_usergroup = Usergroup.objects.create(group=add_group,user=request.user,label=1)
            if not update_data['perm'] or not update_data['project']:
                msg ='信息填写不完整，请检查'
            else:
                project_id = update_data['project'].split(',')[0]
                project = Directory.objects.get(id=project_id)
                add_perm = Properm.objects.create(project=project,group=add_group,perm=update_data['perm'])
                msg = '提交成功'
            return JsonResponse({'code': 0,'msg': msg,'id':add_group.id})
        else:
            Progroup.objects.get(id=group_id).update(group=group_name)                      ## 更新用户组     
    if update_data:
        try:
            project_id = update_data['project'].split(',')[0]
            project = Directory.objects.get(id=project_id)
            del update_data['project']
            update_data['project'] = project
        except:
            pass
        Properm.objects.filter(id=perm_id).update(**update_data)                               ## 更新权限表项目
        msg = '更新成功'
    return JsonResponse({'code': 0,'msg': msg, 'id':group_id})
    
@check_login
def get_perms(request):
    f_id = request.GET.get('id')
    option = request.GET.get('option')
    if option == '1':
        pro = Directory.objects.get(id=f_id)
    else:
        dirc = Document.objects.get(id=f_id)
        pro = dirc.directory
    while pro.parentid != 0:
        pro = Directory.objects.get(id=pro.parentid)
    user_group = Usergroup.objects.filter(user=request.user).values_list('group',flat=True)
    perms = Properm.objects.filter(group__in=user_group,project=pro).values_list('perm',flat=True)
    if 'owner' in perms:
        perm = 'owner'
    elif 'edit' in perms:
        perm = 'edit'
    elif 'view' in perms:
        perm = 'view'
    else:
        perm = '0'
    return JsonResponse({'perm': perm})