from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.http import HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.views.generic import CreateView

from session.forms import CustomUserCreationForm
from session.tokens import account_activation_token


class SignupView(CreateView):
    """ render signup page """

    form_class = CustomUserCreationForm
    success_url = '/'
    model = User

    def form_valid(self, form):
        """If the form is valid, save the associated model."""
        self.object = form.save(commit=False)
        self.object.is_active = False
        self.object.save()

        current_site = get_current_site(self.request)
        mail_subject = 'Activate your blog account.'
        message = render_to_string('auth/acc_active_mail.html', {
            'user': self.object,
            'domain': current_site.domain,
            'uid': force_text(
                urlsafe_base64_encode(force_bytes(self.object.pk))
            ),
            'token': account_activation_token.make_token(self.object),
        })

        email = EmailMessage(
            mail_subject, message, to=[self.object.email]
        )
        email.send()

        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Création de compte réussie !'
                                       ' Veuillez confirmer votre email.')
        return super(SignupView, self).get_success_url()


class CustomLoginView(SuccessMessageMixin, LoginView):
    """ render login page """

    success_message = "Vous êtes connecté !"
    redirect_authenticated_user = True


def activate(request, uidb64, token):
    """ activate an account by mail """
    uid = force_text(urlsafe_base64_decode(uidb64))
    user = User.objects.get(pk=uid)

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        messages.success(request, 'Compte activé.')
        return HttpResponseRedirect(reverse('index'))
    else:
        return HttpResponse('Activation link is invalid!')
