from django import forms
from .models import Empleado, Caja

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

class CerrarCajaForm(forms.ModelForm):
    class Meta:
        model = Caja
        fields = ['monto_recaudado']