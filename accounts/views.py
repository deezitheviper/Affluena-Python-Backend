from django.shortcuts import render, redirect
from affluena.models import *
from . import forms
from django.forms import inlineformset_factory
from .filters import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from .decorators import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from io import StringIO
import csv
from django.contrib import messages
from affluena.deuxModel  import CustomDeux
from django.core.mail import send_mail
from django.conf import settings

    

@login_required(login_url='login')
@admin_only
def export_email_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="email_list.csv"'

    writer = csv.writer(response,quoting=csv.QUOTE_ALL)

    email_list = []
    users = User.objects.filter(is_staff=False)
    for x in users:
        email_list.append(x.email)
    writer.writerow(email_list)

    return response
    
@login_required(login_url='login')
@admin_only
def export_phone_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="phone_list.csv"'

    writer = csv.writer(response,quoting=csv.QUOTE_ALL)

    phone_list = []
    users = User.objects.filter(is_staff=False)
    for x in users:
        phone_list.append(x.phone)
    writer.writerow(phone_list)

    return response
    
@login_required(login_url='login')
@admin_only
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="payout.csv"'

    writer = csv.writer(response,quoting=csv.QUOTE_ALL)
    nams = ["Name","Account Number","Bank","Amount","due","Narration"]
    writer.writerow(nams)
    pay_list = []
    payout = Payout.objects.filter(status="Pending").order_by('due')
    for x in payout:
        writer.writerow([x.user.full_name,x.user.account_no.strip(),x.user.bank_name,x.amount,x.due,"Affluena Returns"])

    return response
    
@login_required(login_url='login')
@admin_only
def export_ref_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="referralpayout.csv"'

    writer = csv.writer(response,quoting=csv.QUOTE_ALL)
    nams = ["Account Number","Bank","Amount","Narration"]
    writer.writerow(nams)
    pay_list = []
    payout = ReferralPayout.objects.filter(status="Pending").order_by('-date_requested')
    for x in payout:
         writer.writerow([x.user.account_no.strip(),x.user.bank_name,x.amount,"Affluena Referral Returns"])

    return response
    
@login_required(login_url='login')
@admin_only
def export_paid_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="paid.csv"'

    writer = csv.writer(response,quoting=csv.QUOTE_ALL)
    nams = ["Account Number","Bank","Amount","Narration"]
    writer.writerow(nams)
    pay_list = []
    payout = Payout.objects.filter(status="Approved").order_by('-date_requested')
    for x in payout:
        writer.writerow([x.user.account_no.strip(),x.user.bank_name,x.amount,"transfer to {}".format(x.user.username)])

    return response

@login_required(login_url='login')
@super_user_only
def makeAdmin(request,pk):
    user = User.objects.get(id=pk)
    group = Group.objects.get(name="Staff")
    group.user_set.add(user) 
    return redirect('accounts:customer',pk=pk)
          

@login_required(login_url='login')
@super_user_only
def removeAdmin(request,pk):
    user = User.objects.get(id=pk)
    group = Group.objects.get(name="Staff")
    user.groups.remove(group)
    return redirect('accounts:customer',pk=pk)


@login_required(login_url='login')
@admin_only
def orders(request):
    order = Order.objects.all().order_by('-date_ordered')
    myfilter = OrderFilter(request.GET, queryset=order)
    order = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(order, 50)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
       orders = paginator.page(paginator.num_pages)
    
    


    context = {
        'orders': orders,
        'myfilter': myfilter
    }
    return render(request,'accounts/orders.html', context)




@login_required(login_url='login')
@admin_only
def simples(request):
    simple = Simple.objects.all().order_by('-date_requested')
    myfilter = SimpleFilter(request.GET, queryset=simple)
   
    simple = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(simple, 50)
    
    try:
        simples = paginator.page(page)
        
    except PageNotAnInteger:
        
        simples = paginator.page(1)
        
    except EmptyPage:
      simples = paginator.page(paginator.num_pages)
      
    

    context = {
        'simples': simples,
        'myfilter': myfilter
    }
    return render(request,'accounts/simples.html', context)


