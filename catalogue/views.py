import calendar
import datetime
import itertools
import json

from django.conf import settings
from django.db.models import Q, F, Count, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.views.generic import ListView, DetailView, TemplateView
from django.views.generic.edit import FormMixin
from django.http import Http404, HttpResponse
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string

from catalogue.models import Meeting, Place, Comments
from catalogue.forms import CommentsForm
from swingtime.models import EventType


class IndexView(ListView):
    """Render the index page"""

    paginate_by = 8
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
            departments = {
                department['code']: department['name']
                for department in json.load(file)
            }

        self.extra_context = {
            'root_events_types': EventType.get_root_nodes(),
            'departments': departments,
            'filled_departments': Place.objects.values('department').annotate(
                count_meeting=Count('meeting')
            ).filter(count_meeting__gt=0).order_by(
                '-count_meeting', ).distinct()[:5],
            'index': True
        }
        return super(IndexView, self).get(request, *args, **kwargs)


class LegalMentionTemplateView(TemplateView):
    """ render legal mention page"""

    template_name = 'catalogue/legal_mention.html'


class MeetingsView(ListView):
    """ Render events types view"""

    allow_empty = True
    paginate_by = 10
    model = Meeting

    def get_queryset(self):
        self.queryset = self.model.objects.filter(
            Q(event_type__parent=self.eventtype) |
            Q(event_type=self.eventtype)
        )
        return super(MeetingsView, self).get_queryset()

    def get(self, request, *args, **kwargs):
        root_events_types = EventType.get_root_nodes()
        self.eventtype = EventType.objects.filter(
            pk=kwargs['event_type_pk']).first()
        ancestors = self.eventtype.get_ancestors()

        self.extra_context = {
            'root_events_types': root_events_types,
            'eventtype': ancestors[0] if ancestors else self.eventtype,
            'selected_eventtype': self.eventtype
        }
        return super(MeetingsView, self).get(request, *args, **kwargs)


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

        _dict = {
            'root_events_types': EventType.get_root_nodes(),
            'breadcrumb': [{'label': _event_type.label, 'pk': _event_type.pk}
                           for _event_type in ancestors] +
                          [{'label': event_type.label, 'pk': event_type.pk}],
            'eventtype': ancestors[0] if ancestors else event_type,
        }

        recurrences = self.object.recurrences
        occurrences = None

        if recurrences:
            occurrences = recurrences.occurrences(
                dtstart=now + datetime.timedelta(minutes=30)) or None

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
                        )) & (Q(to_meeting__from_commande__enabled=True)
                              | (Q(to_meeting__from_commande__too_late_accepted_payment=True)
                                 & Q(to_meeting__from_commande__payment_status=True)))
                ), 0)
                for i, v in enumerate(occurrences)
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
                .filter(pk=self.object.pk) \
                .annotate(**annotate_space_reserved) \
                .annotate(**annotate_space_residue) \
                .get()

            _calendars, start, end = {}, 0, 0
            for dt_by_month, occurrences_by_month in \
                    itertools.groupby(occurrences, start_month):

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


class MeetingCommentsView(FormMixin, ListView):
    form_class = CommentsForm
    model = Comments
    allow_empty = True
    paginate_by = 6
    ordering = '-date'

    def get(self, request, *args, **kwargs):
        if request.is_ajax():
            self.queryset = self.model.objects.filter(meeting=kwargs.get('meeting_pk')).select_related('user')
            if self.request.GET.get(self.page_kwarg) is not None:
                self.template_name = 'catalogue/comment_post.html'
            return super(MeetingCommentsView, self).get(request, *args, **kwargs)
        else:
            raise Http404("Request have to be ajax.")

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        """
        Handle POST requests: instantiate a form instance with the passed
        POST variables and then check if it's valid.
        """
        if request.is_ajax():
            form = self.get_form()
            if form.is_valid():
                return self.form_valid(form)
            else:
                return self.form_invalid(form)
        else:
            raise Http404("Request have to be ajax.")

    def form_valid(self, form):
        comment = form.save(commit=False)
        comment.user = self.request.user
        comment.meeting = Meeting.objects.get(pk=self.kwargs.get('meeting_pk'))
        comment.save()

        self.queryset = self.model.objects.select_related('user').filter(meeting=self.kwargs.get('meeting_pk'))
        self.object_list = self.get_queryset()

        return HttpResponse(json.dumps({
            'html': render_to_string('catalogue/comment_post.html', self.get_context_data())
        }), content_type='application/json')

    def form_invalid(self, form):
        return HttpResponse(json.dumps({
            'errors_form': list(form.errors.items())
        }), content_type='application/json')

    def get_context_data(self, *, object_list=None, **kwargs):
        """Get the context for this view."""
        queryset = object_list if object_list is not None else self.object_list
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)
        if page_size:
            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size)
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                'object_list': queryset,
                'comments_count': paginator.count
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                'object_list': queryset,
                'comments_count': queryset.count()
            }
        if context_object_name is not None:
            context[context_object_name] = queryset
        context.update(kwargs)
        context.update({'meeting_pk': self.kwargs.get('meeting_pk'), 'form': self.get_form()})
        return context
