from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
import hashlib
from .select_options import COUNTRY
import os
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

def generate_media_path_private_profile_image(self, filename):
    filename, ext = os.path.splitext(filename.lower())
    filename = "%s.%s" %(filename, timezone.now())
    filename = hashlib.md5(filename.encode()).hexdigest()
    return "%s/%s" %(settings.UPLOAD_PATH_PROFILE_IMAGE, filename)


class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, null=True, on_delete=models.CASCADE)
    email_confirmed = models.BooleanField(default=False)
    mobile = models.CharField(max_length=15, null=True)
    about = models.TextField(max_length=200, default='')
    instagram = models.CharField(max_length=20 , null=True, blank=True)
    last_payment_receipt = models.CharField(max_length=20 , null=True)
    cover_image = models.ImageField(default='default_image.jpg', null=True, upload_to=generate_media_path_private_profile_image)
    isVerified = models.BooleanField(null=True, default=False)
    otp_mobile = models.IntegerField(null=True)
    subscribed = models.BooleanField(default=False)
    counter = models.IntegerField(default=0, null=True)   # For HOTP Verification
    last_sub = models.DateTimeField(null=True)
    email_amount = models.PositiveSmallIntegerField(default=0, null=True)
    email_sent = models.PositiveSmallIntegerField(default=0, null=True)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
