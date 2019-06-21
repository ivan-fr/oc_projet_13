import itertools
import json
import urllib.parse
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core import signing
from django.core.signing import Signer
from django.db import transaction
from django.db.models import F, Sum, FloatField, DecimalField
from django.db.models import Q
from django.db.models.functions import Coalesce, ExtractDay, ExtractMonth, \
    ExtractYear
from django.http import Http404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView, DetailView
from django.views.generic.dates import ArchiveIndexView, MonthArchiveView, \
    YearArchiveView
from extra_views import FormSetView
from paypal.standard.forms import PayPalPaymentsForm

from catalogue.models import Meeting
from ventes.forms import CommandeForm
from ventes.models import Commande, CommandeMeeting


class CommandeFormsetView(FormSetView):
    """Render the formset of a commmand"""

    form_class = CommandeForm
    factory_kwargs = {'extra': 0, 'max_num': 3, 'validate_max': True,
                      'min_num': 1, 'validate_min': True,
                      'can_order': False, 'can_delete': False}
    template_name = 'ventes/commande_formset.html'

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            self.initial = json.loads(
                request.GET.get('initial_formset_commande', '[]'))
            sign = signing.dumps(self.initial)

            ids = tuple(set(int(_dict['id']) for _dict in self.initial))
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
        self.extra_context = {
            'not_panier': True
        }
        self.template_name = 'ventes/commande_formset_post.html'
        self.initial = signing.loads(request.POST.get('form-sign'))
        return super(CommandeFormsetView, self).post(request, *args, **kwargs)

    def formset_invalid(self, formset):
        self.initial = signing.loads(self.request.POST.get('form-sign'))

        sign = signing.dumps(self.initial)

        ids = tuple(set(_dict['id'] for _dict in self.initial))
        meetings = dict(
            Meeting.objects.filter(pk__in=ids).values_list('pk', 'price'))
        meetings = {str(key): value for key, value in meetings.items()}

        return self.render_to_response(
            self.get_context_data(formset=formset, meetings=meetings,
                                  sign=sign))

    def formset_valid(self, formset):
        data = {}
        for cleaned_data in formset.cleaned_data:
            try:
                data[cleaned_data['id']] \
                    .append(
                    {'date_meeting': cleaned_data['date'],
                     'quantity': cleaned_data['quantity']})
            except KeyError:
                data[cleaned_data['id']] = [{
                    'date_meeting': cleaned_data['date'],
                    'quantity': cleaned_data['quantity']
                }]

        with transaction.atomic():
            commande = Commande.objects.create(
                user=self.request.user
            )

            for pk, dicts in data.items():
                commandes_meetings = []
                meeting = Meeting.objects.get(pk=pk)
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
    """ Render the command templates """
    template_name = 'ventes/commande.html'
    extra_context = {
        'not_panier': True
    }


class CommandeMixinView(object):
    """ Commande mixin class """
    model = Commande
    date_field = 'date'
    paginate_by = 4
    make_object_list = True
    allow_empty = True

    def get_queryset(self):
        queryset = super(CommandeMixinView, self).get_queryset()
        return queryset.filter(Q(enabled=True) |
                               (Q(enabled=False) &
                                Q(payment_status=True)),
                               user=self.request.user) \
            .prefetch_related("from_commande", 'from_commande__to_meeting') \
            .annotate(
            total_price=Sum(
                F('from_commande__quantity')
                * F('from_commande__to_meeting__price'),
                output_field=DecimalField()
            )
        )


class CommandeArchiveView(CommandeMixinView, ArchiveIndexView):
    """Render command archive"""
    pass


class CommandeYearArchiveView(CommandeMixinView, YearArchiveView):
    """Render command archive by year"""
    pass


class CommandeMonthArchiveView(CommandeMixinView, MonthArchiveView):
    """Render command archive by month"""

    month_format = "%m"


class CommandeView(DetailView):
    """ render the command detail """

    model = Commande
    pk_url_kwarg = 'commande_pk'

    def get_queryset(self):
        queryset = super(CommandeView, self).get_queryset()
        queryset = queryset.filter(
            Q(enabled=True) |
            (Q(enabled=False) &
             Q(payment_status=True))) \
            .prefetch_related("from_commande",
                              'from_commande__to_meeting') \
            .annotate(
            total_price=Coalesce(Sum(
                F('from_commande__quantity')
                * F(
                    'from_commande__to_meeting__price'),
                output_field=FloatField()
            ), 0)
        )
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
                            kwargs={'commande_pk': self.object.pk})
                ),
                "cancel_return": request.build_absolute_uri(
                    reverse('ventes:show-commande',
                            kwargs={'commande_pk': self.object.pk})
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
    """ render success payment of a command"""

    template_name = 'ventes/commande_success.html'


class TurnoverView(TemplateView):
    """ render the turnover view """

    template_name = 'ventes/turnover.html'

    def get(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            raise Http404()

        if self.kwargs.get('year'):
            year = int(self.kwargs.get('year'))
        else:
            now = datetime.now()
            year = now.year

        def group_key(o):
            return datetime(year, o.get('month'), 1)

        queryset = Commande.objects \
            .all() \
            .filter(
            (Q(payment_status=True) & Q(enabled=True)) |
            (Q(payment_status=True) & Q(too_late_accepted_payment=True)),
            date__year=year) \
            .prefetch_related("from_commande", 'from_commande__to_meeting') \
            .annotate(
            year=ExtractYear('date'),
            month=ExtractMonth('date'),
            day=ExtractDay('date')) \
            .values('year', 'month', 'day') \
            .annotate(
            total_price=Sum(
                F('from_commande__quantity')
                * F('from_commande__to_meeting__price'),
                output_field=DecimalField()
            )).order_by('month')

        by_month = [(dt, list(c)) for dt, c in
                    itertools.groupby(queryset, group_key)]

        i = 0
        for dt, occurrences in by_month:
            total_payment_by_month = 0
            for occurrence in occurrences:
                total_payment_by_month += occurrence.get('total_price', 0)
            by_month[i][1].append(total_payment_by_month)
            i += 1

        kwargs = {
            'year': year,
            'by_month': by_month,
            'next_year': year + 1,
            'last_year': year - 1
        }

        return super(TurnoverView, self).get(request, *args, **kwargs)
