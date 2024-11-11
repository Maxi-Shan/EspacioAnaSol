from django import forms
from .models import Empleado, Caja, Servicios, Turno, Cliente, Reservas, Venta, DetalleVenta
from django.forms import ModelForm

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
        fields = ['fecha', 'hora', 'estado_turno']  # Asegúrate de incluir el estado si lo necesitas

    # Personaliza los widgets para la selección de fecha y hora
    fecha = forms.DateField(widget=forms.SelectDateWidget())  # Selector de fecha
    hora = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))  # Selector de hora


class MultipleTurnoForm(forms.Form):
    fecha = forms.DateField(widget=forms.SelectDateWidget())
    servicio = forms.ModelChoiceField(queryset=Servicios.objects.all())

    # Definir campos para seleccionar 4 empleados
    empleado1 = forms.ModelChoiceField(queryset=Empleado.objects.all(), label="Empleado 1")
    empleado2 = forms.ModelChoiceField(queryset=Empleado.objects.all(), label="Empleado 2")
    empleado3 = forms.ModelChoiceField(queryset=Empleado.objects.all(), label="Empleado 3")
    empleado4 = forms.ModelChoiceField(queryset=Empleado.objects.all(), label="Empleado 4")

    # Definir campos para seleccionar 4 horas
    hora1 = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Hora 1")
    hora2 = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Hora 2")
    hora3 = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Hora 3")
    hora4 = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}), label="Hora 4")

class ClienteForm(ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'correo_electronico', 'numero_telefono']

class ReservaForm(forms.Form):
    servicio = forms.ModelChoiceField(queryset=Servicios.objects.all(), required=True)
    fecha = forms.DateField(required=True)
    hora = forms.TimeField(required=True)

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['id_caja', 'id_cliente', 'fecha_venta', 'hs_venta', 'monto_total', 'estado_venta']

class DetalleVentaForm(forms.ModelForm):
    class Meta:
        model = DetalleVenta
        fields = ['id_venta', 'id_reserva', 'metodo_pago', 'monto_subtotal', 'comprobante', 'estado_reserva']

class VentaForm(forms.ModelForm):
    class Meta:
        model = Venta
        fields = ['monto_total', 'estado_venta']
        widgets = {
            'monto_total': forms.NumberInput(attrs={'class': 'form-control'}),
            'estado_venta': forms.Select(attrs={'class': 'form-control'}),
        }