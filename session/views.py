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
from django.views.generic import CreateView, ListView, DetailView
from django.views.generic.edit import FormMixin
from django.http import Http404
from django.db.models import Count, Q, F

from session.forms import CustomUserCreationForm
from session.tokens import account_activation_token

from session.models import Thread, ChatMessage
from session.forms import ComposeForm


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


class WhoIsOnlineView(ListView):
    model = User
    allow_empty = True
    paginate_by = 10

    def get_queryset(self):
        queryset = super(WhoIsOnlineView, self).get_queryset()
        queryset.filter(is_superuser=True)
        return queryset


class ThreadView(DetailView, FormMixin):
    form_class = ComposeForm
    success_url = None

    def get_queryset(self):
        return Thread.objects.by_user(self.request.user)

    def get_object(self, queryset=None):
        other_username = self.kwargs.get("username")
        obj, created = Thread.objects.get_or_new(self.request.user, other_username)
        if obj is None:
            raise Http404()
        return obj

    def get_context_data(self, **kwargs):
        if self.object.first == self.request.user:
            kwargs['user_recipient'] = self.object.second
        else:
            kwargs['user_recipient'] = self.object.first

        return super().get_context_data(**kwargs)

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        thread = self.get_object()
        user = self.request.user
        message = form.cleaned_data.get("message")
        ChatMessage.objects.create(user=user, thread=thread, message=message)
        if self.request.user == thread.second:
            self.success_url = reverse(
                'session:thread',
                kwargs={
                    'username': thread.first.username,
                })
        else:
            self.success_url = reverse(
                'session:thread',
                kwargs={
                    'username': thread.second.username,
                })
        return super().form_valid(form)


class InboxView(ListView):
    model = Thread

    def get_queryset(self):
        return self.model.objects.by_user(self.request.user).annotate(
            nb_message_not_me=Count(F("chatmessage"),
                                    filter=~Q(chatmessage__user=self.request.user)),
            nb_message=Count(F("chatmessage"))
        )
