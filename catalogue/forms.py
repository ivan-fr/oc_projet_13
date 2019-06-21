from dal import autocomplete
from django import forms
from django.forms.utils import ErrorList
from django.utils.html import escape
from django.utils.safestring import mark_safe

from catalogue.models import Meeting, Comments
from swingtime.models import EventType


class MeetingForm(forms.ModelForm):
    """Meeting form for admin interface"""

    event_type = forms.TypedChoiceField(coerce=int)

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None, **kwargs):
        choices = self.mk_dropdown_tree(EventType)
        self.declared_fields['event_type'].choices = choices

        super(MeetingForm, self).__init__(data, files, auto_id, prefix,
                                          initial, error_class, label_suffix,
                                          empty_permitted, instance, **kwargs)

    class Meta:
        model = Meeting
        fields = ('title', 'price', 'event_type', 'photo',
                  'place', 'directors',
                  'authors', 'artists', 'recurrences')
        widgets = {
            'directors': autocomplete.ModelSelect2Multiple(
                'catalogue:select2_mtm_directors'
            ),
            'authors': autocomplete.ModelSelect2Multiple(
                'catalogue:select2_mtm_authors'
            ),
            'artists': autocomplete.ModelSelect2Multiple(
                'catalogue:select2_mtm_artists'
            )
        }

    @staticmethod
    def mk_indent(level):
        return '&nbsp;&nbsp;&nbsp;&nbsp;' * (level - 1)

    @classmethod
    def mk_dropdown_tree(cls, model):
        """ Creates a tree-like list of choices """

        options = []
        for node in model.get_tree():
            options.append(
                (node.pk, mark_safe(cls.mk_indent(node.get_depth())
                                    + escape(node))))
        return options

    def clean_event_type(self):
        return EventType.objects.get(pk=self.cleaned_data['event_type'])


class CommentsForm(forms.ModelForm):
    class Meta:
        model = Comments
        fields = ('texte',)
        widgets = {
            'texte': forms.Textarea(attrs={'rows': 4}),
        }
