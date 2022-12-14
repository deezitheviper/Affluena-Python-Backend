
from rest_framework import viewsets
from rest_framework.generics import ListAPIView, CreateAPIView, GenericAPIView
from rest_framework.mixins import UpdateModelMixin, DestroyModelMixin
from rest_framework.response import Response
from rest_framework.mixins import CreateModelMixin
from affluena.models import *
from affluena.models import CompletedPlan as kitmodel
from .serializers import *
from affluena.api.serializers import *
from rest_framework.views import APIView
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.parsers import MultiPartParser, FormParser
from uuid import uuid4
from affluena.models import Payout as Payouts
import requests
from binascii import unhexlify,hexlify
from django.core.mail import send_mail
from affluena.services import *



def send_phone(code, phone):
    url = "https://api.80kobosms.com/v2/app/sendsms"
    access_token = ""
    message = "Your Withdrawal Confirmation code: {}".format(code)
    
    PARAMS = {'message':message,'sender_name':"Affluena",'recipients':phone}
    r = requests.post(url,
      headers={'Content-Type':'application/json',
               'Authorization': 'Bearer {}'.format(access_token)}, params=PARAMS)
    print(r.text)

def send_mfa_code(phone, mfa_code):
        code = mfa_code 
        send_phone(code, phone)
        


class PhoneRequestDetail(APIView): 
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        serializer_class = Phone(data=request.data)
        if serializer_class.is_valid():
            data = serializer_class.validated_data
            phone = data.get('phone')
            bin_key = uuid4().hex
            key = unhexlify(bin_key) 
            code = generate_mfa_code(key, drift=1)
            client_key = hexlify(key)
            send_mfa_code(phone,code)
            return Response({"success": "Verification code sent","key":client_key})
        return Response({'error': "Failed"}, status=status.HTTP_400_BAD_REQUEST)

class PhoneVerifyDetail(APIView):  
    permission_classes = (IsAuthenticated,)
    def post(self, request, *args, **kwargs):
        serializer_class = PhoneVerify(data=request.data)  
        if serializer_class.is_valid():
             data = serializer_class.validated_data
             code = data.get('phonecode')
             bin_key = data.get('bin_key')
             verified = verify_mfa_code(unhexlify(bin_key),code) 
             if verified:
                return Response({"success": "Verified"})
        return Response({'error': "Invalid code"}, status=status.HTTP_400_BAD_REQUEST)

class MessageView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('username', None)
        msg =  Message.objects.filter(user__username=username).values()
           
        
        return Response({'msg': msg})



