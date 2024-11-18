from AuthApp.models import  Notifications
from django.contrib.auth.models import AnonymousUser


def content(request):
    # Check if the user is authenticated
    if isinstance(request.user, AnonymousUser):
        # Return default values for anonymous users
        total_note = 0
        all_note4 = []
    else:
        # Fetch notifications for logged-in users
        users = request.user
      
        total_note = Notifications.objects.filter(to_user=users, seen_status=False).count()
        all_note4 = Notifications.objects.filter(to_user=users, seen_status=False).order_by('-created_at')[0:4]

    
    
    # Return the variables to be globally available in templates
    return {
        'total_note': total_note,
        'all_note4': all_note4,
    
    }
