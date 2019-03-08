from django.contrib.auth.forms import UserCreationForm


class CustomUserCreationForm(UserCreationForm):
    """add email field to the registration form"""

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email')
