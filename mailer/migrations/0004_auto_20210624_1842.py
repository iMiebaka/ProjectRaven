# Generated by Django 3.2.4 on 2021-06-24 18:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0003_emailgsent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailsent',
            name='reciever_csv',
            field=models.CharField(max_length=70, null=True),
        ),
        migrations.AlterField(
            model_name='emailsent',
            name='sender_csv',
            field=models.CharField(max_length=70, null=True),
        ),
        migrations.DeleteModel(
            name='EmailgSent',
        ),
    ]