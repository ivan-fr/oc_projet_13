from django.urls import path, include, re_path
from django.contrib.auth.decorators import login_required
from ventes import views

app_name = 'ventes'

commandes_patterns = [
    path(
        '<int:year>/<int:month>/',
        login_required(views.CommandeMonthArchiveView.as_view()),
        name="commandes-month"
    ),
    path(
        '<int:year>/',
        login_required(views.CommandeYearArchiveView.as_view()),
        name="commandes-year"
    ),
    path(
        '',
        login_required(views.CommandeArchiveView.as_view()),
        name="commandes"
    )
]

urlpatterns = [
    path('commande/formset/', views.CommandeFormsetView.as_view(),
         name='commande-formset'),
    path('commande/', login_required(views.CommandeTemplateView.as_view()),
         name='commande'),
    re_path(r'^commande-success/(?P<commande_pk>[\d]+)/$', login_required(
        views.CommandePaymentSuccesTemplateView.as_view()),
            name='commande-success'),
    re_path(r'^commande/(?P<commande_pk>[\d]+)/$',
            login_required(views.CommandeView.as_view()), name='show-commande'),
    path('commandes/', include(commandes_patterns)),
    path('commandes/turnover/', views.TurnoverView.as_view(),
         name='commandes-turnover'),
    re_path(r'^commandes/turnover/(?P<year>[\d]+)/$',
         views.TurnoverView.as_view(),
         name='commandes-turnover-year')
]
