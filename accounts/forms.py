from django.forms import ModelForm
from affluena.models import *
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django import forms




class RemarkForm(forms.Form):
   message = forms.CharField(label='Message',widget=forms.Textarea(attrs={"class":"form-control","id":"exampleFormControlTextarea1","rows":3}))
  



class CustomerForm(ModelForm):
    class Meta: 
        model = User
        fields = '__all__'  
        exclude = ['user','slug']

class MessageCustomer(ModelForm):
    class Meta:
        model = Message
        fields = ('text',)
        widgets={
            'text':forms.Textarea(attrs={'class':'form-control'}),
             }
        labels = {
            "text": _("Message"),
        }

class StaffForm(ModelForm):
    class Meta:
        model = User
        fields = ('first_name','last_name','address','phone','city','state','country','bank_name','account_no','account_name','contribution_type')


class OrderForm(ModelForm):
    class Meta: 
        model = Order
        fields = ('status',)  

class SimpleTopUpForm(ModelForm):
    class Meta:
        model = TopUp
        fields = ('status',) 

class CompoundTopUpForm(ModelForm):
    class Meta:
        model = TopUpCompound
        fields = ('status',)

    
class SForm(ModelForm):
    class Meta:
        model = Simple
        fields = ('status',)  
 

class CForm(ModelForm):
    class Meta:
        model = Compound
        fields = ('status',)  

class PayoutForm(ModelForm):
    class Meta:
        model = Payout
        fields = ('status',)
        

class RefPayoutForm(ModelForm):
    class Meta:
        model = ReferralPayout
        fields = ('status',)  

class LoanForm(ModelForm):
    class Meta:
        model = Loan
        fields = ('status',)  

class UserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','password1','password2']  
        widgets={
            'username':forms.TextInput(attrs={'class':'form__input','placeholder':'Username'}),
            'email':forms.EmailInput(attrs={'class':'form__input','placeholder':'Email','id':'email'}),
             }



      