from django.shortcuts import render,redirect
import ast
from django.http import HttpResponse,JsonResponse
# Create your views here.
from django.db.models import Count
from django.http import HttpResponse
from django.db import models
from .models import Server
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .check_login_views import check_login
from django.contrib.auth.models import ContentType, Permission, User
from xlwt import *
import io,os

@check_login
def get_list(request):
    submit_value = request.GET.get("btn_submit")
    fullname = request.session['fullname']
    user_id = request.session['user_id']

    productid = request.GET.get("productid",'')
    brand = request.GET.get("brand",'')
    servername = request.GET.get("servername",'')
    model = request.GET.get("model",'')
    function = request.GET.get("function",'')
    data_center = request.GET.get("data_center",'')
    select_number = request.GET.get('page_number')

    if submit_value:
        serverlist = Server.objects.filter(productid__icontains=productid).filter(brand__icontains=brand)\
            .filter(servername__icontains=servername).filter(model__icontains=model).filter(function__icontains=function)\
            .filter(data_center__icontains=data_center).order_by()
    else:
        serverlist = Server.objects.all().order_by()
    
    count = serverlist.count()
    paginator = Paginator(serverlist,20)
    number = paginator.num_pages
    
    if select_number:
        page_number = select_number
    else:
        page_number = 1  
       
    if submit_value == 'pre':
        page_number = int(page_number) - 1
        if page_number < 1:
            page_number = 1
    elif submit_value == 'next':
        page_number = int(page_number) + 1
        if page_number > number:
            page_number = number

    get_number = int(page_number)
    if get_number > number or get_number < 1:
        page_number = number

    page = paginator.page(page_number)
    strat = (int(page_number) - 1) * 20

    content = {'strat': strat,'page_number': page_number,'fullname': fullname,'number': number,
        'productid': productid,'brand': brand,'servername': servername,'model': model,
        'function': function,'data_center': data_center, 'user_id': user_id,'info': page,'count':count,
    }
      
    return render(request,'ops/server.html',context=content)

@check_login
def add_or_edit(request,id=''):
    fullname = request.session['fullname']
    user_id = request.session['user_id']
    content = {'fullname': fullname, 'user_id': user_id}
    if not id:
        return render(request,'ops/add_or_edit_server.html',context=content)
    else:
        info = Server.objects.get(id=id)
        content = {
            'fullname': fullname,
            'user_id': user_id,
            'info': info
        }
        return render(request, 'ops/add_or_edit_server.html', context=content)

@check_login
def export_excel(request):
    server_list = Server.objects.all().order_by()
    ws = Workbook(encoding='utf-8')
    w = ws.add_sheet(u"物理机信息")
    w.write(0, 0, u"产品编号")
    w.write(0, 1, u"品牌")
    w.write(0, 2, u"设备名称")
    w.write(0, 3, u"设备型号")
    w.write(0, 4, u"状态")
    w.write(0, 5, u"CPU型号")
    w.write(0, 6, u"CPU颗数")
    w.write(0, 7, u"单颗核心")
    w.write(0, 8, u"内存数量")
    w.write(0, 9, u"内存总量(GB)")
    w.write(0, 10, u"SSD数量")
    w.write(0, 11, u"SSD总量(GB)")
    w.write(0, 12, u"HDD数量")
    w.write(0, 13, u"HDD总量(TB)")
    w.write(0, 14, u"raid模式")
    w.write(0, 15, u"IDRAC IP")
    w.write(0, 16, u"购买日期")
    w.write(0, 17, u"质保终止")
    w.write(0, 18, u"设备功能")
    w.write(0, 19, u"数据中心")
    w.write(0, 20, u"网络接入")
    w.write(0, 21, u"idrac网络接入")
    w.write(0, 22, u"机柜位置")
    w.write(0, 23, u"具体U位")

    excel_row = 1
    for obj in server_list:
        w.write(excel_row, 0, obj.productid)
        w.write(excel_row, 1, obj.brand)
        w.write(excel_row, 2, obj.servername)
        w.write(excel_row, 3, obj.model)
        w.write(excel_row, 4, obj.status)
        w.write(excel_row, 5, obj.cpu_model)
        w.write(excel_row, 6, obj.cpu_quantity)
        w.write(excel_row, 7, obj.cpu_core)
        w.write(excel_row, 8, obj.memory_quantity)
        w.write(excel_row, 9, obj.memory_total)
        w.write(excel_row, 10, obj.ssd_quantity)
        w.write(excel_row, 11, obj.ssd_total)
        w.write(excel_row, 12, obj.hdd_quantity)
        w.write(excel_row, 13, obj.hdd_total)
        w.write(excel_row, 14, obj.raid_type)
        w.write(excel_row, 15, obj.idrac_ip)
        w.write(excel_row, 16, obj.purchase_date)
        w.write(excel_row, 17, obj.warranty_end)
        w.write(excel_row, 18, obj.function)
        w.write(excel_row, 19, obj.data_center)
        w.write(excel_row, 20, obj.network)
        w.write(excel_row, 21, obj.idrac_network)
        w.write(excel_row, 22, obj.rack)
        w.write(excel_row, 23, obj.rack_u)
        excel_row += 1
    exist_file = os.path.exists("download/server.xls")
    if exist_file:
        os.remove(r"download/server.xls")
    ws.save("download/server.xls")
    sio = io.StringIO()
    response = HttpResponse(sio.getvalue(), content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=server.xls'
    ws.save(response)
    return response