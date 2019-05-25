import datetime

from django import forms
from django.db.models import F, Sum, Q
from django.db.models.functions import Coalesce
from django.utils import timezone

from catalogue.models import Meeting


class CommandeForm(forms.Form):
    """form of command validation"""

    id = forms.IntegerField(min_value=1, disabled=True)
    name = forms.CharField(max_length=32, min_length=2, disabled=True)
    date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], disabled=True)
    count = forms.IntegerField(min_value=1, max_value=9)

    def clean(self):
        if not self.is_valid():
            raise forms.ValidationError('Formulaire invalide.')

        _id = self.cleaned_data['id']

        try:
            meeting = Meeting.objects.filter(pk=_id) \
                .annotate(
                nombre_de_place_reserve=Coalesce(Sum(
                    F('to_meeting__quantity'),
                    filter=Q(to_meeting__date_meeting=self.cleaned_data['date'])
                ), 0)
            ).annotate(
                place_restante=F('place__space_available')
                               - F('nombre_de_place_reserve')
                               - self.cleaned_data['count']
            ).first()

            if meeting.place_restante <= 0:
                raise forms.ValidationError('Nombre de places dépassées.')

            now = datetime.datetime.now()

            recurrences = meeting.recurrences
            occurrences = None

            if recurrences:
                occurrences = recurrences.occurrences(
                    dtstart=now + datetime.timedelta(minutes=30)) or None
            else:
                raise forms.ValidationError("Il n'y a pas d'occurence.")

            if not occurrences:
                raise forms.ValidationError("Il n'y a pas d'occurence.")
            occurrences = [timezone.make_aware(date.replace(second=0)) for date
                           in occurrences]
            if self.cleaned_data['date'] not in occurrences:
                raise forms.ValidationError("Mauvaise occurrence.")
        except Meeting.DoesNotExist:
            raise forms.ValidationError("L'événement n'éxiste pas.")

        return super(CommandeForm, self).clean()
