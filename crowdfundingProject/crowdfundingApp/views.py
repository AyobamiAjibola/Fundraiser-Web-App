import json
from django.shortcuts import render, redirect
from .forms import RegisterForm, UpdateUserForm, FundraiserForm, AccountForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.views import View
from django.contrib import messages
from django.http import HttpResponse
import re
from .models import Crowdfunding, Profile, Donation, Transaction
from django.views.generic.edit import FormView
from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decouple import config
from django.views.generic import ListView
from utils.generic import format_amount, calc_progress, character_breaker, cal_total_amt, currency_display_donation
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST
from fundsWithdrawApp.models import PaymentRequest

from django.http import JsonResponse
from django.conf import settings


def get_user_profile_data(user):
    profile = Profile.objects.get(user=user)
    
    initial = ""
    if profile.user.first_name and profile.user.last_name:
        initial = f"{profile.user.first_name[0].upper()}{profile.user.last_name[0].upper()}"
    else:
        initial = f"{profile.user.username[0].upper()}{profile.user.username[1].upper()}"
        
    return {
        'first_name': profile.user.first_name or profile.user.username,
        'image': profile.image,
        'initials': initial
    }

def home(request):
    user = request.user
    if user.is_authenticated:
        data = get_user_profile_data(user)
    else:
        data = {}
        
    return render(request, 'home/index.html', {
        'profile': data
    })

@csrf_exempt
def paystack_proxy(request):
    if request.method == 'GET':
        headers = {
            'Authorization': config('PAYSTACK_SK'),
        }
        response = requests.get(config('BASE_URL'), headers=headers)
        return JsonResponse(response.json())
    
def modified_campaigns(campaigns):
    mod_campaigns = [
        {
            'pk': campaign.pk,
            'title': campaign.title,
            'status': campaign.status,
            'image': campaign.image,
            'location': f"{campaign.lga}, {campaign.state} State", 
            'beneficiary': f"{campaign.firstName.capitalize()} {campaign.lastName.capitalize()}",
            'description': f"{character_breaker(campaign.description, 100)}..." if len(campaign.description) > 100 else campaign.description,
            'amountRaised': format_amount(campaign.amountRaised),
            'amountNeeded': format_amount(campaign.amountNeeded),
            'progressValue': calc_progress(campaign.amountRaised, campaign.amountNeeded),
            'likes': 0 if campaign.likes == '' else len(campaign.likes.split(','))
        }
        for campaign in campaigns
    ]
    
    return mod_campaigns

def modified_payments(payments):
    mod_payments = [
        {
            'firstName': f"{payment.user.first_name.capitalize()}",
            'lastName': f"{payment.user.last_name.capitalize()}",
            'amount': format_amount(payment.amount),
            'status': payment.status,
            'pk': payment.pk
        }
        for payment in payments
    ]
    
    return mod_payments

def modified_donations(donations):
    mod_donations = [
        {
            'name': 'Anonymous' if not donation.user 
                                else f"{character_breaker(donation.user.first_name.capitalize(), 9)}..." 
                                    if len(donation.user.first_name.capitalize()) > 9 
                                    else donation.user.first_name.capitalize(),
            'amount': currency_display_donation(donation.amount)
        }
        for donation in donations
    ]
    
    return mod_donations

def dash_modified_campaigns(campaigns):
    mod_campaigns = [
        {
            'pk': campaign.pk,
            'title': campaign.title,
            'status': campaign.status,
            'location': f"{campaign.lga}, {campaign.state} State", 
            'beneficiary': f"{campaign.firstName.capitalize()} {campaign.lastName.capitalize()}",
            'amountRaised': format_amount(campaign.amountRaised),
            'amountNeeded': format_amount(campaign.amountNeeded),
        }
        for campaign in campaigns
    ]
    
    return mod_campaigns
    
