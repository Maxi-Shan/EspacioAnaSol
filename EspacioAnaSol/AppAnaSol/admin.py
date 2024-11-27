from django.contrib import admin
from .models import Empleado, Servicios, Turno, Reservas, Venta, DetalleVenta, EmpleadoXTurno, ServicioXTurno, Cliente
from .forms import ServiciosForm

class ServiciosAdmin(admin.ModelAdmin):
    form = ServiciosForm
    list_display = ['nombre_del_servicio', 'descripcion_del_servicio', 'precio_del_servicio', 'duracion', 'senia', 'imagen']

admin.site.register(Empleado)
admin.site.register(Servicios)
admin.site.register(Turno)
admin.site.register(Reservas)
admin.site.register(Venta)
admin.site.register(DetalleVenta)
admin.site.register(EmpleadoXTurno)
admin.site.register(ServicioXTurno)
admin.site.register(Cliente)

