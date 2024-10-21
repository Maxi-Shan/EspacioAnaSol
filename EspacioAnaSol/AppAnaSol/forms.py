from django import forms
from .models import Empleado, Caja, Servicios, Turno, Cliente, Venta, Reservas, DetalleVenta

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
    ESTADO_TURNO_CHOICES = [
        (True, 'Reservado'),
        (False, 'Disponible')
    ]

    estado_turno = forms.ChoiceField(choices=ESTADO_TURNO_CHOICES, widget=forms.Select())

    class Meta:
        model = Turno
        fields = ['fecha', 'hora', 'estado_turno']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'hora': forms.TimeInput(attrs={'type': 'time'}),
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
                (1, 'En Proceso'),
                (2, 'No Completada')
            ])
        }

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['metodo_pago', 'estado_reserva']

class EstadoReservaForm(forms.ModelForm):
    ESTADO_CHOICES = [
        ('En Proceso', 'En Proceso'),
        ('Confirmada', 'Confirmada'),
        ('Cancelada', 'Cancelada'),
    ]
    
    estado_reserva = forms.ChoiceField(choices=ESTADO_CHOICES)

    class Meta:
        model = Reservas
        fields = ['estado_reserva'] 