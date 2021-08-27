from datetime import datetime
from re import sub
from time import timezone
from django.conf import settings
from django.contrib.auth.decorators import login_required # new
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt # new
from django.shortcuts import redirect, render, get_list_or_404, reverse
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.models import User
from django.contrib import messages
from django.urls import resolve
from datetime import datetime
import stripe
import hashlib
from decouple import config
import json
from .models import ActiveAccount, SubscriptionOption, PaymentHistory
from django.apps import apps
Profile = apps.get_model('accounts', 'Profile')


@login_required
def complete_paypal(request):
    if request.is_ajax and request.method == 'POST':
        details_val = json.loads(request.body.decode('utf-8'))['details_val']
        purchase_option = json.loads(request.body.decode('utf-8'))['sub_type']
        char_val = f'{details_val}{datetime.now()}'
        customer_payment_reciept = hashlib.md5(char_val.encode()).hexdigest()
        try:
            sub_inti = SubscriptionOption.objects.get(id=purchase_option)
        except:
            return JsonResponse({'err': 'Something went wrong'},status=500)
        details_val = json.loads(details_val)
        print(details_val)
        try:
            if sub_inti.cost != details_val['purchase_units'][0]['amount']['value']:
                print('Invalid Request')
                return JsonResponse({'err': 'Something went wrong'},status=500)
        except:
            return JsonResponse({'err': 'Something went wrong'},status=500)
            
        activate = PaymentHistory.objects.create(
            user = request.user,
            payment_completed = True,
            receipt_status = 'Completed',
            payment_platform_name = 'PayPal',
            sub_option = sub_inti
        )
        activate.payment_platform_reciept = details_val['id']
        activate.payment_platform_desc = details_val['purchase_units'][0]['reference_id']
        activate.email_amount = sub_inti.email_amount
        char_val = f'{activate.user}{activate}{datetime.now()}'
        customer_payment_reciept = hashlib.md5(char_val.encode()).hexdigest()
        activate.customer_payment_reciept = customer_payment_reciept
        activate.save()

        #Update User model
        profile = Profile.objects.get(user=activate.user)
        profile.subscribed = True
        profile.email_amount = activate.email_amount
        profile.last_payment_receipt = activate.customer_payment_reciept
        profile.last_sub = datetime.now()
        profile.save()
        print("Payment was successful.")
        # TODO: run some custom code here
        content = {
            'message': 'Payment Completed'
        }
        return JsonResponse(content, status=200)


@login_required
def subscription(request):
    # print(request.path_info)
    current_payment_name, current_payment_id,  sub_id, sub_amount = activation_check(request.user)
    data = """
 {"id": "5O190127TN364715T",
  "status": "PAYER_ACTION_REQUIRED",
  "intent": "CAPTURE",
  "payment_source": {
    "alipay": {
      "name": "John Doe",
      "country_code": "C2"
    }
  },
  "purchase_units": [
    {
      "reference_id": "d9f80740-38f0-11e8-b467-0ed5f89f718b",
      "amount": {
        "currency_code": "USD",
        "value": "100.00"
      },
      "payee": {
        "email_address": "payee@example.com"
      }
    }
  ],
  "create_time": "2018-04-01T21:18:49Z",
  "links": [
    {
      "href": "https://www.paypal.com/payment/alipay?token=5O190127TN364715T",
      "rel": "payer-action",
      "method": "GET"
    },
    {
      "href": "https://api-m.paypal.com/v2/checkout/orders/5O190127TN364715T",
      "rel": "self",
      "method": "GET"
    }
  ]}
"""
    content = {
        "nav_select": nav_select('','','','active', True, request.user.is_superuser),
        "debug": settings.DEBUG,
        "current_payment_name": current_payment_name,
        "payment_id": sub_id,
        "payment_amount": sub_amount,
        "PAYPAL_CLIENT_ID": config('PAYPAL_CLIENT_ID'),
        "current_payment_id": current_payment_id
    }
    print(config('PAYPAL_CLIENT_ID'))
    return render(request, 'subscription.html', content)


def activation_check(user):
    sub_id = Profile.objects.get(user=user)
    try:
        if sub_id.email_amount < 1 or sub_id.subscribed is False:
            current_sub_id = None
            current_sub_name = None
        else:
            current_sub = PaymentHistory.objects.get(customer_payment_reciept=sub_id.last_payment_receipt)
            current_sub_name = current_sub.sub_option.name
            current_sub_id = current_sub.id
    except PaymentHistory.DoesNotExist:
        current_sub_id = None
        current_sub_name = None
    sub_list_option = SubscriptionOption.objects.all()
    sub_name = {}
    sub_amount = {}
    sub_id = {}
    for sl in sub_list_option:
        sub_name[sl.name] = current_sub_name == sl.name
        sub_id[sl.name] = sl.id
        sub_amount[sl.name] = sl.cost

    return sub_name, current_sub_id, sub_id, sub_amount

@login_required
def delay_payment(request):
    profile = Profile.objects.get(user=request.user)
    profile.subscribed = True
    profile.customer_payment_reciept = 'Trial Version'
    profile.save()
    return redirect('mailer:send_email')

@login_required
def cancel_subscription(request):
    if request.method == 'POST':
        # id_val = request.POST['id_val']    
        # print(id_val)    
        try:
            profile = Profile.objects.get(user=request.user)
            active_ac = PaymentHistory.objects.get(customer_payment_reciept=profile.last_payment_receipt)
            active_ac.receipt_status = 'Cancelled'
            profile.email_amount = 0
            profile.un_sub_hint = request.user
            profile.subscribed = False
            active_ac.save()
            profile.save()
            messages.success(request, 'You unsubscription is was successful')
        except PaymentHistory.DoesNotExist:
            messages.error(request, 'No subscription found')
        return redirect('payments:subscription')


