#El archivo urls.py en la aplicacion de Django es esencial para mapear las URLs de la aplicacion con las vistas correspondientes. Es como una guia que le dice a django que funcion debe ejecutar cuando el usuario ingresa una URL especifica en el navegador
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.base, name='inicio'),
    path('EspacioAnaSol/', views.base, name='inicio'),
    path('elegir_servicio/', views.servicios, name='elegir_servicio'),
    path('elegir_turno/<str:servicio>/', views.elegir_turno, name='elegir_turno'),
    path('confirmacion_turno/<str:servicio_nombre>/', views.confirmacion_turno, name='confirmacion_turno'),
    path('tiempo_agotado/', views.tiempo_agotado, name='tiempo_agotado'),
    path('mostrar_turnos/', views.mostrar_turnos, name='mostrar_turnos'),
    path('procesando_reserva/<int:pk>/', views.procesando_reserva, name='procesando_reserva'),
    path('descargar-pdf/', views.generar_pdf, name='descargar_pdf'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)