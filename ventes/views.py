import json
from extra_views import FormSetView
from ventes.forms import CommandeForm
from django.views.generic import TemplateView
from django.http import Http404
from django.core import signing

from catalogue.models import Meeting


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

    def post(self, request, *args, **kwargs):
        self.initial = signing.loads(request.POST.get('form-sign'))
        return super(CommandeView, self).post(request, *args, **kwargs)


class CommandeTemplateView(TemplateView):
    template_name = 'ventes/commande.html'
