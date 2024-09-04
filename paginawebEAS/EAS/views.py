from django.shortcuts import render, redirect, get_object_or_404
from .models import Empleado, Caja, Servicios
from .forms import EmpleadoForm
from .forms import CajaForm
from .forms import ServiciosForm

def pagina_principal(request):
    empleados = Empleado.objects.all()
    return render(request, 'pagina_principal.html', {'empleados': empleados})

def gestion_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'gestion_empleados.html', {'empleados': empleados})

def crear_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('gestion_empleados')
    else:
        form = EmpleadoForm()
    return render(request, 'formulario_empleado.html', {'form': form})

def modificar_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, request.FILES, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('gestion_empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'formulario_empleado.html', {'form': form})

def eliminar_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    if request.method == 'POST':
        empleado.delete()
        return redirect('gestion_empleados')
    return render(request, 'confirmar_eliminar.html', {'empleado': empleado})

def activar_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    empleado.estado_empleado = True
    empleado.save()
    return redirect('gestion_empleados')

def suspender_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    empleado.estado_empleado = False
    empleado.save()
    return redirect('gestion_empleados')

def listar_cajas(request):
    cajas = Caja.objects.all()
    return render(request, 'listar_cajas.html', {'cajas': cajas})

def abrir_caja(request):
    if request.method == 'POST':
        form = CajaForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            caja.abrir_caja()
            return redirect('listar_cajas')
    else:
        form = CajaForm()
    return render(request, 'abrir_caja.html', {'form': form})

def cerrar_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)
    caja.cerrar_caja()
    return redirect('listar_cajas')

def modificar_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)
    if request.method == 'POST':
        form = CajaForm(request.POST, instance=caja)
        if form.is_valid():
            form.save()
            return redirect('listar_cajas')
    else:
        form = CajaForm(instance=caja)
    return render(request, 'modificar_caja.html', {'form': form})

def eliminar_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)
    caja.delete()
    return redirect('listar_cajas')

def listar_servicios(request):
    servicios = Servicios.objects.all()
    return render(request, 'listar_servicios.html', {'servicios': servicios})

def crear_servicio(request):
    if request.method == 'POST':
        form = ServiciosForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_servicios')
    else:
        form = ServiciosForm()
    return render(request, 'crear_servicio.html', {'form': form})

def modificar_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    if request.method == 'POST':
        form = ServiciosForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            return redirect('listar_servicios')
    else:
        form = ServiciosForm(instance=servicio)
    return render(request, 'modificar_servicio.html', {'form': form})

def eliminar_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    if request.method == 'POST':
        servicio.delete()
        return redirect('listar_servicios')
    return render(request, 'eliminar_servicio.html', {'servicio': servicio})