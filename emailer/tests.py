
from django.test import TestCase
from django.core import mail
from django.core.urlresolvers import reverse
from django.test.client import Client

from django.utils import translation

from shop.models import Order
from emailer.views import _payment_success_email
from emailer.models import Subscriber


class EmailsTestCase(TestCase):
    
    fixtures = ['testdata.xml']    

    def test_order_reminder_email(self):
        """Send order reminder email"""
        
        # test in English
        order = Order.objects.filter(is_paid=False, is_giveaway=False, reminder_email_sent=False).order_by('?')[0]
        response = self.client.get(reverse('send_reminder_email', args=[order.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, 'Was it something we said?')
        mail.outbox = []
        
        
        # now test in German
        translation.activate('de')
        order = Order.objects.filter(owner__language='de').order_by('?')[0]
        response = self.client.get(reverse('send_reminder_email', args=[order.id]))
        self.assertEqual(response.status_code, 302)
        self.assertEquals(len(mail.outbox), 1)
        self.assertEquals(mail.outbox[0].subject, 'War es etwas, was wir gesagt haben?')      



    def test_payment_success_email(self):
        """Send order confirmation email"""
        
        order = Order.objects.filter(is_paid=False, is_giveaway=False, reminder_email_sent=False).order_by('?')[0]
        self.assertEqual(_payment_success_email(order), True)
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[0].subject, 'Order confirmed - minrivertea.com')
        mail.outbox = []
        
        translation.activate('de')
        order = Order.objects.filter(owner__language='de').order_by('?')[0]
        self.assertEqual(_payment_success_email(order), True)
        self.assertEquals(len(mail.outbox), 2)
        self.assertEquals(mail.outbox[0].subject, 'Order confirmed - minrivertea.com')
    
    
    def test_email_signup(self):
    
        data = dict(email='johnny@walker.com',)
        url = reverse('email_signup')
        
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        signup = Subscriber.objects.filter(email=data['email'])[0]
        self.assertEquals(signup.language, 'en')
        
        
        











