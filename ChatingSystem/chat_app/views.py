from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import *
from .serializers import *




class Chatlists(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        chats = Chat.objects.filter(participants = request.user)
        serializers = ChatListSerializer(chats, many=True)
        
        return Response({"success":True,"message":"data fatched!","data":serializers.data}, status=status.HTTP_200_OK)
    


class MessageList_Chats(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request,pk):
        chats = Chat.objects.get(id = pk)
        messages = Message.objects.filter(chat = chats)
        serializers = Message_List_Serializer(messages, many=True)
        serializer2 = ChatListSerializer(chats)
        return Response({"success":True,"message":"data fatched!","chat":serializer2.data,"data":serializers.data}, status=status.HTTP_200_OK)