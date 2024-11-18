from django.db import models

# Create your models here.
from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.core.exceptions import ValidationError
from django.db import models



class CustomUser(AbstractUser):
    profile_pic = models.ImageField(upload_to="profile_picture", null=True, blank=True)
    phone = models.CharField(max_length=16 , unique= True)
    email =models.EmailField(max_length=200, unique=True)

    steet = models.CharField(max_length=100,null=True, blank=True)
    city = models.CharField(max_length=100,null=True, blank=True)
    postcode = models.CharField(max_length=6,null=True, blank=True)
    state = models.TextField(null=True, blank=True) # About discripttion User
    nid_no = models.CharField(max_length=20,null=True, blank=True)
    country = models.CharField(max_length=150, default="Bangladesh")
    binenceaccountno = models.CharField(max_length=50, blank= True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)

    is_email_varified = models.BooleanField(default = False)
    is_phone_varified = models.BooleanField(default = False)
    two_stepverified = models.BooleanField(default=False) # workit
    is_nid_varified = models.BooleanField(default=False)
    privacy_polyci = models.BooleanField(default=True)


    Changesmadetoyouraccount = models.BooleanField(default=True)
    Informationonnewtrade = models.BooleanField(default=True)
    Marketingandpromooffers = models.BooleanField(default=True)


    def __str__(self):
        return f'{self.username} {self.phone}'
    



class UserLoginActivity(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    city = models.CharField(max_length=100, null=True, blank=True)
    country = models.CharField(max_length=100, null=True, blank=True)
    region = models.CharField(max_length=100, null=True, blank=True)
    timezone = models.CharField(max_length=100, null=True, blank=True)
    regionName= models.CharField(max_length=100, null=True, blank=True)
    isp =  models.CharField(max_length=100, null=True, blank=True)
    org = models.CharField(max_length=100, null=True, blank=True)
    AS = models.CharField(max_length=100, null=True, blank=True)
    device_name = models.CharField(max_length=250 , null=True, blank=True)    

    def __str__(self):
        return f'{self.user.username} logged in at {self.login_time} in {self.device_name}'



class OTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    updatred_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f'{self.email} {self.otp}'


class Notifications(models.Model):
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=250)
    discription = models.TextField()
    seen_status = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updatred_at = models.DateTimeField(auto_now=True, null=True,blank=True)
    def __str__(self):
        return f'{self.to_user.email} {self.title}'
    

class Massege(models.Model):
    from_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sentder')
    to_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE,  related_name='reciver')

    text = models.TextField()
    photo = models.FileField(upload_to="massage")

    seen_status = models.BooleanField(False)
    connect = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True,blank=True)
    updatred_at = models.DateTimeField(auto_now=True, null=True,blank=True)
    def __str__(self):
        return f'{self.to_user.email} {self.title}'
    




class Team(models.Model):
    team_admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE,related_name='admin_teams')
    
    members = models.ManyToManyField(CustomUser, related_name='teams')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_boll_fiel = models.BooleanField(default=False)
    def __str__(self):
        return f'Team led by {self.team_admin}'




class MyRefeList(models.Model):
    team_admin = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    members = models.ManyToManyField(CustomUser, related_name='references_user')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    extra_boll_fiel = models.BooleanField(default=False)
    def __str__(self):
        return f'Reference led by {self.team_admin}'
    



class DynamicControlScheduling(models.Model):
    admin_user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)

    diposite = models.BooleanField(default=True)
    imvest = models.BooleanField(default=True)
    payout = models.BooleanField(default=True)
    getreward = models.BooleanField(default=True)
    manage_fund = models.BooleanField(default=True)


    payout_charge = models.FloatField(default=5.00)
    reference_persentice = models.FloatField(default=5.00)
    inv_persentice = models.FloatField(default=5.00)

    sw1 = models.BooleanField(default=False)
    sw2 = models.BooleanField(default=False)
    sw3 = models.BooleanField(default=False)
    sw4 = models.BooleanField(default=True)
    sw5 = models.BooleanField(default=True)
    sw6 = models.BooleanField(default=True)


    sks = models.CharField(max_length=150)

    sks1 = models.CharField(max_length=150, null=True, blank=True)
    sks2 = models.CharField(max_length=150, null=True, blank=True)

    sks3 = models.CharField(max_length=150, null=True, blank=True)
    sks4 = models.CharField(max_length=150, null=True, blank=True)

    time1 = models.IntegerField(default=5)  
    time2 = models.IntegerField(default=5) 



    # Prevent deletion
    def delete(self, *args, **kwargs):
        raise Exception("This object cannot be deleted.")
    
    def __str__(self):
        return f"{self.admin_user.email}"


    


class MytodaysIncome(models.Model):
    income_admin = models.OneToOneField(CustomUser, null=True, blank=True, on_delete=models.SET_NULL)
    incomefee = models.FloatField(default=0.00)
    charge = models.FloatField(default=0.00)
    sw1 = models.BooleanField(default=False)

    # Prevent deletion of this model
    def delete(self, *args, **kwargs):
        raise ValidationError("Deletion of MytodaysIncome instances is not allowed.")

    # Prevent changing the income_admin field once it has been set
    def save(self, *args, **kwargs):
        if self.pk:  # Check if the object already exists (update operation)
            old_instance = MytodaysIncome.objects.get(pk=self.pk)
            if old_instance.income_admin != self.income_admin:
                raise ValidationError("Changing the income_admin field is not allowed.")
        
        super(MytodaysIncome, self).save(*args, **kwargs)
    def __str__(self):
        return f'{self.income_admin.email}'

    
    