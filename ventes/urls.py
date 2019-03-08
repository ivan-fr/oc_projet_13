from django.urls import path
from ventes import views

app_name = 'ventes'
urlpatterns = [
    path('commande/formset/', views.CommandeView.as_view(), name='commande-formset'),
    path('commande/', views.CommandeTemplateView.as_view(), name='commande'),
]
