#!/usr/bin/python
# -*- coding: utf-8 -*-


from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from shop.models import UniqueProduct, Category, Product, Basket, BasketItem


class OrderTestCase(TestCase):
    
    fixtures = ['testdata.json']    

    def test_home(self):
        """Check that the homepage is working"""
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        

    def test_categories(self):
        """Just try to view the categories"""
        
        categories = Category.objects.all()
        for x in categories:
            url = x.get_absolute_url()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    
    def test_products(self):
        """Try and view all the products and make sure there's no errors"""
        
        products = Product.objects.filter(is_active=True)
        for x in products:
            url = x.get_absolute_url()
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)
    
            
        
        
        
    def test_order_process(self):
        
        """ Go through the entire order process and test"""
        
        # ADD SOMETHIGN TO THE BASKET
        unique_product = UniqueProduct.objects.filter(is_active=True, currency__code='GBP').order_by('?')[0]
        r = self.client.get(reverse('add_to_basket', args=[unique_product.id]))
        self.assertEqual(r.status_code, 302)
        
        # GO TO THE BASKET PAGE
        r = self.client.get(reverse('basket'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['basket_quantity'], 1)
        self.assertTrue('Your basket (1 item)' in r.content)
        
        
        # SWITCH TO USD
        r = self.client.get("".join((reverse('set_currency'), '?curr=USD')))
        self.assertEqual(r.status_code, 302)
        
        # SWITCH TO EUR
        r = self.client.get("".join((reverse('set_currency'), '?curr=EUR')))
        self.assertEqual(r.status_code, 302)
        
        
        # MAKE SURE BASKET ITEMS ARE IN NEW CURRENCY
        r = self.client.get(reverse('basket'))
        self.assertTrue(self.client.session['BASKET_ID'] != None)
        basket = Basket.objects.get(id=self.client.session['BASKET_ID'])
        basket_items = BasketItem.objects.filter(basket=basket)
        for x in basket_items:
            self.assertEqual(x.item.currency.code, 'EUR')
        
        
        # REVERT TO GBP
        r = self.client.get("".join((reverse('set_currency'), '?curr=GBP')))        
        
        # HEAD TO ORDER_STEP_ONE
        r = self.client.get(reverse('order_step_one'))   
        self.assertEqual(r.status_code, 200)
        self.assertTrue(self.client.session['BASKET_ID'] != None)
        self.assertTrue('This just takes 1 minute - your name and email please!' in r.content)
        
        # POST SOME INCORRECT DATA
        user_data = {
            'first_name': "Hanson",
            'last_name': "O'Reilly",
            'email': 'fake @ email.com',
            'house_name_number': '',
            'address_line_1': '',
            'address_line_2': '',
            'town_city': '',
            'postcode': '',
            'country': 'united kingdom',
        }
        
        r = self.client.post(reverse('order_step_one'), user_data)
        self.assertTrue('* Please enter all the information in the mandatory fields (highlighted red) below:' in r.content)
        
        # POST CORRECT DATA
        user_data['email'] = 'fake@email.com'
        user_data['house_name_number'] = '123 Fine Street'
        user_data['town_city'] = 'Londinium'
        user_data['postcode'] = 'E2 8AB'
        
        r = self.client.post(reverse('order_step_one'), user_data)
        self.assertEqual(r.status_code, 200)
        
        # REFRESH THE PAGE AND CHECK WE HAVE AN ORDER AND SHOPPER NOW
        r = self.client.get(reverse('order_confirm'))
        self.assertTrue(self.client.session['ORDER_ID'] != None)
        
        print self.client.session['ORDER_ID']
        
        self.assertTrue(len(Order.objects.filter(pk=self.client.session['ORDER_ID'])) > 0)
        self.assertTrue(len(Shopper.objects.filter(user__email=data['email'])) > 0)
        
        # TODO - go back and add a discount
        # TODO - try to pay / check paypal
        # TODO - change languages?
        