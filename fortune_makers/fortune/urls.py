from django.urls import path
from django.urls import reverse
from django.conf import settings
from django.conf.urls.static import static

from . import views

app_name = 'fortune'

urlpatterns = [
    #path('admin/', admin.site.urls),
    # path('summary/', views.summary, name='summary'),
    path('get_mpesa_records/', views.get_mpesa_records, name='mpesa_records'),
    # path('', views.homepage, name = 'homepage'),
    path('homepage/', views.homepage, name = 'homepage'),
    path('', views.homepage, name='homepage'),
    path('privacy/', views.privacy_view, name='privacy'),
    path('terms/', views.terms_view, name='terms'),
    path('faqs/', views.faqs_view, name='faqs'),

    path('products/', views.search_products, name='products'),    
    path('payment/', views.payment_view, name='payment'),
    path('summary/', views.summary_view, name='summary'),
    path('wallet/', views.wallet_view, name='wallet'),
    path('logged_in_users/', views.logged_in_users_view, name='logged_in_users'),
    path('quick_guide/', views.quick_guide_view, name='quick_guide'),
    # path('index/', views.index_view, name='index'),
    path('mpesa/', views.mpesa_view, name='mpesa'),

    path('register/', views.register_request, name='register'),
    path('login/', views.login_request, name='login'),
    path('logout/', views.logout_request, name= 'logout'),

    
    # path('invoice/', views.invoice_view, name='invoice'),
    # path('my_profile/', views.my_profile_view, name='my_profile'),
    # path('<str:ref_code>/', views.my_profile_view, name='my_profile'),
    # path('<str:ref_code>/', views.my_profile_view, name='my_profile'),
    path('my_referral/', views.my_referral_view, name='my_referral'),
    path('my_invoices/', views.my_invoices_view, name='my_invoices'),
    path('my_investments/', views.my_investments_view, name='my_investments'),
    path('download_invoice_csv/', views.generate_invoice_csv, name='invoice_csv_download'),
    path('download_invoice_pdf/', views.generate_invoice_pdf, name='invoice_pdf_download'),

    # path('register/', views.register_request, name='register'),
    # path('login/', views.login_request, name='login'),
    # path('logout/', views.logout_request, name= 'logout'),

    path('product1/', views.p1_view, name='product1'),
    path('product2/', views.p2_view, name='product2'),
    path('product3/', views.p3_view, name='product3'),
    path('product4/', views.p4_view, name='product4'),
    path('product5/', views.p5_view, name='product5'),
    path('product6/', views.p6_view, name='product6'),

    path('payment/', views.payment_view, name='payment'),
    # path('complete/', views.complete_view, name='complete'),        

    path('my_profile/', views.my_profile_view, name='my_profile'),
    path('<str:ref_code>/', views.my_profile_view, name='my_profile'),

    
    # path('change/profile/', ChangeProfileView.as_view(), name='change_profile'),
    # path('change/password/', ChangePasswordView.as_view(), name='change_password'),
]
