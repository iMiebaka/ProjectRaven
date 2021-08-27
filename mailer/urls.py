from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

app_name = 'mailer'
urlpatterns = [
    path("", views.send_email, name="send_email"),
    path("email-history", views.email_history, name="email_history"),
    path("ajax/get-more-email-history", views.get_more_history, name="get_more_history"),
    path("track-emailupload-progress", views.track_progress, name="track_progress"),
]


#handler404 = f'{app_name}.views.error_404'
#handler500 = f'{app_name}.views.error_500'
#handler403 = f'{app_name}.views.error_403'
#handler400 = f'{app_name}.views.error_400'
