from django import forms
from django.forms import ModelForm
from shop.models import Currency, UniqueProduct
from django.contrib.admin import widgets
    
class UpdateCustomerPackageForm(forms.Form):
    posted = forms.DateTimeField(required=False)
    postage_cost = forms.DecimalField(required=False)
    postage_currency = forms.ChoiceField(required=False, choices=Currency.objects.all())
    
    
class AddStocksForm(forms.Form):
    quantity = forms.IntegerField(required=True)
    produced = forms.DateTimeField(required=False)
    unique_product = forms.ModelChoiceField(required=True, 
        queryset=UniqueProduct.objects.filter(is_active=True, currency__code='GBP'),
    )
    batch = forms.CharField(required=True)
    
    def __init__(self, *args, **kwargs):
        super(AddStocksForm, self).__init__(*args, **kwargs)
        self.fields['produced'].widget = widgets.AdminSplitDateTime()
    