class RefView(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('username', None)
        u = User.objects.get(username=username)
        refs =[]
        r = u.referredBy.all()
        for x in r:
            user = {
                "username": x.user.username,
                "date_joined": x.user.date_joined,
            }
            refs.append(user)
           
        
        return Response({'refs': refs})


class CheckCart(APIView):
    
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('username', None)
        u = User.objects.get(username=username)
        topup = u.can_topup 
        simple = ""
        compound = ""
        c = ""
        s = ""
        s_o = ""
        s_expired = ""
        c_o = ""
        c_expired = ""
        
        if u.simple_con == True:
            
            
            x = u.simple.last()
            
            if x:
                s= "Simple Interest"
                s_expired = x.due.date() < datetime.today().date()
                s_o = u.simple.values().last()
        
            
        if u.compounding == True:
            
            x = u.compound.last()
            if x:
                c = "Compound Interest"
                c_expired = x.due.date() < datetime.today().date()
                c_o = u.compound.values().last()

        return Response({"s_expired": s_expired,"c_expired": c_expired,"paypending":u.paypending, "s": s, "c":c, "simple":s_o,"compound":c_o,"topup":topup})

class ProfileView(APIView):
    
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('username', None)
        profile = Profile.objects.get(user__username=username)
        account_b = "{:,}".format(profile.user.account_balance)
        u = User.objects.get(username=username)
        cp = u.compounding
        refCount = u.referredBy.count()
        flush = u.date_joined + timedelta(hours=7)
        p=""
        payed = u.payed
        pay_pending = u.paypending
        o = u.orders.last()
        if o:
            p = o.product
        s_d=""
        s_expired = ""
        c_d=""
        c_expired = ""
        if u.simple_con == True:
            s = u.simple.last()
            if s:
                s_d = u.stats.paydate
                s_expired = s.due.date() < datetime.today().date()
       
            
        if u.compounding == True:
            s = u.compound.last()
            if s:
                c_d = u.stats.cpaydate
                c_expired = s.due.date() < datetime.today().date()
    
    
        return Response({"code": profile.code,"pay_pending": pay_pending,"account_b": account_b,"c_expired":c_expired,"s_expired":s_expired, "c_due":c_d, "s_due":s_d, "payed":payed, "flush": flush,"refCount":refCount,"cp":cp })  

class TxView(APIView):
    
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('username', None)
        u = User.objects.get(username=username)
        txs = []

        if  u.simple.last() and u.compound.last():
            txs += u.simple.all().values()
        if u.compound.last():
            txs += u.compound.all().values()

       
    
    
        return Response({"txs": txs})  

class WithdrawCheck(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('username', None)
        u = User.objects.get(username=username)
        s_available = False
        c_available = False
        l = []
        if u.simple_con == True:
            for s in u.simple.all():
                if s.due.date() < datetime.now().date() :
                    s_available = True
                    user = {
                        "product": "Simple Interest",
                        "amount": s.amount,
                    }
                    l.append(user)
        if u.compounding == True:
           for s in u.compounding.all():
                if s.due.date() < datetime.now().date():
                    c_available = True
                    user = {
                        "product": "Compound Interest",
                        "amount": s.amount,
                    }
                    l.append(user)
        return Response({"s_available": s_available,"c_available": c_available, "log":l}) 
        
        
class LoanView(APIView):
    
    permission_classes = (IsAuthenticated,)
    def get(self, request, *args, **kwargs):
        username = self.request.query_params.get('username', None)
        u = User.objects.get(username=username)
        payed = u.payed
        p=""
        o = u.orders.last()
        if o:
            p = o.product
        active = False
        loans = False
        l = ""
        if u.compounding == True:
            s = u.compound.first()
            if s.duration >= 12:
                d = s.date_requested
                c = datetime.now(timezone.utc) - d 
                if c.days > 90:
                    l = int(s.profit) * 0.3
                    active = True
        if u.loans.last():
            loans = True
        return Response({"active": active, 'available':l, 'loan':loans})  




class OrderListView(ListAPIView):
    
    serializer_class = OrderSerializer 
    
    
    def get_queryset(self):
        queryset = Order.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(customer__username=username)
        return queryset






class TopUpList(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TopUpListS

    def get_queryset(self):
        queryset = TopUp.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset

class TopUpCList(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = TopUpCListS

    def get_queryset(self):
        queryset = TopUpCompound.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset



class CompoundList(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompoundSerializer

    def get_queryset(self):
        queryset = Compound.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset

class Compoundn(GenericAPIView, CreateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompoundSerializer
    queryset = Compound.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class SimpleList(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = SimpleSerializer

    def get_queryset(self):
        queryset = Simple.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset

class getSimpleInt(GenericAPIView, CreateModelMixin):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = SimpleSerializer
    queryset = Simple.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class LoanList(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = LoanSerializer
    
    def get_queryset(self):
        queryset = Loan.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset

class getLoan(GenericAPIView, CreateModelMixin):
    
    permission_classes = (IsAuthenticated,)
    serializer_class = LoanSerializer
    queryset = Loan.objects.all()

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class WithdrawList(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = WithdrawSerializer

    def get_queryset(self):
        queryset = Withdraw.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset       

class PayoutList(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = PayOutSerializer

    def get_queryset(self):
        queryset = Payouts.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
        return queryset  

class Payout(GenericAPIView, CreateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = WithdrawSerializer
    queryset = Withdraw.objects.all()

    def post(self, request, *args, **kwargs):
        
        return self.create(request, *args, **kwargs)        


class PostOrder(GenericAPIView, CreateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = PostOrderSerializer
    queryset = Order.objects.all()

    def post(self, request, *args, **kwargs):
          
          return self.create(request, *args, **kwargs)    

class PostTopup(GenericAPIView, CreateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = TopUpSerializer
    queryset = []

    def post(self, request, *args, **kwargs):
          
          return self.create(request, *args, **kwargs)

class PostCTopup(GenericAPIView, CreateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = TopUpCSerializer
    queryset = []

    def post(self, request, *args, **kwargs):
          
          return self.create(request, *args, **kwargs)

class UpdateOrder(GenericAPIView, UpdateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = UpdateOrderSerializer
    queryset = Order.objects.all()
    def update(self, request, *args, **kwargs):
        txid = request.query_params.get('txid',None)
        partial = kwargs.pop('partial', False)
        instance = self.queryset.filter(txid=txid).last()
        serializer = self.get_serializer(instance,data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

class UpdateSimple(GenericAPIView, UpdateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = SimpleSerializer
    queryset = Simple.objects.all()
    def update(self, request, *args, **kwargs):
        pk = request.query_params.get('pk',None)
        partial = kwargs.pop('partial', False)
        instance = self.queryset.get(pk=pk)
        serializer = self.get_serializer(instance,data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
          
          return self.partial_update(request, *args, **kwargs) 

class UpdateCompound(GenericAPIView, UpdateModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = CompoundSerializer
    queryset = Compound.objects.all()
    def update(self, request, *args, **kwargs):
        pk = request.query_params.get('pk',None)
        partial = kwargs.pop('partial', False)
        instance = self.queryset.get(pk=pk)
        serializer = self.get_serializer(instance,data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        if instance:
            serializer = self.get_serializer(instance, data=request.data, partial=partial)
            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

        if getattr(instance, '_prefetched_objects_cache', None):
            # If 'prefetch_related' has been applied to a queryset, we need to
            # forcibly invalidate the prefetch cache on the instance.
            instance._prefetched_objects_cache = {}

        return Response(serializer.data)

    def put(self, request, *args, **kwargs):
          
          return self.partial_update(request, *args, **kwargs) 

class destroyOrder(GenericAPIView, DestroyModelMixin):
    permission_classes = (IsAuthenticated,)
    serializer_class = OrderSerializer
    queryset = Order.objects.all()

    def destroy(self, request, *args, **kwargs):
        txid = request.query_params.get('id')
        instance = self.queryset.filter(id=txid).first()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def post(self, request, *args,**kwargs):
        return self.destroy(request, *args, **kwargs)

        


class StatusListView(ListAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = StatusSerializer
    

    def get_queryset(self):
        username = self.request.query_params.get('username', None)

        queryset = Stat.objects.filter(user__username=username)
        return queryset          

    

class ChartView(ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    def get_queryset(self):
        queryset = User.objects.all()
        username = self.request.query_params.get('username', None)
        
        if username is not None:
            queryset = queryset.filter(username=username)
            user = User.objects.get(username=username) 
            date = user.orders.date.all()
            print(date)
            """
            now = datetime.datetime.now()
            result = [now.strftime("%B")]
            for _ in range(0, 6):
                now = now.replace(day=1) + relativedelta(months=1) #- datetime.timedelta(days=1)
                result.append(now.strftime("%B"))
            print(result)
            """
class UserHistory(ListAPIView):
    serializer_class =  HistorySerializer
    permission_classes = (IsAuthenticated,)
    
    def get_queryset(self):
        queryset = Stat.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)
            
            
        return queryset

class CompletedKit(ListAPIView):
    serializer_class = KitSerializer
    permission_classes = (IsAuthenticated,)
    

    def get_queryset(self):
        queryset = kitmodel.objects.all()
        username = self.request.query_params.get('username', None)
        if username is not None:
            queryset = queryset.filter(user__username=username)

        return queryset
