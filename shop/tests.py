

from django.test import TestCase

from shop.models import UniqueProduct


class OrderTestCase(TestCase):
    
    fixtures = ['shop_testdata.json']

    def test_add_to_basket(self):
        """try to add something to a basket """
        print "Testing add_to_basket"
        up = UniqueProduct.objects.filter(is_active=True).order_by('?')[0]
        
        url = reverse('add_to_basket', args[up.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        print "   works!"
    
    def test_remove_from_basket(self):
        """try to remove something from basket"""
        up = UniqueProduct.objects.filter(is_active=True).order_by('?')[0]
        url = reverse('remove_from_basket', args=[up.id])
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
        
        