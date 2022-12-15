import string
import random
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from allauth.account.signals import user_signed_up
from dateutil.relativedelta import relativedelta
from datetime import datetime,timedelta
from simple_history.models import HistoricalRecords
from django.dispatch import receiver
from django.urls import reverse_lazy
from .utils import generate_ref_code,create_simple_pdf,create_compound_pdf,sendEmailUtil
import random
from django.core.validators import RegexValidator
from allauth.account.utils import complete_signup
from io import BytesIO
from django.core.files import File
from .utils import render_to_pdf
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from django.core.mail import send_mail,EmailMultiAlternatives
from calendar import monthrange
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from allauth.account.signals import email_confirmed
from uuid import uuid4
from datetime import datetime
from django.utils import timezone
# Create your models here.
 
class User(AbstractUser):
    STATUS = (
        ('Simple Interest', 'Simple Interest'),
        ('Compound Interest', 'Compound Interest')
    )
  
    full_name = models.CharField(max_length=400,blank=True, null=True)
    address = models.CharField(max_length=300,blank=True, null=True)
    phone_regex = RegexValidator( regex   =r'^\+?1?\d{9,14}$', message ="Phone number must be entered in the format: '+999999999'. Up to 14 digits allowed.")
    phone = models.CharField(validators=[phone_regex], max_length=17, unique=True,blank=True, null=True)
    city = models.CharField(max_length=200,blank=True, null=True)
    country = models.CharField(max_length=200,blank=True, null=True)
    state = models.CharField(max_length=200,blank=True, null=True)
    next_of_kin = models.CharField(max_length=200,blank=True, null=True)
    bank_name = models.CharField(max_length=200,blank=True, null=True)
    account_no = models.CharField(max_length=200,blank=True, null=True)
    account_name = models.CharField(max_length=300,blank=True, null=True)
    two_FA = models.BooleanField(default=False)
    is_super = models.BooleanField(default=False)
    contribution_amount = models.DecimalField(max_digits=15, decimal_places=2,default=0.00)
    contribution_type = models.CharField(max_length=200, choices=STATUS, blank=True, null=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    account_balance = models.DecimalField(max_digits=15, blank=True, null=True,decimal_places=0, default=0,)
    active_package = models.CharField(max_length=300,blank=True, null=True)
    email_verified = models.BooleanField(default=False,blank=True, null=True)
    compounding = models.BooleanField(default=False,blank=True, null=True)
    simple_con = models.BooleanField(default=False,blank=True, null=True)
    totalWithdrawn = models.DecimalField(max_digits=15,blank=True, null=True,decimal_places=2, default=0)
    payed = models.BooleanField(default=False,null=True)
    paypending = models.BooleanField(default=True,null=True)
    pdf= models.FileField(upload_to='pdfs/', null=True, blank=True)
    referral_code=models.CharField(max_length=200, blank=True, null=True)
    profit = models.DecimalField(max_digits=15,decimal_places=2,default=0, blank=True, null=True)
    compound_profit = models.DecimalField(max_digits=15,decimal_places=2,default=0, blank=True, null=True)
    can_topup = models.BooleanField(default=True,null=True)
    can_refer = models.BooleanField(default=True,null=True)
   





    
    def __str__(self):
        return self.username

    def monthjoined(self):
        return self.date_joined.strftime('%Y')


       


class Message(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="messages")
    text = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return str(self.user)

   


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        verbose_name='user',
        related_name="profile"
    )
    code = models.CharField(max_length=200, blank=True, null=True)
    referredBy = models.ForeignKey(User, related_name='referredBy', on_delete=models.CASCADE, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)



    def __str__(self):
        return self.user.username


    def get_reffered_profile(self):
        pass

    

class Payout(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    )
    PROD = (
       ('Simple Interest', 'Simple Interest'),
        ('Compound Interest', 'Compound Interest')
    )
    DUR = (
        (6,6),
        ( 9,9),
        (12, 12),
        (24, 24),
    )
    duration = models.IntegerField(choices=DUR,default=6)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payed_out")
    amount = models.DecimalField(max_digits=15,decimal_places=2)
    status = models.CharField(max_length=200, choices=STATUS, default="Pending")
    date_requested =  models.DateTimeField(auto_now_add=True, null=True)
    due = models.DateTimeField(null=True)
    product = models.CharField(max_length=200, choices=PROD,default="Simple Interest")


    def __str__(self):
        return self.user.username
        
