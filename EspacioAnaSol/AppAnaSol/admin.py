from django.contrib import admin
from .models import Empleado, Servicios
from .forms import ServiciosForm

class ServiciosAdmin(admin.ModelAdmin):
    form = ServiciosForm
    list_display = ['nombre_del_servicio', 'descripcion_del_servicio', 'precio_del_servicio', 'duracion', 'senia', 'imagen']

admin.site.register(Empleado)
admin.site.register(Servicios, ServiciosAdmin)



