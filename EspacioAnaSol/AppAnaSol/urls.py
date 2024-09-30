from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('inicio/', views.inicio, name='inicio'),
    path('login/', views.login_view, name='login'),
    path('pagina_principal/', views.pagina_principal, name='pagina_principal'),
    path('pagina_admin/', views.pagina_admin, name='pagina_admin'),
    path('Clientes/', views.clientes_view, name='Clientes'),
    path('Ventas/', views.ventas_view, name='Ventas'),
    path('Turnos/', views.turnos_view, name='Turnos'),
    path('Servicios/', views.servicios_view, name='Servicios'),
    path('Caja/', views.caja_view, name='Caja'),
    path('empleados/', views.listar_empleados, name='listar_empleados'),
    path('empleados/crear/', views.crear_empleado, name='crear_empleado'),
    path('empleados/editar/<int:dni>/', views.editar_empleado, name='editar_empleado'),
    path('empleados/eliminar/<int:dni>/', views.eliminar_empleado, name='eliminar_empleado'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
