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


def _send_email(receiver, subject_line, text, request=None, html=None, sender=None):
    
    sender = settings.SITE_EMAIL
    
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

    receiver = order.owner.email
    subject_line = "Was it something I said?"
    text = render_to_string('shop/emails/text/send_reminder_email.txt', {
        'order': order, 
        'url': reverse('order_url', args=[order.hashkey])}
    )
    
    _send_email(receiver, subject_line, text)
                    
    order.reminder_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')  


# sends an email to a completed order owner, asking them if they want to send a sample to a friend
def _free_sampler_email(request, id):
    order = get_object_or_404(Order, pk=id)
    shopper = order.owner
    if order.sampler_email_sent:
        return False

    receiver = shopper.email
    subject_line = "Give a tea gift to a friend, courtesy of the Min River Tea Farm"
            
    # create email
    text = render_to_string('shop/emails/text/send_sample_to_friend_email.txt', {'shopper': shopper})
    html = render_to_string('shop/emails/html/send_sample_to_friend.html', {
    	'shopper': shopper,
    	'subject': subject_line,
    })
    
    _send_email(request, receiver, subject_line, text, html)
        
    order.sampler_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')


# send email to user asking for a review of a product
def _product_review_email(order_id):
    order = get_object_or_404(Order, id=order_id)
    
    subject_line = "minrivertea.com - how to brew your tea"
    receiver = order.owner.email
    
    text = render_to_string('shop/emails/text/review_email.txt', {
        'shopper': order.owner, 
        }
    )
    
    html = render_to_string('shop/emails/html/html_review_email.html', {
        'shopper': order.owner,
        'subject': subject_line,
    })
    
    _send_email(receiver, subject_line, text, html)
    
    order.review_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')  


def _admin_notify_new_review(tea, review):
    
    text = "%s %s just posted a review of %s" % (review.first_name, review.last_name, tea.name)              
    subject_line = "New Review Posted - %s" % tea.name 
    receiver = settings.SITE_EMAIL
      
    _send_email(request, receiver, subject_line, text)
    
    return


def _admin_notify_contact(data):

    text = render_to_string('shop/emails/text/contact_template.txt', {
    	 'message': data['your_message'],
      	 'your_email': data['your_email'],
      	 'your_name': data['your_name'],
    })
    
    receiver = settings.SITE_EMAIL
    subject_line = "MINRIVERTEA.COM - WEBSITE CONTACT SUBMISSION"
    _send_email(receiver, subject_line, text)
    
    return

def _send_two_month_reminder_email(order):

    text_template = "shop/emails/text/two_month_reminder.txt"
    html_template = 'shop/emails/html/two_month_reminder.html'

    items = []
    
    
    for item in order.items.all():
           # what happens if the item they ordered isn't available?
           if item.item.is_active == False or item.item.parent_product.coming_soon == True:
               # if it's not available, suggest another product
               new_product = UniqueProduct.objects.filter(
                   parent_product=item.item.parent_product, 
                   is_sale_price=False
               ).exclude(id=item.item.id).order_by('-price')
               text_template = 'shop/emails/text/suggest_replacement.txt'
               html_template = 'shop/emails/html/suggest_replacement.html'
               
               if len(new_product) == 0:
                   # if there isn't a valid replacement, then don't send the email.
                   print "no replacement for %s" % item
                   return False
               else:
                   product = new_product[0]
                   if product in items:
                       pass
                   else:
                       items.append(product)
           else:
               if item.item in items:
                   pass
               else:
                   items.append(item.item)         
    
    if len(items) == 0:
        return
    
    print items
    
    receiver = order.owner.email
    subject_line = "Have you finished your tea yet?"
    if not order.hashkey:
        order.hashkey = uuid.uuid1().hex
        order.save()
    
    url = "http://www.minrivertea.com/order/repeat/%s" % order.hashkey
    text = render_to_string(text_template, {
        'url': url,
        'order': order,
        'items': items,	
    })
    html = render_to_string(html_template, {
        'url': url,
        'order': order,
        'items': items,
        'subject': subject_line,
    })
    
    _send_email(receiver, subject_line, text, html)
    print "Email sent to: %s" % receiver
    order.owner.reminder_email_sent = datetime.now()
    order.owner.save()
    
    return True

def _admin_cron_update(data, subject_line):
    text = render_to_string('shop/emails/text/admin_cron_update.txt', {
        'data': data,	
    })
    receiver = settings.SITE_EMAIL
    subject_line = subject_line
    _send_email(receiver, subject_line, text)

def _payment_success_email(order):
    
    # CUSTOMER EMAIL
    receiver = order.owner.email
    subject_line = "Order confirmed - Min River Tea Farm" 
    
    text = render_to_string('shop/emails/text/order_confirm_customer.txt', {'order': order})
    html = render_to_string('shop/emails/html/html_order_confirm.html', {'order': order, 'subject': subject_line})
    
    _send_email(receiver, subject_line, text, html)
    
     
    # ADMIN EMAIL (reset some of the values!!)
    receiver = settings.SITE_EMAIL
    subject_line = "NEW ORDER - %s" % order.invoice_id 
    text = render_to_string('shop/emails/text/order_confirm_admin.txt', {'order': order})
    _send_email(receiver, subject_line, text)

    return HttpResponse()

def _payment_flagged_email(request, order):

    receiver = settings.SITE_EMAIL
    text = render_to_string('shop/emails/text/order_confirm_admin.txt', {'order': order})
    subject_line = "FLAGGED ORDER - %s" % invoice_id 
      
    _send_email(request, receiver, subject_line, text)
    
    return
