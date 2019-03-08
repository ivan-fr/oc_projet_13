from django.urls import path
from django.contrib.auth import views as auth_views

from session import views

app_name = 'session'
urlpatterns = [
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
