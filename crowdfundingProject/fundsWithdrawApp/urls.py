from django.urls import path
from . import views

urlpatterns = [
    path('funds-withdraw/', views.fundWithdraw, name='withdraw-funds'),
    path('api/withdraw-fund', views.withdrawFund, name='withdraw-fund'),
]