@login_required(login_url='login')
@admin_only
def compounds(request):
    compound = Compound.objects.all().order_by('-date_requested')
    myfilter = CompoundFilter(request.GET, queryset=compound)
    compound = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(compound, 50)

    try:
        compounds = paginator.page(page)
    except PageNotAnInteger:
        compounds = paginator.page(1)
    except EmptyPage:
      compounds = paginator.page(paginator.num_pages)
    
    


    context = {
        'compounds': compounds,
        'myfilter': myfilter

    }
    return render(request,'accounts/compounds.html', context)



@login_required(login_url='login')
@admin_only
def topups(request):
    simple = TopUp.objects.all().order_by('-date_added')
    myfilter = SimpleTopFilter(request.GET, queryset=simple)
   
    simple = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(simple, 50)
    
    try:
        simples = paginator.page(page)
        
    except PageNotAnInteger:
        
        simples = paginator.page(1)
        
    except EmptyPage:
      simples = paginator.page(paginator.num_pages)
      
    

    context = {
        'simples': simples,
        'myfilter': myfilter
    }
    return render(request,'accounts/topups.html', context)




@login_required(login_url='login')
@admin_only
def ctopups(request):
    compound = TopUpCompound.objects.all().order_by('-topup_date')
    myfilter = CompoundTopFilter(request.GET, queryset=compound)
    compound = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(compound, 50)

    try:
        compounds = paginator.page(page)
    except PageNotAnInteger:
        compounds = paginator.page(1)
    except EmptyPage:
      compounds = paginator.page(paginator.num_pages)
    
    


    context = {
        'compounds': compounds,
        'myfilter': myfilter

    }
    return render(request,'accounts/ctopups.html', context)

@login_required(login_url='login')
@admin_only
def loans(request):
    loan = Loan.objects.all().order_by('-date_ordered')
    myfilter = LoanFilter(request.GET, queryset=loan)
    loan = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(loan, 50)
    try:
        loans = paginator.page(page)
    except PageNotAnInteger:
        loans = paginator.page(1)
    except EmptyPage:
       loans = paginator.page(paginator.num_pages)
    
    


    context = {
        'loans': loans,
        'myfilter': myfilter
    }
    return render(request,'accounts/loans.html', context)
    
@login_required(login_url='login')
@admin_only
def all_payouts(request):
    payout = Payout.objects.all().order_by('-due')
    myfilter = PayoutFilter(request.GET, queryset=payout)
    payout = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(payout, 50)
    try:
        payouts = paginator.page(page)
    except PageNotAnInteger:
        payouts = paginator.page(1)
    except EmptyPage:
       payouts = paginator.page(paginator.num_pages)
    
    


    context = {
        'payouts': payouts,
        'myfilter': myfilter
    }
    return render(request,'accounts/all_payouts.html', context)
    
@login_required(login_url='login')
@admin_only
def all_refpayouts(request):
    payout = ReferralPayout.objects.all().order_by('-date_requested')
    myfilter = RefPayoutFilter(request.GET, queryset=payout)
    payout = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(payout, 50)
    try:
        payouts = paginator.page(page)
    except PageNotAnInteger:
        payouts = paginator.page(1)
    except EmptyPage:
       payouts = paginator.page(paginator.num_pages)
    
    context = {
        'payouts': payouts,
        'myfilter': myfilter
    }
    return render(request,'accounts/all_refpayouts.html', context)

@login_required(login_url='login')
@admin_only
def payouts(request):
    payout = Payout.objects.filter(status="Pending").order_by('due')
    myfilter = PayoutFilter(request.GET, queryset=payout)
    payout = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(payout, 50)
    try:
        payouts = paginator.page(page)
    except PageNotAnInteger:
        payouts = paginator.page(1)
    except EmptyPage:
       payouts = paginator.page(paginator.num_pages)
    
    


    context = {
        'payouts': payouts,
        'myfilter': myfilter
    }
    return render(request,'accounts/payouts.html', context)
    
    
