from django.shortcuts import render
from django.views import View

# Create your tests here.

class ChatMessageSocket(View):
    def get(self, request):
        
        return render(self, "messagesocket_test.html")
    


class CallerWS1(View):
    def get(self, request):
        
        return render(self, "caller1.html")
    


class CallerWS2(View):
    def get(self, request):
        
        return render(self, "caller2.html")