@csrf_exempt
def validate_account(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        bank_code = data.get("bankCode")
        account_num = data.get("accountNumber")
        
        if not bank_code or not account_num:
            return JsonResponse({'error': 'Invalid input'}, status=400)
        
        bvn_verify_url = f"https://api.paystack.co/bank/resolve?account_number={account_num}&bank_code={bank_code}"
        
        paystack_config = {
            'headers': {
                'Authorization': config('PAYSTACK_SK'),
                'Content-Type': 'application/json',
            }
        }
        
        try:
            response = requests.get(bvn_verify_url, headers=paystack_config['headers'])
            response.raise_for_status()
            response_data = response.json()
            return JsonResponse(response_data)
        except requests.exceptions.RequestException as e:
            print(f"Error during request: {e}")
            return JsonResponse({'error': 'Failed to verify account'}, status=500)
    
def campaigns_view(request):
    user = request.user
    if user.is_authenticated:
        data = get_user_profile_data(user)
    else:
        data = {}
    
    return render(request, 'fundraiser/campaigns.html', {
        'profile': data
    })

# USING FORMVIEW DJANGO
class RegisterView(FormView):
    template_name = 'accounts/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('dashboard')
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect(self.success_url)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        last_name = form.cleaned_data.get("last_name")
        first_name = form.cleaned_data.get("first_name")
        email = form.cleaned_data.get("email")
        password = form.cleaned_data.get("password")

        # Create user
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            username=email  # Use email as username
        )
        
        if user:
            login(self.request, user, backend='crowdfundingApp.backend.EmailBackend')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Internal server error.')
            return self.form_invalid(form)

# REGISTER VIEW MANUAL 
# def register_view(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')

#     if request.method == "POST":
#         form = RegisterForm(request.POST)

#         if form.is_valid():
#             username = form.cleaned_data.get("username")
#             last_name = form.cleaned_data.get("last_name")
#             first_name = form.cleaned_data.get("first_name")
#             email = form.cleaned_data.get("email")
#             password = form.cleaned_data.get("password")

#             user = User.objects.create_user(
#                 first_name=first_name,
#                 last_name=last_name,
#                 email=email,
#                 password=password,
#                 username=username
#             )

#             login(request, user)
#             return redirect('dashboard')
#     else:
#         form = RegisterForm()
#     return render(request, 'accounts/register.html', {'form':form})

def check_password(request):
    password = request.POST.get('password', None)

    # Define the regex pattern for password validation
    pattern = re.compile(
        r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=]).{8,}$'
    )
    
    if password:
        if pattern.match(password):
            return HttpResponse('<div style="color: green;">Password is valid.</div>')
        else:
            return HttpResponse('<div style="color: red;">Password does not meet requirement.</div>')
    else:
        return HttpResponse('<div style="color: red;">Please provide a password.</div>')

def check_confirm_password(request):
    password_confirm = request.POST.get('password_confirm', None)
    password = request.POST.get('password', None)
    
    if password and password_confirm and password != password_confirm:
        return HttpResponse('<div style="color: red;">Passwords do not match!</div>')
    else:
        return HttpResponse('')

def check_email(request):
    email = request.POST.get('email', None)
    
    # Check if the email is provided
    if email:
        try:
            # Validate the email format
            validate_email(email)
        except ValidationError:
            return HttpResponse('<div style="color: red;">Invalid email format</div>')

        # Check if the email is already in use by another user
        if User.objects.filter(email=email).exists():
            return HttpResponse('<div style="color: red;">Email is already in use</div>')
        else:
            return HttpResponse('<div style="color: green;">Email is available</div>')
    else:
        return HttpResponse('<div style="color: red;">Please provide an email address.</div>')
    
def check_email_update(request):
    email = request.POST.get('email', None)
    current_user = request.user
    
    if email:
        try:
            # Validate the email format
            validate_email(email)
        except ValidationError:
            return HttpResponse('<div style="color: red;">Invalid email format</div>')
        
        if User.objects.filter(email=email).exclude(pk=current_user.pk).exists():
            return HttpResponse('<div style="color: red;">Email is already in use</div>')
        else:
            return HttpResponse('<div style="color: green;">Email is available</div>')
    else:
        return HttpResponse('<div style="color: red;">Please provide an email address.</div>')

def check_username(request):
    username = request.POST.get('username', None)
    if username:
        if User.objects.filter(username=username.strip()).exists():
            return HttpResponse('<div id="username-error" class="err">username is already taken</div>')
        else:
            return HttpResponse('<div id="username-error" class="success">username is not taken</div>')
    else:
        return HttpResponse('<div id="username-error" class="err">Please provide a username.</div>')
    
# def login_view(request):
#     if request.user.is_authenticated:
#         return redirect('dashboard')
    
#     error_message = None
#     if request.method == "POST":
#         email = request.POST.get("email")
#         password = request.POST.get("password")

#         try:
#             user = User.objects.get(email=email)
#             user = authenticate(request, username=user.username, password=password)
#         except User.DoesNotExist:
#             user = None

