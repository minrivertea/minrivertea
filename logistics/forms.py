from django import forms
from django.forms import ModelForm
from shop.models import Currency
    
class UpdateCustomerPackageForm(forms.Form):
    posted = forms.DateTimeField(required=False)
    postage_cost = forms.DecimalField(required=False)
    postage_currency = forms.ChoiceField(required=False, choices=Currency.objects.all())
    
    