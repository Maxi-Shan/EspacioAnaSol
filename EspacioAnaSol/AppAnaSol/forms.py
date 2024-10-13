from django import forms
from .models import Empleado, Caja, Servicios, Turno, Cliente, Venta

class LoginForm(forms.Form):
    dni = forms.IntegerField()
    contraseña = forms.CharField(widget=forms.PasswordInput)

class EmpleadoForm(forms.ModelForm):
    class Meta:
        model = Empleado
        fields = ['dni', 'nombre', 'apellido', 'domicilio', 'correo_electronico', 'numero_telefono', 'contraseña', 'estado_empleado', 'es_admin']

class AbrirCajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ['monto_inicial']


class ServiciosForm(forms.ModelForm):
    class Meta:
        model = Servicios
        fields = ['nombre_del_servicio', 'imagen', 'descripcion_del_servicio', 'duracion', 'precio_del_servicio', 'valor_sello']

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['fecha', 'hora', 'estado_turno']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),  # Selector de fecha
            'hora': forms.TimeInput(attrs={'type': 'time'}),  # Selector de hora
        }

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'correo_electronico', 'numero_telefono']

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['monto_total', 'estado_venta']  
        widgets = {
            'estado_venta': forms.Select(choices=[
                (0, 'Completada'),
                (1, 'En proceso')
            ])
        }