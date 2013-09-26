from django import forms
from django.forms import ModelForm
from django.contrib.auth.models import User

from minriver.countries import all_countries, COUNTRY_CHOICES

        
class PostageCostForm(forms.Form):
    cost = forms.DecimalField(required=True) 
    order = forms.CharField(required=True)
    
    
class EmailSignupForm(forms.Form):
    email = forms.CharField(required=True)
    
class CreateSendEmailForm(forms.Form):
    subject_line = forms.CharField(required=True)
    content = forms.CharField(required=True, widget=forms.Textarea)
    