@login_required(login_url='login')
@admin_only
def approve_payouts(request):
    payout = Payout.objects.filter(status="Pending").order_by('due')
    myfilter = PayoutFilter(request.GET, queryset=payout)
    payout = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(payout, 50)
    try:
        payouts = paginator.page(page)
    except PageNotAnInteger:
        payouts = paginator.page(1)
    except EmptyPage:
       payouts = paginator.page(paginator.num_pages)
    
    if request.method == 'POST':
        a_payouts = request.POST.getlist('payouts')
        success = False
        for x in a_payouts:
            p = Payout.objects.get(id=x)
            p.status = "Approved"
            p.save()
            success = True
        if success == True:
            messages.success(request, "Selected Payouts have been approved succesfully.")
           
        if not a_payouts:
            context = {
                'payouts': payouts,
                'myfilter': myfilter
            }
            messages.error(request, "Items must be selected in order to perform actions on them. No items have been changed.")
            return render(request,'accounts/payouts.html', context)




    context = {
        'payouts': payouts,
        'myfilter': myfilter
    }
    return render(request,'accounts/payouts.html', context)


@login_required(login_url='login')
@admin_only
def approve_refpayouts(request):       
    payout = ReferralPayout.objects.filter(status="Pending").order_by('-date_requested')
    myfilter = RefPayoutFilter(request.GET, queryset=payout)
    payout = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(payout, 50)
    try:
        payouts = paginator.page(page)
    except PageNotAnInteger:
        payouts = paginator.page(1)
    except EmptyPage:
       payouts = paginator.page(paginator.num_pages)
    
    if request.method == 'POST':
        a_payouts = request.POST.getlist('payouts')
        success = False
        for x in a_payouts:
            p = ReferralPayout.objects.get(id=x)
            p.status = "Approved"
            p.save()
            success = True
        if success == True:
            messages.success(request, "Selected Payouts have been approved succesfully.")
        if not a_payouts:
            context = {
                'payouts': payouts,
                'myfilter': myfilter
            }
            messages.error(request, "Items must be selected in order to perform actions on them. No items have been changed.")
            return render(request,'accounts/ref_payouts.html', context)




    context = {
        'payouts': payouts,
        'myfilter': myfilter
    }
    return render(request,'accounts/ref_payouts.html', context)

@login_required(login_url='login')
@admin_only
def refpayouts(request):
    payout = ReferralPayout.objects.filter(status="Pending").order_by('-date_requested')
    myfilter = RefPayoutFilter(request.GET, queryset=payout)
    payout = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(payout, 50)
    try:
        payouts = paginator.page(page)
    except PageNotAnInteger:
        payouts = paginator.page(1)
    except EmptyPage:
       payouts = paginator.page(paginator.num_pages)
    
    context = {
        'payouts': payouts,
        'myfilter': myfilter
    }
    return render(request,'accounts/ref_payouts.html', context)


@login_required(login_url='login')
@super_user_only
def update_refpayout(request,pk,c_pk):
    payout = ReferralPayout.objects.get(pk=pk)
    form = forms.RefPayoutForm(instance=payout)
    if request.method == 'POST':
        form = forms.PayoutForm(request.POST, instance=payout)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Succesfully")
            return redirect('accounts:refpayouts') 
        else:
            form = forms.PayoutForm(instance=payout)           
    context = {
        'form':form,
        'payout':payout
    }
    return render(request, 'accounts/update_ref.html', context)     


@login_required(login_url='login')
@super_user_only
def delete_refpayout(request, pk):
    payout = ReferralPayout.objects.get(pk=pk)
    if request.method == 'POST':
        payout.delete()
        messages.success(request, "Deleted Succesfully")
        return redirect('accounts:refpayouts') 
    context = {
        'item': payout
    }    
    return render(request, 'accounts/delete_ref.html', context)

@login_required(login_url='login')
@admin_only
def updateCustomer(request,pk):
    customer= User.objects.get(id=pk)
    cform = forms.CustomerForm(instance=customer)
    staffForm = forms.StaffForm(instance=customer)
    if request.user.is_superuser:
        form = cform
    else:
        form = staffForm
    if request.method == 'POST':
        print(request)
        form = forms.CustomerForm(request.POST, instance=customer) 
        if form.is_valid():
            form.save() 
            return redirect('accounts:customer',pk=pk)
        else:
            form = forms.CustomerForm(instance=customer)
    context = {
        'form':form, 
        'customer': customer
    }        
    return render(request, 'accounts/update_customer.html', context)    


