from django import forms
from catalogue.models import Meeting
from django.utils import timezone
from django.db.models import F, Sum, Q
from django.db.models.functions import Coalesce


class CommandeForm(forms.Form):
    id = forms.IntegerField(min_value=1, disabled=True)
    name = forms.CharField(max_length=32, min_length=2, disabled=True)
    date = forms.DateTimeField(input_formats=['%d/%m/%Y %H:%M'], disabled=True)
    count = forms.IntegerField(min_value=1, max_value=9)

    def clean(self):
        id = self.cleaned_data['id']

        if not 1 <= self.cleaned_data['count'] <= 9:
            raise forms.ValidationError('Mauvaise quantité.')

        try:
            meeting = Meeting.objects.filter(pk=id) \
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

            occurrences = getattr(meeting.recurrences, 'occurrences', None)
            if not occurrences:
                raise forms.ValidationError("Il n'y a pas d'occurence.")
            occurrences = [timezone.make_aware(date.replace(second=0)) for date
                           in occurrences()]
            if self.cleaned_data['date'] not in occurrences:
                raise forms.ValidationError("Mauvaise occurrence.")
        except Meeting.DoesNotExist:
            raise forms.ValidationError("L'événement n'existe pas.")

        return super(CommandeForm, self).clean()
