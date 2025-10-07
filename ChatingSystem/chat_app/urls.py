from django.urls import path
from .views import *

urlpatterns = [
    path('', Chatlists.as_view()),
    path('message/<int:pk>/', MessageList_Chats.as_view())

]
