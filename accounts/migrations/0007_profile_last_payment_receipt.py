# Generated by Django 3.2.4 on 2021-07-01 19:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20210628_1936'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='last_payment_receipt',
            field=models.CharField(max_length=20, null=True),
        ),
    ]
