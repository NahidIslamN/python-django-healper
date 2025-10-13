from celery import shared_task
from django.core.mail import send_mail


@shared_task
def sent_email_to(email, text, subject):
    send_mail(subject, text, 'from@example.com', [email])
    return 'successfully sent'