class ReferralPayout(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="ref_payed_out")
    amount = models.DecimalField(max_digits=15,decimal_places=2)
    status = models.CharField(max_length=200, choices=STATUS, default="Pending")
    date_requested =  models.DateTimeField(auto_now_add=True, null=True)
   
    def __str__(self):
        return self.user.username

class Compound(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    )
    R = (
        
        ('DEPOSIT','DEPOSIT'),
        ('TOP UP','TOP UP'),
        ('EDIT','EDIT'),
        ('DATE','DATE'),
        ('NOPDF','NOPDF'),
        ('NEWPDF','NEWPDF'),
    )
    DUR = (
        (6,6),
        ( 9,9),
        (12, 12),
        (24, 24),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="compound")
    active = models.BooleanField(default=False)
    change = models.CharField(max_length=200, choices=R, default="DEPOSIT")
    duration = models.IntegerField(choices=DUR)
    status = models.CharField(max_length=200, choices=STATUS)
    amount = models.DecimalField(max_digits=15,decimal_places=2)
    date_requested =  models.DateTimeField(auto_now_add=True, null=True)
    completed = models.BooleanField(default=False)
    ticket = models.FileField(upload_to='pdfs/ticket', null=True, blank=True)
    pdf= models.FileField(upload_to='pdfs/compound', null=True, blank=True)
    profit = models.DecimalField(max_digits=15,decimal_places=2, blank=True, null=True)
    txid = models.CharField(max_length=300, blank=True, null=True)
    due = models.DateTimeField()
    paydate = models.DateTimeField(null=True, blank=True)
    


    def __str__(self):
        return self.user.username

    def save(self, *args, **kwargs):
        if self.status == "Approved":

            if self.change == "TOP UP":
                pass
            if self.change == "DATE":
                self.profit = (int(self.amount)*((1+(240/(100*12)))**(int(self.duration)))) - int(self.amount)
                self.due = self.date_requested + relativedelta(months=+int(self.duration))
                create_compound_pdf(self)
            if self.change == "EDIT":
                self.profit = (int(self.amount)*((1+(240/(100*12)))**(int(self.duration)))) - int(self.amount)
                create_compound_pdf(self)
            if self.change == "DEPOSIT":
                
                profit = int(self.amount)*((1+(240/(100*12)))**(int(self.duration)))
                acca = profit - int(self.amount)
                self.profit =  acca
                self.user.compound_profit += int(acca)
                self.user.compounding = True
                self.user.save()
                
            if self.change == "NEWPDF":
                create_compound_pdf(self)
            if self.change == "NOPDF":
                pass
            

        super().save(*args, **kwargs) 

class Simple(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        
    )
    R = (
        ('DEPOSIT','DEPOSIT'),
        ('TOP UP','TOP UP'),
        ('EDIT','EDIT'),
        ('DATE','DATE'),
         ('NOPDF','NOPDF'),
        ('NEWPDF','NEWPDF'),

        
    )
   
    DUR = (
        (6,6),
        ( 9,9),
        (12, 12),
        (24, 24),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="simple")
    active = models.BooleanField(default=False)
    completed = models.BooleanField(default=False)
    duration = models.IntegerField(default=6,choices=DUR)
    status = models.CharField(max_length=200, choices=STATUS)
    change = models.CharField(max_length=200, choices=R, default="DEPOSIT")
    amount = models.DecimalField(max_digits=15,decimal_places=2)
    date_requested =  models.DateTimeField(auto_now_add=True, null=True)

    due = models.DateTimeField(null=True, blank=True)
    ticket = pdf= models.FileField(upload_to='pdfs/ticket', null=True, blank=True)
    pdf= models.FileField(upload_to='pdfs/simple', null=True, blank=True)
    profit = models.DecimalField(max_digits=15,decimal_places=2, blank=True, null=True)
    txid = models.CharField(max_length=300, blank=True, null=True)
    paydate = models.DateTimeField(null=True, blank=True)
   


        
    def __str__(self):
        return self.user.username
    
    


    def save(self, *args, **kwargs):
        if self.status == "Approved":
          
            if self.change == "TOP UP":
                pass
            if self.change == "DATE":
                self.profit = int(self.amount)*0.4*int(self.duration)
                self.due = self.date_requested + relativedelta(months=+int(self.duration))
                create_simple_pdf(self)
            if self.change == "EDIT":
                self.profit = int(self.amount)*0.4*int(self.duration)
                create_simple_pdf(self)
                
            if self.change == "DEPOSIT":
                
                profit = int(self.amount)*0.4*int(self.duration)
                self.profit =  profit
                self.user.profit += int(profit)
                self.user.simple_con = True
                self.user.save()
                
            if self.change == "NEWPDF":
                create_compound_pdf(self)
            if self.change == "NOPDF":
                pass
            
            

        super().save(*args, **kwargs) 