@login_required(login_url='login')
@admin_only
def messageCustomer(request,pk):
    user = User.objects.get(id=pk)
    form = forms.MessageCustomer()
    if request.method == 'POST':
        form = forms.MessageCustomer(request.POST) 
        
        if form.is_valid():
            c = form.save(commit=False)
            c.user= user
            c.save()
            form.save()
            messages.success(request, "Message sent to {}".format(user.username))
            return redirect('accounts:message',pk=pk)
        else:
            
            form = forms.MessageCustomer(instance=user)
    context = {
        'form':form,
        'customer': user
    }        
    return render(request, 'accounts/message_customer.html', context) 
    
@login_required(login_url='login')
@allowed_users(allowed_roles=['Staff'])
def referrals(request,pk):
    customer = User.objects.get(pk=pk)
    refCount = customer.referredBy.count()
    referral = Profile.objects.filter(referredBy=customer).order_by("-user__date_joined")

    page = request.GET.get('page', 1)

    paginator = Paginator(referral, 10)
    try:
        referrals = paginator.page(page)
    except PageNotAnInteger:
        referrals = paginator.page(1)
    except EmptyPage:
       referrals = paginator.page(paginator.num_pages)
    
    context = {
        'customer':customer,
        "refList": referrals,
        "refCount":refCount
    }
    return render(request, 'accounts/referral_list.html', context) 

@login_required(login_url='login')
@allowed_users(allowed_roles=['Staff'])
def customer(request,pk):
    customer = User.objects.get(id=pk)
    capital = customer.account_balance
    profit =  customer.stats.profit
    totalEarning = customer.stats.totalEarning
    refEarn = customer.stats.referral_earning
    refCount = customer.referredBy.count()
    stf = Group.objects.get(name="Staff")
    group = customer.groups.all()
    if stf in group:
        staff = "Staff"
    elif customer.is_superuser:
        staff = "Admin" 
    else:
        staff = 'Customer'  
     
    
    simple_c = customer.simple.count()
    compound_c = customer.compound.count()
    order = customer.orders.all().order_by('-date_ordered')
    myfilter = OrderFilter(request.GET, queryset=order)
    order = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(order, 10)
    try:
        orders = paginator.page(page)
    except PageNotAnInteger:
        orders = paginator.page(1)
    except EmptyPage:
       orders = paginator.page(paginator.num_pages)

    context = {
        'customer':customer,
        'group': staff,
        'orders': orders,
        'myfilter': myfilter,
        'customer_o': order.count(),
        'simple_c':simple_c,
        'compound_c': compound_c,
        "capital":capital,
        'profit':profit,
        "refEarn": refEarn,
        "refCount":refCount,
        "totalEarning":totalEarning 
    }
    return render(request, 'accounts/customer.html', context) 


@login_required(login_url='login')
@allowed_users(allowed_roles=['Staff'])
def customers(request):
    customer = User.objects.all().order_by('-date_joined') 
    myfilter = CustomerFilter(request.GET, queryset=customer)
    customer = myfilter.qs
    page = request.GET.get('page', 1)

    paginator = Paginator(customer, 50)
    try:
        customers = paginator.page(page)
    except PageNotAnInteger:
        customers = paginator.page(1)
    except EmptyPage:
       customers = paginator.page(paginator.num_pages)
    
    context = {
        'customers':customers,
        'myfilter': myfilter,
    }
    return render(request, 'accounts/customers.html', context) 
 

@login_required(login_url='login')
@allowed_users(allowed_roles=['Staff'])
def account_setting(request):
    user = None
    try:
        user = request.user.customer or request.user
        print(user)
    except AttributeError:
        print('attribute error')

        form = forms.StaffForm(instance=user)
        if request.method == 'POST':
            form = forms.StaffForm(request.POST,request.FILES, instance=user)
            if form.is_valid(): 
                form.save()
                return redirect('accounts:edit')

        context={
            'form':form
        }
        return render(request, 'accounts/edit.html', context) 

