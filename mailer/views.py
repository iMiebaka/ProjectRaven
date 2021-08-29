import json
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_list_or_404
from django.conf import settings
import csv
import pandas as pd
import numpy as np
from .models import EmailSent, EmailSentInti
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import EmailSent, EmailFile
from django.core.mail import get_connection, EmailMessage, BadHeaderError
from django.contrib import messages
from time import sleep
import hashlib
from django.core.cache import cache
from datetime import datetime
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt # new
from pathlib import Path
import django_excel as excel
from django.contrib.sites.shortcuts import get_current_site

from django.apps import apps
PaymentHistory = apps.get_model('payments', 'PaymentHistory')
Profile = apps.get_model('accounts', 'Profile')
# Create your views here.

file_extension = ['.csv', '.xlsx', '.CVS', '.XLSX']
url_link = 'http://a2def894f1cf.ngrok.io'


@login_required
def send_email(request):
    if request.method == 'POST':
        try:
            profile_init = Profile.objects.get(user=request.user)
            email_amount = profile_init.email_amount
            payment_history = PaymentHistory.objects.get(customer_payment_reciept=profile_init.last_payment_receipt)

            if email_amount < 1 or request.user.profile.subscribed is False:
                profile_init.subscribed = False
                profile_init.save()
                content = {
                    'data': 'error',
                    'email_amount': email_amount,
                    'message': f'You have {email_amount} emails to send \n Make subscription to send Email',
                }
                return JsonResponse(content)
        except Profile.DoesNotExist or PaymentHistory.DoesNotExist:
            content = {
                'data': 'error',
                'message': 'Make subscription to send Email',
            }
            return JsonResponse(content)

        if Path(str(request.FILES['sender_email'])).suffix not in file_extension:
            content = {
                'data': 'error',
                'message': f'Sender Email does not support {Path(str(request.FILES["sender_email"])).suffix} extension',
            }
            return JsonResponse(content)
        if Path(str(request.FILES['reciever_email'])).suffix not in file_extension:
            content = {
                'data': 'error',
                'message': f'Reciever Email does not support {Path(str(request.FILES["reciever_email"])).suffix} extension',
            }
            return JsonResponse(content)
        
        attachment_file = EmailFile(
            cache_checker = request.POST['cache_checker'].strip()
        )

        email_subject = request.POST['email_subject'].strip()
        cache_checker = request.POST['cache_checker'].strip()
        email_body = request.POST['email_body'].strip()

        cache.set(cache_checker, 'Uploading Attachement...', 120)

        attachment_file.sender_attachment = request.FILES["sender_email"]
        attachment_file.reciever_attachment = request.FILES["reciever_email"]
        attachment_file.save()
        if Path(str(request.FILES['sender_email'])).suffix == '.csv':
            # df_sender = pd.read_csv(f'{url_link}{attachment_file.sender_attachment.url}') 
            df_sender = pd.read_csv(f'{request.scheme}://{str(get_current_site(request))}{attachment_file.sender_attachment.url}') 
        if Path(str(request.FILES['sender_email'])).suffix == '.xlsx':
            # df_sender = pd.read_excel(f'{url_link}{attachment_file.sender_attachment.url}',sheet_name='Sheet1', engine='openpyxl') 
            df_sender = pd.read_excel(f'{request.scheme}://{str(get_current_site(request))}{attachment_file.sender_attachment.url}',sheet_name='Sheet1', engine='openpyxl') 
        
        if Path(str(request.FILES['reciever_email'])).suffix == '.csv':
            df_reciever = pd.read_csv(f'{request.scheme}://{str(get_current_site(request))}{attachment_file.reciever_attachment.url}') 
            # df_reciever = pd.read_csv(f'{url_link}{attachment_file.reciever_attachment.url}') 
        if Path(str(request.FILES['reciever_email'])).suffix == '.xlsx':
            # df_reciever = pd.read_excel(f'{url_link}{attachment_file.reciever_attachment.url}',sheet_name='Sheet', engine='openpyxl') 
            df_reciever = pd.read_excel(f'{request.scheme}://{str(get_current_site(request))}{attachment_file.reciever_attachment.url}',sheet_name='Sheet', engine='openpyxl') 
        
        # sender_email = csv.DictReader(request.FILES['sender_email'].read().decode('utf-8').splitlines())
        # reciever_email = csv.DictReader(request.FILES['reciever_email'].read().decode('utf-8').splitlines())

        sender_email = []
        sender_password = []
        email_reciever = []
        sender_tracker = 0
        email_reciever_length = 1
        cache.set(cache_checker, 'Parsing Attachement...', 120)

        try:
            [ sender_email.append(df_sender['email'][i]) for i in range(0, df_sender.shape[0])]
            [ sender_password.append(df_sender['password'][i]) for i in range(0, df_sender.shape[0])]
            [ email_reciever.append(df_reciever['email'][i])  for i in range(0, df_reciever.shape[0])]
            attachment_file.delete()
        except:
            content = {
                'data': 'error',
                'message': f'Attachment files have missing data',
            }
            attachment_file.delete()
            return JsonResponse(content)
        if len(sender_email) != len(sender_password):
            content = {
                'data': 'error',
                'message': f'Sender files have missing data',
            }
            return JsonResponse(content)
        if len(email_reciever) > 1:
            cache.set(cache_checker, 'Sending Emails...', 120)
        else:    
            cache.set(cache_checker, 'Sending Email...', 120)
        for i, se in enumerate(email_reciever):
            if email_amount == 0:
                try:
                    current_email = Profile.objects.get(user=request.user)
                    current_email.email_amount = email_amount
                    current_email.save()
                    payment_history.receipt_status = 'Exhusted'
                    payment_history.last_email_amount = email_amount
                    payment_history.save()
                    content = {
                        'data': 'error',
                        'email_amount': email_amount,
                        'message': 'You have exhusted the your mail credit',
                    }
                    return JsonResponse(content)
                except Profile.DoesNotExist or PaymentHistory.DoesNotExist:
                    content = {
                        'data': 'error',
                        'message': 'Invalid Request',
                    }
                    return JsonResponse(content)
            if sender_tracker >= len(sender_email):
                sender_tracker = 0
            connection = get_connection(
                host='smtp.gmail.com',
                port=587,
                username=sender_email[sender_tracker],
                password=sender_password[sender_tracker], 
                use_tls=True) 
            # print(f"""
            # To: {se}
            # From: {sender_email[sender_tracker]}
            # Subject: {email_subject}
            # Body: {email_body}
            # """)

            try:
                # EmailMultiAlternatives(subject='', body='', from_email=None, to=None, bcc=None, connection=None, attachments=None, headers=None, alternatives=None, cc=None, reply_to=None)
                EmailMessage(email_subject, email_body, sender_email[sender_tracker], [se,], connection=connection).send(fail_silently=False)
                print('Email Sent')
                email_init = EmailSent(
                    user = request.user,
                    sender_email = sender_email[sender_tracker],
                    reciever_email = se,
                    subject = email_subject,
                    message = email_body,   
                    cache_checker = cache_checker   
                )
                email_init.save()
                print('Email Saved')
                cache.set(cache_checker, f'Email Left: {i+1} out of {len(email_reciever)}', 120)
                sleep(1) #Remove Delay in production
                email_init.delivery_status = True
                email_init.save()
                email_reciever_length = email_reciever_length + 1
                profile_email_count = profile_init.email_sent + 1
                profile_init.email_sent = profile_email_count
                profile_init.save()
                payment_history.last_email_amount = email_amount - 1
                payment_history.save()

            except BadHeaderError or AttributeError:
                content = {
                    'data': 'error',
                    'message': 'Invalid header found',
                }
                email_init.delete()
                return JsonResponse(content)
            sender_tracker = sender_tracker + 1
            email_amount = email_amount - 1
        EmailSentInti(
            email_init = email_init
        ).save()
        try:
            # profile_email_count = profile_init.email_sent + 1
            # profile_init.email_sent = profile_email_count
            profile_init.email_amount = email_amount
            profile_init.save()
            # payment_history = PaymentHistory.objects.get(customer_payment_reciept=current_email.last_payment_receipt)
            # payment_history.email_amount = email_amount
            # payment_history.save()
        except Profile.DoesNotExist:  #or PaymentHistory.DoesNotExist:
            content = {
                'data': 'error',
                'message': 'Invalid Request',
            }
            return JsonResponse(content)

        cache_variable = cache.get(cache_checker)
        str_code = f'{request.user}{datetime.now()}'
        cache_checker =hashlib.md5(str_code.encode()).hexdigest()
        content = {
            'data': 'success',
            'message': 'Done Sending',
            'cache_variable' : cache_variable,
            'cache_checker': cache_checker,
            'email_amount': email_amount
        }
        return JsonResponse(content)

    if request.method =='GET':
        email_amount = Profile.objects.get(user=request.user).email_amount
        str_code = f'{request.user}{datetime.now()}'
        cache_checker = hashlib.md5(str_code.encode()).hexdigest()
        ck = request.COOKIES.get('TTL_EV')
        # ck.delete()
        content = {
            'email_amount': email_amount,
            'cache_checker': cache_checker,
            'debug': settings.DEBUG,
            'nav_select': nav_select('active','','','',False, request.user.is_superuser)
        }     
        return render(request, 'email.html', content)