class TopUp(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Simple,related_name="top_up" ,on_delete=models.CASCADE)
    status = models.CharField(max_length=200, choices=STATUS)
    amount = models.DecimalField(max_digits=15,decimal_places=2, default=0)
    date_added =  models.DateTimeField(auto_now_add=True, null=True)
    topup_date = models.DateTimeField(null=True, blank=True)
    proof = models.ImageField(blank=True, null=True, upload_to="proof")
    txid = models.CharField(max_length=300, blank=True, null=True)
    diff = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.status == "Approved":
                today = datetime.today()
                d = self.plan.due.date()
                fut = datetime.strptime(str(d), "%Y-%m-%d")
                diff = 0
                while today <= fut:
                    today += timedelta(days=monthrange(today.day, today.month)[1])
                    diff += 1
                self.plan.change = "TOP UP"
                self.plan.amount += self.amount
                amount = int(self.plan.amount) 
                profit = int(amount)*0.4*(diff)
                self.plan.profit =  profit
                self.plan.save()
                self.user.account_balance += self.amount
                self.user.profit = profit
               
                self.user.save()
        super().save(*args, **kwargs)


    def __str__(self):
         return self.user.full_name

class TopUpCompound(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    plan = models.ForeignKey(Compound,related_name="top_up", on_delete=models.CASCADE)
    status = models.CharField(max_length=200, choices=STATUS)
    amount = models.DecimalField(max_digits=15,decimal_places=2, default=0)
    date_added =  models.DateTimeField(auto_now_add=True, null=True)
    topup_date = models.DateTimeField(null=True, blank=True)
    proof = models.ImageField(blank=True, null=True, upload_to="proof")
    txid = models.CharField(max_length=300, blank=True, null=True)
    diff = models.IntegerField(default=1)

    def save(self, *args, **kwargs):
        if self.status == "Approved":
                today = datetime.today()
                d = self.due.date()
                fut = datetime.strptime(str(d), "%Y-%m-%d")
                diff = 0
                while today <= fut:
                    today += timedelta(days=monthrange(today.day, today.month)[1])
                    diff += 1
                amount = int(self.plan.amount) + int(self.amount)
                profit = int(amount)*((1+(240/(100*12)))**(int(diff)))
                acca = profit - self.amount
                self.plan.change = "TOP UP"
                self.plan.amount += self.amount
                self.plan.save()
                self.profit =  acca
                self.user.compound_profit += int(acca)
                self.user.account_balance += self.amount
                self.user.save()
                
        super().save(*args, **kwargs)

        def __str__(self):
            return self.user.full_name

class Withdraw(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15,decimal_places=2)
    status = models.CharField(max_length=200, choices=STATUS)
    date_ordered = models.DateTimeField(auto_now_add=True, verbose_name="Date Requested")
    date_approved = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.user.username


    
    def save(self, *args, **kwargs):
        if self.status == "Approved":
            u = self.user
            u.totalWithdrawn += self.amount
            u.save()
        super().save(*args, **kwargs)    


        
        
    



class Loan(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved')
    )
    user = models.ForeignKey(User, related_name="loans", on_delete=models.CASCADE)
    plan = models.ForeignKey(Compound,related_name="loans", on_delete=models.CASCADE,null=True)
    amount = models.DecimalField(max_digits=15,decimal_places=2)
    status = models.CharField(max_length=200, choices=STATUS)
    date_ordered = models.DateTimeField(auto_now_add=True, verbose_name="Date Requested")
    date_approved = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return self.user.username


    
    def save(self, *args, **kwargs):
        if self.status == "Approved":
            message = "Your Loan application for the amount of {} been 30% of  your expected profit which is {}. has been approved".format(self.amount,self.plan.profit )
            send_mail('Loan Approval', message, settings.DEFAULT_FROM_EMAIL, ['{}'.format(self.user.email)])
        super().save(*args, **kwargs) 

class Order(models.Model):
    STATUS = (
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
    )

    PROD = (
       ('Simple Interest', 'Simple Interest'),
        ('Compound Interest', 'Compound Interest')
    )

    DUR = (
        (6,6),
        ( 9,9),
        (12, 12),
        (24, 24),
    )
    customer = models.ForeignKey(User, related_name='orders',on_delete=models.CASCADE, null=True)
    product = models.CharField(max_length=200, choices=PROD)
    status = models.CharField(max_length=200, choices=STATUS)
    duration = models.IntegerField(choices=DUR)
    amount = models.DecimalField(max_digits=15, decimal_places=2,default=0.00)
    proof = models.ImageField(blank=True, null=True, upload_to="proof")
    date_ordered = models.DateTimeField(auto_now_add=True)
    created     = models.DateTimeField(editable=False)
    modified    = models.DateTimeField()
    txid = models.CharField(max_length=300, blank=True, null=True)
    tx_ref = models.CharField(max_length=300, blank=True, null=True)
    flw_ref = models.CharField(max_length=300, blank=True, null=True)
    first = models.BooleanField(default=False, blank=True, null=True)


    
    def __str__(self):
        return self.customer.username


    def save(self,*args, **kwargs):
        acc = self.customer
        acc.payed = True
        acc.paypending = True
        acc.save()
        if not self.id:
            self.created = timezone.now()
        self.modified = timezone.now() 
        if  self.status == "Approved":
                acc = self.customer
                amountx = self.amount
              
                #if self.first == True :
                    #amountx = int(self.amount) - 5000
                    #acc.account_balance += amountx
                    #acc.paypending = False
                    #acc.save()
                #else:
                    #amountx = self.amount
                    #acc.account_balance += amountx
                    #acc.paypending = False
                    #acc.save()
                
                
                if self.product == "Compound Interest":
                    acc.compounding = True
                    acc.save()
                    compound = Compound.objects.create(user=self.customer, active=True, 
                    duration=self.duration, due = self.date_ordered + relativedelta(months=+int(self.duration)),
                    status=self.status,
                    amount=amountx, txid = self.txid, paydate = self.date_ordered + relativedelta(months=+1)
                    )
                    
                    compound.save()
                elif self.product == "Simple Interest":
                    acc.simple_con = True
                    acc.save()
               
                    simple = Simple.objects.create(user=self.customer, active=True, 
                    duration=int(self.duration), due = self.created + relativedelta(months=+int(self.duration)),
                    status=self.status,
                    amount=amountx,txid = self.txid,paydate = self.created + relativedelta(months=+1)
                    )
                    simple.save()

                """ 
                Disable a user from getting referral earning
                ref = User.objects.get(username=)
                if acc.profile.referredBy == ref:
                    print("Passed on this niggar")
                    pass
                
                """
                if acc.profile.referredBy:
                    u = acc.profile.referredBy
                    u.stats.new_refEarning = int(amountx) * 0.02
                    u.stats.changeReason = "Refferal Earning"
                    u.stats.save()
        super().save(*args, **kwargs)
        





class Stat(models.Model):
    STATUS = (
        ('Interest Earning','ROI' ),
        ('Refferal Earning','Refferal'),
    )
    
    user = models.OneToOneField(User, related_name="stats", on_delete=models.CASCADE)
    payed_out = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    newprofit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    newcprofit = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    profit = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name="ROI")
    cprofit = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name="ROI")
    totalEarning = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name="Total Earning")
    referral_earning = models.DecimalField(max_digits=15, decimal_places=2, default=0,verbose_name="Affiliate Earning")
    new_refEarning = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    changeReason = models.CharField(max_length=100, choices=STATUS, default='Interest Earning')
    history = HistoricalRecords()
    paydate = models.DateTimeField(null=True, blank=True)
    cpaydate = models.DateTimeField(null=True, blank=True)
    
    ref_payout = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
   

 

    
    def __str__(self):
        return self.user.username

    def save(self,*args, **kwargs):
        self.profit += int(self.newprofit) 
        self.cprofit += int(self.newcprofit) 
        self.totalEarning += int(self.newprofit) + int(self.new_refEarning)
        self.referral_earning += int(self.new_refEarning)
        self.ref_payout += int(self.new_refEarning)
        self.newprofit = 0
        self.new_refEarning =  0    
        super().save(*args, **kwargs)    

    class Meta: 
        
        # Add verbose name 
        verbose_name = 'User Stat'    

