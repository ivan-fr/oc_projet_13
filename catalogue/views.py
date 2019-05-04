import calendar
import datetime
import itertools
import json

from django.conf import settings
from django.db.models import Q, F, Count, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.views.generic import ListView, DetailView

from catalogue.models import Meeting, Place
from swingtime.models import EventType


class IndexView(ListView):
    """Render the index page"""

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
                for department in json.load(file)
            }
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
    """ Render events types view"""

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
    """ Render the meeting views with calendar """
    model = Meeting
    pk_url_kwarg = 'meeting_pk'

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset().select_related('event_type', 'place') \
            .prefetch_related('notes', 'authors', 'artists', 'directors')

        self.object = self.get_object(queryset=queryset)

        event_type = self.object.event_type
        ancestors = event_type.get_ancestors()

        now = datetime.datetime.now()

        occurrences = getattr(self.object.recurrences.occurrences(
            dtstart=now + datetime.timedelta(minutes=30)), 'occurrences', None)

        _dict = {
            'root_events_types': EventType.get_root_nodes(),
            'breadcrumb': [{'label': _event_type.label, 'pk': _event_type.pk}
                           for _event_type in ancestors] +
                          [{'label': event_type.label, 'pk': event_type.pk}],
            'eventtype': ancestors[0] if ancestors else event_type,
        }

        if occurrences:
            # if there is a occurence, render a calendar.

            def start_month(o):
                return datetime.datetime(o.year, o.month, 1)

            def start_day(o):
                return o.day

            annotate_space_reserved = {
                str(i): Coalesce(Sum(
                    F('to_meeting__quantity'),
                    filter=Q(
                        to_meeting__date_meeting=timezone.make_aware(
                            v.replace(second=0)
                        )
                    )
                ), 0)
                for i, v in enumerate(occurrences())
            }

            annotate_space_residue = {}
            annotate_space_reserved_interger = tuple(
                int(i_str) for i_str
                in annotate_space_reserved.keys()
            )
            for key in sorted(annotate_space_reserved_interger):
                annotate_space_residue['nb_space_residue_' + str(key)] = \
                    F('place__space_available') - F(str(key))

            space_available = self.get_queryset() \
                .objects.filter(pk=self.object.pk) \
                .annotate(**annotate_space_reserved) \
                .annotate(**annotate_space_residue)

            _calendars, start, end = {}, 0, 0
            for dt_by_month, occurrences_by_month in \
                    itertools.groupby(occurrences(), start_month):

                by_day = []
                for dt_by_day, o_d in itertools.groupby(
                        occurrences_by_month, start_day):
                    o_d = list(o_d)
                    end += len(o_d)
                    by_day.append(
                        (dt_by_day,
                         list(
                             zip(
                                 o_d,
                                 list(
                                     annotate_space_residue.keys()
                                 )[start:end]
                             )
                         ))
                    )
                    start = end

                by_day = dict(by_day)

                entire_cal = []
                cal = calendar.monthcalendar(dt_by_month.year,
                                             dt_by_month.month)
                for row in cal:
                    _row = []
                    for d in row:
                        if d:
                            if datetime.datetime(dt_by_month.year,
                                                 dt_by_month.month, 1) > \
                                    datetime.datetime(
                                        now.year,
                                        now.month, 1) or \
                                    datetime.datetime(
                                        dt_by_month.year,
                                        dt_by_month.month,
                                        d, 23, 59, 59) >= now:
                                _row.append((d, by_day.get(d, [])))
                                continue
                        _row.append((None, []))
                    if _row != [(None, [])] * len(_row):
                        entire_cal.append(_row)

                _calendars[dt_by_month] = entire_cal

            _dict['calendars'] = _calendars
            _dict['space_available'] = space_available

        context = self.get_context_data(**_dict)
        return self.render_to_response(context)
