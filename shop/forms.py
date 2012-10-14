from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

from captcha.fields import CaptchaField

from minriver.shop.models import Address, Order, Discount, Shopper, Product, Notify, BasketItem
from minriver.countries import all_countries, COUNTRY_CHOICES

 
class AddressAddForm(ModelForm): 
    class Meta:
        model = Address
        exclude = ('owner', 'is_preferred',)
        
            
# handles the submission of their personal details during the order process
class OrderStepOneForm(forms.Form):
    email = forms.EmailField(required=True, 
        error_messages={'required': '* Please give an email address', 'invalid': '* Please enter a valid e-mail address.'})
    first_name = forms.CharField(max_length=200, required=True, error_messages={'required': '* Please give your first name'})
    last_name = forms.CharField(max_length=200, required=True, error_messages={'required': '* Please give your last name'})
    house_name_number = forms.CharField(max_length=200, required=True)
    address_line_1 = forms.CharField(max_length=200, required=False)
    address_line_2 = forms.CharField(max_length=200, required=False)
    town_city = forms.CharField(max_length=200, required=True, error_messages={'required': '* Please provide a town or city name'})
    province_state = forms.CharField(max_length=200, required=False)
    postcode = forms.CharField(max_length=200, required=True)
    country = forms.ChoiceField(required=True, choices=COUNTRY_CHOICES)
    phone = forms.CharField(max_length=80, required=False)
    subscribed = forms.BooleanField(required=False)
    
    def clean(self):
        
        cleaned_data = self.cleaned_data      
        if cleaned_data.get('province_state'):
            if cleaned_data.get('town_city'):
                sep = ', '
            else:
                cleaned_data['town_city'] = ''
                sep = ''
            
            string = ''.join((sep, cleaned_data.get('province_state')))
            cleaned_data["town_city"] =  ''.join((cleaned_data.get('town_city'), string))
            del cleaned_data['province_state']
           
        
        return cleaned_data

class UpdateDiscountForm(forms.Form):
    discount_code = forms.CharField(required=True)

# handles the contact us form
class ContactForm(forms.Form):
    your_name = forms.CharField(required=True)
    your_email = forms.EmailField(required=True, error_messages={'required': 'Please enter a valid email address'})
    your_message = forms.CharField(widget=forms.Textarea, required=False)
    captcha = CaptchaField()

class UpdateProfileForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False, error_messages={'required': 'Please enter a valid email address'})
  
# the form for submitting a tell-a-friend email address
class TellAFriendForm(forms.Form):
    recipient = forms.EmailField(required=True, error_messages={'required': '* You must give an email address for your friend'})
    sender = forms.EmailField(required=True, error_messages={'required': '* You must give your own email address'})
    message = forms.CharField(required=False, widget=forms.Textarea)

# after the user has finished ordering, handles submission of their twitter username
class SubmitTwitterForm(forms.Form):
    twitter_username = forms.CharField()
    
# handles the testimonials or reviews of a particular tea (views.review)
class ReviewForm(forms.Form):
    text = forms.CharField(required=True, widget=forms.Textarea)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    email = forms.EmailField(required=True, error_messages={'required': '* You must give a valid email address'})

class NotifyForm(forms.Form):
    email = forms.EmailField(required=True, error_messages={'required': 'Please enter a valid email address'})
    country = forms.ChoiceField(required=False, choices=all_countries)

class SelectWishlistItemsForm(forms.Form):
    hashkey = forms.CharField()
    items = forms.CharField(required=False)
    

class WishlistSubmitEmailForm(forms.Form):
    email = forms.CharField()
    order = forms.CharField()    
    
class PostageCostForm(forms.Form):
    cost = forms.DecimalField(required=True) 
    order = forms.CharField(required=True)
    
    
class EmailSignupForm(forms.Form):
    email = forms.CharField(required=True)
    
class CreateSendEmailForm(forms.Form):
    subject_line = forms.CharField(required=True)
    content = forms.CharField(required=True, widget=forms.Textarea)




class ValentinesForm(forms.Form):
    email = forms.EmailField(error_messages={'required': '* Please give an email address', 'invalid': '* Please enter a valid e-mail address.'})
    name = forms.CharField(max_length=200, required=True, error_messages={'required': '* Please give your surname'})
    address_line_1 = forms.CharField(max_length=200, required=False)
    address_line_2 = forms.CharField(max_length=200, required=False)
    town_city = forms.CharField(max_length=200, required=False)
    postcode = forms.CharField(max_length=200, required=False)
