from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
# from django.contrib.auth.models import User
from .models import Product, Payment, Profile, Withdraw


# UserAdmin.fieldsets += ('Custom fields set', {'fields': ('phone_number',)}),

class ProductAdmin(admin.ModelAdmin):
        search_fields = ['name', 'code', 'amount']
        list_display = ('name', 'ui_name', 'amount', 'code', 'investment_period', 'percentage_return')

class PaymentAdmin(admin.ModelAdmin):
        search_fields = ['phn_number', 'mpesa_code', 'package', 'paid_by']
        list_display = ('package', 'phn_number', 'amount', 'mpesa_code', 'status', 'created_date', 'paid_by')

class ProfileAdmin(admin.ModelAdmin):
        search_fields = ['user', 'code', 'recommended_by']
        list_display = ('user', 'code', 'recommended_by', 'created', 'updated')

class WithdrawReferralAdmin(admin.ModelAdmin):
        search_fields = ['phn_number', 'amount', 'withdrawn_by']
        list_display = ('withdrawn_by', 'phn_number', 'amount', 'status', 'created_date')

admin.site.register(Product, ProductAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Withdraw, WithdrawReferralAdmin)
# admin.site.register(UserAdmin)
