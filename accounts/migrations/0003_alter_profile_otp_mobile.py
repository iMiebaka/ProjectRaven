# Generated by Django 3.2.4 on 2021-06-25 10:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_alter_profile_about'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='otp_mobile',
            field=models.IntegerField(null=True),
        ),
    ]
