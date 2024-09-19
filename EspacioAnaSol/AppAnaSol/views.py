from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import LoginForm
from .models import Empleado

def inicio(request):
    return render(request, 'inicio.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            contraseña = form.cleaned_data['contraseña']
            try:
                empleado = Empleado.objects.get(dni=dni, contraseña=contraseña)
            except Empleado.DoesNotExist:
                messages.error(request, 'DNI o contraseña incorrectos.')
                return render(request, 'login.html', {'form': form})

            if empleado.estado_empleado:
                request.session['empleado_id'] = empleado.dni
                return redirect('pagina_principal')
            else:
                messages.error(request, 'Empleado inactivo.')
                return render(request, 'login.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def pagina_principal(request):
    if 'empleado_id' not in request.session:
        return redirect('login')

    empleado_id = request.session['empleado_id']
    try:
        empleado = Empleado.objects.get(dni=empleado_id)
    except Empleado.DoesNotExist:
        return redirect('login')

    return render(request, 'pagina_principal.html', {'empleado': empleado})

def login_admin_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            contraseña = form.cleaned_data['contraseña']
            try:
                empleado = Empleado.objects.first()  # Solo el primer empleado puede ser administrador
            except Empleado.DoesNotExist:
                messages.error(request, 'No hay empleados registrados.')
                return render(request, 'login_admin.html', {'form': form})

            if empleado.dni == dni and empleado.contraseña == contraseña:
                if empleado.estado_empleado:
                    # Guardar el DNI del empleado en la sesión
                    request.session['empleado_id'] = empleado.dni
                    return redirect('pagina_admin')
                else:
                    messages.error(request, 'Empleado inactivo.')
                    return render(request, 'login_admin.html', {'form': form})
            else:
                messages.error(request, 'DNI o contraseña incorrectos.')
                return render(request, 'login_admin.html', {'form': form})
    else:
        form = LoginForm()
    return render(request, 'login_admin.html', {'form': form})

def pagina_admin(request):
    # Verificar si el empleado está logueado como administrador
    if 'empleado_id' not in request.session:
        return redirect('login_admin')

    empleado_id = request.session['empleado_id']
    try:
        empleado = Empleado.objects.first()  # Solo el primer empleado es administrador
        if empleado.dni != empleado_id:
            return redirect('login_admin')
    except Empleado.DoesNotExist:
        return redirect('login_admin')

    return render(request, 'pagina_admin.html', {'empleado': empleado})