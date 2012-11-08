from django import forms


class EmailSignupForm(forms.Form):
    email = forms.CharField(required=True)