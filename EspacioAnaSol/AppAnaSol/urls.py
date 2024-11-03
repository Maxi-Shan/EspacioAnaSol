from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('pagina-principal/', views.pagina_principal, name='pagina_principal'),
    path('empleados/', views.list_empleados, name='list_empleados'),
    path('empleados/add/', views.add_empleado, name='add_empleado'),
    path('empleados/update/<str:dni>/', views.update_empleado, name='update_empleado'),
    path('empleados/delete/<str:dni>/', views.delete_empleado, name='delete_empleado'),
    path('empleados/update-status/<str:dni>/', views.update_empleado_status, name='update_empleado_status'),
    path('abrir-caja/', views.abrir_caja, name='abrir_caja'),
    path('cajas/', views.list_cajas, name='list_cajas'),
    path('cerrar-caja/<int:id_caja>/', views.cerrar_caja, name='cerrar_caja'),
    path('cajas/modificar/<int:id_caja>/', views.update_caja, name='update_caja'),
    path('cajas/eliminar/<int:id_caja>/', views.delete_caja, name='delete_caja'),
    path('servicios/', views.list_servicios, name='list_servicios'),
    path('servicios/add/', views.add_servicio, name='add_servicio'),
    path('servicios/update/<int:id_servicio>/', views.update_servicio, name='update_servicio'),
    path('servicios/delete/<int:id_servicio>/', views.delete_servicio, name='delete_servicio'),
    path('turnos/', views.list_turnos, name='list_turnos'),
    path('turnos/add/', views.add_turno, name='add_turno'),
    path('turnos/update/<int:turno_id>/', views.update_turno, name='update_turno'),
    path('turnos/delete/<int:turno_id>/', views.delete_turno, name='delete_turno'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
