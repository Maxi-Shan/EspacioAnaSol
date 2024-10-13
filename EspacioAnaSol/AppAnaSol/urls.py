from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('inicio/', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('pagina_principal/', views.pagina_principal, name='pagina_principal'),
    path('pagina_admin/', views.pagina_admin, name='pagina_admin'),
    path('empleados/', views.listar_empleados, name='listar_empleados'),
    path('empleados/crear/', views.crear_empleado, name='crear_empleado'),
    path('empleados/modificar/<int:dni>/', views.modificar_empleado, name='modificar_empleado'),
    path('empleados/eliminar/<int:dni>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('cajas/', views.listar_cajas, name='listar_cajas'),
    path('cajas/abrir/', views.abrir_caja, name='abrir_caja'),
    path('cajas/cerrar/<int:id_caja>/', views.cerrar_caja, name='cerrar_caja'),
    path('modificar_montos/<int:id_caja>/', views.modificar_caja, name='modificar_caja'),
    path('eliminar_caja/<int:id_caja>/', views.eliminar_caja, name='eliminar_caja'),
    path('servicios/', views.listar_servicios, name='listar_servicios'),
    path('crear_servicio/', views.crear_servicio, name='crear_servicio'),
    path('servicios/modificar/<int:id_servicio>/', views.modificar_servicio, name='modificar_servicio'),
    path('servicios/eliminar/<int:id_servicio>/', views.eliminar_servicio, name='eliminar_servicio'),
    path('listar_turnos/', views.listar_turnos, name='listar_turnos'),
    path('crear-registro-turno/', views.crear_registro_turno, name='crear_registro_turno'),
    path('modificar-registro-turno/<int:turno_id>/', views.modificar_registro_turno, name='modificar_registro_turno'),
    path('eliminar-registro-turno/<int:turno_id>/', views.eliminar_registro_turno, name='eliminar_registro_turno'),
    path('registrar_cliente/', views.registrar_cliente, name='registrar_cliente'),
    path('listar_clientes/', views.listar_clientes, name='listar_clientes'),
    path('listar_ventas/', views.listar_ventas, name='listar_ventas'),
    path('crear_venta/', views.crear_venta, name='crear_venta'),
    path('modificar_venta/<int:venta_id>/', views.modificar_venta, name='modificar_venta'),
    path('eliminar_venta/<int:venta_id>/', views.eliminar_venta, name='eliminar_venta'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)