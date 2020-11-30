from django.shortcuts import render,redirect
from functools import wraps

def check_login(func):
    @wraps(func)
    def inner(request,*args,**kwargs):
        ret = request.session.get("login")
        if ret == "success":
            return func(request, *args, **kwargs)
        else:
            return redirect('/ops/login/')
    return inner