class CompletedPlan(models.Model):
    user = models.ForeignKey(User, related_name="completed_kits", on_delete=models.CASCADE)
    order = models.ForeignKey(Order, related_name="completed_kits", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=15, decimal_places=2,default=0.00)
    
    history = HistoricalRecords()


    def __str__(self):
        return self.order.product

def generate_obj_pdf(instance_id):
        obj = User.objects.get(id=instance_id)
        context = {'instance': obj}
        pdf = render_to_pdf('pdf/invoices.html', context)
        filename = "YourPDF_Order{}.pdf" 
        obj.pdf.save(filename, File(BytesIO(pdf.content)))





def userInstance(instance):
    Stat.objects.create(user=instance)
    
@receiver(email_confirmed)
def emailconfirmed_(request, email_address, **kwargs):
    Message.objects.create(user=email_address.user, text="Welcome to Affluena")

@receiver(post_save, sender=User)
def create_user_profile(sender,instance, created, **kwargs):
    if created:
        if instance.referral_code is not None:
            
            try:
                refferer = Profile.objects.get(code=instance.referral_code)  
                Profile.objects.create(user=instance,code=generate_ref_code(),referredBy=refferer.user)
                userInstance(instance)
            except ObjectDoesNotExist:
                Profile.objects.create(user=instance,code=generate_ref_code())
                userInstance(instance)
        else :
            Profile.objects.create(user=instance,code=generate_ref_code())
            userInstance(instance)
        instance.profile.save()
        instance.stats.save()
        message = "A user {0} has just registered on the website".format(instance.full_name)
        send_mail('New Registration', message, settings.DEFAULT_FROM_EMAIL, [settings.DEFAULT_FROM_EMAIL])





