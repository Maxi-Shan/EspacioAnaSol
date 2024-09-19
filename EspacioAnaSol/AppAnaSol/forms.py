from django import forms

class LoginForm(forms.Form):
    dni = forms.IntegerField(label='DNI')
    contraseña = forms.CharField(widget=forms.PasswordInput, label='Contraseña')