#         if user is not None:
#             login(request, user)
#             next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
#             return redirect(next_url)
#         else:
#             # messages.add_message(request, messages.ERROR, 'Invalid Credentials!', extra_tags='danger')
#             messages.error(request, 'Invalid Credentials!')
#             # error_message = "Invalid Credentials!"
#     return render(request, 'accounts/login.html', {'error':error_message})

# MANUAL LOGING ----- I CHANGED THE BACKEND TO HANDLE EMAIL REGISTRATION.
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        # Authenticate using the custom EmailBackend
        user = authenticate(request, username=email, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next') or 'dashboard'
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email or password')
    
    return render(request, 'accounts/login.html')  # Render your login template

#USING LOGIN VIEW
# class LoginView(DjangoLoginView):
#     template_name = 'accounts/login.html'
#     success_url = reverse_lazy('dashboard')

#     def dispatch(self, request, *args, **kwargs):
#         if request.user.is_authenticated:
#             return redirect(self.success_url)
#         return super().dispatch(request, *args, **kwargs)

#     def form_valid(self, form):
#         email = self.request.POST.get('email')
#         password = self.request.POST.get('password')
        
#         # Authenticate using the custom EmailBackend
#         user = authenticate(self.request, username=email, password=password)
        
#         if user is not None:
#             login(self.request, user)
#             next_url = self.request.POST.get('next') or self.request.GET.get('next') or self.success_url
#             return redirect(next_url)
#         else:
#             messages.error(self.request, 'Invalid email or password')
#             return self.form_invalid(form)

#     def form_invalid(self, form):
#         print("Form errors:", form.errors)
#         messages.error(self.request, 'Invalid email or password')
#         return super().form_invalid(form)
    
@login_required
def dashboard_view(request):
    user = request.user
    if user.is_authenticated:
        data = get_user_profile_data(user)
        # campaigns = user.crowdfundings.all()
        dashData = {
            # "active_campaign": True if len([campaign for campaign in campaigns if campaign.status == 'active']) > 0 else False,
            "isSuperUser": True if request.user.is_superuser else False
        }
    else:
        data = {}
    
    form = FundraiserForm()
    account_form = AccountForm()
    
    return render(request, 'dashboard/index.html', {
        'form': form,
        'account_form': account_form,
        'profile': data,
        'dashboard': dashData
    })

@login_required
def logout_confirmation(request):
    return render(request, 'accounts/logout.html')

@login_required
def logout_view(request):
    
    if request.method == "POST":
        logout(request)
        return redirect('login')
    else:
        return redirect('dashboard')
    
@login_required
def update_form(request):
    user = request.user
    profile = Profile.objects.get(user=user)
    
    form = UpdateUserForm(instance=user)
    if request.method == "POST":
        form = UpdateUserForm(request.POST, request.FILES, instance=user)
        
        if form.is_valid():
            form.save()  # Save User data
            # Update Profile data
            profile.user.email = form.cleaned_data.get('email')
            profile.address = form.cleaned_data.get('address')
            profile.image = form.cleaned_data.get('image')
            profile.state = form.cleaned_data.get('state')
            profile.lga = form.cleaned_data.get('lga')
            profile.save()
            return redirect('dashboard')

    profile_data = {
        'email': profile.user.email,
        'first_name': profile.user.first_name or '',
        'last_name': profile.user.last_name or '',
        'address': profile.address or '',
        'state': profile.state or '',
        'lga': profile.lga or '',
        'image': profile.image
    }

    return render(request, 'dashboard/profile.html', {'form': form, 'profile': profile_data})

class CampaignList(ListView):
    template_name = 'partials/campaign-list.html'
    model = Crowdfunding
    context_object_name = 'campaigns'

    def get_queryset(self):
        campaigns = Crowdfunding.objects.filter(status='active')
        
        return modified_campaigns(campaigns)

class CampaignListTable(ListView):
    template_name = 'partials/campaign-list-table.html'
    model = Crowdfunding
    context_object_name = 'campaigns'

    def get_queryset(self):
        user = self.request.user
        campaigns = Crowdfunding.objects.all() if self.request.user.is_superuser else user.crowdfundings.all()
        return dash_modified_campaigns(campaigns)

    def get_context_data(self, **kwargs):
        # Get the default context data from ListView
        context = super().get_context_data(**kwargs)

        # Calculate dash_data
        user = self.request.user
        campaigns = Crowdfunding.objects.all() if self.request.user.is_superuser else user.crowdfundings.all()
        dash_data = {
            'campaigns': len(campaigns),
            'totalAmount': cal_total_amt(campaigns),
            'rejected': len([campaign for campaign in campaigns if campaign.status == 'rejected']),
            'isSuperUser': True if self.request.user.is_superuser else False
        }
        
        payments = PaymentRequest.objects.all()
        mod_payment_request = modified_payments(payments)

        context['dash_data'] = dash_data
        context['payment_data'] = mod_payment_request
        
        return context

def delete_campaign(request, pk):
    campaign = get_object_or_404(Crowdfunding, pk=pk)
    
    if campaign.status == 'active':
        messages.error(request, 'You cannot delete an active campaign.')
    else:
        #request.user.crowdfundings.remove(campaign) 
        campaign.delete()
    
    campaigns = request.user.crowdfundings.all()
    
    dash_data = {
        'campaigns': len(campaigns),
        'totalAmount': cal_total_amt(campaigns),
        'rejected': len([campaign for campaign in campaigns if campaign.status == 'rejected'])
    }

    return render(request, 'partials/campaign-list-table.html', { 'campaigns': dash_modified_campaigns(campaigns), 'dash_data': dash_data })

@login_required
def create_campaign_view(request):
    user = request.user
    if user.is_authenticated:
        data = get_user_profile_data(user)
    else:
        data = {}
        
    existingCampaigns = user.crowdfundings.all()
    if len(existingCampaigns) > 0 and [campaign for campaign in existingCampaigns if campaign.status == 'active']:
        #messages.error(request, 'You already have an active campaign.')
        return HttpResponse('<div style="color: red;">You already have an active campaign.</div>')

    if request.method == 'POST':
        form = FundraiserForm(request.POST, request.FILES)
        account_form = AccountForm(request.POST)
     
        if form.is_valid() and account_form.is_valid():
            account = account_form.save(commit=False)
            account.save()

            # Create and save the Crowdfunding instance
            crowdfunding = form.save(commit=False)
            crowdfunding.user = user
            crowdfunding.account = account
            crowdfunding.save()

            # If HTMX request, return updated campaign list and form
            if request.headers.get('HX-Request'):
                campaigns = user.crowdfundings.all()
                
                form = FundraiserForm()
                account_form = AccountForm()
                
                dash_data = {
                    'campaigns': len(campaigns),
                    'totalAmount': cal_total_amt(campaigns),
                    'rejected': len([campaign for campaign in campaigns if campaign.status == 'rejected'])
                }
                
                return render(request, 'partials/campaign-list-table.html', { 'campaigns': dash_modified_campaigns(campaigns), 'dash_data': dash_data })

            return redirect('dashboard')
        else:
            print("Form Errors:", form.errors)
            print("Account Form Errors:", account_form.errors)

            return render(request, 'dashboard/index.html', { 'form': form, 'account_form': account_form, 'profile': data })
    else:
        form = FundraiserForm()
        account_form = AccountForm()

    return render(request, 'dashboard/index.html', { 'form': form, 'account_form': account_form, 'profile': data })

@login_required
def update_campaign_view(request, pk):
    user = request.user
    campaign = get_object_or_404(Crowdfunding, pk=pk, user=user)
    
    if user.is_authenticated:
        data = get_user_profile_data(user)
    else:
        data = {}
    
    if request.method == 'POST':
        form = FundraiserForm(request.POST, request.FILES, instance=campaign)
        account_form = AccountForm(request.POST, instance=campaign.account)

        if form.is_valid() and account_form.is_valid():
            # Update account information
            account = account_form.save(commit=False)
            account.save()

            # Update the Crowdfunding instance
            crowdfunding = form.save(commit=False)
            crowdfunding.user = user
            crowdfunding.account = account
            crowdfunding.save()

            # Check if the request is an HTMX request
            if request.headers.get('HX-Request'):
                return render(request, 'dashboard/campaign.html')

        else:
            # Print form errors for debugging
            print("Form Errors:", form.errors)
            print("Account Form Errors:", account_form.errors)

    else:
        form = FundraiserForm(instance=campaign)
        account_form = AccountForm(instance=campaign.account)

    return render(request, 'dashboard/campaign.html', { 
        'form': form, 
        'account_form': account_form, 
        'profile': data, 
        'campaign': campaign 
    })

def campaign_view(request, pk):
    campaign = get_object_or_404(Crowdfunding, pk=pk)
    campaignArr = campaign.likes.split(',')
    
    donations = Donation.objects.filter(crowdfunding=campaign)
    
    mod_donations = modified_donations(donations)

    payload = {
        'pk': campaign.pk,
        'title': campaign.title,
        'status': campaign.status,
        'image': campaign.image,
        'location': f"{campaign.lga}, {campaign.state} State", 
        'beneficiary': f"{campaign.firstName.capitalize()} {campaign.lastName.capitalize()}",
        'description': campaign.description,
        'amountRaised': format_amount(campaign.amountRaised),
        'amountNeeded': format_amount(campaign.amountNeeded),
        'progressValue': calc_progress(campaign.amountRaised, campaign.amountNeeded),
        'liked': str(request.user.pk) in campaignArr,
        'likes': len(campaignArr),
        'donations': mod_donations
    }
        
    return render(request, 'fundraiser/campaign.html', { 'campaign': payload })

@csrf_exempt
def donate(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            campaignId = data.get("campaignId")
            amount = int(data.get('amount')) 
            user = request.user

            # Ensure campaign exists
            try:
                campaign = Crowdfunding.objects.get(pk=campaignId)
            except Crowdfunding.DoesNotExist:
                return JsonResponse({'error': 'Campaign not found'}, status=404)

            # Check if the campaign is still active
            if campaign.status == "done":
                return JsonResponse({'message': "You can no longer donate, the campaign is completed."}, status=403)

            # Check if amount is valid
            if amount < 500:
                return JsonResponse({'error': 'Amount must be greater than 500'}, status=400)

            # Prepare Paystack headers and data
            headers = {
                "Authorization": f"{config('PAYSTACK_SK')}",
                "Content-Type": "application/json",
            }
            
            metadata = {
                "cancel_action": f"{config('PAYSTACK_CB_URL')}transactions?status=cancelled"
            }
            
            email = 'anonymous@gmail.com' if not user.is_authenticated else user.email
            data = {
                "email": email,
                "amount": amount * 100,
                "callback_url": f"{config('PAYSTACK_CB_URL')}",
                "metadata": metadata
            }

            # Make request to Paystack to initialize transaction
            response = requests.post('https://api.paystack.co/transaction/initialize', json=data, headers=headers)

            # Handle Paystack response
            if response.status_code != 200:
                return JsonResponse({'error': 'Payment initialization failed'}, status=500)

            res_data = response.json()

            if res_data.get('status') and res_data.get('data') and 'reference' in res_data['data']:
                authorization_url = res_data['data']['authorization_url']
                
                transaction = Transaction(
                    user = None if not user.is_authenticated else user,#None if user == "AnonymousUser" else user.pk,
                    amount=amount,
                    reference=res_data['data']['reference'],
                    campaign=campaign,
                    type="PAYMENT",
                    authorizationUrl=authorization_url
                )
                
                transaction.save()

                return JsonResponse({'data': {'authorizationUrl': authorization_url}}, status=200)

            # If there's an issue with Paystack response
            return JsonResponse({'error': res_data.get('message', 'An error occurred')}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

        except Exception as e:
            return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

    # If request method is not POST
    return JsonResponse({'error': 'Invalid request method'}, status=405)

@csrf_exempt
def verify_payment(request):
    ref = request.GET.get('reference')
    user = request.user
    
    if not ref:
        return JsonResponse({'error': 'Payment reference is required'}, status=400)

    try:
        transaction = Transaction.objects.get(reference=ref)
    except Transaction.DoesNotExist:
        return JsonResponse({'error': 'Transaction not found'}, status=404)
    
    campaign = Crowdfunding.objects.get(pk=transaction.campaign.pk)
    
    headers = {
        "Authorization": f"{config('PAYSTACK_SK')}",
    }

    # timeout = httpx.Timeout(connect=10.0, read=20.0)
    # async with httpx.AsyncClient(timeout=timeout) as client:
    #     response = await client.get(f'https://api.paystack.co/transaction/verify/{ref}', headers=headers)
    # res_data = response.json()
    
    response = requests.get(f'https://api.paystack.co/transaction/verify/{ref}', headers=headers)
    res_data = response.json()

    response_data = res_data['data']

    if res_data['status']:
        
        donation = Donation(
            user= None if not user.is_authenticated else user,
            crowdfunding = campaign,
            date=response_data['paid_at'],
            amount=transaction.amount
        )
        amount_raised = 0 if campaign.amountRaised is None else campaign.amountRaised

        campaignPayload = {
            "amountRaised": amount_raised  + transaction.amount
        }

        payload = {
            "status": response_data['status'],
            "channel": response_data['authorization']['channel'],
            "cardType": response_data['authorization']['card_type'],
            "bank": response_data['authorization']['bank'],
            "last4": response_data['authorization']['last4'],
            "expMonth": response_data['authorization']['exp_month'],
            "expYear": response_data['authorization']['exp_year'],
            "countryCode": response_data['authorization']['country_code'],
            "brand": response_data['authorization']['brand'],
            "currency": response_data['currency'],
            "paidAt": response_data['paid_at'],
            "type": transaction.type
        }
        
        for key, value in payload.items():
            setattr(transaction, key, value)
            
        for key, value in campaignPayload.items():
            setattr(campaign, key, value)

        transaction.save()
        donation.save()
        campaign.save()
        
        return JsonResponse({'message': 'Payment successful', 'data': res_data['data']}, status=200)
    else:
        # Payment failed
        return JsonResponse({'error': res_data['message']}, status=400)

@csrf_exempt
@require_POST
def like_campaign(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'You are not authenticated.'}, status=401)

    try:
        data = json.loads(request.body)
        campaign_id = data.get("campaignId")

        try:
            campaign = Crowdfunding.objects.get(pk=campaign_id)
        except Crowdfunding.DoesNotExist:
            return JsonResponse({'error': 'Campaign not found'}, status=404)

        campaignArr = campaign.likes.split(",") if campaign.likes else []
        if str(request.user.pk) not in campaignArr:
            campaignArr.append(str(request.user.pk))
        else:
            return JsonResponse({'message': 'You already liked this campaign.'}, status=200)

        # Update the likes field
        campaign.likes = ",".join(campaignArr)
        campaign.save()

        return JsonResponse({'message': 'Successfully liked campaign.'}, status=200)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
    
@csrf_exempt
@require_POST
def toggleStatus(request):
    if not request.user.is_superuser:
        return JsonResponse({'error': 'You are not authorized.'}, status=401)
    
    try:
        data = json.loads(request.body)
        status = data.get("status")
        campaignId = int(data.get("campaignId"))

        try:
            campaign = Crowdfunding.objects.get(pk=campaignId)
        except Crowdfunding.DoesNotExist:
            return JsonResponse({'error': 'Campaign not found'}, status=404)
        
        campaignPayload = {
            "status": status
        }
        
        for key, value in campaignPayload.items():
            setattr(campaign, key, value)
            
        campaign.save()
        
        return JsonResponse({'message': 'Successfully updated status.'}, status=200)
        
    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)
        

# @csrf_exempt
# def paystack_webhook(request):
#     if request.method == 'POST':
#         try:
#             # Verify the Paystack signature
#             paystack_signature = request.headers.get('x-paystack-signature')
#             secret_key = config('PAYSTACK_SECRET_KEY'),

#             # The raw POST data
#             payload = request.body

#             # Generate an HMAC signature using the secret key and compare with Paystack's signature
#             computed_signature = hmac.new(
#                 key=bytes(secret_key, 'utf-8'),
#                 msg=payload,
#                 digestmod=hashlib.sha512
#             ).hexdigest()

#             if computed_signature != paystack_signature:
#                 return JsonResponse({'status': 'error', 'message': 'Invalid signature'}, status=400)

#             # Parse the payload
#             event = json.loads(payload)

#             # Process the event (e.g., payment verification)
#             event_type = event.get('event')
#             data = event.get('data')

#             if event_type == 'charge.success':
#                 # Handle successful payment here (e.g., update order/payment status)
#                 print(f"Payment was successful: {data}")
#                 # You could verify the transaction again via Paystack's API if needed

#             elif event_type == 'charge.failed':
#                 # Handle failed payment
#                 print(f"Payment failed: {data}")

#             return JsonResponse({'status': 'success'}, status=200)
        
#         except Exception as e:
#             print(f"Error processing webhook: {str(e)}")
#             return JsonResponse({'status': 'error', 'message': 'Internal error'}, status=500)
#     return JsonResponse({'status': 'error', 'message': 'Invalid request'}, status=400)

#Protected View
class ProtectedView(LoginRequiredMixin, View):
    login_url = '/login/'
    # 'next' - to redirect URL
    redirect_field_name = 'redirect_to'
    
    # def post(self, request):
        
    #     if request.method == "GET":
    #         form = RegisterForm()
            
    #     return render(request, 'accounts/profile.html', {'form':form})
        

        # return render(request, 'dashboard/profile.html')

