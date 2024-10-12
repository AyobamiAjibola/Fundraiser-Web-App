from django import forms
from django.contrib.auth.models import User
import re
from .models import Crowdfunding, Account

class RegisterForm(forms.ModelForm):
    
    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.helper = FormHelper(self)
    #     # self.helper.form_action = reverse_lazy('register')
    #     self.helper.add_input(Submit('submit', 'Submit'))
    #     self.helper.form_id = 'university-form'
    #     self.helper.attrs = {
    #         'hx-post': reverse_lazy('register'),
    #         'hx-target': '#university-form',
    #         'hx-swap': 'outerHTML'
    #     }
    
    # password_confirm = forms.CharField(
    #     widget=forms.PasswordInput(attrs={
    #         'hx-get': reverse_lazy('check_confirm_password'),
    #         'hx-target': '#div_id_confirm_password',
    #         'hx-trigger': 'keyup[target.value.length > 3]'
    #     }), 
    #     label='Confirm Password'
    # )
    password_confirm = forms.CharField(label='Password confirm*', widget=forms.PasswordInput, required=True)
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = [
            # 'username',
            'first_name', 
            'last_name',
            'email',
            'password',
            'password_confirm'
        ]
        # widgets = {
        #     'password': forms.PasswordInput(),
        #     'email': forms.EmailInput(attrs={
        #         'hx-get': reverse_lazy('check_email'),
        #         'hx-target': '#div_id_email',
        #         'hx-trigger': 'keyup[target.value.length > 5 && target.value.includes("@")]'
        #     }),
        #     'username': forms.TextInput(attrs={
        #         'hx-get': reverse_lazy('check_username'),
        #         'hx-target': '#div_id_username',
        #         'hx-trigger': 'keyup[target.value.length > 3]'
        #     })
        # }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        pattern = re.compile(
            r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@#$%^&+=]).{8,}$'
        )
        
        if pattern.match(password) is not True:
            raise forms.ValidationError("Password does not meet requirement!")
        
        return password
        
    def clean_password_confirm(self):
        password = self.cleaned_data.get('password')
        password_confirm = self.cleaned_data.get('password_confirm')
        
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match!")
        
        return password_confirm

    def clean_email(self):
        email = self.cleaned_data.get('email')
        
        if email and User.objects.filter(email=email).exists():
            raise forms.ValidationError("Email is already in use.")
        
        return email

    def save(self, commit=True):
        user = super().save(commit=False)  # Don't save the user yet
        user.set_password(self.cleaned_data['password'])  # Hash the password
        if commit:
            user.save()  # Now save the user with the hashed password
        return user


    # def save(self, commit=True):
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data['password'])
    #     if commit:
    #         user.save()
    #         Profile.objects.create(
    #             user=user,
    #             address=self.cleaned_data['address'],
    #             is_admin=self.cleaned_data['is_admin'],
    #             image=self.cleaned_data['image'],
    #             state=self.cleaned_data['state'],
    #             lga=self.cleaned_data['lga'],
    #         )
    #     return user
    
class UpdateUserForm(forms.ModelForm):
    image = forms.ImageField(required=False)
    state = forms.CharField(max_length=100, required=False)
    lga = forms.CharField(max_length=100, required=False)
    address = forms.CharField(required=False)

    class Meta:
        model = User
        fields = [
            # 'username',
            'first_name', 
            'last_name', 
            'email', 
            'address',
            'image', 
            'state', 
            'lga'
        ]
        labels = {
            'image': 'Profile Picture',
        }
    
    # def __init__(self, *args, **kwargs):
    #     self.request = kwargs.pop('request', None)
    #     super(UpdateUserForm, self).__init__(*args, **kwargs)

    # def clean_email(self):
    #     email = self.cleaned_data.get('email')
    #     if self.request and self.request.user and self.request.user.is_authenticated:
    #         current_user = self.request.user
    #     else:
    #         raise forms.ValidationError('User is not authenticated.')

    #     if email and User.objects.filter(email=email).exclude(pk=current_user.pk).exists():
    #         raise forms.ValidationError('Email is already in use.')
        
    #     return email

    # def save(self, commit=True):
    #     user = super().save(commit=False)
        
    #     # Update the User model
    #     if commit:
    #         user.save()
        
    #     # Retrieve the Profile instance based on the User
    #     # profile, created = Profile.objects.get_or_create(user=user)
        
    #     # Retrieve the Profile instance assuming it already exists
    #     profile = user.profile
        
    #     # Update the profile fields
    #     profile.address = self.cleaned_data.get('address')
    #     profile.image = self.cleaned_data.get('image')
    #     profile.state = self.cleaned_data.get('state')
    #     profile.lga = self.cleaned_data.get('lga')
        
    #     # Save the profile
    #     if commit:
    #         profile.save()

    #     return user

class FundraiserForm(forms.ModelForm):
    image = forms.ImageField(required=True)
    state = forms.CharField(max_length=100, required=True)
    lga = forms.CharField(max_length=100, required=True)
    address = forms.CharField(required=True)
    title = forms.CharField(max_length=100, required=True)
    description = forms.CharField(max_length=1000, required=False)
    firstName = forms.CharField(max_length=100, required=True)
    lastName = forms.CharField(max_length=100, required=True)
    
    class Meta:
        model = Crowdfunding
        fields = [
            'title',
            'description',
            'address',
            'image',
            'amountNeeded',
            'state',
            'lga',
            'firstName',
            'lastName'
        ]
        labels = {
            'image': 'Profile Picture',
            'amountNeeded': 'Amount Needed'
        }
        
        # def save(self, commit=True):
        #     crowdfunding = super().save(commit=False)
        #     if commit:
        #         crowdfunding.save()
        #         account_data = {
        #             'accountName': self.cleaned_data['accountName'],
        #             'bank': self.cleaned_data['bank'],
        #             'accountNumber': self.cleaned_data['accountNumber'],
        #             'bankCode': self.cleaned_data['bankCode']
        #         }
        #         Account.objects.update_or_create(
        #             crowdfunding=crowdfunding, defaults=account_data)
        #     return crowdfunding

class AccountForm(forms.ModelForm):
    accountName = forms.CharField(max_length=100, required=True)
    bank = forms.CharField(max_length=100, required=True)
    accountNumber = forms.CharField(required=True)
    bankCode = forms.CharField(max_length=100, required=False)
    
    class Meta:
        model = Account
        fields = ['accountName', 'bank', 'accountNumber', 'bankCode']
        labels = {
            'accountName': 'Account Name',
            'accountNumber': 'Account Number'
        }
    