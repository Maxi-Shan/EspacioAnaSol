from django import forms
from .models import Cliente, Reservas, Turno, Servicios

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'correo_electronico', 'numero_telefono']

class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reservas
        fields = ['id_cliente', 'id_turno', 'id_servicio']