@csrf_exempt
@login_required
def track_progress(request):
    if request.method == 'POST' and request.is_ajax():
        cache_variable = request.POST['cache_variable']
        content = {
            'cache_variable' : cache.get(cache_variable)
        }
        return JsonResponse(content)



@login_required
def email_history(request):
    if request.method == 'GET':
        page = request.GET.get('page', 1)
        page_length = request.GET.get('page_length', 10)
        search = request.GET.get('search', '')
        request.session['history_length'] = 1

        request.session['history_length'] = page_length
        page_value = {}
        if len(search) > 0:
            post = EmailSentInti.objects.filter(email_init__user=request.user, email_init__subject__icontains=search).order_by("-created_on") | EmailSentInti.objects.filter(email_init__user=request.user, email_init__message__icontains=search).order_by("-created_on")
        else:
            post = EmailSentInti.objects.filter(email_init__user=request.user).order_by("-created_on")
        page_value['total'] = post.count()
        paginator = Paginator(post[:10], page_length)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        print(posts)
        if post.count() >= page_length:
            page_value['next_end'] = page_length
        else:
            page_value['next_end'] = post.count()
        qs = []
        for p in posts:
            sub_qs = {}
            valid_email = EmailSent.objects.filter(cache_checker=p.email_init.cache_checker, delivery_status=True)
            amount = human_format(valid_email.count())
            title = valid_email.first().subject
        
            sub_qs['title'] = title
            sub_qs['amount'] = amount
            qs.append(sub_qs)

        content = {
            # "page_lenght": request.session['history_length'],
            "total_mail": post.count(),
            "debug": settings.DEBUG,
            "posts": qs,
            "search_var": search,
            # "email_history": posts,
            "page_value": page_value,
            "nav_select": nav_select('','active','','', False, request.user.is_superuser)

        }
    return render(request, 'history.html', content)
    
