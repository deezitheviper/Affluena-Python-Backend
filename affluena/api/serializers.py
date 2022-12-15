from rest_framework import serializers
from affluena.models import *
from datetime import datetime
from django.contrib.auth import get_user_model

UserModel = get_user_model()
dt = datetime.now()




class PhoneVerify(serializers.Serializer):
    phonecode = serializers.CharField()
    bin_key = serializers.CharField()

class Phone(serializers.Serializer):
    phone = serializers.CharField()


    
class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = ("account_balance","totalWithdrawn")




class OrderSerializer(serializers.ModelSerializer):
    customer = serializers.CharField(source='customer.username', read_only=True)
    date = serializers.DateTimeField(source='date_ordered', format="%Y-%m-%d", read_only=True)
    user_e = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ("__all__")

    def get_user_e(self, obj):
        serializer_data = UserSerializer(obj.customer).data
        usern =  serializer_data.get('username')
        user = User.objects.get(username=usern)
        UserE = user.account_balance
        
        try:
            userT = user.stats.allStorage
            userB = UserE + userT
        except AttributeError:
             userB = 0           
        return {
            "accountB":userB
        }    
class PostOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("customer","product","amount","status","txid","id","tx_ref","flw_ref","duration")        

class TopUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopUp
        fields = ("user","plan","amount","status","proof") 

class TopUpCSerializer(serializers.ModelSerializer):
    class Meta:
        model = TopUpCompound
        fields = ("user","plan","amount","status","proof") 

class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ("status",)        
                
class DestroyOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order                

class TopUpListS(serializers.ModelSerializer):
    class Meta:
        model = TopUp
        fields = ("__all__")

class TopUpCListS(serializers.ModelSerializer):
    class Meta:
        model = TopUpCompound
        fields = ("__all__")


class SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Simple
        fields = ("__all__")
        
class LoanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Loan
        fields = ("__all__")


class CompoundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compound
        fields = ("__all__")


class WithdrawSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source='date_ordered', format="%Y-%m-%d", read_only=True)
    date_approve = serializers.DateTimeField(source='date_approved', format="%Y-%m-%d", read_only=True)
    string_d = serializers.DateTimeField(source='date_ordered', format="%b %d ", read_only=True)
    string_d = serializers.DateTimeField(source='date_approved', format="%b %d ", read_only=True)
   
    class Meta:
        model = Withdraw
        fields = ("__all__")     

class PayOutSerializer(serializers.ModelSerializer):
    date = serializers.DateTimeField(source='date_requested', format="%Y-%m-%d", read_only=True)
    string_d = serializers.DateTimeField(source='date_requested', format="%b %d ", read_only=True)
    class Meta:
        model = Payout
        fields = ("user","amount","status","date_requested","string_d","date")                


class HistoricalRecordField(serializers.ListField):
     
    child = serializers.DictField()
     

    def to_representation(self, data):
        ret = super().to_representation(data.values())
        j = 0
        for i in ret:
            time = str(i['history_date'])
            date = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f%z').strftime('%B %d %Y')
            day = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f%z').strftime('%B %d')
            allstorage = i['totalEarning']
            storage = i['profit']
            ret[j]['history_date'] = date
            ret[j]["date_day"] = day
            j+=1
        
        return ret

class KitRecordField(serializers.ListField):
     
    child = serializers.DictField()
    

    def to_representation(self, data):
        ret = super().to_representation(data.values())[:6]
        ur = User.objects.all()
        pd = Product.objects.all()

        j = 0
        for i in ret:
            time = str(i['history_date'])
            date = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f%z').strftime('%B')
            day = datetime.strptime(time, '%Y-%m-%d %H:%M:%S.%f%z').strftime('%B %d')
            pduct = i["product_id"]
            pc = pd.filter(id=pduct)
            pn = pc[j].name
            ret[j]['product'] = pn
            user_id = i["user_id"]
            user = ur.filter(id=user_id)
            uc = user[j].completed_kits.count()
            ret[j]["number"] = uc
            ret[j]['history_date'] = date
            ret[j]["date_day"] = day
            j+=1
        
        return ret        

class StatusSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Stat
        exclude = ("newprofit","new_refEarning")

    

class sHistory(serializers.ModelSerializer):
    def __init__(self, model, *args, fields='__all__', **kwargs):
        self.Meta.model = model
        self.Meta.fields = fields
        super().__init__()

    class Meta:
        pass

class HistorySerializer(serializers.ModelSerializer):
    history = HistoricalRecordField()

    class Meta:
        model = Stat
        fields = ( 
                  'history',
                  )
    


class UserSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = User
        fields = '__all__'    

class CompSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CompletedPlan
        fields = '__all__'    

class KitSerializer(serializers.ModelSerializer):
    history = KitRecordField()

    class Meta:
        model = CompletedPlan
        fields = ( 
                  'history',
                  )
        
   

