import json

from django.views.generic.dates import ArchiveIndexView, MonthArchiveView, \
    YearArchiveView, WeekArchiveView
from django.views.generic import TemplateView
from django.http import Http404
from django.core import signing
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.db.models import Q, F, Sum, FloatField

from catalogue.models import Meeting
from ventes.models import Commande, CommandeMeeting
from extra_views import FormSetView
from ventes.forms import CommandeForm


class CommandeView(FormSetView):
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
        return super(CommandeView, self).post(request, *args, **kwargs)

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
                CommandeMeeting.objects.bulk_create(
                    [CommandeMeeting(
                        from_commande=commande,
                        to_meeting=Meeting.objects.get(pk=key), **_dict)
                        for _dict in dicts]
                )

        return super(CommandeView, self).formset_valid(formset)


class CommandeTemplateView(TemplateView):
    template_name = 'ventes/commande.html'


class CommandeMixinView(object):
    model = Commande
    date_field = 'date'
    paginate_by = 10
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


class CommandeWeekArchiveView(CommandeMixinView, WeekArchiveView):
    week_format = "%W"
