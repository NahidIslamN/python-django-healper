
from django.contrib import messages
from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth import authenticate, login, logout

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from AuthApp.models import UserLoginActivity


import requests

from AuthApp.models import *
from BanckManagement.models import BankAccount






from .models import UserLoginActivity







######## Email Varification #######

from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from AuthApp.models import OTP
import random
from django.utils import timezone
from datetime import datetime, timedelta

###### Email varifications ######


def generate_otp():
    return str(random.randint(100000, 999999))


def send_otp_email(email, otp):
    subject = 'QuickTrade OTP'
    html_message = render_to_string('auth/email_template.html', {'otp': otp})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, 'from@example.com', [email], html_message=html_message)


def generate_and_send_otp(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        if CustomUser.objects.filter(email = email).exists():
            otp = generate_otp()
            send_otp_email(email, otp)
            if OTP.objects.filter(email = email).exists():
                inst = OTP.objects.get(email = email)
                inst.otp = otp
                inst.save()
            else:
                inst = OTP.objects.create(
                        email = email,
                        otp = otp,
                        )
                inst.save()
            return redirect(f'/auth/verify-otp/{email}/')
        else:
            messages.info(request,"Invailed Email Address !")
            return redirect("/forget-account/")
    return render(request, 'auth/generate_otp.html')


def verify_otp(request , email):
    if request.method == 'POST':
        email_adress = email 
        otp_entered = request.POST.get('otp')
        try:
            otp_instance = OTP.objects.get(email=email_adress)
            otp_expiry_time = otp_instance.created_at + timedelta(minutes=5)
            otp_expiry_time2 = otp_instance.updatred_at + timedelta(minutes=5)
           

            if otp_expiry_time >= timezone.now() or otp_expiry_time2>= timezone.now() :
                if otp_instance.otp == otp_entered:
                    userssss = CustomUser.objects.get(email = email)
                    # OTP matched, do something here
                    try:
                        new_pass = request.POST.get('newpass')
                        confirm_pass = request.POST.get('confirmpass')
                      
                        if new_pass == confirm_pass:
                            userssss.set_password(new_pass)
                            userssss.save()

                            title = "Security Alart!"
                            discription = "Your password has been change just now with email varification!"
                            N = Notifications.objects.create(
                                    to_user = userssss,
                                    title = title,
                                    discription = discription                            
                            )
                            N.save()
                            login(request, userssss)
                        else:
                            messages.info(request,"Password not change and didn't matched!")
                            return redirect ("/user/deshboard/")

                    except:
                        pass                    
                    
                    return redirect("/user/deshboard/")
                else:
                    messages.info(request,"Worng Varification Code !")
                    return redirect("/auth/forget-account/")
            else:
                # OTP matched, do something here
                messages.info(request,"Time Expired!")
                return redirect("/auth/forget-account/")
            
        except CustomUser.DoesNotExist:
            messages.info(request,"Failed Veryfied !")
            return redirect("/auth/forget-account/")
    return render (request,'auth/verify_otp.html')





########### Verify Email Adress

class SentOtp(View):
    def get(self,request):

        return render(request, 'auth/generate_otp.html')
    def post(self,request):
        email = request.POST.get('email')
        if CustomUser.objects.filter(email = email).exists():
            otp = generate_otp()
            send_otp_email(email, otp)
            if OTP.objects.filter(email = email).exists():
                inst = OTP.objects.get(email = email)
                inst.otp = otp
                inst.save()
            else:
                inst = OTP.objects.create(
                        email = email,
                        otp = otp,
                        )
                inst.save()
            return redirect(f'/auth/verify-email/{email}/')
        else:
            messages.info(request,"Invailed Email Address !")
            return redirect("/forget-account/")
        



def verify_email(request , email):    
    if request.method == 'POST':
        email_adress = email 
        otp_entered = request.POST.get('otp')
        try:
            otp_instance = OTP.objects.get(email=email_adress)
            otp_expiry_time = otp_instance.created_at + timedelta(minutes=5)
            otp_expiry_time2 = otp_instance.updatred_at + timedelta(minutes=5)
           

            if otp_expiry_time >= timezone.now() or otp_expiry_time2>= timezone.now() :
                if otp_instance.otp == otp_entered:
                    userssss = CustomUser.objects.get(email = email)
                    # OTP matched, do something here
                    try:
                        if userssss.is_email_varified:
                            pass
                        else:
                            userssss.is_email_varified = True
                            userssss.save()


                        login(request, userssss)
                        return redirect("/user/deshboard/")     

                    except:
                        pass                                     
                    
                    
                else:
                    messages.info(request,"Worng Varification Code !")
                    return redirect("/auth/forget-account/")
            else:
                # OTP matched, do something here
                messages.info(request,"Time Expired!")
                return redirect("/auth/forget-account/")
            
        except CustomUser.DoesNotExist:
            messages.info(request,"Failed Veryfied !")
            return redirect("/auth/forget-account/")
    return render (request,'auth/verifyemail.html')











# Email varification end



# Create your views here.




class LoginViews(View):
    def get(self, request):

        return render(request,'auth/login.html')
    def post(self, request):
        login_data = request.POST
        username =  login_data.get('username')
        password = login_data.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            users = CustomUser.objects.get(username = username)
            if users.two_stepverified:
              
               return redirect('/auth/email_varification/')
            
            elif users.is_email_varified:
                login(request, user)
                return redirect('/user/deshboard/')
           
            else:
                return redirect('/auth/email_varification/')
                       
        else: 
            messages.info(request,'Uname or Password Invalid!')
            return redirect('/auth/signin/')
        
class LogoutViews(View):
    def get(self, request):
        logout(request)

        return redirect('/')




class WhereLogin(View):
    @method_decorator(login_required)
    def get(self,request):
        user  = request.user
        logindata = UserLoginActivity.objects.filter(user = user).order_by('-login_time')

        cp = {
            'loginactivities':logindata,
        }
        return render(request, 'BasicApp/wherelogin.html', context=cp)

class remove_logininfo(View):
    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        logindata = UserLoginActivity.objects.filter(user = user).order_by('-login_time')
        logindata.delete()
        logout(request)

        return redirect('/auth/where_logedin/')
    


        
class SignUP(View):
    def get(self, request):
        URL = 'https://restcountries.com/v3.1/all'
        
        try:
            # Get data from the API and convert to JSON
            response = requests.get(url=URL)
            response.raise_for_status()  # Raise an HTTPError if the request was unsuccessful
            country_data = response.json()  # Convert response to JSON
            
        except requests.exceptions.RequestException as e:
            # Handle any errors that occur during the API request
            messages.info(request,"an eror occur pleace try again later!")
            admins = CustomUser.objects.filter(is_superuser = True)
            title = "County apis is not working!"
            discribe = f"User can't create account because country apis is not working! contuct with your developer and fixed the probelm. {e}"
            for admin in admins:
                note=Notifications.objects.create(
                        to_user = admin,
                        title = title,
                        discription = discribe

                )
                note.save()
            
            country_data = []  # Return an empty list in case of error

        # Pass the country data to the template context
        context = {
            "countries": country_data
        }
        
        return render(request, 'auth/signup.html', context=context)

    def post(self, request):
        images = request.FILES.get('Images')        

        data = request.POST      
    
        if CustomUser.objects.filter(email = data.get('email')).exists():
            messages.info(request, "username or email already taken!")
            URL = 'https://restcountries.com/v3.1/all'
        
            try:
                # Get data from the API and convert to JSON
                response = requests.get(url=URL)
                response.raise_for_status()  # Raise an HTTPError if the request was unsuccessful
                country_data = response.json()  # Convert response to JSON
                
            except requests.exceptions.RequestException as e:
                # Handle any errors that occur during the API request
                messages.info(request,"an eror occur pleace try again later!")
                admins = CustomUser.objects.filter(is_superuser = True)
                title = "County apis is not working!"
                discribe = f"User can't create account because country apis is not working! contuct with your developer and fixed the probelm. {e}"
                for admin in admins:
                    note=Notifications.objects.create(
                            to_user = admin,
                            title = title,
                            discription = discribe

                    )
                    note.save()
                
                country_data = []  # Return an empty list in case of error

            # Pass the country data to the template context
            cp = {
                "countries": country_data,
                'data':data
            }            

            return render(request, 'auth/signup.html', context=cp)
        


        elif CustomUser.objects.filter(phone = data.get('phone')).exists():
            messages.info(request, "phone pumber already taken !")
            URL = 'https://restcountries.com/v3.1/all'
        
            try:
                # Get data from the API and convert to JSON
                response = requests.get(url=URL)
                response.raise_for_status()  # Raise an HTTPError if the request was unsuccessful
                country_data = response.json()  # Convert response to JSON
                
            except requests.exceptions.RequestException as e:
                # Handle any errors that occur during the API request
                messages.info(request,"an eror occur pleace try again later!")
                admins = CustomUser.objects.filter(is_superuser = True)
                title = "County apis is not working!"
                discribe = f"User can't create account because country apis is not working! contuct with your developer and fixed the probelm. {e}"
                for admin in admins:
                    note=Notifications.objects.create(
                            to_user = admin,
                            title = title,
                            discription = discribe

                    )
                    note.save()
                
                country_data = []  # Return an empty list in case of error

            # Pass the country data to the template context
            cp = {
                "countries": country_data,
                'data':data
            }            

            return render(request, 'auth/signup.html', context=cp)
        
        elif data.get('password') != data.get('password2'):
            messages.info(request, "password was not matched!")
            URL = 'https://restcountries.com/v3.1/all'
        
            try:
                # Get data from the API and convert to JSON
                response = requests.get(url=URL)
                response.raise_for_status()  # Raise an HTTPError if the request was unsuccessful
                country_data = response.json()  # Convert response to JSON
                
            except requests.exceptions.RequestException as e:
                # Handle any errors that occur during the API request
                messages.info(request,"an eror occur pleace try again later!")
                admins = CustomUser.objects.filter(is_superuser = True)
                title = "County apis is not working!"
                discribe = f"User can't create account because country apis is not working! contuct with your developer and fixed the probelm. {e}"
                for admin in admins:
                    note=Notifications.objects.create(
                            to_user = admin,
                            title = title,
                            discription = discribe

                    )
                    note.save()
                
                country_data = []  # Return an empty list in case of error

            # Pass the country data to the template context
            cp = {
                "countries": country_data,
                'data':data
            }            

            return render(request, 'auth/signup.html', context=cp)
        elif  CustomUser.objects.filter(nid_no = data.get('nid')).exists():
            messages.info(request,"NID number already taken!")  
            URL = 'https://restcountries.com/v3.1/all'
        
            try:
                # Get data from the API and convert to JSON
                response = requests.get(url=URL)
                response.raise_for_status()  # Raise an HTTPError if the request was unsuccessful
                country_data = response.json()  # Convert response to JSON
                
            except requests.exceptions.RequestException as e:
                # Handle any errors that occur during the API request
                messages.info(request,"an eror occur pleace try again later!")
                admins = CustomUser.objects.filter(is_superuser = True)
                title = "County apis is not working!"
                discribe = f"User can't create account because country apis is not working! contuct with your developer and fixed the probelm. {e}"
                for admin in admins:
                    note=Notifications.objects.create(
                            to_user = admin,
                            title = title,
                            discription = discribe

                    )
                    note.save()
                
                country_data = []  # Return an empty list in case of error

            # Pass the country data to the template context
            cp = {
                "countries": country_data,
                'data':data
            }            

            return render(request, 'auth/signup.html', context=cp) 
        
        elif data.get('checkbox') != "True":
            messages.info(request,'Pleace agree whith the privacy policy!')
            URL = 'https://restcountries.com/v3.1/all'
        
            try:
                # Get data from the API and convert to JSON
                response = requests.get(url=URL)
                response.raise_for_status()  # Raise an HTTPError if the request was unsuccessful
                country_data = response.json()  # Convert response to JSON
                
            except requests.exceptions.RequestException as e:
                # Handle any errors that occur during the API request
                messages.info(request,"an eror occur pleace try again later!")
                admins = CustomUser.objects.filter(is_superuser = True)
                title = "County apis is not working!"
                discribe = f"User can't create account because country apis is not working! contuct with your developer and fixed the probelm. {e}"
                for admin in admins:
                    note=Notifications.objects.create(
                            to_user = admin,
                            title = title,
                            discription = discribe

                    )
                    note.save()
                
                country_data = []  # Return an empty list in case of error

            # Pass the country data to the template context
            cp = {
                "countries": country_data,
                'data':data
            }            

            return render(request, 'auth/signup.html', context=cp)
        
        else:
            c = CustomUser.objects.create(
                first_name = data.get('first_name'),
                last_name = data.get('last_name'),
                username = data.get('email'),
                email = data.get('email'),
                phone = data.get('phone'),
                profile_pic = images,
                nid_no = data.get('nid'),
                country = data.get('country'),
                binenceaccountno = data.get("binenceaccountno"),
            )
            c.set_password(data.get('password'))
            c.save()

            BA = BankAccount.objects.create(
                account_admin = c
            )
            BA.save()

            T = Team.objects.create(
                    team_admin = c,
                                 
            )
            T.members.add(c)
            T.save()


            R = MyRefeList.objects.create(
                team_admin = c,
                          
            )
            R.save()
            refuser = data.get('referencess')
      
            if CustomUser.objects.filter(email = refuser).exists():
                us = CustomUser.objects.get(email = refuser)
                USRefList = MyRefeList.objects.get(team_admin = us )
                USRefList.members.add(c)
                USRefList.save()
            else:
                pass



            TIT = MytodaysIncome.objects.create(
                income_admin = c
            )
            TIT.save()



            
            messages.info(request, "User Created Successfully!")

            return redirect('/auth/signup/')  
        
class ViewMyProfile(View):
    @method_decorator(login_required)
    def get(self, request):

        return render(request, 'auth/userprofile.html')

    @method_decorator(login_required)
    def post(self, request):     
        data = request.POST        
        users = request.user
        method = request.POST.get('_method', '').upper()

        if method == "UPDATE":  
            imgages = request.FILES.get('pppp')        

            if imgages:
                users.profile_pic = imgages 

            users.first_name = data.get('first_name')

            users.last_name = data.get('last_name')        
            
            users.phone = data.get('phone')
            
            users.country = data.get('country')
            
            users.city = data.get('city')
            
            users.steet = data.get('steet')
            
            users.state = data.get('about')

            users.nid_no = data.get('nid')

            users.postcode = data.get('postcode')

            if users.email != data.get('email'):
                if CustomUser.objects.filter(email = data.get('email') ).exists():
                    messages.info(request,'Email Already taken !')
                else:
                    users.email = data.get('email')
                    users.username = data.get('email')
                    users.is_email_varified = False

            users.save()

            if users.Changesmadetoyouraccount:
                title = "Made Change Your Account"
                disc = "Your profile info hasbeen change just now."
                N = Notifications.objects.create(
                    to_user = users,
                    title = title,
                    discription = disc
                )
                N.save()
                            
            return redirect('/auth/profile/')
        

        elif method == "CHANGESETTINGS":
            madechangeaccount = data.get('madechangeaccount')
            two_stepverified = data.get("two_stepverified")
            Marketingandpromooffers = data.get("Marketingandpromooffers")
            Informationonnewtrade = data.get("Informationonnewtrade")

            if madechangeaccount is not None:
                users.Changesmadetoyouraccount = True
            else:
                users.Changesmadetoyouraccount = False   

            if two_stepverified is not None:
                users.two_stepverified = True
            else:
                users.two_stepverified = False

            if Marketingandpromooffers is not None:
                users.Marketingandpromooffers = True
            else:
                users.Marketingandpromooffers = False

            if Informationonnewtrade is not None:
                users.Informationonnewtrade = True
            else:
                users.Informationonnewtrade = False

            users.save()
            if users.Changesmadetoyouraccount or 0==0:
                title = "Account Setting Change"
                disc = "YourSetting has been change just now."
                N = Notifications.objects.create(
                    to_user = users,
                    title = title,
                    discription = disc
                )
                N.save()

            return redirect('/auth/profile/')

            


        elif method == "CHANGEPASSKEY":
           
            if users.check_password(data.get('old_password')):
                if data.get('new_password') == data.get('confirm_password'):
                    users.set_password(data.get('new_password'))
                    users.save()
                    if users.Changesmadetoyouraccount or 0==0:
                        title = "Security Alart!"
                        disc = "Your Password has been change just now."
                        N = Notifications.objects.create(
                            to_user = users,
                            title = title,
                            discription = disc
                        )
                        N.save()
                    messages.info(request,'Password Changed Successfully!')
                    return redirect('/auth/profile/')
                else:
                    messages.info(request,"Password didn't matched!")
                    return redirect('/auth/profile/')
            else:
                messages.info(request,'Incrrect old password!')
                return redirect('/auth/profile/')

        else:
            return redirect('/auth/profile/')


        
    



############ Admin Place ########### VerySecure ################

class AllUsers(View):
    @method_decorator(login_required)
    def get(self, request):
        user = request.user
        if user.is_superuser:
            allusers = CustomUser.objects.all()

            cp = {
                'allusers':allusers,
            }        
            return render(request,'auth/admin/allusers.html', context=cp)
        else:
            logout(request)
            return redirect("/user/deshboard/")  



