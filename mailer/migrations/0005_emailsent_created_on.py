# Generated by Django 3.2.4 on 2021-06-24 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0004_auto_20210624_1842'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailsent',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]