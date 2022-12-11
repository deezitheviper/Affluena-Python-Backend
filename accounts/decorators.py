from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request,*args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/staff-board')
        else: 
             return view_func(request,*args,**kwargs)
    return wrapper_func

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name
            if group in allowed_roles or group == "Staff" or request.user.is_superuser and request.user.is_authenticated:
                return view_func(request, *args, **kwargs)
            else:
                 return HttpResponse('UnAuthorized Access')      
        return wrapper_func
    return decorator           

def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == 'None':
            return redirect('logout')
        if group == 'Staff' or request.user.is_staff or group == 'admin':
            return view_func(request, *args, **kwargs)
        else:
            return redirect('logout')

    return wrapper_function       

def super_user_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
        if group == 'None':
            return redirect('logout')
        if request.user.is_superuser:
            return view_func(request, *args, **kwargs)
        else:
            return redirect('logout')

    return wrapper_function    