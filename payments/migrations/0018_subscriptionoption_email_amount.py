# Generated by Django 3.2.4 on 2021-07-01 20:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0017_auto_20210701_2025'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionoption',
            name='email_amount',
            field=models.PositiveSmallIntegerField(default=0, null=True),
        ),
    ]