@login_required
def get_more_history(request):
    if request.method == 'GET':
        data = request.GET.get('data',None)
        search = request.GET.get('search', '')
        page = request.GET.get('page_tracker_number',None)
        print(page)
        if data == 'x1x':
            page_length = 10
            search = request.GET.get('search', '')
            page_value = {}
            if len(search) > 0:
                post = EmailSentInti.objects.filter(email_init__user=request.user, email_init__subject__icontains=search).order_by("-created_on") | EmailSentInti.objects.filter(email_init__user=request.user, email_init__message__icontains=search).order_by("-created_on")
            else:
                post = EmailSentInti.objects.filter(email_init__user=request.user).order_by("-created_on")
            page_value['total'] = post.count()
            paginator = Paginator(post, 10)
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            qs = []
            print(posts)
            print(posts.number)
            if post.count() >= page_length:
                page_value['next_end'] = page_length
            else:
                page_value['next_end'] = post.count()
            print(page_value['next_end'])
            for p in posts:
                sub_qs = {}
                valid_email = EmailSent.objects.filter(cache_checker=p.email_init.cache_checker, delivery_status=True)
                amount = human_format(valid_email.count())
                title = valid_email.first().subject
            
                sub_qs['title'] = title
                sub_qs['amount'] = amount
                qs.append(sub_qs)
            request.session['history_length'] = request.session['history_length'] + 1
            data = json.dumps(qs)
            content = {
                "data": data,
                "page_value": page_value,
                "move_over": posts.has_next()

            }
            return JsonResponse(content)

def nav_select(email, history, settings, sub, show_sub, superuser):
    content = {
        'email' : email,
        'history' : history,
        'settings' : settings,
        'superuser' : superuser,
        'show_sub' : show_sub
    }
    return content

def human_format(num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '%i%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])
