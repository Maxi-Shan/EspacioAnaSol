from django import forms
from .models import Empleado
from .models import Caja
from .models import Servicios

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['dni', 'nombre', 'apellido', 'domicilio', 'correo_electronico', 'numero_telefono', 'imagen', 'contraseña', 'estado_empleado']
        widgets = {
            'contraseña': forms.PasswordInput(),
        }

class CajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ['empleado', 'monto_inicial', 'monto_recaudado', 'monto_final']

class ServiciosForm(forms.ModelForm):
    class Meta:
        model = Servicios
        fields = ['nombre_del_servicio', 'descripcion_del_servicio', 'categoria_del_servicio', 'precio_del_servicio', 'nota_adicional', 'imagen']