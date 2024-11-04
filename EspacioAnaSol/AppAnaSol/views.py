from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.utils.timezone import now
from django.contrib import messages
from django.utils import timezone
from .models import Caja, Empleado, Servicios, ServicioXTurno, Turno, EmpleadoXTurno, Cliente, Venta, DetalleVenta, Reservas, D_VentaXServicio
from .forms import LoginForm, EmpleadoForm, AbrirCajaForm, ServiciosForm, TurnoForm, ClienteForm, VentaForm, EstadoReservaForm, DetalleVentaForm, MultipleTurnoForm
from django.http import JsonResponse

def obtener_empleado_autenticado(request):
    dni_empleado = request.session.get('empleado_dni')
    return get_object_or_404(Empleado, dni=dni_empleado)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            contraseña = form.cleaned_data['contraseña']
            print(f'DNI: {dni}, Contraseña: {contraseña}')  # Verifica los datos ingresados
            ...
            try:
                empleado = Empleado.objects.get(dni=dni)
                if empleado.verificar_contraseña(contraseña):
                    request.session['empleado_dni'] = empleado.dni
                    return redirect('pagina_principal')  # Asegúrate de que esta vista exista
                else:
                    messages.error(request, 'DNI o contraseña incorrectos.')
            except Empleado.DoesNotExist:
                messages.error(request, 'DNI o contraseña no existen.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def requerir_autenticacion(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'empleado_dni' not in request.session:
            return redirect('login')  # Ajusta si el nombre de la URL es diferente
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        empleado = obtener_empleado_autenticado(request)
        if not empleado.es_admin:
            return redirect('pagina_principal')  # Redirige a la página principal si no es admin
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@requerir_autenticacion
def pagina_principal(request):
    if 'empleado_dni' not in request.session:
        return redirect('login')  # Ajusta si el nombre de la URL es diferente
    empleado = obtener_empleado_autenticado(request)

    return render(request, 'pagina_principal.html', {
        'es_admin': empleado.es_admin  
    })


@admin_required
def list_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'list_empleados.html', {'empleados': empleados})

@admin_required
def delete_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    if request.method == "POST":
        empleado.delete()
        return redirect('list_empleados')
    return render(request, 'delete_confirm.html', {'empleado': empleado})

@admin_required
def update_empleado_status(request, dni):
    empleado = Empleado.objects.get(dni=dni)
    if request.method == 'POST':
        estado_empleado = request.POST.get('estado_empleado')
        es_admin = request.POST.get('es_admin')

        # Convierte 'True'/'False' a booleanos
        empleado.estado_empleado = estado_empleado
        empleado.es_admin = es_admin == 'True'  # Solo true si el valor es la cadena 'True'

        # Guarda los cambios
        empleado.save()
        return redirect('list_empleados')  # Redirige a la lista de empleados

@admin_required
def add_empleado(request):
    if request.method == "POST":
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_empleados')
    else:
        form = EmpleadoForm()
    return render(request, 'add_empleado.html', {'form': form})

@admin_required
@login_required  # Asegúrate de usar el decorador correcto
def update_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)  # Verifica que este DNI exista
    if request.method == "POST":
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            return redirect('list_empleados')  # Asegúrate de tener esta URL definida
    else:
        form = EmpleadoForm(instance=empleado)

    return render(request, 'update_empleado.html', {'form': form, 'empleado': empleado})  # Asegúrate de pasar el empleado


@requerir_autenticacion
def abrir_caja(request):
    if request.method == 'POST':
        monto_inicial = request.POST.get('monto_inicial')
        print(f'Monto Inicial: {monto_inicial}') 

        # Asegúrate de que monto_inicial sea un número válido
        try:
            monto_inicial = float(monto_inicial)  # Convierte a float
        except ValueError:
            return render(request, 'abrir_caja.html', {'error': 'Monto inicial no válido.'})

        # Intenta obtener el empleado basado en el dni
        dni_empleado = request.session.get('empleado_dni')  # Obtenemos el dni del empleado desde la sesión
        try:
            empleado = Empleado.objects.get(dni=dni_empleado)
        except Empleado.DoesNotExist:
            return render(request, 'abrir_caja.html', {'error': 'Empleado no encontrado.'})

        # Crea la nueva caja
        nueva_caja = Caja(
            empleado=empleado,
            monto_inicial=monto_inicial,
            estado=True  # Asegúrate de que el estado esté configurado como abierto
        )
        nueva_caja.save()

        return redirect('list_cajas')

    return render(request, 'abrir_caja.html')



@requerir_autenticacion
def list_cajas(request):
    # Obtener el empleado autenticado
    empleado = obtener_empleado_autenticado(request)

    # Verificar si el empleado es admin
    es_admin = empleado.es_admin

    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()  # Verifica si hay cajas abiertas

    # Sumar el monto total por cada caja
    for caja in cajas:
        monto_recaudado = caja.monto_recaudado if caja.monto_recaudado else 0
        caja.monto_total = caja.monto_inicial + monto_recaudado  # Suma de los montos

    return render(request, 'list_cajas.html', {
        'cajas': cajas,
        'cajas_abiertas': cajas_abiertas,
        'es_admin': es_admin,  # Pasar el estado de admin al contexto
    })

@requerir_autenticacion
def cerrar_caja(request, id_caja):
    caja = Caja.objects.get(id_caja=id_caja)

    if request.method == 'POST':
        # Esta parte se queda igual, pero debes asegurarte de que la lógica de cierre de caja esté correcta
        caja.cerrar_caja(obtener_empleado_autenticado(request))  # Aquí se usa el empleado que cierra la caja
        return redirect('list_cajas')

    return render(request, 'cerrar_caja.html', {'caja': caja})

