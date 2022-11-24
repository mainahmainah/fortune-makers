from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from .models import Product, Payment, Profile, Withdraw
from .utils import generate_ref_code
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# for csv generation
import csv
# for pdf generation
from django.template.loader import render_to_string
# from weasyprint import HTML
import tempfile
from .forms import NewUserForm, PaymentCreate, WithdrawForm, MpesaForm, WithdrawCreate, WithdrawFormReferral
# Create your views here.
from django.http import HttpResponse
from django.db.models import Avg, Max, Min, Sum
from django.contrib import messages

from datetime import datetime
from datetime import timedelta
import math

# registration
from django.contrib.auth.models import Group, User
from django.contrib.auth.forms import AuthenticationForm #add this
from django.contrib.auth import login, logout, authenticate, REDIRECT_FIELD_NAME
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
# from django.utils.http import is_safe_url
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.utils.translation import gettext_lazy as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters
from django.views.generic import View, FormView
from django.conf import settings


from django.contrib.sessions.models import Session
from importlib import import_module
from django.conf import settings

def homepage(request):
    return render(request, 'fortune/homepage.html')

def privacy_view(request):
    return render(request, 'fortune/privacy.html')

def terms_view(request):
    return render(request, 'fortune/terms.html')

def faqs_view(request):
    return render(request, 'fortune/faqs.html')

def check_activated(request, user):
    mpesa_records = Payment.objects.all().order_by("-created_date").values()
    total_in = mpesa_records.filter(status=True).values(
            'created_date','phn_number','mpesa_code','package','status','amount')
    total_inv = total_in.filter(paid_by=user)[:1]

    amount2 = []
    if total_inv:
        for i in total_inv:
            amount = i['amount']
            amount2.append(amount)
    if len(amount2) > 0:
        return True
    else:
        return False

@login_required
def payment_view(request):
    user = request.user
    user_id = user.id
    account_number = int(user_id+10000)
    end_subscription = None
    # Find the end of subscription
    record = Payment.objects.filter(reference=account_number).values()
    if record.count() > 0:
        sorted_record = sorted(record, key = lambda i: i['created_at'])
        record_date = sorted_record[-1]['created_at'].date()
        end_subscription = record_date + timedelta(days=30)
    return render(request, 'fortune/payment.html', {
     'end_subscription':end_subscription})

@login_required
def get_mpesa_records(request):
    user = request.user
    mpesa_records = Payment.objects.all().order_by("-created_date")
    total_inv = []
    total_invoices = 0
    if mpesa_records.count() > 0:
        total_inv = mpesa_records.values(
            'created_date','phn_number','mpesa_code','package','amount')
        total_invoice = total_inv.aggregate(price_sum=Sum('amount'))
        total_invoices = int(total_invoice['price_sum'])
    else:
            total_invoices = 0

    return render(request, 'fortune/fortune_mpesa_records.html', {
        'mpesa_records': mpesa_records, 'total_invoices': total_invoices})


# def my_referral_view(request):
#     if not request.user.is_authenticated:
#         return redirect('fortune:login')

    return render(request, 'fortune/my_referral.html')

def my_invoices_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')
    user = request.user
    mpesa_records = Payment.objects.all().order_by("-created_date")
    total_inv = []
    total_invoices = 0
    if mpesa_records.count() > 0:
        total_inv = mpesa_records.filter(paid_by=user).values(
            'created_date','phn_number','mpesa_code','package','status','amount')
        if total_inv.count()>0:
            total_invoice = total_inv.aggregate(price_sum=Sum('amount'))
            total_invoices = int(total_invoice['price_sum'])
        else:
            total_invoices = 0

    return render(request, 'fortune/my_invoices.html', {
        'total_inv': total_inv, 'total_invoices':total_invoices})


def my_referral_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')

    qs = Profile.objects.all()
    user_list = []
    for profile in qs:
        if profile.recommended_by == request.user:
            user_list.append(profile.user)

    print("users list",user_list)

    m_records = []

    for i in user_list:
        if check_activated(request, i):
            m_records.append(i)

    print("m records",m_records)
    active_referalls=len(m_records)
    total_commission = active_referalls*100

    print("m records",active_referalls)
    # print("======callled====    ")
    if Profile.objects.get(user=request.user) is not None:
        my_recs = Profile.objects.get(user=request.user).get_recommened_profiles()
    else:
        my_recs = {}

    inactive_referrals = set(user_list)-set(m_records)

    return render(request, 'fortune/my_referral.html', {
        'my_recs': my_recs, 'total_commission':total_commission
        , 'm_records':m_records, 'inactive_referrals':inactive_referrals
        , 'user_list':user_list})  