@login_required(login_url='login')
@super_user_only
def order(request,pk):
    order_formset = inlineformset_factory(User,Order, fields=('product','status'), extra=7)
    customer = User.objects.get(pk=pk)
    formset = order_formset(instance=customer)
    #form = forms.OrderForm() 
    if request.method == 'POST':
        #form = forms.OrderForm(request.POST)
        formset = order_formset(request.POST, instance=customer)
        if formset.is_valid():
            formset.save()
            return redirect('home') 
        else:
            formset = order_formset(instance=customer)        
    context = {
        'formset':formset
    }
    return render(request, 'accounts/order_form.html', context)      


@login_required(login_url='login')
@super_user_only
def update_order(request,pk,c_pk):
    order = Order.objects.get(pk=pk)
    form = forms.OrderForm(instance=order)
    if request.method == 'POST':
        form = forms.OrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Succesfully")
            return redirect('accounts:customer',pk=c_pk) 
        else:
            form = forms.OrderForm(instance=order)           
    context = {
        'form':form,
        'order':order
    }
    return render(request, 'accounts/update_order.html', context)     


@login_required(login_url='login')
@super_user_only
def update_simple(request,pk,c_pk):
    simple = Simple.objects.get(pk=pk)
    form = forms.SForm(instance=simple)
    if request.method == 'POST':
        form = forms.SForm(request.POST, instance=simple)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Succesfully")
            return redirect('accounts:simples') 
        else:
            form = forms.SForm(instance=simple)           
    context = {
        'form':form,
        'simple':simple
    }
    return render(request, 'accounts/update_simple.html', context)

@login_required(login_url='login')
@super_user_only
def update_compound(request,pk,c_pk):
    compound = Compound.objects.get(pk=pk)
    form = forms.CForm(instance=compound)
    if request.method == 'POST':
        form = forms.CForm(request.POST, instance=compound)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Succesfully")
            return redirect('accounts:compounds') 
        else:
            form = forms.CForm(instance=compound)           
    context = {
        'form':form,
        'compound':compound
    }
    return render(request, 'accounts/update_compound.html', context)

@login_required(login_url='login')
@super_user_only
def update_Stopup(request,pk,c_pk):
    topup = TopUp.objects.get(pk=pk)
    form = forms.SimpleTopUpForm(instance=topup)
    if request.method == 'POST':
        form = forms.SimpleTopUpForm(request.POST, instance=topup)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Succesfully")
            return redirect('accounts:topups') 
        else:
            form = forms.SimpleTopUpForm(instance=topup)           
    context = {
        'form':form,
        'topup':topup
    }
    return render(request, 'accounts/update_topup.html', context)

@login_required(login_url='login')
@super_user_only
def update_Ctopup(request,pk,c_pk):
    topup = TopUpCompound.objects.get(pk=pk)
    form = forms.CompoundTopUpForm(instance=topup)
    if request.method == 'POST':
        form = forms.CompoundTopUpForm(request.POST, instance=topup)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Succesfully")
            return redirect('accounts:ctopups') 
        else:
            form = forms.CompoundTopUpForm(instance=topup)           
    context = {
        'form':form,
        'topup':topup
    }
    return render(request, 'accounts/update_topup.html', context)

@login_required(login_url='login')
@super_user_only
def delete_order(request, pk):
    order = Order.objects.get(pk=pk)
    form = forms.RemarkForm()
    message = None
    if request.method == 'POST':
        form = forms.RemarkForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            message = cleaned.get('message')
        order.delete()
        messages.success(request, "Deleted Succesfully")
        if message:
            send_mail('Payment Rejected', message, settings.DEFAULT_FROM_EMAIL, ['{}'.format(order.customer.email)])
        return redirect('board') 
    context = {
        'item': order,
        'form':form
    }    
    return render(request, 'accounts/delete_order.html', context)

@login_required(login_url='login')
@super_user_only
def delete_Stopup(request, pk):
    topup = TopUp.objects.get(pk=pk)
    if request.method == 'POST':
        topup.delete()
        return redirect('board') 
    context = {
        'item': topup,
        'namespace': 'deleteS'
    }    
    return render(request, 'accounts/delete_topup.html', context)


