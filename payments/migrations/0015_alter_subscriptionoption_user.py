# Generated by Django 3.2.4 on 2021-07-01 11:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('payments', '0014_rename_paymen_state_paymenthistory_paymen_completed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscriptionoption',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
    ]
