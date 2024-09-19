from django.contrib import admin
from .models import Turno, Empleado
# Register your models here.
admin.site.register(Empleado)
admin.site.register(Turno)
#Creen super usuario para acceder a la administracion en django 
#Comando python manage.py createsuperuser