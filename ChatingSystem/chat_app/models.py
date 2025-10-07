from django.db import models
from django.conf import settings

User = settings.AUTH_USER_MODEL

# ----------------- Chat Models -----------------

class Chat(models.Model):
    CHAT_TYPE_CHOICES = (
        ('private', 'Private'),
        ('group', 'Group'),
    )
    chat_type = models.CharField(max_length=10, choices=CHAT_TYPE_CHOICES, default='private')
    participants = models.ManyToManyField(User, related_name="chats")
    name = models.CharField(max_length=255, blank=True, null=True)  # only for groups
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or f"{self.chat_type} Chat {self.id}"
    
    class Meta:
        ordering = ['-updated_at']


class ChatInvite(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="invites")
    inviter = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_invites")
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name="received_invites")
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)


class BlockList(models.Model):
    blocker = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_users")
    blocked = models.ForeignKey(User, on_delete=models.CASCADE, related_name="blocked_by")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('blocker', 'blocked')


# ----------------- Messaging Models -----------------



class MessageReaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    emoji = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)



class Call(models.Model):
    CALL_TYPE_CHOICES = (
        ('audio', 'Audio'),
        ('video', 'Video'),
    )
    call_type = models.CharField(max_length=10, choices=CALL_TYPE_CHOICES)
    is_active = models.BooleanField(default=True)
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    def __str__(self):
        return f"{self.call_type} call {self.id}"


class MessageFiles(models.Model):
    title = models.CharField(max_length=30, null=True, blank=True)
    file = models.FileField(upload_to="messages_files", blank=True)



class Message(models.Model):
    STATUS_CHOICES = (
        ('sent', 'Sent'),
        ('delivered', 'Delivered'),
        ('seen', 'Seen'),
    )
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name="sent_messages")
    text = models.TextField(blank=True, null=True)
    files = models.ManyToManyField(MessageFiles, blank=True, related_name="files")  # images/docs/audio/video
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="sent")
    reactions = models.ManyToManyField(MessageReaction, related_name='message_reactions')

    seen_users = models.ManyToManyField(User, related_name="seen_users", blank=True)
    calls = models.ForeignKey(Call, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_edited = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} -> Chat {self.chat.id}"
    
    class Meta:
        ordering = ['-created_at']


class TypingIndicator(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="typing")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="typing_in")
    is_typing = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        unique_together = ('chat', 'user')


