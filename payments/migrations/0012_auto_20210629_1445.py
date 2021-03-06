# Generated by Django 3.2.4 on 2021-06-29 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0011_alter_subscriptionoption_stripe_price_code'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymenthistory',
            name='paymen_state',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='payment_desc',
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='payment_platform',
            field=models.CharField(max_length=10, null=True),
        ),
        migrations.AddField(
            model_name='paymenthistory',
            name='payment_reciept',
            field=models.CharField(max_length=40, null=True),
        ),
    ]
