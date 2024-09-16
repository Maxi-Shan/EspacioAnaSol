#El archivo urls.py en la aplicacion de Django es esencial para mapear las URLs de la aplicacion con las vistas correspondientes. Es como una guia que le dice a django que funcion debe ejecutar cuando el usuario ingresa una URL especifica en el navegador
from django.urls import path
from . import views

urlpatterns = [
    path('servicios/', views.servicios, name= 'servicios'),
]