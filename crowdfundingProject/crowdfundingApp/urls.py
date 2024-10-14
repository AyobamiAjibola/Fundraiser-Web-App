from django.urls import path
from . import views
from .views import RegisterView, CampaignList, CampaignListTable

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('login/', views.login_view, name='login'),
    # path('register/', views.register_view, name='register'),
    path('register/', RegisterView.as_view(), name='register'),
    # path('login/', LoginView.as_view(), name='login'),
    path('campaigns/', views.campaigns_view, name='campaigns'),
    path('check_email/', views.check_email, name='check_email'),
    path('check_email_update/', views.check_email_update, name='check_email_update'),
    path('check_confirm_password/', views.check_confirm_password, name='check_confirm_password'),
    path('api/paystack-proxy/', views.paystack_proxy, name='paystack_proxy'),
    path('api/validate-account', views.validate_account, name='validate_account'),
    path('campaign-list/', CampaignList.as_view(), name='campaign-list'),
    # path('paystack/webhook/', views.paystack_webhook, name='paystack_webhook'),
    path('api/donate', views.donate, name='donate'),
    path('api/verify-payment', views.verify_payment, name='verify-payment'),
    path('api/like-campaign', views.like_campaign, name='like-campaign'),
    path('api/update-status', views.toggleStatus, name='update-status'),
]

protected_urlpatterns = [
    # path('dashboard/profile/', views.ProtectedView.as_view(), name='profile'),
    path('dashboard/profile/', views.update_form, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('logout_confirmation/', views.logout_confirmation, name='logout_confirmation'),
    path('create-campaign/', views.create_campaign_view, name='create-campaign'),
    path('campaign-list-table/', CampaignListTable.as_view(), name='campaign-list-table'),
    path('campaign/<int:pk>/', views.campaign_view, name='campaign'),
]

htmx_urlpatterns = [
    path('check_username/', views.check_username, name='check_username'),
    path('check_email/', views.check_email, name='check_email'),
    path('check_confirm_password/', views.check_confirm_password, name='check_confirm_password'),
    path('check_password/', views.check_password, name='check_password'),
    path('delete_campaign/<int:pk>/', views.delete_campaign, name='delete_campaign'),
    path('campaign/update/<int:pk>/', views.update_campaign_view, name='update_campaign')
]

urlpatterns += protected_urlpatterns + htmx_urlpatterns