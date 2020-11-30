from django.shortcuts import render,redirect
import ast
from django.http import HttpResponse,JsonResponse
# Create your views here.
from django.db.models import Count
from django.http import HttpResponse
from django.db import models
from .models import Cmanage
from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger
from .check_login_views import check_login
from django.contrib.auth.models import ContentType, Permission, User

@check_login 
def cmanage_list(request):
    fullname = request.session['fullname']
    user_id = request.session['user_id']
    start_date = request.GET.get("ipt_str")
    end_date = request.GET.get("ipt_end")
    query = request.GET.get("btn_query")
    if query:
        if start_date:
            orders = Cmanage.objects.filter(cdate__gte=start_date,cdate__lte=end_date)
        else:
            orders = Cmanage.objects.all()
    else:
        orders = Cmanage.objects.all()
    
    orders_count = orders.count()
    paginator = Paginator(orders,20)
    number = paginator.num_pages
    select_number = request.GET.get('page_number')
    if select_number:
        page_number = select_number
    else:
        page_number = 1
    if query == 'pre':
        page_number = int(page_number) - 1
        if page_number < 1:
            page_number = 1
    elif query == 'next':
        page_number = int(page_number) + 1
        if page_number > number:
            page_number = number
    else:
        page_number = 1

    # get_number = int(page_number)
    # if get_number > number or get_number < 1:
    #     page_number = number

    page = paginator.page(page_number)

    user_results = User.objects.filter().values_list('first_name',flat=True)
    users = list(user_results)
    content = {'fullname': fullname, 'user_id':user_id, 'info': page, 'users': users,
        'start_date': start_date, 'end_date': end_date, 'orders_count': orders_count,
    }
    return render(request,'ops/change_manage.html',context=content)

@check_login
def add_order(request):
    fullname = request.session['fullname']
    user_id = request.session['user_id']

    user_results = User.objects.filter().values_list('first_name',flat=True)
    users = list(user_results)

    content = {
        'fullname': fullname,
        'user_id': user_id,
        'info': users,
    }
    return render(request,'ops/add_order.html',context=content)