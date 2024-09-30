from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Caja, Empleado
from .forms import LoginForm
from .forms import EmpleadoForm
from django.contrib.auth.mixins import UserPassesTestMixin
from django.utils import timezone
from .forms import AbrirCajaForm, CerrarCajaForm

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            contraseña = form.cleaned_data['contraseña']
            try:
                empleado = Empleado.objects.get(dni=dni, contraseña=contraseña)
                if not empleado.estado_empleado:
                    messages.error(request, 'Este empleado está suspendido')
                    return redirect('login')
                else:
                    request.session['empleado_dni'] = empleado.dni  # Almacena el dni en la sesión
                    if empleado.es_admin:
                        return redirect('pagina_admin')
                    else:
                        return redirect('pagina_principal')
            except Empleado.DoesNotExist:
                messages.error(request, 'DNI o contraseña incorrectos o no registrados')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        if not request.empleado or not request.empleado.es_admin:
            messages.error(request, "Acceso denegado. Solo los administradores pueden acceder.")
            return redirect('pagina_principal')  
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func

@login_required
@admin_required
def listar_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'listar_empleados.html', {'empleados': empleados})

@login_required
@admin_required
def crear_empleado(request):
    if request.method == 'POST':
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado creado exitosamente.')
            return redirect('listar_empleados')
    else:
        form = EmpleadoForm()
    return render(request, 'crear_empleado.html', {'form': form})

@login_required
@admin_required
def editar_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado exitosamente.')
            return redirect('listar_empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'editar_empleado.html', {'form': form})

@login_required
@admin_required
def eliminar_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado exitosamente.')
        return redirect('listar_empleados')
    return render(request, 'eliminar_empleado.html', {'empleado': empleado})


def inicio(request):
    return render(request, 'inicio.html')

@login_required
def pagina_principal(request):
    return render(request, 'pagina_principal.html')

@admin_required
def pagina_admin(request):
    return render(request, 'pagina_admin.html')

@login_required
@admin_required
def clientes_view(request):
    return render(request, 'clientes.html')

@login_required
@admin_required
def ventas_view(request):
    return render(request, 'ventas.html')

@login_required
@admin_required
def turnos_view(request):
    return render(request, 'turnos.html')

@login_required
@admin_required
def servicios_view(request):
    return render(request, 'servicios.html')

@login_required
@admin_required
def caja_view(request):
    return render(request, 'caja.html')


def logout_view(request):
    logout(request)
    return redirect('login') 