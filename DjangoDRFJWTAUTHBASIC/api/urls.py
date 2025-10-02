from django.urls import path
from .views import *

urlpatterns = [
    path("signup/", SignupView.as_view()),
    path("verify/<str:username>/", Verify_Email_Signup.as_view()),
    path("login/", LoginView.as_view()),
    path("changepassword/", ChangePassword.as_view(),),
    path("forgetpassword/", FogetPasswordView.as_view(),),
    path("vefiry_for_forget/<str:username>/", Verify_User_ForgetPassword.as_view()),
    path('google/', GoogleLoginView.as_view(),)

]
