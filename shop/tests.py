#!/usr/bin/python
# -*- coding: utf8 -*-


from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from shop.models import UniqueProduct, Category, Product, Basket, BasketItem


class OrderTestCase(TestCase):
    
    fixtures = ['testdata.xml']    

    def test_home(self):
        """Check that the homepage is working"""
        url = reverse('home')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        

    def test_view_categories(self):
        """Just try to view the categories"""
        url = reverse('teas')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        url = reverse('teaware')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        url = reverse('green_tea')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        url = reverse('red_tea')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        url = reverse('white_tea')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        url = reverse('oolong_tea')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        url = reverse('tea_boxes')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        url = reverse('tasters')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

        
    def test_order_process(self):
        
        # view a product page
        prod = Product.objects.filter(is_active=True).order_by('?')[0]
        r = self.client.get(reverse('tea_view', args=[prod.slug]))
        self.assertEqual(r.status_code, 200)
        
        # add something to the basket
        up = UniqueProduct.objects.filter(is_active=True, parent_product=prod, currency__code='GBP')[0]
        baseline_price = up.price
        r = self.client.get(reverse('add_to_basket', args=[up.id]))
        self.assertEqual(r.status_code, 302)
        
        
        # go to the basket page
        r = self.client.get(reverse('basket'))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['basket_quantity'], 1)
        self.assertTrue('Your basket (1 item)' in r.content)
        
        # switch the currencies a few times
        r = self.client.get('/currency/?curr=USD')
        self.assertEqual(r.status_code, 302)
        self.assertTrue('$' in r.content)
        r = self.client.get('/currency/?curr=EUR')
        self.assertEqual(r.status_code, 302)
        self.assertTrue('€' in r.content)
        
        # MAKE SURE BASKET ITEMS ARE IN NEW CURRENCY
        r = self.client.get(reverse('basket'))
        self.assertTrue(self.client.session['BASKET_ID'] != None)
        basket = Basket.objects.get(id=self.client.session['BASKET_ID'])
        basket_items = BasketItem.objects.filter(basket=basket)
        for x in basket_items:
            self.assertEqual(x.item.currency.code, 'EUR')
            self.assertTrue(x.item.price > baseline_price)
        
        # REVERT TO GBP
        r = self.client.get('/currency/?curr=GBP')        
        
        # HEAD TO ORDER_STEP_ONE
        r = self.client.get(reverse('order_step_one'))   
        self.assertEqual(response.status_code, 200)
        self.assertTrue(self.client.session['BASKET_ID'] != None)
        self.assertTrue('This just takes 1 minute - your name and email please!' in response.content)
        
        # POST SOME INCORRECT DATA
        data = dict(
            first_name="Hanson",
            last_name="O'Reilly",
            email='fake @ email.com',
            house_name_number='',
            address_line_1='',
            address_line_2='',
            town_city='',
            postcode='',
            country='united kingdom',
        )
        response = self.client.post(reverse('order_step_one'), data)
        self.assertTrue('* Please enter all the information in the mandatory fields (highlighted red) below:' in response.content)
        
        # POST CORRECT DATA
        data['email'] = 'fake@email.com'
        data['house_name_number'] = '123 Fine Street'
        data['town_city'] = 'Londinium'
        data['postcode'] = 'E2 8AB'
        r = self.client.post(reverse('order_step_one', data))
        self.assertEqual(r.status_code, 302)
        self.assertTrue("You don't have any items in your basket" not in r.content)
        
        # REFRESH THE PAGE AND CHECK WE HAVE AN ORDER AND SHOPPER NOW
        r = self.client.get(reverse('order_confirm'))
        self.assertTrue(self.client.session['ORDER_ID'] != None)
        self.assertTrue(len(Order.objects.filter(pk=self.client.session['ORDER_ID'])) > 0)
        self.assertTrue(len(Shopper.objects.filter(user__email=data['email'])) > 0)
        
        # TODO - go back and add a discount
        
        # TODO - try to pay / check paypal
        
        # TODO - change languages?
        