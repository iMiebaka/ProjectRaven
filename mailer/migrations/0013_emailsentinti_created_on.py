# Generated by Django 3.2.4 on 2021-06-28 12:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0012_emailsentinti'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailsentinti',
            name='created_on',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
    ]
