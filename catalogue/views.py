from datetime import datetime
import itertools
import json

from django.conf import settings
from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from catalogue.models import Meeting, Place
from swingtime.models import EventType

from django.db.models import Q, F, Count


class IndexView(ListView):
    paginate_by = 5
    allow_empty = True
    template_name = 'catalogue/index_list.html'
    model = Meeting
    ordering = 'title'

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            place__department=self.kwargs.get('department_code')
        ).select_related('place')
        return super(IndexView, self).get_queryset()

    def get(self, request, *args, **kwargs):
        with open(settings.DEPARTMENTS_FILE, "r", encoding="utf-8") as file:
            self.departments = {
                department['code']: department['name']
                for department in json.load(file)}
        return super(IndexView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, object_list=None, **kwargs):
        _dict = {
            'root_events_types': EventType.get_root_nodes(),
            'departments': self.departments,
            'filled_departments': Place.objects.values('department').annotate(
                count_meeting=Count('meeting')
            ).filter(count_meeting__gt=0).order_by(
                '-count_meeting', ).distinct()[:5],
            'index': True
        }
        _dict.update(kwargs)
        return super(IndexView, self).get_context_data(object_list=None,
                                                       **_dict)


class EventTypeView(ListView):
    allow_empty = True
    paginate_by = 10
    model = Meeting

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            Q(event_type__parent=self.eventtype) |
            Q(event_type=self.eventtype)
        )
        return super(EventTypeView, self).get_queryset()

    def get(self, request, *args, **kwargs):
        self.root_events_types = EventType.get_root_nodes()
        self.eventtype = EventType.objects.filter(
            pk=kwargs['event_type_pk']).first()
        self.ancestors = self.eventtype.get_ancestors()
        return super(EventTypeView, self).get(request, *args, **kwargs)

    def get_context_data(self, *args, object_list=None, **kwargs):
        _dict = {
            'root_events_types': self.root_events_types,
            'eventtype': self.ancestors[0] if self.ancestors else
            self.eventtype,
            'selected_eventtype': self.eventtype
        }
        _dict.update(kwargs)
        return super(EventTypeView, self).get_context_data(object_list=None,
                                                           **_dict)


class MeetingView(DetailView):
    model = Meeting
    pk_url_kwarg = 'meeting_pk'

    def get_queryset(self):
        queryset = super(MeetingView, self).get_queryset()
        return queryset.select_related('event_type', 'place') \
            .prefetch_related('notes', 'authors', 'artists', 'directors')

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        event_type = self.object.event_type
        ancestors = event_type.get_ancestors()

        year = int(datetime.now().year)

        occurrences = getattr(self.object.recurrences, 'occurrences', None)

        def group_key(o):
            return datetime(year, o.month, 1)

        _dict = {
            'root_events_types': EventType.get_root_nodes(),
            'breadcrumb': [{'label': _event_type.label, 'pk': _event_type.pk}
                           for _event_type in ancestors] +
                          [{'label': event_type.label, 'pk': event_type.pk}],
            'eventtype': ancestors[0] if ancestors else event_type,
            'year': year,
        }

        if occurrences:
            _dict['by_month'] = [(dt, list(o)) for dt, o in
                                 itertools.groupby(occurrences(), group_key) if
                                 occurrences]

        context = self.get_context_data(**_dict)
        return self.render_to_response(context)
