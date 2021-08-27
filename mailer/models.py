from django.db import models
from django.db.models.fields import DateField
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
import hashlib, os
# Create your models here.


def file_for_email(self, filename):
    filename, ext = os.path.splitext(filename.lower())
    filename = "%s.%s" %(filename, timezone.now())
    filename = hashlib.md5(filename.encode()).hexdigest()
    return "%s/%s%s" %(settings.UPLOAD_PATH_DOC_FILE, filename, ext)

class EmailSent(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    sender_email = models.CharField(max_length=30, null=True)
    reciever_email = models.CharField(max_length=30, null=True)
    subject = models.CharField(max_length=70, null=False)
    message = models.CharField(max_length=1000, null=False)
    delivery_status = models.BooleanField(default=False)
    delivery_status_read = models.BooleanField(default=False)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    cache_checker = models.CharField(max_length=20, null=True)


class EmailFile(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    sender_attachment = models.FileField(null=True, upload_to=file_for_email)
    reciever_attachment = models.FileField(null=True, upload_to=file_for_email)
    cache_checker = models.CharField(max_length=20, null=True)


class EmailSentInti(models.Model):
    email_init = models.OneToOneField('EmailSent', on_delete=models.CASCADE)
    created_on = models.DateTimeField(auto_now_add=True, null=True)
    
    def sender(self):
        return self.email_init.user
    
    def cache_name(self):
        return self.email_init.cache_checker