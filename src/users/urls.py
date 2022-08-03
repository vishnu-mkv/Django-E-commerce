from django.urls import path

from .views import register_view, account_activate_view, registration_success_view, resend_activation_view, LogInView, logout_view

app_name = 'accounts'

urlpatterns = [
    path('register/', register_view, name='register'),
    path('login/', LogInView.as_view(), name='login'),
    path('register/success/', registration_success_view, name='register_success'),
    path('activate/<key>/', account_activate_view, name='email-activate'),
    path('resend/activate/', resend_activation_view, name='email-resend'),
    path('logout/', logout_view, name='logout'),
]

