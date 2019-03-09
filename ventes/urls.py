from django.urls import path
from django.contrib.auth.decorators import login_required
from ventes import views

app_name = 'ventes'
urlpatterns = [
    path('commande/formset/', views.CommandeView.as_view(),
         name='commande-formset'),
    path('commande/', login_required(views.CommandeTemplateView.as_view()),
         name='commande'),
]