@login_required(login_url='login')
@super_user_only
def delete_Ctopup(request, pk):
    topup = TopUpCompound.objects.get(pk=pk)
    if request.method == 'POST':
        topup.delete()
        messages.success(request, "Deleted Succesfully")
        return redirect('board') 
    context = {
        'item': topup,
        'namespace': 'deleteC'
    }    
    return render(request, 'accounts/delete_ctopup.html', context)

@login_required(login_url='login')
@super_user_only
def update_payout(request,pk,c_pk):
    payout = Payout.objects.get(pk=pk)
    form = forms.PayoutForm(instance=payout)
    if request.method == 'POST':
        form = forms.PayoutForm(request.POST, instance=payout)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Succesfully")
            return redirect('accounts:payouts') 
        else:
            form = forms.PayoutForm(instance=payout)           
    context = {
        'form':form,
        'payout':payout
    }
    return render(request, 'accounts/update_payout.html', context)     


@login_required(login_url='login')
@super_user_only
def delete_payout(request, pk):
    payout = Payout.objects.get(pk=pk)
    if request.method == 'POST':
        payout.delete()
        messages.success(request, "Deleted Succesfully")
        return redirect('accounts:payouts') 
    context = {
        'item': payout
    }    
    return render(request, 'accounts/delete_payout.html', context)

@login_required(login_url='login')
@super_user_only
def update_loan(request,pk,c_pk):
    loan = Loan.objects.get(pk=pk)
    form = forms.LoanForm(instance=loan)
    if request.method == 'POST':
        form = forms.LoanForm(request.POST, instance=loan)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Succesfully")
            return redirect('accounts:loans') 
        else:
            form = forms.LoanForm(instance=loan)           
    context = {
        'form':form,
        'loan':loan
    }
    return render(request, 'accounts/update_loan.html', context)     


@login_required(login_url='login')
@super_user_only
def delete_loan(request, pk):
    loan = Loan.objects.get(pk=pk)
    if request.method == 'POST':
        loan.delete()
        messages.success(request, "Deleted Succesfully")
        return redirect('accounts:loans') 
    context = {
        'item': loan
    }    
    return render(request, 'accounts/delete_loan.html', context)



@login_required(login_url='login')
@super_user_only
def remove_user(request,pk):
    x = User.objects.get(id=pk)
    if request.method == 'POST':
            if x.is_superuser:
                pass
            else:
                CustomDeux.objects.get(user=x).delete()
                x.delete()
                messages.success(request, "User Deleted")
                return redirect('board')
    context = {
        'item':x
    }
    return render(request, 'accounts/delete_customer.html', context)


def mailer(text,email):
    message = text
    send_mail('Account Notification', message, settings.DEFAULT_FROM_EMAIL, ['{}'.format(email)])
    
@login_required(login_url='login')
@super_user_only
def disable_user(request,pk):
    form = forms.RemarkForm()
    xcustomer = User.objects.get(id=pk)
    message = None
    if request.method == "POST":
        form = forms.RemarkForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data
            message = cleaned.get('message')
            

        if xcustomer.is_active == True:
            
            xcustomer.is_active = False
            xcustomer.save()
      
            for x in xcustomer.simple.all():
                x.change = "Top Up"
                x.status = "Pending"
                x.save()
            for x in xcustomer.compound.all():
                x.change = "Top Up"
                x.status = "Pending"
                x.save()
            messages.success(request, "User Disabled Successfully")
            if message:
                mailer(message,xcustomer.email)
            return redirect('accounts:customer',pk=pk) 
        if xcustomer.is_active == False:
            xcustomer.is_active = True
            xcustomer.save()
            for x in xcustomer.simple.all():
                x.change = "Top Up"
                x.status = "Approved"
                x.save()
            for x in xcustomer.compound.all():
                x.change = "Top Up"
                x.status = "Approved"
                x.save()
            messages.success(request, "User Activated Successfully")
            if message:
                mailer(message,xcustomer.email)
            return redirect('accounts:customer',pk=pk) 

    context = {
            'form' : form,
            'item':xcustomer
        }
    
    return render(request,'accounts/disable_user.html', context)