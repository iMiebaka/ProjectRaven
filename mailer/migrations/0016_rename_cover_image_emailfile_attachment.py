# Generated by Django 3.2.4 on 2021-07-01 11:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mailer', '0015_emailfile'),
    ]

    operations = [
        migrations.RenameField(
            model_name='emailfile',
            old_name='cover_image',
            new_name='attachment',
        ),
    ]
