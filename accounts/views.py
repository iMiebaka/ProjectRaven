from django.contrib.auth import (login as auth_login,  authenticate, logout)
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.http import JsonResponse
import re
from datetime import datetime
from django.core.mail import EmailMessage, BadHeaderError, get_connection
from django.http import HttpResponse
import string
import hashlib
import time 
# from django.contrib.auth.forms import UserCreationForm
# from django.contrib.auth.forms import PasswordResetForm
# from django.template.loader import render_to_string
# from django.db.models.query_utils import Q
# from django.utils.http import urlsafe_base64_encode
# from django.contrib.auth.tokens import default_token_generator
# from django.utils.encoding import force_bytes
# from django.utils.encoding import force_text
# from django.urls import reverse_lazy
# from django.views.generic import View, UpdateView
# from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from .models import Profile
from django.conf import settings as settings_var # new
import pyotp
import json
import base64
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import ast
from decouple import config
from django.apps import apps
EmailSent = apps.get_model('mailer', 'EmailSent')
EmailSentInti = apps.get_model('mailer', 'EmailSentInti')
PaymentHistory = apps.get_model('payments', 'PaymentHistory')

# Create your views here.

EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL')

connection = get_connection(
        host=EMAIL_HOST,
        port=EMAIL_PORT,
        username=EMAIL_HOST_USER,
        password=EMAIL_HOST_PASSWORD, 
        use_tls=EMAIL_USE_TLS) 

def login_reverse(request):
    return redirect('accounts:login')


def login(request):
    if request.user.is_authenticated:
        messages.error(request,'Please logout first')
        return redirect('mailer:send_email')
    else:
        if request.method == 'GET':
            if request.COOKIES.get('auth') is None:
                remember_me = ''
            else:
                remember_me = ast.literal_eval(request.COOKIES.get('auth'))
            content = {
                "debug": settings_var.DEBUG,
                "bt_highlighte_signing": True,
                "remember_me": remember_me
            }
            corresponder = render(request, 'login.html', content)
            # corresponder.set_cookie('auth', {'user': 'mi','pass':'123'}, max_age=0)
            return corresponder

        if request.method == 'POST':
            email = request.POST['email'].strip()
            raw_password = request.POST['password'].strip()
            try:
                remember_me = request.POST['remember_me']
                corresponder = redirect('mailer:send_email')
                corresponder.set_cookie('auth', {'email': email,'pass': raw_password,'remember_me' : 'checked'})
                # print(remember_me = 'checked')
            except KeyError:
                remember_me = ''
                corresponder = redirect('mailer:send_email')
                corresponder.set_cookie('auth', None, max_age=0)
            
            try:
                username = User.objects.get(email__iexact=email).username
                # print(username)
                check_state = User.objects.get(email__iexact=email).is_active
                if check_state is False:
                    messages.error(request, 'User account in not activated')
                    return redirect('accounts:reset_account')

            except User.DoesNotExist:
                messages.error(request, 'Email account is not registered')
                content = {
                    "debug": settings_var.DEBUG,
                    "bt_highlighte_signing": True
                }
                return render(request, 'login.html', content)
            user = authenticate(username=username, password=raw_password)
            if user is not None:
                if user.is_active is False:
                    messages.error(request, 'User account in not activated')
                    return redirect('accounts:reset_account')
                else:
                    auth_login(request, user)
                    messages.success(request, "Logged in")
                    if remember_me == 'on':
                        request.session.set_expiry(0)
                    return corresponder
            else:
                messages.error(request, 'Invalid Password or account in not activated')
                return redirect('accounts:login')
        else:
            content = {
                "debug": settings_var.DEBUG,
                "bt_highlighte_signing": True
            }
            return render(request, 'login.html', content)
            


