from django import forms
from django.forms import ModelForm
from shop.models import Currency, UniqueProduct
    
class UpdateCustomerPackageForm(forms.Form):
    posted = forms.DateTimeField(required=False)
    postage_cost = forms.DecimalField(required=False)
    postage_currency = forms.ChoiceField(required=False, choices=Currency.objects.all())
    
    
class AddStocksForm(forms.Form):
    quantity = forms.IntegerField(required=True)
    unique_product = forms.CharField(required=True)
    batch = forms.CharField(required=True)
    