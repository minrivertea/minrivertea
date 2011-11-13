# this collects together all of the 'send email' functions just for ease of reference

from django.conf import settings
from django.template import RequestContext
from django.http import HttpResponseRedirect, HttpResponse 
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse

import os, md5
import datetime
import uuid
import re

from minriver.shop.models import *


def _send_email(request, sender, receiver, subject_line, text, html=None):
    
    # if there is an HTML version, do a multi email
    if html and text:
        msg = EmailMultiAlternatives(subject_line, text, sender, [receiver])
        msg.attach_alternative(html, "text/html")
        msg.send() 
    
    # otherwise just send a text version
    else:
        send_mail(
              subject_line, 
              text, 
              sender,
              [receiver], 
              fail_silently=False
        )


# sends a reminder to the owner of an INCOMPLETE order
def _order_reminder_email(request, id):
    order = get_object_or_404(Order, pk=id)
    order.hashkey = uuid.uuid1().hex
    shopper = order.owner
    if order.reminder_email_sent:
        return False

    sender = settings.SITE_EMAIL
    receiver = order.owner.email
    subject_line = "Was it something I said?"
    text = render_to_string('shop/emails/text/send_reminder_email.txt', {'order': order, 'url': reverse('order_url', args=[order.hashkey])})
    
    _send_email(request, sender, receiver, subject_line, text)
                    
    order.reminder_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')  


# sends an email to a completed order owner, asking them if they want to send a sample to a friend
def _free_sampler_email(request, id):
    order = get_object_or_404(Order, pk=id)
    shopper = order.owner
    if order.sampler_email_sent:
        return False

    sender = settings.SITE_EMAIL
    receiver = shopper.email
    subject_line = "Give a tea gift to a friend, courtesy of the Min River Tea Farm"
            
    # create email
    text = render_to_string('shop/emails/text/send_sample_to_friend_email.txt', {'shopper': shopper})
    html = render_to_string('shop/emails/html/send_sample_to_friend.html', {
    	'shopper': shopper,
    	'subject': subject_line,
    })
    
    _send_email(request, sender, receiver, subject_line, text, html)
        
    order.sampler_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')


# send email to user asking for a review of a product
def _product_review_email(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    subject_line = "minrivertea.com - how to brew your tea"
    sender = settings.SITE_EMAIL
    receiver = order.owner.email
    
    text = render_to_string('shop/emails/text/review_email.txt', {
        'shopper': order.owner, 
        'items': order.items.all(),
        }
    )
    
    html = render_to_string('shop/emails/html/html_review_email.html', {
        'items': order.items.all(),
        'shopper': order.owner,
        'subject': subject_line,
    })
    
    _send_email(request, sender, receiver, subject_line, text, html)
    
    order.review_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')  


def _admin_notify_new_review(request, tea, review):
    
    text = "%s %s just posted a review of %s" % (review.first_name, review.last_name, tea.name)              
    subject_line = "New Review Posted - %s" % tea.name 
    sender = settings.SITE_EMAIL
    receiver = settings.SITE_EMAIL
      
    _send_email(request, sender, receiver, subject_line, text)
    
    return


def _admin_notify_contact(request, data):

    text = render_to_string('shop/emails/text/contact_template.txt', {
    	 'message': data['your_message'],
      	 'your_email': data['your_email'],
      	 'your_name': data['your_name'],
    })
    
    receiver = settings.SITE_EMAIL
    sender = settings.SITE_EMAIL
    subject_line = "MINRIVERTEA.COM - WEBSITE CONTACT SUBMISSION"
    _send_email(request, sender, receiver, subject_line, text)
    
    return