@login_required
def admin_settings(request):
    if request.method == 'GET':
        if request.user.is_superuser is False:
            return redirect('mailer:send_email')
        page = request.GET.get('page', 1)
        page_length = request.GET.get('page_length', 10)
        search = request.GET.get('search', '')
        page_value = {}
        print(page)
        print(search)
        if len(search) > 0:
            post = Profile.objects.filter(user__first_name__icontains=search) | Profile.objects.filter(user__last_name__icontains=search) | Profile.objects.filter(user__username__icontains=search)
            # post = [i.id for i in post]
            post = PaymentHistory.objects.filter(user__in=[i.id for i in post]).order_by('-created_on') 
        else:
            post = PaymentHistory.objects.all().order_by('-created_on') 

        page_value['total'] = post.count()
        print(post[:11].count())
        paginator = Paginator(post[:page_length], page_length)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        qs = []

        if post.count() >= page_length:
            page_value['next_end'] = page_length
        else:
            page_value['next_end'] = post.count()
        print(posts)
        for p in posts:
            sub_qs = {}
            complete_payment  = p.payment_completed
            cancelled_payment  = p.receipt_status
            email_sent = human_format(p.last_email_amount)

            sub_qs['name'] = f'{p.user.first_name} {p.user.last_name}'
            sub_qs['email_sent'] = email_sent
            sub_qs['image'] = p.user.profile.cover_image.url
            sub_qs['complete_payment'] = complete_payment
            sub_qs['payment_status'] = cancelled_payment
            sub_qs['last_payment_receipt'] = p.user.profile.last_payment_receipt
            sub_qs['sub_state'] = p.user.profile.subscribed
            qs.append(sub_qs)
        content = {
            "total_mail": EmailSentInti.objects.all().count(),
            "debug": settings_var.DEBUG,
            "search_var": search,
            "posts": qs,
            "email_history": posts,
            "page_value": page_value,
            "nav_select": nav_select('','','','', False, 'active',request.user.is_superuser)
        }
        return render(request, 'admin_settings.html', content)
    
def remove_sub_by_admin(request):
    if request.method == 'POST' and request.is_ajax():
        if request.user.is_superuser is False:
            return JsonResponse(None)
            # return redirect('mailer:send_email')

        receipt = request.POST['culprit']
        try:
            un_sub = Profile.objects.get(last_payment_receipt=receipt)
            un_sub.subscribed = False
            last_email_count = un_sub.email_amount
            un_sub.email_amount = 0
            un_sub.save()
            payment_history = PaymentHistory.objects.get(customer_payment_reciept=receipt)
            payment_history.receipt_status = 'Cancelled'
            payment_history.un_sub_hint = request.user
            payment_history.save()
        except Profile.DoesNotExist or PaymentHistory.DoesNotExist:
            return JsonResponse(None)
        content = {
            'message' : f'Receipt of {receipt} has been unsubscribed',
            'receipt' : f'{receipt}',
            'data': True 
        }
        return JsonResponse(content)


def human_format(num):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0
        return '%i%s' % (num, ['', 'K', 'M', 'B', 'T', 'P'][magnitude])


@login_required
def accounts(request):
    return redirect('accounts:login')
    # if request.method == 'POST':
    #     pass
    # if request.method == 'GET':
    #     content = {
    #         "debug": settings_var.DEBUG,
    #         "bt_highlighte_signing": True
    #     }
    # return render(request, 'accounts.html', content)


