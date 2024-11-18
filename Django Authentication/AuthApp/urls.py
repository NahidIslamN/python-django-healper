

from django.urls import path
from AuthApp.views import *



urlpatterns = [
    path('signin/', LoginViews.as_view(), name='signin'),
    path('signout/', LogoutViews.as_view(), name='signout'),
    path('signup/',SignUP.as_view(), name='signup'),
    path('profile/', ViewMyProfile.as_view(), name='profile'),
    path('forget-account/', generate_and_send_otp, name='forget-account'),
    path('verify-otp/<email>/',verify_otp, name="verify-otp"),

    path('email_varification/',SentOtp.as_view(), name='email_varification'),
    path('verify-email/<email>/', verify_email, name='verify-email'),
    path('admin-users/',AllUsers.as_view()),
    
    
]



