from django.shortcuts import render, redirect
from .models import Servicios, Turno
from .forms import TurnoForm

# Create your views here.
def base(request):
    return render(request, 'base.html')

def servicios(request):
    servicios = Servicios.objects.all()
    return render(request, 'elegir_servicio.html', {'servicios': servicios})

def elegir_turno(request):
    if request.method == 'POST':
        form = TurnoForm(request.POST)
        if form.is_valid():
            turno = form.save(commit=False)
            turno.estado_turno = 'pendiente'
            form.save()
            return redirect('turno_exito')
        
    else:
        form = TurnoForm()

    servicios = Servicios.objects.all()
    return render(request, 'elegir_turno.html', {'form': form, 'servicios': servicios})

def turno_exito(request):
    return render(request, 'turno_exito.html')