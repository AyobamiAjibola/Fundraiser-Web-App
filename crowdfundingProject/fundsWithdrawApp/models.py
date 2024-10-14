from django.db import models
from django.contrib.auth.models import User

class PaymentRequest(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='payment_request', null=True, blank=True)
    status = models.TextField(max_length=255, null=False, blank=False, default='pending')
