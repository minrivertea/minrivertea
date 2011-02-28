from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

from minriver.shop.models import Address, Order, Discount, Shopper
 
 
 
 
class AddressAddForm(ModelForm): 
    class Meta:
        model = Address
        exclude = ('owner', 'is_preferred',)
            
    
class OrderCheckDetailsForm(forms.Form):
    email = forms.EmailField(error_messages={'required': '* Please give an email address', 'invalid': '* Please enter a valid e-mail address.'})
    first_name = forms.CharField(max_length=200, required=True, error_messages={'required': '* Please give your first name'})
    last_name = forms.CharField(max_length=200, required=True, error_messages={'required': '* Please give your surname'})
    house_name_number = forms.CharField(max_length=200, required=False)
    address_line_1 = forms.CharField(max_length=200, required=False)
    address_line_2 = forms.CharField(max_length=200, required=False)
    town_city = forms.CharField(max_length=200, required=False)
    postcode = forms.CharField(max_length=200, required=False)
    subscribed = forms.BooleanField(required=False)
    
    def clean(self):
        cleaned_data = self.cleaned_data
        postcode = cleaned_data.get("postcode")
        house_name_number = cleaned_data.get("house_name_number")
        if not postcode:
             if not house_name_number:
                 raise forms.ValidationError("* You must provide a postcode and house name or number")
             else:
                 raise forms.ValidationError("* You must provide a postcode")
        
        if not house_name_number:
                raise forms.ValidationError("* You must provide a house name or number")
        
        
        return cleaned_data
    

class UpdateDiscountForm(forms.Form):
    discount = forms.CharField(required=False, error_messages={'required': 'Please choose a star rating'})
    
    def clean_discount(self):
        discount = self.cleaned_data['discount']
        if discount:
            d = Discount.objects.filter(discount_code=self.cleaned_data['discount'])
            if not d:
                raise forms.ValidationError("That's not a valid discount code")
        else: 
            pass
        
        return discount


class UpdateProfileForm(forms.Form):
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    email = forms.EmailField(required=False, error_messages={'required': 'Please enter a valid email address'})
    
class PhotoUploadForm(forms.Form):
    photo = forms.ImageField()
    email = forms.EmailField()
    first_name = forms.CharField(max_length=200, error_messages={'required': 'You must give your first name'})
    last_name = forms.CharField(max_length=200, error_messages={'required': 'You must give your last name'})
    description = forms.CharField(widget=forms.Textarea, required=False)

class TellAFriendForm(forms.Form):
    recipient = forms.EmailField(required=True, error_messages={'required': '* You must give an email address for your friend'})
    sender = forms.EmailField(required=True, error_messages={'required': '* You must give your own email address'})
    message = forms.CharField(required=False, widget=forms.Textarea)
    