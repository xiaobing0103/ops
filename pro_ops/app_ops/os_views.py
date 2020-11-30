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
from xlwt import *
import io,os

@check_login
def get_list(request):
    zbx_stau = request.GET.get("zbx_stau")
    submit_value = request.GET.get("btn_submit")
    fullname = request.session['fullname']
    user_id = request.session['user_id']
    
    #前端更改zabbix监控状态
    if zbx_stau:
        ip = request.GET.get("ip")
        Os.objects.filter(ip=ip).update(zbx_stau=zbx_stau)
        msg={
            'code':200,
        }
        return JsonResponse(msg)

    #前端请求查询，返回查询的结果集
    productid = request.GET.get("productid",'')
    hostname = request.GET.get("hostname",'')
    version = request.GET.get("system_version",'')
    ip = request.GET.get("ip",'')
    esxi_ip = request.GET.get("esxi_ip",'')
    server_type = request.GET.get("server_type",'')
    select_number = request.GET.get('page_number')

    if submit_value:
        oslist = Os.objects.filter(productid__icontains=productid).filter(hostname__icontains=hostname)\
            .filter(system_version__icontains=version).filter(ip__icontains=ip).filter(esxi_ip__icontains=esxi_ip)\
            .filter(server_type__icontains=server_type).order_by()
    #前端查询所有数据集
    else:
        oslist = Os.objects.all().order_by()
   
    #django分页
    paginator = Paginator(oslist,20)
    number = paginator.num_pages
    
    #判断是否选择了跳转页码
    if select_number:
        page_number = select_number
    else:
        page_number = 1
    
    #翻页设置
    if submit_value == 'pre':
        page_number = int(page_number) - 1
        if page_number < 1:
            page_number = 1
    elif submit_value == 'next':
        page_number = int(page_number) + 1
        if page_number > number:
            page_number = number

    #判断前端跳转页码输入是否合法
    get_number = int(page_number)
    if get_number > number or get_number < 1:
        page_number = number

    #传给前端的页面
    page = paginator.page(page_number)
    #数据项目编号
    strat = (int(page_number) - 1) * 20
    count = oslist.count()
    
    os_data = {'strat':strat,'page_number': page_number,'number': number,'fullname': fullname,
        'productid': productid,'hostname': hostname,'system_version': version,'user_id': user_id,
        'ip': ip,'esxi_ip': esxi_ip,'server_type': server_type,'count': count,'list2':page,
    }
    return render(request,'ops/os.html',context=os_data)

@check_login
def add_or_edit(request,id=''):
    fullname = request.session['fullname']
    user_id = request.session['user_id']
    if not id:
        return render(request,'ops/add_or_edit_os.html',{'fullname':fullname})
    else:
        info = Os.objects.get(id=id)
        content = {
            'fullname': fullname,
            'user_id': user_id,
            'info': info
        }
        return render(request, 'ops/add_or_edit_os.html', context=content)

@check_login
def export_excel(request):
    server_list = Os.objects.all().order_by()
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(u"操作系统信息")
    w.write(0, 0, u"产品编号")
    w.write(0, 1, u"机器类型")
    w.write(0, 2, u"主机名")
    w.write(0, 3, u"操作系统")
    w.write(0, 4, u"状态")
    w.write(0, 5, u"内核信息")
    w.write(0, 6, u"CPU核心")
    w.write(0, 7, u"内存")
    w.write(0, 8, u"硬盘")
    w.write(0, 9, u"vlan")
    w.write(0, 10, u"IP")
    w.write(0, 11, u"宿主机")
    w.write(0, 12, u"监控状态")
    w.write(0, 13, u"应用信息")
    w.write(0, 14, u"应用负责人")
    w.write(0, 15, u"备注")

    excel_row = 1
    for obj in server_list:
        w.write(excel_row, 0, obj.productid)
        w.write(excel_row, 1, obj.server_type)
        w.write(excel_row, 2, obj.hostname)
        w.write(excel_row, 3, obj.system_version)
        w.write(excel_row, 4, obj.status)
        w.write(excel_row, 5, obj.kernel)
        w.write(excel_row, 6, obj.core_quantity)
        w.write(excel_row, 7, obj.memory)
        w.write(excel_row, 8, obj.hdd)
        w.write(excel_row, 9, obj.vlan)
        w.write(excel_row, 10, obj.ip)
        w.write(excel_row, 11, obj.esxi_ip)
        w.write(excel_row, 12, obj.zbx_stau)
        w.write(excel_row, 13, obj.application)
        w.write(excel_row, 14, obj.administrator)
        w.write(excel_row, 15, obj.remarks)
        excel_row += 1

    exist_file = os.path.exists("download/os.xls")
    if exist_file:
        os.remove(r"download/os.xls")
    ws.save("download/os.xls")
    sio = io.StringIO()
    response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=os.xls'
    ws.save(response)
    return response