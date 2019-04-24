from django.contrib.auth.forms import UserCreationForm
from django import forms


class CustomUserCreationForm(UserCreationForm):
    """add email field to the registration form"""
    email = forms.EmailField(max_length=200, help_text='Required')

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')
