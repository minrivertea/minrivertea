
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.test.client import Client

from shop.models import UniqueProduct


class OrderTestCase(TestCase):
    
    fixtures = ['testdata.xml']    

    def test_add_basket_items(self):
        """Try to add something to a basket """

        up = UniqueProduct.objects.filter(is_active=True).order_by('?')[0]
        
        # try add something to the basket
        url = reverse('add_to_basket', args=[up.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        response = self.client.get('/')
        self.assertEqual(response.context['basket_quantity'], 1)
    
    def test_view_basket(self):
        """Try to view the basket page"""
        # first viewing it without any items in basket
        url = reverse('basket')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        
        # now add something to basket and view again
        up = UniqueProduct.objects.filter(is_active=True).order_by('?')[0]
        url = reverse('add_to_basket', args=[up.id])
        response = self.client.get(url)
        
        url = reverse('basket')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
    

      
        
        
        """
        data = dict(email='alexandra.byrnes @ thechilternrailways.co.uk',
                    password1='secret', password2='different',
                    first_name='Alexandra',
                    last_name='',
                    )
        response = self.client.post(url, data)
        assert response.status_code == 200
        self.assertTrue('You must agree to the terms to register' in response.content)
        self.assertTrue('You must type the same password each time' in response.content)
        self.assertTrue('This field is required' in response.content) # last name
        self.assertTrue('Enter a valid e-mail address' in response.content)
        
        data['email'] = 'alexandra.byrnes@thechilternrailways.co.uk'
        data['password2'] = 'secret'
        data['last_name'] = 'Byrnes'
        data['tos'] = 'true'
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['Location'].endswith(reverse('registration_complete')))
        """
        
        