def my_recommendations_view(request):
    profile = Profile.objects.get(user=request.user)
    my_recs = profile.get_recommened_profiles()
    context = {'my_recs': my_recs}
    return render(request, 'profiles/my_profile.html', context)


def my_profile_view(request, *args, **kwargs):
    code = str(kwargs.get('ref_code'))
    print("ref code",code)
    try:
        profile = Profile.objects.get(code=code)
        request.session['ref_profile'] = profile.id
        # print('id', profile.id)
    except:
        pass
    # print(request.session.get_expiry_age())
    # return render(request, 'fortune/index.html')
    return render(request, 'fortune/homepage.html')


def my_investments_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')

    user = request.user
    mpesa_records = Payment.objects.all().order_by("-created_date")
    total_inv = []
    total_invoices = 0
    if mpesa_records.count() > 0:
        total_inv = mpesa_records.filter(paid_by=user).values(
            'created_date','phn_number','mpesa_code','package','status','amount')
        if total_inv.count()>0:
            total_invoice = total_inv.aggregate(price_sum=Sum('amount'))
            total_invoices = int(total_invoice['price_sum'])
        else:
            total_invoices = 0

    return render(request, 'fortune/my_investments.html', {
        'total_inv': total_inv, 'total_invoices':total_invoices})


def generate_invoice_pdf(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')

    user=request.user
    user_id = user.id
    account_number = int(user_id+10000)
    total = Payment.objects.all()
    total_invoice = total.filter(id=user_id)

    # Rendered
    html_string = render_to_string('fortune/invoice_pdf.html', {'total_invoice': total_invoice})
    html = HTML(string=html_string)
    result = html.write_pdf()

    # Creating http response
    response = HttpResponse(content_type='application/pdf;')
    response['Content-Disposition'] = 'inline; filename=invoice.pdf'
    response['Content-Transfer-Encoding'] = 'binary'
    with tempfile.NamedTemporaryFile(delete=True) as output:
        output.write(result)
        output.flush()
        output = open(output.name, 'rb')
        response.write(output.read())

    return response


def generate_invoice_csv(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')

    user=request.user
    user_id = user.id
    account_number = int(user_id+10000)
    total = Payment.objects.all()
    items = total.filter(id=user_id)
    # items = Revenue.objects.all()
    response = HttpResponse(content_type = 'text/csv')
    response['Content-Disposition'] = 'attachment;filename="invoice.csv"'

    writer = csv.writer(response,delimiter=',')
    writer.writerow(['Paid On','Amount', 'First Name', 'Last Name', 'Phone Number', 'Mpesa Code'])
    for obj in items:
        writer.writerow([obj.created_date,obj.amount,obj.first_name,obj.last_name,obj.phn_number,obj.mpesa_code])
 
    return response


def summary_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')

    user = request.user
    ref_codes = Profile.objects.all()
    print("ref codes=======............................",ref_codes)

    my_ref_code = ref_codes.filter(user=user).values('code')
    print("my ref code=======",my_ref_code)
    # my_ref_code2 = 'adcd'
    my_ref_code2 = my_ref_code[0]['code']
    print("my ref code-2--------",my_ref_code2)
    my_host = request.get_host()
    print("my host=========",my_host)
    my_ref_code_url = 'https://'+str(my_host)+'/'+str(my_ref_code2)
    print("my ref code url=========",my_ref_code_url)
          
    mpesa_records = Payment.objects.all().order_by("-created_date")
    total_inv = []
    total_invoices = 0
    total_earnings = 0
    daily_earnings = 0
    total_amount = 0
    total_package = []
    if mpesa_records.count() > 0:
        total_inv = mpesa_records.filter(paid_by=user).values(
            'created_date','phn_number','mpesa_code','package','status','amount')

        total_created_date = []
        total_amount = []
        total_package = []
        my_total_dates = []
        if total_inv:
            for i in total_inv:
                if i['status']== True:
                    amount = i['amount']
                    package = i['package']
                    total_amount.append(amount)
                    total_package.append(package)

                    today = datetime.now().date()
                    record_create_date = i['created_date'].date()
                    my_date = (today - record_create_date)
                    print("days since creation=========",my_date)
                    my_date1 = (my_date.days * amount * 7.5)/100
                    my_total_dates.append(my_date1)
                    total_created_date.append(my_date.days)

        today = datetime.now().date()
        total_earnings = sum(my_total_dates)
        if total_inv.count()>0:
            total_invoice = total_inv.aggregate(price_sum=Sum('amount'))
            total_invoices = int(total_invoice['price_sum'])
        else:
            total_invoices = 0
        sum_totals = sum(total_amount)    

        daily_earnings = ((sum_totals * 7.5) / 100)
        print("daily earnings=========",daily_earnings)

    return render(request, 'fortune/summary.html', {
        'total_invoices':total_invoices, 'daily_earnings':daily_earnings
        , 'total_earnings':total_earnings, 'total_amount':total_amount
        ,'total_package':total_package ,'my_ref_code_url':my_ref_code_url
        ,'user':user})
    # return render(request, 'fortune/summary.html')

def activated(request):
    pass

def wallet_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')
          
    user = request.user
    total_withdrawn_by_all_users=[]
    withdraw_records = Withdraw.objects.all().order_by("-created_date").values()
    print("records of all withdrawn by all users==============",withdraw_records)
    total_withdrawn = 0
    fees2 = []
    amount3 = []
    if withdraw_records:
        for i in withdraw_records:
            amount = i['amount']
            fee = i['fee']
            fees2.append(fee)
            total_withdrawn_by_all_users.append(amount)
            if i['status']==True:
                amount2 = i['amount']
                amount3.append(amount2)

    # calculate approved withdrawals
    active_withdrawals = sum(amount3)
    # calculate all withdrawals active and pending
    total_withdrawn=sum(total_withdrawn_by_all_users)
    # calculate fees for all withdrawals active and pending
    total_users_fees = sum(fees2)

    mpesa_records = Payment.objects.all().order_by("-created_date").values()
    total_deposit_by_all_users = []
    users_total_deposit = 0
    total_users_deposit = 0
    if mpesa_records:
        for i in mpesa_records:
            if i['status']== True:
                amount = i['amount']
                total_deposit_by_all_users.append(amount)
    # confirmed mpesa deposits by all users            
    users_total_deposit=sum(total_deposit_by_all_users)

    total_withdrawn = []
    total_withdrawn_by_user = 0
    fees = []
    total_fees = 0
    if withdraw_records.count() > 0:
        total_inv = withdraw_records.filter(withdrawn_by=user).values(
            'created_date','phn_number','status','amount', 'fee')
        for i in total_inv:
            fee = i['fee']
            fees.append(fee)
            amount = i['amount']
            total_withdrawn.append(amount)
    
    total_withdrawn_by_user = sum(total_withdrawn)

    total_fees = sum(fees)
    my_interest = []
    wallet_balance = 0
    active_profit = (users_total_deposit - active_withdrawals) + total_users_fees
    if mpesa_records.count() > 0:
        total_in = mpesa_records.filter(paid_by=user).values(
            'created_date','phn_number','mpesa_code','package','status','amount')

        if total_in:
            for i in total_in:
                if i['status']== True:
                    amount = i['amount']
                    today = datetime.now().date()
                    record_create_date = i['created_date'].date()
                    no_of_days = (today - record_create_date)
                    interest = ((no_of_days.days * amount * 7.5)/100)
                    my_interest.append(interest)


    wallet_balance = sum(my_interest) - (total_fees + total_withdrawn_by_user) 
    print("wallet balance",wallet_balance)

    if wallet_balance > 250:
        withdrawable_balance = math.floor(wallet_balance/100)*100
        print("withdrawable balance",withdrawable_balance)
    else:
        withdrawable_balance = 0

    # if Profile.objects.get(user=request.user) is not None:
    #     my_recs = Profile.objects.get(user=request.user).get_recommened_profiles()
    # else:
    #     my_recs = {}
    # my_recs_count = len(my_recs)
    # total_commission = my_recs_count*100


    qs = Profile.objects.all()
    user_list = []
    for profile in qs:
        if profile.recommended_by == request.user:
            user_list.append(profile.user)

    print("users list",user_list)

    m_records = []

    for i in user_list:
        if check_activated(request, i):
            m_records.append(i)

    active_referalls=len(m_records)
    total_commission = active_referalls*100
    # only display withdraw forms if above condition met
    # remember that for you to display the form you must call the method having the form logic
    total_inv = withdraw_records.filter(withdrawn_by=user)
    form=WithdrawForm()
    # print("withdraw form==========",form)
    if request.method == 'POST':
        print("method is post==========----------============")
        withdraw_records = Withdraw.objects.all().order_by("-created_date")
        total_inv = withdraw_records.filter(withdrawn_by=user)
        form = WithdrawForm(request.POST)
        # print("withdraw form==========",form)
        if form.is_valid():
            print("form valid----------------")
            today=datetime.today().weekday()
            print("today====---====",today)
            amount = form.cleaned_data['amount']
            phn_number = form.cleaned_data['phn_number']

            create_inv = WithdrawCreate()
            post = create_inv.save(commit=False)
            if amount > withdrawable_balance:
                messages.add_message(request, messages.WARNING,
                    "Sorry..You can't withdraw more than your withdrawable balance.")
                return redirect("fortune:wallet")
            elif amount < 250:
                messages.add_message(request, messages.WARNING,
                    "Sorry..The minimum amount you can withdraw is Ksh. 250")
                return redirect("fortune:wallet")
            elif today == 1 or today == 3 or today == 5 or today == 6:
                messages.add_message(request, messages.WARNING,
                    "Sorry..You can only withdraw on Monday, Wednesday and Friday")
                return redirect("fortune:wallet")
            elif total_inv.count()==1 and amount < 500:
                messages.add_message(request, messages.WARNING,
                    "Sorry..Your second withdrawal cannot be less than ksh.500")
                return redirect("fortune:wallet")
            elif total_inv.count()==2 and amount < 1000:
                messages.add_message(request, messages.WARNING,
                    "Sorry..Your third withdrawal cannot be less than ksh.1,000")
                return redirect("fortune:wallet")
            elif total_inv.count()==3 and amount < 2000:
                messages.add_message(request, messages.WARNING,
                    "Sorry..Your fourth withdrawal cannot be less than ksh.2,000")
                return redirect("fortune:wallet")
            elif total_inv.count()==4 and amount < 5000:
                messages.add_message(request, messages.WARNING,
                    "Sorry..Your fifth withdrawal cannot be less than ksh.5,000")
                return redirect("fortune:wallet")
            elif total_inv.count()==5 and amount < 10000:
                messages.add_message(request, messages.WARNING,
                    "Sorry..Your sixth withdrawal cannot be less than ksh.10,000")
                return redirect("fortune:wallet")

            post_amount1 = math.floor(amount/100)*100
            print("post amount 1",post_amount1)
            post_amount = post_amount1 - ((5/100)*post_amount1)
            print("post amount",post_amount)
            fee = ((5/100)*post_amount1)
            print("fee",fee)
            post.amount = post_amount
            post.phn_number = phn_number
            post.fee = fee
            post.withdrawn_by = request.user
            post.save()
            messages.add_message(request, messages.INFO,
                "Your withdrawal is successful. Please wait for an admin to approve."
                "Please note that Withdrawals are only processed between 9 AM and 9 PM")
            return redirect("fortune:wallet")

        else:
            form = WithdrawForm()      

    # print all records in withdraw table filtering by current user

    return render(request, 'fortune/my_wallet.html',{
        'withdrawable_balance':withdrawable_balance
        ,'total_commission':total_commission
        ,'form': form, 'total_inv':total_inv
        , 'wallet_balance':wallet_balance
        , 'users_total_deposit':users_total_deposit
        , 'total_users_deposit':total_users_deposit
        , 'total_fees':total_fees
        , 'total_users_fees':total_users_fees
        , 'active_profit':active_profit})

def get_current_users():
    active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
    user_id_list = []
    for session in active_sessions:
        data = session.get_decoded()
        user_id_list.append(data.get('_auth_user_id', None))
    # Query all logged in users based on id list
    return User.objects.filter(id__in=user_id_list)

@login_required
def logged_in_users_view(request):
    logged_users = get_current_users()
    # print("logged users",logged_users)
    return render(request, 'fortune/logged_in_users.html', {
        'logged_users': logged_users})

def quick_guide_view(request):
    return render(request, 'fortune/quick_guide.html')

def index_view(request):
    products = Product.objects.all().order_by("code").values()
    all_products_list=products[0]
    key_access = list(all_products_list.keys())
    values_access = list(all_products_list.values())
    # product1
    product1_id = values_access[0]
    product_name = values_access[1]
    product1_ui_name = values_access[2]
    product_amount = values_access[3]
    product_code = values_access[4]
    product_investment_period = values_access[5]
    percentage_return = values_access[6]

    return render(request, 'fortune/index.html', {
        'products': products,'product1_ui_name':product1_ui_name})


def p1_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')
    products = Product.objects.all().values().order_by("code")
    all_products_list=products[0]
    key_access = list(all_products_list.keys())
    values_access = list(all_products_list.values())
    # print("values....",values_access)
    pid = values_access[0]
    name = values_access[1]
    ui_name = values_access[2]
    amount = values_access[3]
    # print("amount..",amount)
    code = values_access[4]
    investment_period = values_access[5]
    percentage_return = values_access[6]
    request.session['name'] = name
    request.session['ui_name'] = ui_name
    request.session['amount'] = amount
    request.session['investment_period'] = investment_period
    request.session['percentage_return'] = percentage_return
    total_return = ((amount*7.5*75) / 100)
    request.session['expected_amount'] = total_return
    # print('total return',total_return)
    expected_amount = request.session.get('expected_amount')
    # print('total return',expected_amount)

    return render(request, 'fortune/product1.html', {
        'ui_name':ui_name, 'name':name
        , 'amount':amount, 'investment_period':investment_period
        ,'percentage_return':percentage_return, 'expected_amount':expected_amount})


def p2_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')
    products = Product.objects.all().values().order_by("code")
    all_products_list=products[1]    
    key_access = list(all_products_list.keys())
    values_access = list(all_products_list.values())
    pid = values_access[0]
    name = values_access[1]
    ui_name = values_access[2]
    amount = values_access[3]
    code = values_access[4]
    investment_period = values_access[5]
    percentage_return = values_access[6]
    request.session['name'] = name
    request.session['ui_name'] = ui_name
    request.session['amount'] = amount
    request.session['investment_period'] = investment_period
    request.session['percentage_return'] = percentage_return
    expected_amount = ((amount*7.5*75) / 100)
    request.session['expected_amount'] = expected_amount

    # return HttpResponse(status = 200)

    return render(request, 'fortune/product2.html', {
        'ui_name':ui_name, 'name':name
        , 'amount':amount, 'investment_period':investment_period
        ,'percentage_return':percentage_return, 'expected_amount':expected_amount})


def p3_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')
    products = Product.objects.all().values().order_by("code")
    all_products_list=products[2]
    key_access = list(all_products_list.keys())
    values_access = list(all_products_list.values())
    pid = values_access[0]
    name = values_access[1]
    ui_name = values_access[2]
    amount = values_access[3]
    code = values_access[4]
    investment_period = values_access[5]
    percentage_return = values_access[6]
    request.session['name'] = name
    request.session['ui_name'] = ui_name
    request.session['amount'] = amount
    request.session['investment_period'] = investment_period
    request.session['percentage_return'] = percentage_return
    expected_amount = ((amount*7.5*75) / 100)
    request.session['expected_amount'] = expected_amount

    return render(request, 'fortune/product3.html', {
        'ui_name':ui_name, 'name':name
        , 'amount':amount, 'investment_period':investment_period
        ,'percentage_return':percentage_return, 'expected_amount':expected_amount})

def p4_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')
    products = Product.objects.all().values().order_by("code")
    all_products_list=products[3]
    key_access = list(all_products_list.keys())
    values_access = list(all_products_list.values())
    pid = values_access[0]
    name = values_access[1]
    ui_name = values_access[2]
    amount = values_access[3]
    code = values_access[4]
    investment_period = values_access[5]
    percentage_return = values_access[6]
    request.session['name'] = name
    request.session['ui_name'] = ui_name
    request.session['amount'] = amount
    request.session['investment_period'] = investment_period
    request.session['percentage_return'] = percentage_return
    expected_amount = ((amount*7.5*75) / 100)
    request.session['expected_amount'] = expected_amount


    return render(request, 'fortune/product4.html', {
        'ui_name':ui_name, 'name':name
        , 'amount':amount, 'investment_period':investment_period
        ,'percentage_return':percentage_return, 'expected_amount':expected_amount})  

def p5_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')
    products = Product.objects.all().values().order_by("code")
    all_products_list=products[4]
    key_access = list(all_products_list.keys())
    values_access = list(all_products_list.values())
    pid = values_access[0]
    name = values_access[1]
    ui_name = values_access[2]
    amount = values_access[3]
    code = values_access[4]
    investment_period = values_access[5]
    percentage_return = values_access[6]
    request.session['name'] = name
    request.session['ui_name'] = ui_name
    request.session['amount'] = amount
    request.session['investment_period'] = investment_period
    request.session['percentage_return'] = percentage_return
    expected_amount = ((amount*7.5*75) / 100)
    request.session['expected_amount'] = expected_amount

    return render(request, 'fortune/product5.html', {
        'ui_name':ui_name, 'name':name
        , 'amount':amount, 'investment_period':investment_period
        ,'percentage_return':percentage_return, 'expected_amount':expected_amount})


def p6_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')
    products = Product.objects.all().values().order_by("code")
    all_products_list=products[5]
    key_access = list(all_products_list.keys())
    values_access = list(all_products_list.values())
    pid = values_access[0]
    name = values_access[1]
    ui_name = values_access[2]
    amount = values_access[3]
    code = values_access[4]
    investment_period = values_access[5]
    percentage_return = values_access[6]
    request.session['name'] = name
    request.session['ui_name'] = ui_name
    request.session['amount'] = amount
    request.session['investment_period'] = investment_period
    request.session['percentage_return'] = percentage_return
    expected_amount = ((amount*7.5*75) / 100)
    request.session['expected_amount'] = expected_amount

    return render(request, 'fortune/product6.html', {
        'ui_name':ui_name, 'name':name
        , 'amount':amount, 'investment_period':investment_period
        ,'percentage_return':percentage_return, 'expected_amount':expected_amount})

                         
def register_request(request):
    profile_id = request.session.get('ref_profile')
    print('profile_id', profile_id)
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            if profile_id is not None:
                recommended_by_profile = Profile.objects.get(id=profile_id)

                user = form.save()
                registered_user = User.objects.get(id=user.id)
                registered_profile = Profile.objects.get(user=registered_user)
                registered_profile.recommended_by = recommended_by_profile.user
                registered_profile.save()
            else:
                user = form.save()
            login(request, user)
            messages.add_message(request, messages.SUCCESS, "Registration Was Successfull, Please Login")
            return redirect("fortune:login")
        # messages.warning(request, 'Please correct the error below.')
        
        messages.error(request, form.errors)
        # messages.error(request, "Unsuccessful registration. Invalid information.")
    form = NewUserForm()
    return render (request=request, template_name="fortune/register.html", context={"register_form":form})


def login_request(request):
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.add_message(request, messages.SUCCESS, 
                    "You are now logged in. Please scroll down to purchase a package of your choice and enjoy hyper returns")
                return redirect("fortune:homepage")
            # else:
            #     messages.error(request,form.errors)
        else:
            messages.add_message(request, messages.ERROR, form.errors)
            # messages.error(request, form.errors)
            form = AuthenticationForm()
    form = AuthenticationForm()
    return render(request=request, template_name="fortune/login.html", context={"login_form":form})


def logout_request(request):
    logout(request)
    messages.add_message(request, messages.INFO, "You have successfully logged out.")
    # messages.info(request, "You have successfully logged out.")  
    return redirect("fortune:homepage")

def search_products(request):
    products = Product.objects.all().values().order_by("code")
    all_products_list=(products[0])
    key_access = list(all_products_list.keys())
    values_access = list(all_products_list.values())
    # product1
    product1_id = values_access[0]
    product_name = values_access[1]
    product1_ui_name = values_access[2]
    product_amount = values_access[3]
    product_code = values_access[4]
    product_investment_period = values_access[5]
    percentage_return = values_access[6]

    # product1=all_products.id

    # total_invoice = total.filter(reference=account_number)
    return render(request, 'fortune/index.html', {
        'products': products,'ui_name':product1_ui_name})

def payment_view(request):
    if not request.user.is_authenticated:
        return redirect('fortune:login')
    amount = request.session.get('p2_name')
    return render(request, 'fortune/payment.html',)


def mpesa_view(request):
    user=request.user
    amount = request.session.get('amount')
    name = request.session.get('name')
    form=MpesaForm()
    if request.method == 'POST':
        form = MpesaForm(request.POST)
        if form.is_valid():
            mpesa_code = form.cleaned_data['mpesa_code']
            request.session['mpesa_code'] = mpesa_code    
            create_inv = PaymentCreate()
            post = create_inv.save(commit=False)
            post.package = request.session.get('name')
            post.amount = request.session.get('amount')
            post.paid_by = request.user
            post.mpesa_code = request.session.get('mpesa_code')
            post.created_date = timezone.now()
            # post.phn_number = user.phone_number
            post.save()
            messages.add_message(request, messages.INFO, "Thank you for investing with Fortune Makers. Please wait for an admin to approve your payment.")
            return redirect("fortune:my_investments")
        else:
            form = MpesaForm()

    return render(request, 'mpesa.html', {'form': form, 'amount':amount, 'name':name})
