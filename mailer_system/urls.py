from time import sleep
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.storage import staticfiles_storage
from time import sleep
import threading

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('mailer.urls')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    # path('paypal/', include('paypal.standard.ipn.urls')),
]

# if settings.DEBUG:
urlpatterns += static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT) 

def greet_them():
    for i in range(10000):
        print(i)
        sleep(1)

# threading.Thread(target=greet_them,).start()


#handler404 = 'payments.views.error_404'
#handler404 = 'accounts.views.error_404'
#handler404 = 'mailer.views.error_404'

