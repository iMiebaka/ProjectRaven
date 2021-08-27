from django.contrib import admin
from .models import EmailSent, EmailSentInti
# Register your models here.

class EmailSentAdmin(admin.ModelAdmin):
    list_display = ('cache_checker','user','sender_email','reciever_email', 'created_on',)
    search_fields = ('cache_checker','user','sender_email','reciever_email',)

class EmailSentInitiAdmin(admin.ModelAdmin):
    list_display = ('email_init','sender','cache_name','created_on',)
    search_fields = ('email_init','sender','cache_name',)


admin.site.register(EmailSent,EmailSentAdmin)
admin.site.register(EmailSentInti,EmailSentInitiAdmin)