# this collects together all of the 'send email' functions just for ease of reference

from django.conf import settings
from django.template import RequestContext, TemplateDoesNotExist
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMultiAlternatives
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.translation import activate, get_language, get_language_from_request

import os
import datetime
import uuid
import re

from shop.models import *
from shop.utils import _render, weight_converter, _apply_deals, _get_basket_value
from emailer.models import Subscriber, Newsletter
from emailer.forms import EmailSignupForm
from shop.forms import CreateSendEmailForm



def _send_email(recipient, subject_line, template, extra_context=None, sender=None, admin=False):
     
    # CREATE THE MESSAGE BODY FROM THE TEMPLATE AND CONTEXT
    extra_context = extra_context or {}
    email_signature = render_to_string(
        'emailer/email_signature.txt', 
        {'site_name': settings.SITE_NAME, 'site_url': settings.SITE_URL,}
    )
    html_email_signature = render_to_string(
        'emailer/email_signature.html', 
        {'site_name': settings.SITE_NAME, 'site_url': settings.SITE_URL,}
    )
    context = {
        'EMAIL_SIGNATURE': email_signature,
        'HTML_EMAIL_SIGNATURE': html_email_signature,
        'static_url': settings.STATIC_URL,
        'SITE_NAME': settings.SITE_NAME,
        'site_name': settings.SITE_NAME,
        'SITE_URL': settings.SITE_URL,
        'site_url': settings.SITE_URL,
        'SUBJECT_LINE': subject_line,
        'email_base_template': settings.EMAIL_BASE_HTML_TEMPLATE
    }
    
    context = dict(context.items() + extra_context.items())
    
    # MODIFY THE RECIPIENTS IF ITS AN ADMIN EMAIL
    if admin:
        recipient = [x[1] for x in settings.NOTIFICATIONS_GROUP]
    else:
        recipient = [recipient]
        
    # WHO IS SENDING IT?
    if sender:
        sender = sender
    else:
        sender = settings.SITE_EMAIL
        
    # CHECK IF THERE'S AN HTML TEMPLATE?
    text_content = render_to_string(template, context)
    html_content = None
    try:
        html_template_name = template.replace('.txt', '.html')
        html_content = render_to_string(html_template_name, context)
    except TemplateDoesNotExist:
        pass
    
    # HERE IS THE ACTUAL MESSAGE NOW
    msg = EmailMultiAlternatives(subject_line, text_content, sender, recipient)    

    
    if html_content:
        # USING PREMAILER TO PUT STYLES INLINE FOR CRAPPY YAHOO AND AOL WHO STRIP STYLES
        from premailer import transform
        html_content = transform(html_content)
        msg.attach_alternative(html_content, "text/html")
        # msg.content_subtype = "html" # DONT DO THIS!
    
    
    
    msg.send()
    return True



def abandoned_basket(order):
    """
    This sends a reminder to someone who abandoned their order 
    halfway through. This means they gave us their details, and
    then just stopped ordering. So, we're emailing them as a reminder
    and giving them a 1-click link.
    """
    
    if not order.hashkey:
        order.hashkey = uuid.uuid1().hex
        order.save()
    
    shopper = order.owner
    activate(shopper.language)
   
    recipient = order.owner.email
    template = 'shop/emails/abandoned_basket.txt'
    subject_line = _("%s - do you want to finish your order?") % settings.SITE_NAME
    
    url = reverse('order_url', args=[order.hashkey])
    extra_context = {
            'url': url,
            'order': order,
    }
    
    _send_email(recipient, subject_line, template, extra_context)
    return True 
    

def product_review(order):
    """
    Sent roughly 3 weeks after someone completes an order
    and asks the customer to review their purchases.
    """
        
    # GET AND PREPARE THE ORDER
    if not order.hashkey:
        order.hashkey = uuid.uuid1().hex
        order.save()
    
    # MAKE SURE IT'S THE CORRECT LANGUAGE
    activate(order.owner.language)

    # NOW PREPARE THE EMAIL CONTEXT
    subject_line = _("%s - please give us your thoughts!") % settings.SITE_NAME
    recipient = order.owner.email
    template = 'shop/emails/review_order.txt'
    extra_context = {
        'order': order,
        'url': reverse('review_order', args=[order.hashkey]),
     }
    
    _send_email(recipient, subject_line, template, extra_context)
    return True


def _admin_notify_new_review(tea, review):
    
    extra_context = {'text': "%s %s just posted a review of %s - %s" % (review.first_name, review.last_name, tea.name, settings.SITE_URL), }              
    subject_line = "New Review Posted - %s - %s" % (tea.name, settings.SITE_NAME) 
    recipient = settings.SITE_EMAIL
    template = 'shop/emails/blank.txt'
    
    _send_email(recipient, subject_line, template, extra_context, admin=True)    
    return


def _admin_notify_contact(data):

    recipient = settings.SITE_EMAIL
    subject_line = "%s - Website Contact Submission" % settings.SITE_NAME
    template = 'shop/emails/contact_template.txt'
    extra_context = {
    	 'message': data['your_message'],
      	 'your_email': data['your_email'],
      	 'your_name': data['your_name'],
    }

    _send_email(recipient, subject_line, template, extra_context, admin=True)    
    return



