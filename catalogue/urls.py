from dal import autocomplete
from django.urls import path, re_path

from catalogue import views
from catalogue.models import Director, Author, Artist

app_name = 'catalogue'
urlpatterns = [
    path('slct2_mtm_directors/',
         autocomplete.Select2QuerySetView.as_view(model=Director),
         name='select2_mtm_directors', ),
    path('slct2_mtm_authors/',
         autocomplete.Select2QuerySetView.as_view(model=Author),
         name='select2_mtm_authors', ),
    path('slct2_mtm_artists/',
         autocomplete.Select2QuerySetView.as_view(model=Artist),
         name='select2_mtm_artists', ),
    re_path(r'^(?P<department_code>[\d]+)/$', views.IndexView.as_view(),
            name='index'),
    re_path(r'^event_type/(?P<event_type_pk>[\d]+)/$',
            views.EventTypeView.as_view(), name='show-eventtype'),
    re_path(r'^meeting/(?P<meeting_pk>[\d]+)/$',
            views.MeetingView.as_view(), name='show-meeting'),
    path('legal-mention/', views.LegalMentionTemplateView.as_view(),
         name='legal_mention')
]
