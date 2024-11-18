from django.contrib import admin
from AuthApp.models import *

# Register your models here.

admin.site.register(CustomUser)
admin.site.register(UserLoginActivity)
admin.site.register(OTP)
admin.site.register(Notifications)
admin.site.register(Team)
admin.site.register(Massege)
admin.site.register(MyRefeList)


admin.site.register(DynamicControlScheduling)

admin.site.register(MytodaysIncome)
