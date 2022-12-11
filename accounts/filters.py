import django_filters 
from django_filters import DateFilter
from affluena.models import *

class OrderFilter(django_filters.FilterSet):
    customer__full_name = django_filters.CharFilter(lookup_expr='icontains')
    
    class Meta:
        model = Order
        fields = ('customer__full_name','status')



class SimpleFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Simple
        fields = ('user__full_name','status')


class SimpleTopFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = TopUp
        fields = ('user__full_name','status')
        
class CompoundTopFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = TopUpCompound 
        fields = ('user__full_name','status')
        
class CompoundFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Compound
        fields = ('user__full_name','status')

class PayoutFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Payout
        fields = ('user__full_name','status')
     

class RefPayoutFilter(django_filters.FilterSet):
    class Meta:
        model = ReferralPayout
        fields = ('user__full_name','status')
        
class LoanFilter(django_filters.FilterSet):
    user__full_name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = Loan
        fields = ('user__full_name','status')

class CustomerFilter(django_filters.FilterSet):
    full_name = django_filters.CharFilter(lookup_expr='icontains')
    class Meta:
        model = User
        fields = ('full_name',)