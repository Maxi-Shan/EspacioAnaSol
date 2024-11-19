from django import forms
from datetime import date
from .models import Turno, Empleado, EmpleadoXTurno, Cliente

class TurnoForm(forms.ModelForm):

    class Meta:
        model = Turno
        fields = ['fecha', 'hora']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date', 'class': 'datepicker', 'min': date.today().strftime('%Y-%m-%d'),'onkeydown': 'return false;'}),
            'hora': forms.Select(choices=[
                ('9:00', '9:00 AM'),
                ('11:00', '11:00 AM'),
                ('18:00', '6:00 PM'),
                ('20:00', '8:00 PM'),
            ])
        }


    empleado = forms.ModelChoiceField(queryset=Empleado.objects.all(), to_field_name='dni', label='Selecciona un Empleado')

    def clean(self):
        cleaned_data = super().clean()
        fecha = cleaned_data.get("fecha")
        hora = cleaned_data.get("hora")
        empleado = cleaned_data.get("empleado")
        
        if EmpleadoXTurno.objects.filter(id_turno__fecha=fecha, id_turno__hora=hora, dni_emp=empleado).exists():
            raise forms.ValidationError("Este empleado ya tiene un turno reservado para esa fecha y hora.")

        return cleaned_data
    
class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nombre', 'apellido', 'numero_telefono', 'correo_electronico']

    def clean_numero_telefono(self):
        numero_telefono = self.cleaned_data['numero_telefono']
        return numero_telefono

    def clean_correo_electronico(self):
        correo_electronico = self.cleaned_data['correo_electronico']
        return correo_electronico

class ComprobanteForm(forms.Form):
    diseño_uñas = forms.FileField(required=False)  # Campo opcional para el diseño de uñas
    senia_comprobante = forms.ImageField(required=True)  # Campo obligatorio para el comprobante de la senia


