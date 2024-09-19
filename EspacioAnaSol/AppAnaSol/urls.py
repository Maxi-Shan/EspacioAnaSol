#El archivo urls.py en la aplicacion de Django es esencial para mapear las URLs de la aplicacion con las vistas correspondientes. Es como una guia que le dice a django que funcion debe ejecutar cuando el usuario ingresa una URL especifica en el navegador
from django.urls import path
from . import views

urlpatterns = [
    path('', views.base, name='inicio'),
    path('elegir_servicio/', views.servicios, name= 'elegir_servicio'),
    path('elegir_turno/', views.elegir_turno, name='elegir_turno'),
    path('turno_exito/', views.turno_exito, name='turno_exito'),
]