def signup(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        raw_password = request.POST['password'].strip()
        email_address = request.POST['email'].strip()
        instagram = request.POST['instagram'].strip()
        phone_number = request.POST['phone_number'].strip()
        if Profile.objects.filter(mobile__iexact=phone_number).exists():
            messages.error(request, "Phone Number Already taken")
            return redirect('accounts:signup')
        _available = User.objects.filter(username__iexact=username).exists() | User.objects.filter(email__iexact=email_address).exists() 
        if User.objects.filter(username__iexact=username).exists():
            messages.error(request, "Username is unavaliable")
            return redirect('accounts:signup')
        if User.objects.filter(email__iexact=email_address).exists():
            messages.error(request, "Email already is registered")
            return redirect('accounts:signup')
        if _available == False:
            try:
                user = User.objects.create_user(
                    username, 
                    email_address,
                    raw_password
                )
                user.first_name = first_name
                user.last_name = last_name
                user.is_active = False
                user.save()
                add_number = Profile.objects.get(user=user)
                add_number.phone_number = phone_number
                add_number.instagram = instagram
                add_number.save()
            except:
                messages.success(request, 'Sign up cannot finish at the moment')
                return redirect('accounts:signup')

            rt_valu = str(email_address) + str(datetime.date(datetime.now())) + 'some-secret'
            try:
                key = base64.b32encode(rt_valu.encode())  # Key is generated
                OTP = pyotp.HOTP(key)  # HOTP Model for OTP is created
                messages.success(request, 'OTP has been sent to your modile device')
            except:
                messages.success(request, 'Could not generate otp')
                return redirect('accounts:signup')


            subject = 'Activate Your Emailing Account'
            email = f""" Hi {user.first_name}
Thank you for signing up
Activate your account 
Your otp is {OTP.at(add_number.counter)}
Please do not share wih anyone
            """
            try:
                EmailMessage(subject, email, EMAIL_HOST_USER, [email_address,], connection=connection).send(fail_silently=False)
                # send_mail(subject, email, settings_var.EMAIL_HOST_USER, [email_address,], fail_silently=False)
                messages.success(request, ('Please Confirm your email to complete registration.'))
                corespondent = redirect("accounts:verify_account")
                request.session['temp_data'] = email_address
                corespondent.set_cookie('TTL_EV', email_address , max_age=200)
                return corespondent

            except BadHeaderError or AttributeError:
                return HttpResponse('Invalid header found.')
            # auth_login(request, user)
            # messages.success(request, "Your account has been successfully created")
    if request.method == 'GET':
        content = {
            'site_view': 'Sign Up / Login',
            "debug": settings_var.DEBUG
        }
        return render(request, 'signup.html', content)

def reset_account_two(request):
    if request.method == 'POST':
        anon_value = request.POST['anon_value'].strip()

        if anon_value == '2':
            reset_account = request.COOKIES.get('TTL_EV')
            email = request.COOKIES.get('TTL_EM')
            if reset_account != 'reset_account':
                return HttpResponseRedirect("/")
            otp_value = request.POST['otp_value'].strip()
            password = request.POST['password'].strip()
            try:
                user = User.objects.get(email__iexact=email)
                profile = Profile.objects.get(user=user, otp_mobile=otp_value)
                profile.otp_mobile = None
                profile.save()
                user.set_password(password)
                user.is_active = True
                user.save()
                return redirect('accounts:login')
            except:
                messages.error(request,('OTP was timed out'))
                content = {
                    "debug": settings_var.DEBUG
                }
                return redirect('reset_account', content)

    if request.method == 'GET':
        content = {
            "debug": settings_var.DEBUG
        }
        return render(request, 'reset_account_copy.html', content)

def reset_account(request):
    if request.method == 'POST':
        anon_value = request.POST['anon_value'].strip()
        if anon_value == '1':
            email_address = request.POST['email'].strip()
            try:
                user = User.objects.get(email__iexact=email_address)
                email_address = user.email
                add_number = Profile.objects.get(user=user)
            except:
                messages.error(request, "Email is not registered")
                content = {
                    "debug": settings_var.DEBUG
                }
                return redirect('accounts:reset_account')
            rt_valu = str(email_address) + str(datetime.date(datetime.now())) + 'some-secret'
            try:
                key = base64.b32encode(rt_valu.encode())  # Key is generated
                OTP = pyotp.HOTP(key)  # HOTP Model for OTP is created
            except:
                messages.success(request, 'Sign up cannot finish at the moment')
                return redirect('accounts:reset_account')

            subject = 'Resetting Your Account'
            email = f"""Hi {user.first_name}
Need to reset your password? 
Use your secret code!

Your otp is {OTP.at(add_number.counter)}

Please do not share wih anyone
If you did not forget your password, you can ignore this email.
                    """
            try:
                EmailMessage(subject, email, EMAIL_HOST_USER, [email_address,], connection=connection).send(fail_silently=False)
                messages.success(request, ('Please Confirm your email to complete registration.'))
                add_number.otp_mobile = OTP.at(add_number.counter)
                add_number.save()
                content = {
                    "debug": settings_var.DEBUG
                }
                messages.success(request, 'OTP has been sent to your email')
                corespondent = redirect('accounts:reset_account_two')
                request.session['temp_data'] = email_address
                corespondent.set_cookie('TTL_EV', 'reset_account' , max_age=7200)
                corespondent.set_cookie('TTL_EM', email_address , max_age=7200)
                return corespondent
            except BadHeaderError:
                messages.error(request,('Invalid header found.'))
                content = {
                    "debug": settings_var.DEBUG
                }
                return redirect('accounts:reset_account')

        if anon_value == '2':
            reset_account = request.COOKIES.get('TTL_EV')
            email = request.COOKIES.get('TTL_EM')
            if email is None:
                messages.error(request,('OTP was timed out'))
                content = {
                    "debug": settings_var.DEBUG
                }
                return redirect('accounts:reset_account')
            if reset_account != 'reset_account':
                return HttpResponseRedirect("/")
            otp_value = request.POST['otp_value'].strip()
            password = request.POST['password'].strip()
            try:
                user = User.objects.get(email__iexact=email)
                profile = Profile.objects.get(user=user, otp_mobile=otp_value)
                profile.otp_mobile = None
                profile.save()
                user.set_password(password)
                user.is_active = True
                user.save()
                return redirect('accounts:login')
            except:
                messages.error(request,('OTP was timed out'))
                content = {
                    "debug": settings_var.DEBUG
                }
                return redirect('accounts:reset_account')

    if request.method == 'GET':
        content = {
            "debug": settings_var.DEBUG
        }
        return render(request, 'reset_account.html', content)

@login_required
def get_more_history(request):
    if request.method == 'GET':
        if request.user.is_superuser is False:
            return JsonResponse(None)

        data = request.GET.get('data',None)
        search = request.GET.get('search', '')
        page = request.GET.get('page_tracker_number',None)
        if data == 'x1x':
            if request.user.is_superuser is False:
                return redirect('mailer:send_email')
            page = request.GET.get('page', 1)
            page_length = 10
            search = request.GET.get('search', '')
            page_value = {}
            if len(search) > 0:
                post = Profile.objects.filter(user__first_name__icontains=search) | Profile.objects.filter(user__last_name__icontains=search) | Profile.objects.filter(user__username__icontains=search)
                # post = [i.id for i in post]
                post = PaymentHistory.objects.filter(user__in=[i.id for i in post]).order_by('-created_on') 
            else:
                post = PaymentHistory.objects.all().order_by('-created_on') 

            page_value['total'] = post.count()
            paginator = Paginator(post[:page_length], page_length)
            try:
                posts = paginator.page(page)
            except PageNotAnInteger:
                posts = paginator.page(1)
            except EmptyPage:
                posts = paginator.page(paginator.num_pages)
            qs = []

            if post.count() >= page_length:
                page_value['next_end'] = page_length
            else:
                page_value['next_end'] = post.count()
            print(posts)
            for p in posts:
                sub_qs = {}
                complete_payment  = p.payment_completed
                cancelled_payment  = p.receipt_status
                email_sent = human_format(p.last_email_amount)

                sub_qs['name'] = f'{p.user.first_name} {p.user.last_name}'
                sub_qs['email_sent'] = email_sent
                sub_qs['image'] = p.user.profile.cover_image.url
                sub_qs['complete_payment'] = complete_payment
                sub_qs['payment_status'] = cancelled_payment
                sub_qs['last_payment_receipt'] = p.user.profile.last_payment_receipt
                sub_qs['sub_state'] = p.user.profile.subscribed
                qs.append(sub_qs)
            data = json.dumps(qs)
            # print(data)
            content = {
                "data": data,
                "page_value": page_value,
                "move_over": posts.has_next()

            }
            return JsonResponse(content)


def logout_view(request):
    if request.user.is_authenticated:
        logout(request)
        messages.success(request, "Logged out")
        return redirect('accounts:login')
    else:
        return HttpResponseRedirect("/")

@login_required
def settings(request):
    if request.method == 'POST':
        username = request.POST['username'].strip()
        first_name = request.POST['first_name'].strip()
        last_name = request.POST['last_name'].strip()
        # cover_image = request.FILES['cover_image']
        phone_number = request.POST['phone_number'].strip()
        email_address = request.POST['email'].strip()
        instagram = request.POST['instagram'].strip()
        user = request.user
        user.username = username
        user.first_name = first_name
        user.last_name = last_name
        user.email = email_address

        profile = Profile.objects.get(user=user)
        profile.instagram = instagram
        profile.phone_number = phone_number
        # if cover_image != None:
        #     profile.cover_image = cover_image
        user.save()
        profile.save()
        messages.success(request, 'Profile Updated')
        return redirect('accounts:settings')
    if request.method == 'GET':
        history = PaymentHistory.objects.filter(user=request.user)
        content = {
            "payment_history": history,
            "debug": settings_var.DEBUG,
            "nav_select": nav_select('','','active','',True,'', request.user.is_superuser)
        }
        return render(request, 'settings.html', content)

def nav_select(email, history, settings, sub, show_sub, admin, superuser):
    content = {
        'email' : email,
        'history' : history,
        'settings' : settings,
        'sub' : sub,
        'show_sub' : show_sub,
        'admin' : admin,
        'superuser' : superuser,
    }
    return content

def settings_reverse(request):
    if request.method == 'GET':
        return redirect('accounts:settings')


def verify_account(request):
    if request.method == 'POST':
        email_address = request.COOKIES.get('TTL_EV')
        # print(request.session['temp_data'])
        if email_address is None:
            messages.error(request, 'OTP is expired')
            return redirect("accounts:reset_account")

        otp = request.POST['text_otp'].strip()
        try:
            user = User.objects.get(email=email_address)
        except User.DoesNotExist:
            messages.error(request, "User does not exist")  # False Call
            return render(request, 'verify.html')
        rt_valu = str(email_address) + str(datetime.date(datetime.now())) + 'some-secret'
        key = base64.b32encode(rt_valu.encode())  # Generating Key
        OTP = pyotp.HOTP(key)  # HOTP Model
        profile = Profile.objects.get(user=user)
        if profile.isVerified:
            messages.error(request, 'OTP is expired')
            corespondent = redirect("accounts:reset_account")
            corespondent.set_cookie('TTL_EV', email_address , max_age=7200)
            return corespondent

        if OTP.verify(otp, profile.counter):  # Verifying the OTP
            profile.isVerified = True
            profile.save()
            user = User.objects.get(email=email_address)
            user.is_active = True
            user.save()
            auth_login(request, user)
            messages.success(request,'Registration Complete')
            return redirect('payments:subscription')
    if request.method == 'GET':
        return render (request, 'verify_email.html')

def resend_otp(request):
    if request.method == 'POST':
        subject = 'Activate Your Emailing Account'
        email_address = request.COOKIES.get('TTL_EV')
        rt_valu = str(email_address) + str(datetime.date(datetime.now())) + 'some-secret'
        try:
            key = base64.b32encode(rt_valu.encode())  # Key is generated
            OTP = pyotp.HOTP(key)  # HOTP Model for OTP is created
            add_number = Profile.objects.get(user=User.objects.get(email=email_address))
        except:
            messages.error(request, 'Could not create otp')
            return render (request, 'verify_email.html')

        email = f"""Thank you for signing up
            Activate your account 
            Your otp is {OTP.at(add_number.counter)}
            Please do not share wih anyone
        """
        try:
            EmailMessage(subject, email, EMAIL_HOST_USER, [email_address,], connection=connection).send(fail_silently=False)
            # send_mail(subject, email, 'admin@example.com' , email_address, fail_silently=False)
            messages.success(request, ('Please Confirm your email to complete registration.'))
            corespondent = redirect("accounts:verify_account")
            corespondent.set_cookie('TTL_EV', email_address , max_age=7200)
            return corespondent

        except BadHeaderError:
            return HttpResponse('Invalid header found.')

    return redirect("accounts:verify_account")


def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def password_strenght(request):
    ajax_request = False
    message = ''
    if request.method == 'POST' and request.is_ajax:
        password = request.POST.get('password')
        if bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&]).{8,30})', password)) == True:
            message = 'Password Strength 5/5'
            ajax_request = True
        if bool(re.match('((\d*)([a-z]*)([A-Z]*).{8,30})', password)) == True:
            message = 'Password Strength 4/5'
            ajax_request = True
        if bool(re.match('((\d*)([a-z]*).{8,30})', password)) == True:
            message = 'Password Strength 3/5'
            ajax_request = True
        if bool(re.match('(([a-z]*).{8,30})', password)) == True:
            message = 'Password Strength 2/5'
            ajax_request = True
        if bool(re.match('(.{8,30})', password)) == True:
            message = 'Password Strength 2/5'
            ajax_request = True
        if bool(re.match('(([a-z]*)', password)) == True:
            message = 'Password Strength 1/5'
            ajax_request = True
    data = {
        'message' : message,
        'ajax_request': ajax_request
    }
    return JsonResponse(data)

def validate_username_signup(request):
    username = request.GET.get('username', None)
    data = {
        'user_is_taken': User.objects.filter(username__iexact=username).exists()
    }
    return JsonResponse(data)

def validate_email_signup(request):
    email = request.GET.get('email', None)
    data = {
        'email_is_taken': User.objects.filter(email__iexact=email).exists()
    }
    return JsonResponse(data)

def error_404(request, exception):
        data = {}
        return render(request,'error/404.html', data)

def error_500(request):
        data = {}
        return render(request,'error/500.html', data)

def error_400(request, exception):
        data = {}
        return render(request,'error/404.html', data)

def error_403(request,  exception):
        data = {}
        return render(request,'error/500.html', data)
