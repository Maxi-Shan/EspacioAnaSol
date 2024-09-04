from django.urls import path
from . import views

urlpatterns = [
    path('', views.pagina_principal, name='pagina_principal'),
    path('gestion_empleados/', views.gestion_empleados, name='gestion_empleados'),
    path('crear_empleado/', views.crear_empleado, name='crear_empleado'),
    path('modificar_empleado/<int:dni>/', views.modificar_empleado, name='modificar_empleado'),
    path('eliminar_empleado/<int:dni>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('activar_empleado/<int:dni>/', views.activar_empleado, name='activar_empleado'),
    path('suspender_empleado/<int:dni>/', views.suspender_empleado, name='suspender_empleado'),
    path('', views.pagina_principal, name='pagina_principal'),
    path('empleados/', views.gestion_empleados, name='gestion_empleados'),
    path('cajas/', views.listar_cajas, name='listar_cajas'),
    path('cajas/abrir/', views.abrir_caja, name='abrir_caja'),
    path('cajas/cerrar/<int:id_caja>/', views.cerrar_caja, name='cerrar_caja'),
    path('cajas/modificar/<int:id_caja>/', views.modificar_caja, name='modificar_caja'),
    path('cajas/eliminar/<int:id_caja>/', views.eliminar_caja, name='eliminar_caja'),
    path('servicios/', views.listar_servicios, name='listar_servicios'),
    path('servicios/crear/', views.crear_servicio, name='crear_servicio'),
    path('servicios/modificar/<int:id_servicio>/', views.modificar_servicio, name='modificar_servicio'),
    path('servicios/eliminar/<int:id_servicio>/', views.eliminar_servicio, name='eliminar_servicio'),
]
