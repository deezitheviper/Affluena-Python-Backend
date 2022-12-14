from django.urls import path, re_path
from affluena.api.views import *

urlpatterns = [
    path('otp-request/', PhoneRequestDetail.as_view()),
    path('otp-verify/', PhoneVerifyDetail.as_view()),
    path('profile', ProfileView.as_view()),
    path('msg-view', MessageView.as_view()),
    path('withdraw-check', WithdrawCheck.as_view()),
    path('loan', LoanView.as_view()),
    path('orders', OrderListView.as_view()),
    path('refs',  RefView.as_view()),
    path('checkCart',  CheckCart.as_view()),
    path('txs', TxView.as_view()),
    path('payouts', PayoutList.as_view()),
    path('compound-id/', Compoundn.as_view()),
    path('withdrawals/', WithdrawList.as_view()),
    path('simpleInt/', SimpleList.as_view()),
    path('getSimpleInt', getSimpleInt.as_view()),
    path('topupList/', TopUpList.as_view()),
    path('ctopupList/', TopUpCList.as_view()),
    path('loanList', LoanList.as_view()),
    path('getLoan', getLoan.as_view()),
    path('payout-now/', Payout.as_view()),
    path('compounds/', CompoundList.as_view()),
    path('post-order/', PostOrder.as_view()),
    path('top-up/', PostTopup.as_view()),
    path('ctop-up/', PostCTopup.as_view()),
    path('update-simple/', UpdateSimple.as_view()),
    path('update-compound/', UpdateCompound.as_view()),
    path('update-order/', UpdateOrder.as_view()),
    path('destroy-idOrder/', destroyOrder.as_view()),
    path('status', StatusListView.as_view()),
    path('data', ChartView.as_view()),
    path('history', UserHistory.as_view()),
    path('completed-kits', CompletedKit.as_view()) 
]