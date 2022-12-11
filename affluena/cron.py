from .models import *
from datetime import timedelta, datetime,timezone
from django.core.mail import send_mail

from affluena.deuxModel  import CustomDeux

def delete_users():
    users = User.objects.filter(payed=False)
    user_list = []
    for x in users:
        if x.date_joined < datetime.now(timezone.utc)-timedelta(hours=7):
            if x.is_superuser:
                pass
            else:
                #CustomDeux.objects.get(user=x).delete()
                #x.delete()
                user_list.append(x)
    print(user_list)

def check_cron():
    for x in Simple.objects.all():
        pay_list = []
        if x.paydate.date() == datetime.today().date():
            pay_list.append(x.user.username)
    print(datetime.today().date(),pay_list)
            
def create_payout():
    
    names = []
    total = 0
    for x in Simple.objects.filter(status="Approved"):
        if x.due is not None and x.user.is_active:
            if x.due.date() > datetime.today().date():
                d = x.paydate - timedelta(days=7)
                due = d.date()
                today = datetime.today().date()
                if today == due:
                    amount = x.amount
                    profit = int(amount)*0.4
                    s = Payout(user=x.user,due=x.paydate,amount=profit,product='Simple Interest')
                    s.save()
                    names.append(x.user.full_name)
                    total += profit
                 
    if names:
        message = "Due Simple interest payout for {} in 7 days, in total of {}".format(names, total)
        send_mail('Due Payout', message, "support@affluena", ['hello@affluena'])
        print(datetime.today().date(),message)


    c_names = []
    c_total = 0
    for c in Compound.objects.filter(status="Approved"):
        if c.due is not None and c.user.is_active:
            if c.due.date() > datetime.today().date():
                due = c.due.date() - timedelta(days=7)
                today = datetime.today().date()
                if today == due:
                    profit = c.profit
                    c = Payout(user=c.user,due=c.paydate.paydate,amount=profit,product='Compound Interest',duration=c.duration)
                    c.save()
                    c_names.append(c.user.full_name)
                    c_total += profit
                    
    if c_names:
        message = "Due Compound interest payout for {} in 7 days. in total of {}".format(c_names, c_total)
        send_mail('Due Compound Payout', message, "support@affluena.org", ['hello@affluena.org'])
        print(datetime.today().date(),message)
   
   
def ref_payout():
    refpayout_names = []
    total=0
    for x in Stat.objects.all():
            if x.ref_payout > 0 and x.user.is_active:
                t = x.ref_payout
                c = ReferralPayout(user=x.user,amount=x.ref_payout,status="Pending")
                c.save()
                x.ref_payout = 0
                x.save()
                refpayout_names.append(x.user.full_name)
                total += t
    if refpayout_names:
        message = "Referral payout for  {} in total of {} ".format(refpayout_names,total)
        send_mail('Referral  Payout', message, "support@affluena.org", ['hello@affluena.org'])
        print(datetime.today().date(),message)
        

def credit_user():
    credit_names = []
    for x in Simple.objects.filter(status="Approved"):
        if x.due is not None and x.user.is_active:
            if x.due.date() > datetime.today().date():
                due = x.paydate.date()
                today = datetime.today().date()
                if today == due:
                    amount = x.amount
                    profit = int(amount)*0.4
                    x.user.stats.newprofit = profit
                    x.user.stats.save()
                    x.change = "TOP UP"
                    x.paydate += relativedelta(months=+1)
                    x.save()
                    credit_names.append(x.user.full_name)
    if credit_names:
        message = "Credited  {0} today".format(credit_names)
        print(datetime.today().date(),message)


    credit_cnames = []
    for  c in Compound.objects.filter(status="Approved"):
        if c.due is not None and c.user.is_active:
            if c.due.date() > datetime.today().date():
                due = c.due.date() 
                today = datetime.today().date()
                if today == due:
                    profit = c.profit
                    c.user.stats.newprofit = int(c.amount) * 0.2
                    c.user.stats.save()
                    c.change = "TOP UP"
                    c.paydate += relativedelta(months=+1)
                    c.save()
                    credit_cnames.append(c.user.full_name)
    if credit_cnames:
        message = "Credited  {0} for compounding  today".format(credit_cnames)
        print(datetime.today().date(),message)