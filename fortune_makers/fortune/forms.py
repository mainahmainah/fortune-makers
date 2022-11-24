from django import forms
# from bootstrap_daterangepicker import widgets, fields

from .models import Product, Payment, Withdraw
from django.contrib.auth.forms import UserCreationForm
from .models import User

# registration
# from datetime import timedelta

# from django.forms import ValidationError
# from django.conf import settings
# from django.contrib.auth.models import User
# from django.utils import timezone
# from django.db.models import Q
# from django.utils.translation import gettext_lazy as _


class NewUserForm(UserCreationForm):
    email = forms.EmailField(required=True)

    def __init__(self, *args, **kwargs):
        super(NewUserForm, self).__init__(*args, **kwargs)

        for fieldname in ['email', 'username', 'password1', 'password2']:
            self.fields[fieldname].help_text = None

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super(NewUserForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return user


class MpesaForm(forms.Form):
    mpesa_code = forms.CharField(max_length = 200)

    def clean_code(self):
        mpesa_code = self.cleaned_data['mpesa_code']
        return mpesa_code

class PaymentCreate(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ('package', 'amount', 'mpesa_code', 'created_date', 'phn_number', 'status')


class WithdrawForm(forms.Form):
    amount = forms.IntegerField(label='Enter the Amount to Withdraw')
    phn_number = forms.CharField(label='Enter the Phone Number', max_length = 200)

    def clean_code(self):
        amount = self.cleaned_data['amount']
        phn_number = self.cleaned_data['phn_number']
        return amount,phn_number

class WithdrawCreate(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = ('phn_number', 'amount', 'fee', 'created_date', 'status')

class WithdrawFormReferral(forms.Form):
    amount = forms.IntegerField(label='Enter the points to convert')
    phn_number = forms.CharField(max_length = 200)

    def clean_code(self):
        amount = self.cleaned_data['amount']
        phn_number = self.cleaned_data['phn_number']
        return amount,phn_number

class WithdrawCreateReferral(forms.ModelForm):
    class Meta:
        model = Withdraw
        fields = ('phn_number', 'amount', 'created_date', 'status')
