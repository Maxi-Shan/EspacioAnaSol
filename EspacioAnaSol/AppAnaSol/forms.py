from django import forms
from .models import Turno

class TurnoForm(forms.ModelForm):
    class Meta:
        model = Turno
        fields = ['fecha', 'hora']
        widgets = {
            'fecha' : forms.DateInput(attrs={'type':'date'}),
            'hora' : forms.TimeInput(attrs={'type':'time'}),
        }