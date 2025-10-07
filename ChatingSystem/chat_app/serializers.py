from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import *

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username','first_name','last_name', 'image', 'last_activity']

class ChatListSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Chat
        fields = ['id', 'chat_type', 'name', 'participants']


class Message_List_Serializer(serializers.ModelSerializer):
    sender = UserSerializer()
    seen_users = UserSerializer(many=True)
    class Meta:
        model = Message
        exclude = ["chat"]
        depth = 1
