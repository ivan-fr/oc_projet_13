from django.urls import path, include
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
    path('<int:year>/week/<int:week>/',
         login_required(views.CommandeWeekArchiveView.as_view()),
         name="commandes-week"),
    path(
        '',
        login_required(views.CommandeArchiveView.as_view()),
        name="commandes"
    )
]

urlpatterns = [
    path('commande/formset/', views.CommandeView.as_view(),
         name='commande-formset'),
    path('commande/', login_required(views.CommandeTemplateView.as_view()),
         name='commande'),
    path('commandes/', include(commandes_patterns)),
]
