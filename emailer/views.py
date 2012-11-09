# this collects together all of the 'send email' functions just for ease of reference

from django.conf import settings
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

import os
import datetime
import uuid
import re

from shop.models import *
from emailer.models import Subscriber
from emailer.forms import EmailSignupForm
from shop.forms import CreateSendEmailForm


def _send_email(receiver, subject_line, text, request=None, sender=None):
    
    if not sender:
        sender = settings.SITE_EMAIL
    
    
    send_mail(
            subject_line, 
            text, 
            sender,
            [receiver], 
            fail_silently=False
    )


# sends a reminder to the owner of an INCOMPLETE order
def order_reminder_email(request, id):
    order = get_object_or_404(Order, pk=id)
    order.hashkey = uuid.uuid1().hex
    shopper = order.owner
    if order.reminder_email_sent:
        return False

    receiver = order.owner.email
    subject_line = "Was it something we said?"
    text = render_to_string('shop/emails/text/send_reminder_email.txt', {
        'order': order, 
        'url': reverse('order_url', args=[order.hashkey])}
    )
    
    _send_email(receiver, subject_line, text)
                    
    order.reminder_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')  



def _tell_a_friend_email(sender, receiver):
    
    text = render_to_string('shop/emails/text/tell_friend.txt', {'sender': sender})
    subject_line = "Check out minrivertea.com"
    
    _send_email(receiver, subject_line, text, sender=sender)    
        
    return

# sends an email to a completed order owner, asking them if they want to send a sample to a friend
def free_sampler_email(request, id):
    order = get_object_or_404(Order, pk=id)
    shopper = order.owner
    if order.sampler_email_sent:
        return False

    receiver = shopper.email
    subject_line = "Give a tea gift to a friend, courtesy of the Min River Tea Farm"
            
    # create email
    text = render_to_string('shop/emails/text/send_sample_to_friend_email.txt', {'shopper': shopper})
    
    _send_email(request, receiver, subject_line, text)
        
    order.sampler_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')


# send email to user asking for a review of a product
def product_review_email(request, orderid):
    order = get_object_or_404(Order, id=orderid)
    
    subject_line = "Two things you can do right now"
    receiver = order.owner.email
    
    text = render_to_string('shop/emails/text/review_email.txt', {
        'shopper': order.owner, 
        'order': order,
        }
    )
    
    _send_email(receiver, subject_line, text)
    
    order.review_email_sent = True
    order.save()
    
    return HttpResponseRedirect('/admin-stuff')  


def _wishlist_confirmation_email(wishlist):
    
    receiver = wishlist.owner.email
    subject_line = "Your Min River Tea Wishlist!"
            
    # create email
    text = render_to_string('shop/emails/text/wishlist_confirmation_email.txt', {'wishlist': wishlist})
    
    _send_email(receiver, subject_line, text)
    
    return

def _admin_notify_new_review(tea, review):
    
    text = "%s %s just posted a review of %s" % (review.first_name, review.last_name, tea.name)              
    subject_line = "New Review Posted - %s" % tea.name 
    receiver = settings.SITE_EMAIL
      
    _send_email(receiver, subject_line, text)
    
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

    receiver = order.owner.email
    subject_line = "Have you finished your tea yet?"
    
    if not order.hashkey:
        order.hashkey = uuid.uuid1().hex
        order.save()
            
    
    url = "http://www.minrivertea.com/order/repeat/%s" % order.hashkey
    
    text = render_to_string(text_template, {
        'url': url,
        'order': order,	
    })
    
    _send_email(receiver, subject_line, text)
    order.owner.reminder_email_sent = datetime.now()
    order.owner.save()
    
    return True # important, make sure this returns True



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
    
    _send_email(receiver, subject_line, text)
    
     
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
      
    _send_email(receiver, subject_line, text)
    
    return
    

def email_signup(request):
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
            
            from django.utils.translation import get_language
            
            try:
                existing_signup = get_object_or_404(Subscriber, email=form.cleaned_data['email'])
                message = "<h3>Looks like you're already signed up! You don't need to do anything else, and you'll receive TEAMails as normal.</h3>"
            except:
                new_signup = Subscriber.objects.create(
                    email = form.cleaned_data['email'],
                    date_signed_up = datetime.now(),
                    language=get_language(),
                    confirmed=True, # TODO - change this so that an email gets sent off immediately asking them to confirm
                )
                new_signup.save()
                message = "<h3>Awesome! You're now signed up to receive TEAMails - they're roughly fortnightly, and you can unsubscribe at any time by clicking the link in the email.</h3>"
            
            if request.is_ajax():
                return HttpResponse(message)
            
            else:
                from minriver.shop.views import render
                return render(request, 'shop/emails/signup_confirmed.html', locals())
                    
    else:
        form = EmailSignupForm()
    
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)
    
    

def email_unsubscribe(request, key):
    subscriber = get_object_or_404(Subscriber, hashkey=key)
    subscriber.date_unsubscribed = datetime.now()
    subscriber.save()
    
    from minriver.shop.views import render
    return render(request, 'shop/emails/unsubscribe_confirmed.html', locals())


@login_required
def create_email(request, id=None):
    from shop.views import render
    if not request.user.is_superuser:
        return Http404
    
    if request.method == 'POST':
        form = CreateSendEmailForm(request.POST)
        if form.is_valid():
            try:
                email_object = get_object_or_404(EmailInstance, subject_line=form.cleaned_data['subject_line'])
                email_object.content = form.cleaned_data['content']
                
            except:
                email_object = EmailInstance.objects.create(
                    subject_line = form.cleaned_data['subject_line'],
                    content = form.cleaned_data['content'],
                )
            
            
            email_object.save()
            recipients_list = _get_subscriber_list()
            recipients_count = len(recipients_list)
            from minriver.shop.views import render
            return render(request, 'shop/emails/create_send_email.html', locals())
    else:
        if id:
            email_object = get_object_or_404(EmailInstance, pk=id)
            data = {'subject_line': email_object.subject_line, 'content': email_object.content}
        else:
            data = None
        
        
        form = CreateSendEmailForm(initial=data)
    
    from minriver.shop.views import render
    return render(request, 'shop/emails/create_send_email.html', locals())


@login_required
def send_email(request, id):
    
    
    email_object = get_object_or_404(EmailInstance, pk=id)
    if email_object.date_sent:
        message = "That email message has already been sent"
        return HttpResponse(message)
        
    email_object.date_sent = datetime.now()
    email_object.save()
    
    recipients_list = _get_subscriber_list()
        
    for r in recipients_list:
        receiver = r.email
        subject_line = email_object.subject_line
        try:
            link = reverse('email_unsubscribe', args=[r.slug])
        except:
            link = reverse('email_unsubscribe', args=[r.hashkey])
            
        text = render_to_string('shop/emails/newsletter_template.txt', {'content': email_object.content, 'link':link})
        _send_email(receiver, subject_line, text)
    
    from shop.views import render
    return render(request, 'shop/emails/email_sent_confirmation.html', locals()) 



def _get_subscriber_list():
    email_signups = Subscriber.objects.filter(date_unsubscribed=None)
    
    def idfun(x): return x 
    seen = {}
    result = []
    for item in email_signups:
        marker = idfun(item.email)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    
    return result