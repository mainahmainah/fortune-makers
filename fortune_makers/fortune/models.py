from django.db import models
from datetime import datetime
from django.utils import timezone
from .utils import generate_ref_code

# registration
from django.contrib.auth.models import User
from django.contrib.auth.models import AbstractUser



class Product(models.Model):
    name = models.CharField(max_length=100)
    ui_name = models.CharField(max_length=200)
    amount = models.IntegerField(default=0)
    code = models.CharField(max_length=100)
    investment_period = models.IntegerField(default=0)
    percentage_return = models.FloatField(default=0)

    def __str__(self):
        return self.name


class Payment(models.Model):
    phn_number = models.CharField(max_length=100)
    mpesa_code = models.CharField(max_length=100)
    package = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.now())
    amount = models.IntegerField(default=0)
    status = models.BooleanField(default=False)
    paid_by = models.CharField(max_length=100)

    def __str__(self):
        return self.mpesa_code

    def __str__(self):
        return self.package

    def __str__(self):
        return self.paid_by

class Withdraw(models.Model):
    phn_number = models.CharField(max_length=100)
    amount = models.IntegerField(default=0)
    fee = models.IntegerField(default=0)
    withdrawn_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.now())
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.phn_number

    def __str__(self):
        return self.withdrawn_by

class WithdrawReferral(models.Model):
    phn_number = models.CharField(max_length=100)
    amount = models.IntegerField(default=0)
    withdrawn_by = models.CharField(max_length=100)
    created_date = models.DateTimeField(default=timezone.now())
    status = models.BooleanField(default=False)

    def __str__(self):
        return self.phn_number

    def __str__(self):
        return self.withdrawn_by


class Profile(models.Model):
    # you should use a one to one link when you need to store extra information about the existing user 
    # model that's not related to the authentication process. we usually call it a User Profile
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=12, blank=True)
    recommended_by = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True, related_name='ref_by')
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}-{self.code}"

    def get_recommened_profiles(self):
        qs = Profile.objects.all()
        # my_recs = [p for p in qs if p.recommended_by == self.user]

        my_recs = []
        for profile in qs:
            if profile.recommended_by == self.user:
                my_recs.append(profile)
        return my_recs

    def save(self, *args, **kwargs):
        print("I have been called=========----====")
        if self.code == "":
            code = generate_ref_code()
            print("code====",code)
            self.code = code
        super(Profile, self).save(*args, **kwargs)
