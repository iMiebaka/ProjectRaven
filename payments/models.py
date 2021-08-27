# from Django.payments.views import subscription
from typing import Text
from django.db import models
from django.db.models.fields import DateField
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.


class SubscriptionOption(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=20)
    stripe_price_code = models.CharField(max_length=40, null=True) 
    paypal_price_code = models.CharField(max_length=40, null=True) 
    cost = models.CharField(max_length=40, null=True) 
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    email_amount = models.PositiveSmallIntegerField(default=0, null=True)

    def __str__(self):
        return self.name

class PaymentHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, related_name="authorized_user", on_delete=models.CASCADE)
    # name = models.CharField(max_length=20)
    # cost = models.CharField(max_length=40, null=True) 
    sub_option = models.ForeignKey('SubscriptionOption', null=True, on_delete=models.SET_NULL)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    payment_platform_name = models.CharField(max_length=10, null=True)
    customer_payment_reciept = models.CharField(max_length=40, null=True)
    receipt_status = models.CharField(max_length=10, default='Incomplete' ,null=True)
    email_amount = models.PositiveSmallIntegerField(default=0, null=True)
    last_email_amount = models.PositiveSmallIntegerField(default=0, null=True)
    payment_platform_reciept = models.CharField(max_length=40, null=True)
    payment_platform_desc = models.CharField(max_length=60, null=True)
    payment_completed = models.BooleanField(default=False)
    un_sub_hint = models.ForeignKey(User, related_name='extended_user', null=True, on_delete=models.CASCADE)

    # def __str__(self):
    #     return f'{self.sub_option} by {self.user.username}' 


class ActiveAccount(models.Model):
    payment_history_init = models.ForeignKey('PaymentHistory', on_delete=models.CASCADE)
