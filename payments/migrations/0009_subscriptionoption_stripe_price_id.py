# Generated by Django 3.2.4 on 2021-06-29 13:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0008_paymenthistory_sub_option'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionoption',
            name='stripe_price_id',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