@admin_required
def update_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)
    
    if request.method == "POST":
        monto_inicial = request.POST.get('monto_inicial')
        # Aquí puedes agregar otros campos que necesites modificar
        
        try:
            caja.monto_inicial = float(monto_inicial)
            # Actualiza otros campos según sea necesario
            caja.save()
            messages.success(request, 'Caja modificada con éxito.')
            return redirect('list_cajas')
        except ValueError:
            messages.error(request, 'Monto inicial no válido.')
    
    return render(request, 'update_caja.html', {'caja': caja})

@admin_required
def delete_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)
    if request.method == "POST":
        caja.delete()
        messages.success(request, 'Caja eliminada con éxito.')
        return redirect('list_cajas')
    
    return render(request, 'delete_caja.html', {'caja': caja})


@requerir_autenticacion
def list_servicios(request):
    servicios = Servicios.objects.all()
    empleado = obtener_empleado_autenticado(request)

    # Verificar si el empleado es admin
    es_admin = empleado.es_admin

    return render(request, 'list_servicios.html', {
        'servicios': servicios,
        'es_admin': es_admin,
        })


@requerir_autenticacion
def add_servicio(request):
    if request.method == 'POST':
        form = ServiciosForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio agregado con éxito.')
            return redirect('list_servicios')
    else:
        form = ServiciosForm()
    return render(request, 'add_servicio.html', {'form': form})


@requerir_autenticacion
def update_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    if request.method == 'POST':
        form = ServiciosForm(request.POST, request.FILES, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado con éxito.')
            return redirect('list_servicios')
    else:
        form = ServiciosForm(instance=servicio)
    return render(request, 'update_servicio.html', {'form': form, 'servicio': servicio})


@requerir_autenticacion
def delete_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado con éxito.')
        return redirect('list_servicios')
    return render(request, 'delete_servicio.html', {'servicio': servicio})

# Crear cuatro turnos a la vez
@requerir_autenticacion
def add_turno(request):
    if request.method == 'POST':
        form = MultipleTurnoForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            servicio = form.cleaned_data['servicio']

            # Obtener las horas del formulario
            horas = [
                form.cleaned_data['hora1'],
                form.cleaned_data['hora2'],
                form.cleaned_data['hora3'],
                form.cleaned_data['hora4'],
            ]

            # Obtener los empleados seleccionados
            empleados = [
                form.cleaned_data['empleado1'],
                form.cleaned_data['empleado2'],
                form.cleaned_data['empleado3'],
                form.cleaned_data['empleado4'],
            ]

            # Crear los turnos con el estado 'disponible'
            for i in range(4):
                turno = Turno.objects.create(
                    fecha=fecha,
                    hora=horas[i],
                    estado_turno='disponible'
                )
                EmpleadoXTurno.objects.create(dni_emp=empleados[i], id_turno=turno)
                ServicioXTurno.objects.create(id_servicio=servicio, id_turno=turno)

            messages.success(request, 'Cuatro turnos creados correctamente.')
            return redirect('list_turnos')  # Redirigir a la lista de turnos
        else:
            messages.error(request, 'Por favor, completa el formulario correctamente.')
    else:
        form = MultipleTurnoForm()

    return render(request, 'add_turno.html', {'form': form})

# Listar turnos
@requerir_autenticacion
def list_turnos(request):
    turnos = Turno.objects.all().prefetch_related('empleadoxturno_set', 'servicioxturno_set')  # Carga los turnos y sus relaciones

    # Crear una lista para almacenar los datos de los turnos
    turnos_data = []
    for turno in turnos:
        empleados = EmpleadoXTurno.objects.filter(id_turno=turno).select_related('dni_emp')
        servicios = ServicioXTurno.objects.filter(id_turno=turno).select_related('id_servicio')
        
        # Obtener el nombre del empleado y del servicio
        empleado_nombres = ', '.join([f"{emp.dni_emp.nombre} {emp.dni_emp.apellido}" for emp in empleados])
        servicio_nombres = ', '.join([servicio.id_servicio.nombre_del_servicio for servicio in servicios])
        
        turnos_data.append({
            'turno': turno,
            'empleados': empleado_nombres,
            'servicios': servicio_nombres
        })

    return render(request, 'list_turnos.html', {'turnos_data': turnos_data})

# Modificar un turno
@requerir_autenticacion
def update_turno(request, turno_id):
    turno = get_object_or_404(Turno, id_turno=turno_id)
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turno actualizado correctamente.')
            return redirect('list_turnos')
    else:
        form = TurnoForm(instance=turno)

    return render(request, 'update_turno.html', {'form': form, 'turno': turno})

def update_turno(request, turno_id):
    turno = get_object_or_404(Turno, id_turno=turno_id)  # Obtener el turno específico
    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()  # Guardar los cambios en el turno
            messages.success(request, 'Turno actualizado correctamente.')
            return redirect('list_turnos')  # Redirigir a la lista de turnos
    else:
        form = TurnoForm(instance=turno)  # Rellenar el formulario con la instancia del turno

    return render(request, 'update_turno.html', {'form': form, 'turno': turno})  # Renderizar el template

# Eliminar un turno
@requerir_autenticacion
def delete_turno(request, turno_id):
    turno = get_object_or_404(Turno, id_turno=turno_id)  # Obtener el turno específico
    if request.method == 'POST':
        turno.delete()  # Eliminar el turno
        messages.success(request, 'Turno eliminado correctamente.')
        return redirect('list_turnos')  # Redirigir a la lista de turnos

    return render(request, 'delete_turno_confirm.html', {'turno': turno})  # Confirmación de eliminación

def list_clientes(request):
    clientes = Cliente.objects.all()  # Retrieve all clients
    return render(request, 'list_clientes.html', {'clientes': clientes})