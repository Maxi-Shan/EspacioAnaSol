from django import forms
from .models import Empleado, Caja, Servicios, Turno, Cliente, DetalleVenta, EmpleadoXTurno
from django.utils import timezone
from django.utils.timezone import now
from calendar import monthrange

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
        fields = ['nombre_del_servicio', 'descripcion_del_servicio', 'duracion', 'precio_del_servicio', 'senia', 'imagen']

class ReservaForm(forms.Form):
    servicio = forms.ModelChoiceField(queryset=Servicios.objects.all(), required=True)
    fecha = forms.DateField(required=True)
    hora = forms.TimeField(required=True)

    def clean_fecha(self):
        fecha = self.cleaned_data.get('fecha')
        if fecha < now().date():
            raise forms.ValidationError("La fecha no puede estar en el pasado.")
        return fecha

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'correo_electronico', 'numero_telefono']


class TurnoForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        hoy = timezone.now().date()
        
        # Calculamos el rango del mes actual
        primer_dia_mes = hoy.replace(day=1)
        _, ultimo_dia_mes = monthrange(hoy.year, hoy.month)
        ultimo_dia_mes = hoy.replace(day=ultimo_dia_mes)
        
        # Configuramos el rango dinámico en el widget de fecha
        self.fields['fecha'].widget.attrs['min'] = hoy
        self.fields['fecha'].widget.attrs['max'] = ultimo_dia_mes

    hora = forms.ChoiceField(
        choices=[("09:00", "9:00 AM"), ("11:00", "11:00 AM"), ("18:00", "6:00 PM"), ("20:00", "8:00 PM")],
        required=True,
    )
    
    fecha = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        required=True,
    )
    
    id_empleado = forms.ModelChoiceField(queryset=Empleado.objects.all(), required=True)
    id_servicio = forms.ModelChoiceField(queryset=Servicios.objects.all(), required=True)

    diseño_uñas = forms.ImageField(required=False)
    senia_comprobante = forms.ImageField(required=False)

    class Meta:
        model = Turno
        fields = ['fecha', 'hora', 'id_empleado', 'id_servicio', 'diseño_uñas', 'senia_comprobante']

    def clean_fecha(self):
        """
        Validar que la fecha no sea pasada y esté dentro del mes actual.
        """
        fecha = self.cleaned_data.get('fecha')
        hoy = timezone.now().date()
        _, ultimo_dia_mes = monthrange(hoy.year, hoy.month)
        ultimo_dia_mes = hoy.replace(day=ultimo_dia_mes)

        if fecha < hoy:
            raise forms.ValidationError("No puedes elegir una fecha pasada.")
        if fecha > ultimo_dia_mes:
            raise forms.ValidationError("Solo puedes elegir fechas dentro de este mes.")
        return fecha

    def clean(self):
        """
        Validar lógica para la disponibilidad de horarios y empleados.
        """
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")
        empleado = cleaned_data.get("id_empleado")

        if not fecha or not hora:
            return cleaned_data

        # Verificar si ya hay un turno en ese horario exacto
        if Turno.objects.filter(fecha=fecha, hora=hora).exists():
            self.add_error("hora", "Ese horario ya está ocupado.")

        # Contar la cantidad de turnos ya registrados para la misma fecha
        turnos_en_fecha = Turno.objects.filter(fecha=fecha).count()
        if turnos_en_fecha >= 4:
            self.add_error("fecha", "No hay horarios disponibles para esta fecha.")

        # Verificar si el empleado ya tiene dos turnos en esa fecha
        if EmpleadoXTurno.objects.filter(dni_emp=empleado, id_turno__fecha=fecha).count() >= 2:
            self.add_error("id_empleado", "Este empleado ya tiene dos turnos en esta fecha.")

        return cleaned_data


class MetodoPagoForm(forms.ModelForm):
    METODO_PAGO_CHOICES = [
        ('efectivo', 'Efectivo'),
        ('transferencia', 'Transferencia'),
        ('efectivo-transferencia', 'Efectivo - Transferencia'),
    ]
    metodo_pago = forms.ChoiceField(choices=METODO_PAGO_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = DetalleVenta
        fields = ['metodo_pago']
        widgets = {
            'metodo_pago': forms.Select(attrs={'class': 'form-control'}),
        }