@receiver(post_save, sender=Order)
def create_user_payed(sender,instance, created, **kwargs): 
     if instance.status == "Approved":
          acc = instance.customer
          acc.payed = True
          acc.paypending = False
          acc.save()
          message = "{0} has said to have made a payment of {1}".format(instance.customer.username,instance.amount)
          send_mail('Payment Made', message, settings.DEFAULT_FROM_EMAIL, ['hello@affluena.org'])


 
    

@receiver(post_save, sender=Simple)
def create_user_simple(sender,instance, created, **kwargs):
    if created:
        user = instance.user
        txid = instance.txid
        invoice = {
            'date': instance.date_requested.strftime('%Y-%m-%d'),
            "no":txid,
            'amount': "{:,.2f}". format(instance.amount),
            'contribution': "Simple Interest",
            "account_name" : user.account_name,
            "email":user.email
           
        }
        invoice_context = {"instance": invoice}
        inv = render_to_pdf('pdf/invoices.html', invoice_context)
        instance.ticket.save("Receipt.pdf", File(BytesIO(inv.content)))
        inv = instance.ticket.read()
        sendEmailUtil(instance,user,inv)
      
@receiver(post_save, sender=Compound)
def create_user_compound(sender,instance, created, **kwargs):
    if created:
        user = instance.user
        txid = instance.txid
        invoice = {
            'date': instance.date_requested.strftime('%Y-%m-%d'),
            "no":txid,
            'amount': "{:,.2f}". format(instance.amount),
            'contribution': "Compound Interest",
            "account_name" : user.account_name,
            "email":user.email
           
        }
      
        invoice_context = {"instance": invoice}
        inv = render_to_pdf('pdf/invoices.html', invoice_context)
        instance.ticket.save("Receipt.pdf", File(BytesIO(inv.content)))
        inv = instance.ticket.read()
        sendEmailUtil(instance,user,inv)
        



@receiver(post_save, sender=Payout)
def create_payout(sender,instance,**kwargs):
    if instance.status == "Approved":
        instance.user.stats.payed_out += instance.amount
        if instance.product == "Simple Interest":
            message = "We have settled you {0} amount for your return for 1 month".format(instance.amount)
            send_mail('Payment Made', message, settings.DEFAULT_FROM_EMAIL, ['{}'.format(instance.user.email)])

        if instance.product == "Compound Interest":
            message = "We have settled you {0} amount for your return for {1} month".format(instance.amount, instance.duration)
            send_mail('Payment Made', message, settings.DEFAULT_FROM_EMAIL, ['{}'.format(instance.user.email)])
      

@receiver(post_save, sender=ReferralPayout)
def create_refpayout(sender,instance,**kwargs):
    if instance.status == "Approved":
        instance.user.stats.ref_payout = 0
        instance.user.stats.save()
        message = "We have settled you {0} amount for your referral earning".format(instance.amount)
        send_mail('Referral Payment Made', message, settings.DEFAULT_FROM_EMAIL, ['{}'.format(instance.user.email)])
        
@receiver(post_save, sender=Message)
def create_message(sender,instance,created,**kwargs):
    if created:
        message = "You have a new message in your inbox "
        #send_mail('New  message', message, settings.DEFAULT_FROM_EMAIL, ['{}'.format(instance.user.email)])
      