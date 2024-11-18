# user_activity/middleware.py

from django.utils.timezone import now
from django.contrib.auth import get_user_model
from .models import UserLoginActivity, Notifications
import requests

import platform

os_name = platform.system()


User = get_user_model()

class UserLoginActivityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        users = request.user
        
        if request.user.is_authenticated and not request.session.get('logged'):
            ip_address = self.get_ip_address(request)
            location = self.get_location(ip_address)


            if UserLoginActivity.objects.filter(user=users, ip_address = ip_address).exists():
                pass
            else:
                UserLoginActivity.objects.create(
                    user=request.user,
                    ip_address=ip_address,
                    latitude=location.get('latitude'),
                    longitude=location.get('longitude'),
                    city=location.get('city'),
                    country=location.get('country'),
                    region = location.get('region'),
                    timezone = location.get('timezone'),
                    regionName = location.get('regionName'),
                    isp = location.get('isp'),
                    org =location.get('org'),
                    AS = location.get('as'),
                    device_name = f"{os_name} PC",

                )

                title = "Security Alart!"
                discript = f"Your id loged in a new ip address ip:{ip_address} at {location.get('country')}, if you are not pleace infrom us for your security"
                n = Notifications.objects.create(
                    to_user = users,
                    title = title,
                    discription = discript

                )
                n.save()
                
            

            # Mark the session as logged
            request.session['logged'] = True

        return response

    def get_ip_address(self, request):
        response = requests.get('https://api.ipify.org/?format=json')
        data = response.json()
      
        return data['ip']


    def get_location(self, ip_address):
        """Get geolocation information based on IP address."""
        response = requests.get(f"http://ip-api.com/json/{ip_address}")
        if response.status_code == 200:
            data = response.json()
            return {
                'latitude': data.get('lat'),
                'longitude': data.get('lon'),
                'city': data.get('city'),
                'country': data.get('country'),
                "region" : data.get('region'),
                "timezone" : data.get('timezone'),
                "regionName" : data.get('regionName'),
                "isp" : data.get('isp'),
                "org" : data.get('org'),
                "as" : data.get('as'),
            }
        return {}
