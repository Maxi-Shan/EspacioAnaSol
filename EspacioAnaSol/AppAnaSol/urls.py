from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('inicio/', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('pagina_principal/', views.pagina_principal, name='pagina_principal'),
    path('login_admin/', views.login_admin_view, name='login_admin'),
    path('pagina_admin/', views.pagina_admin, name='pagina_admin'),
]
