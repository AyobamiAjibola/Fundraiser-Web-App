from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    address = models.CharField(max_length=255, blank=True, null=True)
    is_admin = models.BooleanField(default=False)
    image = models.ImageField(upload_to='images/profile_images/', blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    lga = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username
    
@receiver(post_save, sender=User)
def user_post_save_receiver_create_user(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def user_post_save_receiver_update_user(sender, instance, **kwargs):
    instance.profile.save()

    def __str__(self):
        return f'{self.user} donated {self.amount} on {self.date}'  
    
class Account(models.Model):
    accountName = models.TextField(max_length=255, null=True, blank=True)
    bank = models.TextField(max_length=255, null=True, blank=True)
    accountNumber = models.TextField(max_length=255, null=True, blank=True)
    bankCode = models.TextField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f'{self.accountName} {self.bank} {self.accountNumber} {self.bankCode}'    

class Crowdfunding(models.Model):
    # user = models.ManyToManyField(User, related_name='crowdfundings') THIS ALLOWS MANY USERS TO BE ASSOCIATED TO MANY CROWEDFUND AND VIS A VIS
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='crowdfundings', null=True, blank=True) # with this one user can be associated with many crowedfund but on one crowdfund will associated to one user
    title = models.TextField(max_length=255, null=False)
    description = models.TextField(max_length=1000, null=True, blank=True)
    status = models.TextField(max_length=255, null=False, blank=False, default='inactive')
    address = models.TextField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to='images/fundraiser/', blank=True, null=True)
    likes = models.TextField(blank=True, default="")
    amountNeeded = models.DecimalField(max_digits=10, decimal_places=2)
    amountWithdrawn = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    amountRaised = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, default=0)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account = models.OneToOneField(Account, on_delete=models.DO_NOTHING, related_name='account', null=True)
    state = models.TextField(null=True, blank=True)
    lga = models.TextField(null=True, blank=True)
    firstName = models.TextField(max_length=255, null=False, default='')
    lastName = models.TextField(max_length=255, null=False, default='')
    
class Donation(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='donations', null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    crowdfunding = models.ForeignKey(Crowdfunding, related_name='donations', on_delete=models.DO_NOTHING, null=True) 
    
class Transaction(models.Model):
    reference = models.TextField(max_length=255, null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.TextField(max_length=255, null=False)
    type = models.TextField(max_length=255, null=False)
    authorizationUrl = models.TextField(max_length=255, null=False)
    last4 = models.TextField(max_length=255, null=True)
    expMonth = models.TextField(max_length=255, null=True)
    expYear = models.TextField(max_length=255, null=True)
    channel = models.TextField(max_length=255, null=True)
    cardType = models.TextField(max_length=255, null=True)
    bank = models.TextField(max_length=255, null=True)
    countryCode = models.TextField(max_length=255, null=True)
    brand = models.TextField(max_length=255, null=True)
    currency = models.TextField(max_length=255, null=True)
    paidAt = models.TextField(max_length=255, null=True)
    # user = models.TextField(max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='transactions', null=True, blank=True)
    campaign = models.ForeignKey(Crowdfunding, on_delete=models.DO_NOTHING, related_name='campaignTransaction', null=False, blank=True)
    
# user = User.objects.get(id=1)  # Get a specific user
# user_crowdfundings = user.crowdfundings.all()  # Get all crowdfunding campaigns related to this user

      

