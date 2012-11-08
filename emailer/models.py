from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from urlparse import urlparse

from paypal.standard.ipn.signals import payment_was_successful, payment_was_flagged
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives

from shop.models import Shopper





class EmailInstance(models.Model):
    shopper = models.ForeignKey(Shopper, blank=True, null=True)
    recipient = models.EmailField()
    date_sent = models.DateTimeField(blank=True, null=True)
    subject_line = models.CharField(max_length=256)
    copy = models.TextField(help_text="A copy of the original email sent to the customer")
    template = models.CharField(max_length=200, choices=settings.EMAIL_TEMPLATES)
    language = models.CharField(max_length=100, choices=settings.LANGUAGES)
    


class Newsletter(models.Model):
    text_version = models.TextField()
    html_version = models.TextField()
    is_draft = models.BooleanField(default=True)
    date_sent = models.DateTimeField(blank=True, null=True)



class Subscriber(models.Model):
    email = models.EmailField()
    date_signed_up = models.DateField()
    language = models.CharField(max_length=200, choices=settings.LANGUAGES)
    confirmed = models.BooleanField(default=False)
    date_unsubscribed = models.DateField(blank=True, null=True)
    
    def __unicode__(self):
        return self.email