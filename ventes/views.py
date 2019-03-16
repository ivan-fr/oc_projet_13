import json

import urllib.parse

from django.views.generic.dates import ArchiveIndexView, MonthArchiveView, \
    YearArchiveView
from django.views.generic import TemplateView, DetailView
from django.core import signing
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import F, Sum, FloatField
from django.http import Http404
from django.urls import reverse
from django.conf import settings
from django.core.signing import Signer

from paypal.standard.forms import PayPalPaymentsForm

from catalogue.models import Meeting
from ventes.models import Commande, CommandeMeeting
from extra_views import FormSetView
from ventes.forms import CommandeForm


class CommandeFormsetView(FormSetView):
    form_class = CommandeForm
    factory_kwargs = {'extra': 0, 'max_num': 3, 'validate_max': True,
                      'min_num': 1, 'validate_min': True,
                      'can_order': False, 'can_delete': False}
    template_name = 'ventes/commande_formset.html'

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            self.initial = json.loads(
                request.GET.get('initial_formset_commande'))
            sign = signing.dumps(self.initial)

            ids = tuple(set(_dict['id'] for _dict in self.initial))
            meetings = dict(
                Meeting.objects.filter(pk__in=ids).values_list('pk', 'price'))
            meetings = {str(key): value for key, value in meetings.items()}

            formset = self.construct_formset()
            return self.render_to_response(
                self.get_context_data(formset=formset, meetings=meetings,
                                      sign=sign))
        else:
            raise Http404("Request have to be ajax.")

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        self.initial = signing.loads(request.POST.get('form-sign'))
        return super(CommandeFormsetView, self).post(request, *args, **kwargs)

    def formset_valid(self, formset):
        data = {}
        for cleaned_data in formset.cleaned_data:
            try:
                data[cleaned_data['id']] \
                    .append(
                    {'date_meeting': cleaned_data['date'],
                     'quantity': cleaned_data['count']})
            except KeyError:
                data[cleaned_data['id']] = [{
                    'date_meeting': cleaned_data['date'],
                    'quantity': cleaned_data['count']
                }]

        with transaction.atomic():
            commande = Commande.objects.create(
                user=self.request.user
            )

            for key, dicts in data.items():
                commandes_meetings = []
                meeting = Meeting.objects.get(pk=key)
                for _dict in dicts:
                    commandes_meetings.append(CommandeMeeting(
                        from_commande=commande,
                        to_meeting=meeting,
                        **_dict))

                CommandeMeeting.objects.bulk_create(commandes_meetings)

        self.success_url = reverse(
            'ventes:show-commande',
            kwargs={
                'commande_pk': commande.pk,
            }
        ) + '?' + urllib.parse.urlencode({
            'from_accepted_command': True
        })

        return super(CommandeFormsetView, self).formset_valid(formset)


class CommandeTemplateView(TemplateView):
    template_name = 'ventes/commande.html'


class CommandeMixinView(object):
    model = Commande
    date_field = 'date'
    paginate_by = 4
    make_object_list = True
    allow_empty = True

    def get_queryset(self):
        queryset = super(CommandeMixinView, self).get_queryset()
        return queryset.filter(user=self.request.user) \
            .prefetch_related("from_commande", 'from_commande__to_meeting') \
            .annotate(total_price=Sum(F('from_commande__quantity')
                                      * F('from_commande__to_meeting__price'),
                                      output_field=FloatField()))


class CommandeArchiveView(CommandeMixinView, ArchiveIndexView):
    pass


class CommandeYearArchiveView(CommandeMixinView, YearArchiveView):
    pass


class CommandeMonthArchiveView(CommandeMixinView, MonthArchiveView):
    month_format = "%m"


class CommandeView(DetailView):
    model = Commande
    pk_url_kwarg = 'commande_pk'

    def get_queryset(self):
        queryset = super(CommandeView, self).get_queryset()
        queryset = queryset.prefetch_related("from_commande",
                                             'from_commande__to_meeting') \
            .annotate(total_price=Sum(F('from_commande__quantity')
                                      * F('from_commande__to_meeting__price'),
                                      output_field=FloatField()))
        return queryset

    def get_object(self, queryset=None):
        obj = super(CommandeView, self).get_object(queryset)
        if not self.request.user == obj.user:
            raise Http404('Page inconnue.')
        return obj

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = None

        if not self.object.payment_status:
            signer = Signer()
            # What you want the button to do.
            paypal_dict = {
                "business": settings.PAYPAL_RECEIVER_EMAIL,
                "amount": self.object.total_price,
                "item_name": "Billetterie commande #" + str(self.object.pk)
                             + " " + str(self.object.date),
                "notify_url": request.build_absolute_uri(reverse('paypal-ipn')),
                "return": request.build_absolute_uri(
                    reverse('ventes:commande-success',
                            kwargs={'commande_pk': self.object.pk}
                            )
                ),
                "cancel_return": request.build_absolute_uri(
                    reverse('ventes:show-commande',
                            kwargs={'commande_pk': self.object.pk}
                            )
                ),
                "custom": signer.sign(self.object.pk),
                "currency_code": "EUR"
                # Custom command to correlate to some function later (optional)
            }

            # Create the instance.
            form = PayPalPaymentsForm(initial=paypal_dict)

        context = self.get_context_data(
            paypal_form=form,
            object=self.object,
            from_accepted_command=request.GET.get('from_accepted_command',
                                                  False)
        )
        return self.render_to_response(context)


class CommandePaymentSuccesTemplateView(TemplateView):
    template_name = 'ventes/commande_success.html'
