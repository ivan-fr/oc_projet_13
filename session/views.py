from django.views.generic import CreateView
from django.contrib.auth.views import LoginView
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin

from session.forms import CustomUserCreationForm


class SignupView(CreateView):
    """ render signup page """

    form_class = CustomUserCreationForm
    success_url = '/'
    model = User

    def get_success_url(self):
        messages.success(self.request, 'Création de compte réussie !')
        return super(SignupView, self).get_success_url()


class CustomLoginView(SuccessMessageMixin, LoginView):
    """ render login page """

    success_message = "Vous êtes connecté !"
    redirect_authenticated_user = True