def _reorder_email(order):

    activate(order.owner.language)

    if not order.hashkey:
        order.hashkey = uuid.uuid1().hex
        order.save()
            
    template = "shop/emails/reorder_email.txt"
    recipient = order.owner.email
    subject_line = _("Have you finished your tea yet?")
    
    url = "".join((settings.SITE_URL, reverse('order_repeat', args=[order.hashkey])))
    extra_context = {
        'url': url,
        'order': order,	
    }
    
    _send_email(recipient, subject_line, template, extra_context)    
    return True # important, make sure this returns True



def _admin_cron_update(data, subject_line):
    
    subject_line = subject_line
    recipient = settings.SITE_EMAIL
    template = 'shop/emails/admin_cron_update.txt'
    extra_context = {
        'data': data,	
    }
        
    _send_email(recipient, subject_line, template, extra_context, admin=True)


def _payment_success(order):
    """
    Sends an email to a customer immediately after they successfully complete
    an order on the site. Also sends a confirmation email to the Admins
    """
    
    # PREPARE THE EMAIL INFORMATION
    recipient = order.owner.email
    activate(order.owner.language)
    subject_line = _("Order Confirmed - %(id)s - %(site)s") % {
        'id':order.invoice_id, 
        'site': settings.SITE_NAME,
    }
    template = 'shop/emails/order_confirm_customer.txt'
    
    # PREPARE THE ORDER
    if order.address.country == 'US':
        weight_unit = 'oz'
    else:
        weight_unit = 'g'
        
    basket = _get_basket_value(order=order)
    print basket
    
    for item in basket['basket_items']:
        if item.item.weight:
            if order.address.country == 'US':
                item.weight = weight_converter(item.item.weight)
            else:
                item.weight = item.item.weight
        else:
            item.weight = None
            
    
    extra_context = {
        'order': order,
        'items': basket['basket_items'],
        'currency': basket['currency'],
        'total_price': basket['total_price'],
        'discount': basket['discount'],
        'postage_discount': basket['postage_discount'],
        'weight_unit': weight_unit,
    }
    
    _send_email(recipient, subject_line, template, extra_context)
    
     
    # ADMIN EMAIL (reset some of the values!!)
    recipient = settings.SITE_EMAIL
    lang = activate('en')
    template = 'shop/emails/order_confirm_admin.txt'
    _send_email(recipient, subject_line, template, extra_context, admin=True)
    
    return True



def _payment_flagged(order):
    """
    Does the same as a normal payment email, but sends a 
    flagged order notification to the admin. The customer 
    doesn't see anything different, but admin gets a chance
    to check the order for irregularities.
    """
    # CUSTOMER GETS THEIR EMAIL AS NORMAL
    recipient = order.owner.email
    activate(order.owner.language)
    subject_line = _("Order Confirmed - %(id)s - %(site)s") % {
        'id': order.invoice_id, 
        'site': settings.SITE_NAME
    }
    
    if order.address.country == 'US':
        weight_unit = 'oz'
    else:
        weight_unit = 'g'
    
    items = order.items.all()
    for item in items:
        if item.item.weight:
            if order.address.country == 'US':
                item.weight = weight_converter(item.item.weight)
            else:
                item.weight = item.item.weight
        else:
            item.weight = None
        
    template = 'shop/emails/order_confirm_customer.txt'
    extra_context = {
        'order': order,
        'items': items,
        'weight_unit': weight_unit,
    }
    
    _send_email(recipient, subject_line, template, extra_context)

    # ADMIN GETS WARNING ABOUT FLAGGED ORDER.
    recipient = settings.SITE_EMAIL
    template = 'shop/emails/order_confirm_admin.txt'
    extra_context = {'order': order}
    subject_line = "FLAGGED ORDER - %s" % order.invoice_id 
      
    _send_email(recipient, subject_line, template, extra_context, admin=True)
    return
    

def email_signup(request):
    if request.method == 'POST':
        form = EmailSignupForm(request.POST)
        if form.is_valid():
                        
            try:
                existing_signup = get_object_or_404(Subscriber, email=form.cleaned_data['email'])
                message = _("<h3>Looks like you're already signed up! You don't need to do anything else, and you'll receive TEAMails as normal.</h3>")
            except:
                new_signup = Subscriber.objects.create(
                    email = form.cleaned_data['email'],
                    date_signed_up = datetime.now(),
                    language=get_language(),
                    confirmed=True, # TODO - change this so that an email gets sent off immediately asking them to confirm
                )
                new_signup.save()
                message = _("<h3>Awesome! You're now signed up to receive TEAMails - they're roughly fortnightly, and you can unsubscribe at any time by clicking the link in the email.</h3>")
            
            if request.is_ajax():
                return HttpResponse(message)
            
            else:
                return _render(request, 'shop/emails/signup_confirmed.html', locals())
                    
    else:
        form = EmailSignupForm()
    
    url = request.META.get('HTTP_REFERER','/')
    return HttpResponseRedirect(url)
    


def _get_subscriber_list():
    email_signups = Subscriber.objects.filter(
        date_unsubscribed__isnull=True,     # only those who have nothing for the unsubscribed field
    ).exclude(
        language='de',                      # excluding German language signups for now
    )
    
    
    def idfun(x): return x 
    seen = {}
    result = []
    for item in email_signups:
        if item.hashkey == None:
            item.hashkey = uuid.uuid1().hex
            item.save()
        marker = idfun(item.email)
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    
    return result
