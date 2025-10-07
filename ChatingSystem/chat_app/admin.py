from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(Chat)
admin.site.register(ChatInvite)
admin.site.register(BlockList)
admin.site.register(MessageReaction)
admin.site.register(Call)
admin.site.register(MessageFiles)
admin.site.register(Message)
admin.site.register(TypingIndicator)