def nav_select(email, history, settings, sub, show_sub, superuser):
    content = {
        'email' : email,
        'history' : history,
        'settings' : settings,
        'sub' : sub,
        'superuser' : superuser,
        'show_sub' : show_sub

    }
    return content

def HomePageView(request):
    return render(request, 'home.html', {})

def SuccessView(request):
    return render(request, 'success.html')

def CancelledView(request):
    return render(request, 'cancelled.html')


@login_required
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)

# @csrf_exempt
@login_required
def create_checkout_session(request):
    if request.method == 'POST':
        try:
            plan = Profile.objects.get(user=request.user)
            if plan.subscribed:
                return JsonResponse({'error': str(f'You already have a subscription plan')})
        except PaymentHistory.DoesNotExist:
            pass
        # data = f'{request.user}{datetime.now()}'
        # reciept = hashlib.md5(data.encode()).hexdigest()
        domain_url = f'{request.scheme}://{get_current_site(request)}/payments/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        stripe.Product.retrieve(settings.PRODUCT_TAG)
        pay_id = json.loads(request.body.decode("utf-8"))['purchase_option']
        sub_option = SubscriptionOption.objects.get(id=pay_id)
        price_tag = sub_option.stripe_price_code
        try:
            # Create new Checkout Session for the order
            # Other optional params include:
            # [billing_address_collection] - to display billing address details on the page
            # [customer] - if you have an existing Stripe Customer ID
            # [payment_intent_data] - capture the payment later
            # [customer_email] - prefill the email input in the form
            # For full details see https://stripe.com/docs/api/checkout/sessions/create

            # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=[
                    {
                        'price': price_tag,
                        'quantity': 1,
                    }
                ],
            )
            
            PaymentHistory.objects.create(
                user = request.user,
                # cost = sub_option.cost,
                # name = sub_option.name,
                sub_option = sub_option,
                payment_platform_name = 'Stripe',
                payment_platform_reciept = checkout_session['payment_intent'],
                payment_platform_desc = checkout_session['id'],
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            print(str(e))
            return JsonResponse({'error': str(e)})

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    stripe.Product.retrieve(settings.PRODUCT_TAG)
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # if event['type'] == 'checkout.session.cancelled':
    #     activation = PaymentHistory.objects.get(payment_reciept=event['data']['object']['payment_intent'], payment_desc=event['data']['object']['id'])
    #     activation.delete()

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        activation = PaymentHistory.objects.get(payment_platform_reciept=event['data']['object']['payment_intent'], payment_platform_desc=event['data']['object']['id'])
        activation.payment_completed = True
        activation.receipt_status = 'Completed'
        activation.email_amount = activation.sub_option.email_amount
        char_val = f'{activation.user}{activation}{datetime.now()}'
        customer_payment_reciept = hashlib.md5(char_val.encode()).hexdigest()
        activation.customer_payment_reciept = customer_payment_reciept
        activation.save()

        #Update User model
        profile = Profile.objects.get(user=activation.user)
        profile.subscribed = True
        profile.email_amount = activation.sub_option.email_amount
        profile.last_payment_receipt = activation.customer_payment_reciept
        profile.last_sub = datetime.now()
        profile.save()
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)

def error_404(request, exception):
    return render(request, "error/404.html")

def error_400(request, exception):
    return render(request, "error/400.html")

def error_500(request):
    return render(request, "error/500.html")

def error_403(request, exception):
    return render(request, "error/403.html")



# def process_payment(request):
#     order_id = request.session.get('order_id')
#     order = get_object_or_404(Order, id=order_id)
#     host = request.get_host()

#     paypal_dict = {
#         'business': settings.PAYPAL_RECEIVER_EMAIL,
#         'amount': '%.2f' % order.total_cost().quantize(
#             Decimal('.01')),
#         'item_name': 'Order {}'.format(order.id),
#         'invoice': str(order.id),
#         'currency_code': 'USD',
#         'notify_url': 'http://{}{}'.format(host,
#                                            reverse('paypal-ipn')),
#         'return_url': 'http://{}{}'.format(host,
#                                            reverse('payment_done')),
#         'cancel_return': 'http://{}{}'.format(host,
#                                               reverse('payment_cancelled')),
#     }

#     form = PayPalPaymentsForm(initial=paypal_dict)
#     return render(request, 'ecommerce_app/process_payment.html', {'order': order, 'form': form})

# def process_payment(request):
#     order_id = request.session.get('order_id')
#     order = get_object_or_404(Order, id=order_id)
#     host = request.get_host()

#     paypal_dict = {
#         'business': settings.PAYPAL_RECEIVER_EMAIL,
#         'amount': '%.2f' % order.total_cost().quantize(
#             Decimal('.01')),
#         'item_name': 'Order {}'.format(order.id),
#         'invoice': str(order.id),
#         'currency_code': 'USD',
#         'custom': 'a custom value',
#         'notify_url': 'http://{}{}'.format(host, reverse('paypal-ipn')),
#         'return_url': 'http://{}{}'.format(host, reverse('payment_done')),
#         'cancel_return': 'http://{}{}'.format(host, reverse('payment_cancelled')),
#     }

#     form = PayPalPaymentsForm(initial=paypal_dict)
#     return render(request, 'cart/process_payment.html', {'order': order, 'form': form})

# @csrf_exempt
# def payment_done(request):
#     return render(request, 'ecommerce_app/payment_done.html')


# @csrf_exempt
# def payment_canceled(request):
#     return render(request, 'ecommerce_app/payment_cancelled.html')
