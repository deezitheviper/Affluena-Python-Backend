from django.shortcuts import render,redirect
from affluena.models import *
from accounts import forms
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from accounts.decorators import *
from django.contrib.auth.models import Group
from django.http import  HttpResponseRedirect


@login_required(login_url='login') 
@admin_only
def home(request):
    orders = Order.objects.all()
    orders_c = Order.objects.all().order_by('-date_ordered')[:4]
    simple = Simple.objects.all()
    compound = Compound.objects.all()
    customers = User.objects.all().order_by('-date_joined')[:4]
    payouts = Payout.objects.all() 
    payouts_c = Payout.objects.filter(status="Pending").order_by('-due')[:4]
    total_payouts = payouts.count()
    approved_payouts = payouts.filter(status='Approved').count()
    pending_payouts = payouts.filter(status='Pending').count()
    simples = TopUp.objects.all().order_by('-date_added')[:4]
    compounds = TopUpCompound.objects.all().order_by('-topup_date')[:4]
    total_orders = orders.count()
    total_customers = customers.count()
    delivered = orders.filter(status='Approved').count()
    pending = orders.filter(status='Pending').count()
    total_simple = simple.count()
    total_compound = Compound.objects.all().count()


    context = {
        'orders': orders_c,
        'simple': simple,
         'compound': compound,
          'simples': simples,
         'compounds': compounds,
        'customers': customers,
        'payouts': payouts_c,
        'total_s': total_simple,
        'total_compound': total_compound,
        'total_o': total_orders,
        'total_c': total_customers,
        'pending': pending,
        'delivered': delivered,
        'total_payouts': total_payouts,
        'pending_payouts': pending_payouts,
        'approved_payouts': approved_payouts
    }
    return render(request,'accounts/dashboard.html', context)





@unauthenticated_user
def register(request):
        form =  forms.UserForm()
        if request.method == 'POST':
            form = forms.UserForm(request.POST)
            if form.is_valid():          
                user = form.save()
                return redirect('home')
            
        context = { 
            'form':form
        }
        return render(request,'cms/register.html',context)

@unauthenticated_user
def user_login(request):   
        form = forms.UserForm
        next_page = request.GET.get('next', False)
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            user = authenticate(request,username=username,password=password)
            if user is not None:
               
                stf = Group.objects.get(name="Staff")
                group = user.groups.all()
                if stf in group or user.is_staff:
                    login(request, user)
                    if next_page:
                        return HttpResponseRedirect(next_page)
                    else:
                        return redirect('board')
                else:
                    messages.info(request,"Unauthorized Login")  
            else:
                messages.info(request,"Username or Password is Incorrect")  
        context = {'form':form}
        return render(request,'cms/login.html',context)

@login_required(login_url='login')
def user_logout(request):
    logout(request)
    return redirect('login')    