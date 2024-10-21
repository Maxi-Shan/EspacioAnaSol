from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('servicio/', views.seleccionar_servicio, name='seleccionar_servicio'),
    path('servicio/<int:servicio_id>/turno/', views.seleccionar_turno, name='seleccionar_turno'),
    path('servicio/<int:servicio_id>/turno/registrar/', views.registrar_cliente, name='registrar_cliente'),
    path('obtener_horas/', views.obtener_horas, name='obtener_horas'),
]
