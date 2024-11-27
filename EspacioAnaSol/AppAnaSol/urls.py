from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    # Autenticación
    path('', views.login, name='login'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),

    # Pagina Principal
    path('pagina-principal/', views.pagina_principal, name='pagina_principal'),
    
    # Empleados
    path('empleados/', views.list_empleados, name='list_empleados'),
    path('empleados/add/', views.add_empleado, name='add_empleado'),
    path('empleados/<int:dni>/update/', views.update_empleado, name='update_empleado'),
    path('empleados/<int:dni>/delete/', views.delete_empleado, name='delete_empleado'),
    path('empleados/<int:dni>/update-status/', views.update_empleado_status, name='update_empleado_status'),

    # Cajas
    path('cajas/', views.list_cajas, name='list_cajas'),
    path('cajas/add/', views.abrir_caja, name='abrir_caja'),
    path('cajas/<int:id_caja>/update/', views.update_caja, name='update_caja'),
    path('cajas/<int:id_caja>/close/', views.cerrar_caja, name='cerrar_caja'),
    path('caja/<int:id_caja>/ventas/', views.ventas_por_caja, name='ventas_por_caja'),

    # Servicios
    path('servicios/', views.list_servicios, name='list_servicios'),
    path('servicios/add/', views.add_servicio, name='add_servicio'),
    path('servicios/update/<int:id_servicio>/', views.modificar_servicio, name='modificar_servicio'),
    path('servicios/delete/<int:id_servicio>/', views.delete_servicio, name='delete_servicio'),

    # Turnos
    path('turnos/', views.list_turnos, name='list_turnos'),
    path('turnos/registrar-cliente/', views.registrar_cliente, name='registrar_cliente'),
    path('turnos/registrar-turno/', views.registrar_turno, name='registrar_turno'),
    path('turnos/cancelar-registro/', views.cancelar_registro, name='cancelar_registro'),
    path('modificar-turno/<int:turno_id>/', views.modificar_turno, name='modificar_turno'),
    path('confirmar_turnos/<str:accion>/', views.gestionar_turno, name='confirmar_turnos'),

    # Clientes
    path('clientes/', views.list_clientes, name='list_clientes'),

    # Backups
    path('backup/', views.backup_database, name='backup_database'),    
    path('restore/', views.restore_database, name='restore_database'),
    
    # Ventas, DestalleVentas y Reservas
    path('ventas/', views.list_ventas, name='list_ventas'),
    path('ventas/<int:id_venta>/', views.detalle_venta, name='detalle_venta'),
    path('reservas/', views.list_reservas, name='list_reservas'),
    path('modificar_metodo_pago/<int:venta_id>/', views.modificar_metodo_pago, name='modificar_metodo_pago'),
    path('actualizar_reserva/<int:reserva_id>/', views.actualizar_reserva, name='actualizar_reserva'),

    #graficos
    path('inicio/',views.inicio,name='inicio'),
    path('gturno/',views.gturno,name='gturno'),
    path('gventas/',views.gventas,name='gventas'),
    path('gcaja/',views.gcaja,name='gcaja')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
