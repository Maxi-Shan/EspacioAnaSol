from django.contrib import admin
from .models import Empleado
# Register your models here.
admin.site.register(Empleado)

#Creen super usuario para acceder a la administracion en django 
#Comando python manage.py createsuperuser