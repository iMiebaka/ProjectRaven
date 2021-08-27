from os import name
from django.urls import path
from . import views
# from django.conf.urls import handler404, handler500, handler403, handler400

app_name = 'payments'

urlpatterns = [
    path('', views.subscription, name='subscription'),
    path('cancel-subscription', views.cancel_subscription, name='cancel_subscription'),
    path('config/', views.stripe_config, name='stripe_config'), 
    path('paypal-complete/', views.complete_paypal, name='complete_paypal'), 
    path('delay-payment/', views.delay_payment, name='delay_payment'), 
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('success', views.SuccessView), # new
    path('cancelled/', views.CancelledView), # new
    path('webhook/', views.stripe_webhook, name='stripe_webhook'),
]


# handler404 = f'{app_name}.views.error_404'
# handler403 = f'{app_name}.views.error_403'
# handler400 = f'{app_name}.views.error_400'
# handler500 = f'{app_name}.views.error_500'
