from django.contrib import admin
from .models import *
from django.contrib import messages 
from allauth.socialaccount.models import SocialToken, SocialAccount, SocialApp
from django.contrib.sites.models import Site
from django.contrib.auth.models import Group
from allauth.account.admin  import EmailAddress
from rest_framework.authtoken.models import TokenProxy
from rest_framework.authtoken.admin import TokenAdmin

class UserAdmin(admin.ModelAdmin): 
    search_fields = ['full_name']
    list_display = ('full_name', 'active','account_balance', 'date_joined') 

    def full_name(self, obj):
        return obj.full_name
    
    full_name.short_description = "Name"
  
    def active(self, obj): 
        return obj.is_active == 1

    def make_active(modeladmin, request, queryset): 
        queryset.update(is_active = 1) 
        messages.success(request, "Selected Record(s) Marked as Active Successfully !!") 
  
    def make_inactive(modeladmin, request, queryset): 
        queryset.update(is_active = 0) 
        messages.success(request, "Selected Record(s) Marked as Inactive Successfully !!") 
  
    make_active.short_description = "Make user active"
    make_inactive.short_description = "Make user inactive" 
  
    def has_delete_permission(self, request, obj = None): 
        return False    
    def delete_queryset(modeladmin, request, queryset):
        queryset.delete()
        messages.success(request, "Selected Record(s) Deleted Successfully !!")


    active.boolean = True
    delete_queryset.short_description = "Deleted User"
    
    actions = [make_active,make_inactive, delete_queryset ]

class StatAdmin(admin.ModelAdmin):
    search_fields = ['user__full_name']
    list_display = ('user','profit','totalEarning','referral_earning')
    
class RefAdmin(admin.ModelAdmin):
    search_fields = ['user__full_name']
    list_display = ('full_name','amount','status')
    
    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = "Name"
    
    def make_active(modeladmin, request, queryset): 
        for x in queryset:
            if x.status == "Approved":
                pass
            else:
                x.status = 'Approved'
                x.save()
        messages.success(request, "Selected Record(s) Marked as Approved Successfully !!")  

    def make_inactive(modeladmin, request, queryset): 
        queryset.update(status = 'Pending') 
        messages.success(request, "Selected Record(s) Marked as Pending Successfully !!")    

    make_active.short_description = "Approve Payout"
    make_inactive.short_description = "Revert to Pending" 
    actions = [make_active,make_inactive]

class LoanAdmin(admin.ModelAdmin):
    search_fields = ['user__username']
    list_display = ('user','amount','status','date_ordered')
    
class TopUpAdmin(admin.ModelAdmin):
    search_fields = ['user__full_name']
    list_display = ['full_name','active_amount','top_amount','date_added']

    def full_name(self, obj):
        return obj.user.full_name
    def active_amount(self, obj):
        return obj.plan.amount
    def top_amount(self, obj):
        return obj.amount
    full_name.short_description = "Name"
    active_amount.short_description = "Active Amount"
    top_amount.short_description = "Top Up Amount"

class SimpleAdmin(admin.ModelAdmin):
    search_fields = ['user__full_name']
    list_display = ['full_name','amount','date_requested']
    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = "Name"


class PayoutAdmin(admin.ModelAdmin):
    ordering = ['due']
    search_fields = ['user__full_name']
    list_display = ('full_name','amount','due','status')   
    
    
    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = "Name"
    
    def make_active(modeladmin, request, queryset): 
        for x in queryset:
            if x.status == "Approved":
                pass
            else:
                x.status = 'Approved'
                x.save()
        messages.success(request, "Selected Record(s) Marked as Approved Successfully !!")  

    def make_inactive(modeladmin, request, queryset): 
        queryset.update(status = 'Pending') 
        messages.success(request, "Selected Record(s) Marked as Pending Successfully !!")    

    make_active.short_description = "Approve Payout"
    make_inactive.short_description = "Revert to Pending" 
    actions = [make_active,make_inactive]
    
class OrderAdmin(admin.ModelAdmin):
    search_fields = ['customer__username']
    list_display = ('full_name','product','amount','duration','status','date_ordered','txid')   
    
    def full_name(self, obj):
        return obj.customer.full_name
    full_name.short_description = "Name"
    
    def make_active(modeladmin, request, queryset): 
        for x in queryset:
            if x.status == "Approved":
                pass
            else:
                x.status = 'Approved'
                x.save()
        messages.success(request, "Selected Record(s) Marked as Approved Successfully !!")  

    def make_inactive(modeladmin, request, queryset): 
        queryset.update(status = 'Pending') 
        messages.success(request, "Selected Record(s) Marked as Pending Successfully !!")    

    make_active.short_description = "Approve Order"
    make_inactive.short_description = "Revert to Pending" 
    actions = [make_active,make_inactive]

class WithdrawAdmin(admin.ModelAdmin):
    
    list_display = ('user','amount','status','date_ordered')   
    def make_active(modeladmin, request, queryset): 
        for x in queryset:
            if x.status == "Approved":
                pass
            else:
                x.status = 'Approved'
                x.save()
        messages.success(request, "Selected Record(s) Marked as Approved Successfully !!")  

    def make_inactive(modeladmin, request, queryset): 
        queryset.update(status = 'Pending') 
        messages.success(request, "Selected Record(s) Marked as Pending Successfully !!")    

    make_active.short_description = "Approve Withdrawal"
    make_inactive.short_description = "Revert to Pending" 
    actions = [make_active,make_inactive]

class CompoundAdmin(admin.ModelAdmin):
    
    search_fields = ['user__full_name']
    list_display = ['full_name','amount','date_requested'] 
    def make_active(modeladmin, request, queryset): 
        queryset.update(active = 1) 
        messages.success(request, "Selected Record(s) Marked as Active Successfully !!")  

    def make_inactive(modeladmin, request, queryset): 
        queryset.update(active = 0) 
        messages.success(request, "Selected Record(s) Marked as Inactive Successfully !!")    

    def full_name(self, obj):
        return obj.user.full_name
    full_name.short_description = "Name"
    make_active.short_description = "Activate Compounding"
    make_inactive.short_description = "Deactivate Compounding" 
    actions = [make_active,make_inactive]


admin.site.site_header = 'administration'
admin.site.site_title = 'Admin'
# Register your models here.
admin.site.register(User,UserAdmin) 
admin.site.register(Order,OrderAdmin)
admin.site.register(Simple, SimpleAdmin)
admin.site.register(Message)
admin.site.register(Payout,PayoutAdmin)
admin.site.register(Loan,LoanAdmin)
admin.site.register(ReferralPayout, RefAdmin)
admin.site.register(TopUp,TopUpAdmin)
admin.site.register(TopUpCompound,TopUpAdmin)
admin.site.unregister(SocialToken)
admin.site.unregister(SocialAccount)
admin.site.unregister(SocialApp)
admin.site.register(Stat,StatAdmin)
admin.site.register(Withdraw,WithdrawAdmin)
admin.site.register(Compound,CompoundAdmin)
#admin.site.unregister(Group)
admin.site.unregister(Site)
#admin.site.unregister(EmailAddress)
admin.site.unregister(TokenProxy)
