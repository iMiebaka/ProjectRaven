from celery import Celery
from celery import shared_task
from .models import ActiveAccount
from datetime import timedelta, datetime
from django.apps import apps
Profile = apps.get_model('accounts', 'Profile')
EmailSent = apps.get_model('mailer', 'EmailSent')
from django.utils import timezone

app = Celery()

expiration_date = 30

@shared_task
def check_subscription():
    active_accounts = ActiveAccount.objects.all()
    for sub_state in active_accounts:
        check_date = sub_state.payment_history_init.created_on
        check_date = check_date + timedelta(days=expiration_date)
        current_date = timezone.now()
        if current_date >= check_date:
            user_init = Profile.objects.get(user=sub_state.payment_history_init.user)
            user_init.subscribed = False
            user_init.save()
            sub_state.delete()
            print('Subscription Updated')


@shared_task
def delete_emails():
    emails = EmailSent.objects.all()
    for email in emails:
        print(email)
        check_date = email.created_on
        check_date = check_date + timedelta(days=expiration_date)
        current_date = timezone.now()
        if current_date >= check_date:
            email.delete()
            print('Old Emails Deleted')

