from django.contrib import admin
from .models import Empleado, Cliente, Turno, Servicios, DetalleVenta, Venta, Reservas, Caja

admin.site.register(Empleado)
admin.site.register(Cliente)
admin.site.register(Turno)
admin.site.register(Servicios)
admin.site.register(DetalleVenta)
admin.site.register(Venta)
admin.site.register(Reservas)
admin.site.register(Caja)


