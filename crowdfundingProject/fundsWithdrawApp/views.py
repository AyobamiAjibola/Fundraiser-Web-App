from django.shortcuts import render
from crowdfundingApp.views import get_user_profile_data
from django.contrib.auth.decorators import login_required
from utils.generic import format_amount
import json
from crowdfundingApp.models import Crowdfunding
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from .models import PaymentRequest

@login_required
def fundWithdraw(request):
    user = request.user
    campaign_data = {}

    if user.is_authenticated:
        data = get_user_profile_data(user)

        campaign = user.crowdfundings.filter(status='active').first()
        if campaign:
            campaign_data = {
                "pk": campaign.pk,
                "amountRaised": format_amount(campaign.amountRaised),
                "amountNeeded": format_amount(campaign.amountNeeded),
                "amountWithdrawn": format_amount(campaign.amountWithdrawn or 0)
            }
    else:
        data = {}

    return render(request, 'withdraw/index.html', {
        'profile': data,
        "campaign": campaign_data
    })
    
@csrf_exempt
@require_POST
def withdrawFund(request):
    try:
        data = json.loads(request.body)
        campaignId = int(data.get("campaignId"))
        amount = int(data.get('amount')) 
        user = request.user
        
        userPaymentRequest = PaymentRequest.objects.filter(status='pending').first()
        if userPaymentRequest:
            return JsonResponse({'error': 'You currently have a pending payment request.'}, status=403)
        
        try:
            campaign = Crowdfunding.objects.get(pk=campaignId)
        except Crowdfunding.DoesNotExist:
            return JsonResponse({'error': 'Campaign not found'}, status=404)
        
        if campaign.amountRaised < amount:
            return JsonResponse({'error': "Amount available is less than amount you want to withdraw."}, status=403)

        # Check if amount is valid
        if amount < 500:
            return JsonResponse({'error': 'Amount must be greater than 500'}, status=400)
        
        amount_withdrawn = 0 if campaign.amountWithdrawn is None else campaign.amountWithdrawn
        campaignPayload = {
            # "amountRaised": campaign.amountRaised  - amount,
            "amountWithdrawn": amount_withdrawn + amount
        }
        
        paymentRequest = PaymentRequest(
            amount= amount,
            user= user
        )
        
        for key, value in campaignPayload.items():
            setattr(campaign, key, value)
            
        campaign.save()
        paymentRequest.save()
        
        return JsonResponse({'message': 'Successful! Your account will be credited within 24hrs.'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    except Exception as e:
        return JsonResponse({'error': f'An error occurred: {str(e)}'}, status=500)

