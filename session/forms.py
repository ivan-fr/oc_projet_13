from django import forms
from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    """add email field to the registration form"""

    email = forms.EmailField(max_length=200, required=True)

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')
