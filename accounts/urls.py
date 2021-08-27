from django.urls import path, include
from django.contrib.auth import views as auth_views
# from django.conf.urls import handler404, handler500, handler403, handler400
from . import views

app_name = 'accounts'
urlpatterns = [
    path("", views.accounts, name="accounts"),
    path("signup", views.signup, name="signup"),
    path("signup/", views.signup, name="signup"),
    path("settings", views.settings_reverse, name="settings_reverse"),
    path("settings/", views.settings, name="settings"),
    path("super/settings", views.admin_settings, name="admin_settings"),
    path("super/settings/ajax/get-more-email-history", views.get_more_history, name="get_more_history"),
    path("super/settings/remove-sub", views.remove_sub_by_admin, name="remove_sub_by_admin"),
    path("reset-account/", views.reset_account, name="reset_account"),
    path("reset-account-change-password/", views.reset_account_two, name="reset_account_two"),
    path("login/", views.login, name="login"),
    path("login", views.login_reverse, name="login_reverse"),
    path("logout", views.logout_view, name="logout_view"),    
    path("logout/", views.logout_view, name="logout_view"),    
    path('ajax/validate_username/', views.validate_username, name='validate_username'),
    path('ajax/password_strenght/', views.password_strenght, name='password_strenght'),
    path('ajax/validate_username_signup/', views.validate_username_signup, name='validate_username_signup'),
    path('ajax/validate_email_signup/', views.validate_email_signup, name='validate_email_signup'),
    path("verify_account", views.verify_account, name="verify_account"),
    path("resend-otp", views.resend_otp, name="resend_otp"),
]

# handler404 = f'{app_name}.views.error_404'
# handler500 = f'{app_name}.views.error_500'
# handler403 = f'{app_name}.views.error_403'
# handler400 = f'{app_name}.views.error_400'
