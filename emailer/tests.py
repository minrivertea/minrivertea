
from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.client import Client
from django.conf import settings

from django.utils import translation
from django.utils.translation import ugettext as _


from shop.models import Order
from emailer.views import _payment_success, abandoned_basket, product_review
from emailer.models import Subscriber



class EmailsTestCase(TestCase):
    
    fixtures = ['testdata2.json']
    
    def test_abandoned_basket_email(self):
        """ Make sure the abandoned basket email is being sent correctly"""
        
        # GET AN UNPAID ORDER IN ENGLISH
        order = Order.objects.filter(owner__language='en', reminder_email_sent=False, date_paid__isnull=False).order_by('?')[0]
        
        # TEST IT            
        self.assertEqual(abandoned_basket(order.pk), True)
        self.assertEquals(len(mail.outbox), 1)
        email_subject_line = _("Do you want to finish your order on %s?") % settings.SITE_NAME
        self.assertEquals(mail.outbox[0].subject, email_subject_line)      
        mail.outbox = []
        
        
        # GET A GERMAN ORDER
        translation.activate('de')
        order = Order.objects.filter(owner__language='de', reminder_email_sent=False, date_paid__isnull=False).order_by('?')[0]
        
        # TEST AGAIN IN GERMAN
        self.assertEqual(abandoned_basket(order.pk), True)
        self.assertEquals(len(mail.outbox), 1)
        # self.assertEquals(mail.outbox[0].subject, 'War es etwas, was wir gesagt haben?')      
        mail.outbox = []



    def test_product_review_email(self):
        """ Check the review email sent after an order is placed """
        # GET AN ORDER:
        order = Order.objects.filter(date_paid__isnull=False).order_by('?')[0]
        
        # TEST THE EMAIL IN ENGLISH
        self.assertEqual(product_review(order.id), True)
        self.assertEquals(len(mail.outbox), 1)
        email_subject_line = _("Please review your purchase at %s") % settings.SITE_NAME
        self.assertEquals(mail.outbox[0].subject, email_subject_line)
        mail.outbox = []



    def test_payment_success_email(self):
        """Send order confirmation email"""
        
        
        # GET AN ORDER
        order = Order.objects.filter(
            date_paid__isnull=False, 
            is_giveaway=False).order_by('?')[0]
        
        # TEST IT
        self.assertEqual(_payment_success(order), True)
        self.assertEquals(len(mail.outbox), 2)
        # self.assertEquals(mail.outbox[0].subject, 'Order confirmed - minrivertea.com')
        mail.outbox = []
        
        # TEST IN GERMAN
        translation.activate('de')
        order = Order.objects.filter(owner__language='de').order_by('?')[0]
        self.assertEqual(_payment_success(order), True)
        self.assertEquals(len(mail.outbox), 2)
        # self.assertEquals(mail.outbox[0].subject, 'Order confirmed - minrivertea.com')
    
 








