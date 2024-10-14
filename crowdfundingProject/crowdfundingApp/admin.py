from django.contrib import admin
from .models import Crowdfunding, Profile, Transaction, Donation
# Register your models here.

admin.site.register(Crowdfunding)
admin.site.register(Profile)
admin.site.register(Transaction)
admin.site.register(Donation)