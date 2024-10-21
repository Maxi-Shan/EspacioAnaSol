from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.timezone import now
from django.contrib import messages
from django.utils import timezone
from .models import Caja, Empleado, Servicios, ServicioXTurno, Turno, EmpleadoXTurno, Cliente, Venta, DetalleVenta, Reservas
from .forms import LoginForm, EmpleadoForm, AbrirCajaForm, ServiciosForm, TurnoForm, ClienteForm, VentaForm, EstadoReservaForm, DetalleVentaForm

def login_view(request):
    messages_to_display = []

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            contraseña = form.cleaned_data['contraseña']
            try:
                empleado = Empleado.objects.get(dni=dni)
                if not empleado.verificar_contraseña(contraseña):
                    messages_to_display.append('DNI o contraseña incorrectos o no registrados')
                elif not empleado.estado_empleado:
                    messages_to_display.append('Este empleado está suspendido')
                else:
                    request.session['empleado_dni'] = empleado.dni 
                    if empleado.es_admin:
                        return redirect('pagina_admin')
                    else:
                        return redirect('pagina_principal')
            except Empleado.DoesNotExist:
                messages_to_display.append('DNI o contraseña incorrectos o no registrados')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form, 'messages_to_display': messages_to_display})


@login_required
def pagina_principal(request):
    return render(request, 'pagina_principal.html')

def admin_required(view_func):
    def _wrapped_view_func(request, *args, **kwargs):
        dni_empleado = request.session.get('empleado_dni')
        empleado = get_object_or_404(Empleado, dni=dni_empleado)
        if not empleado.es_admin:
            messages.error(request, "Acceso denegado. Solo los administradores pueden acceder.")
            return redirect('pagina_principal')
        return view_func(request, *args, **kwargs)
    return _wrapped_view_func


@admin_required
def pagina_admin(request):
    return render(request, 'pagina_admin.html')

@admin_required
@login_required
def listar_empleados(request):
    empleados = Empleado.objects.all()
    return render(request, 'listar_empleados.html', {'empleados': empleados})

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


def modificar_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            messages.success(request, 'Empleado actualizado exitosamente.')
            return redirect('listar_empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'modificar_empleado.html', {'form': form})


def eliminar_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    if request.method == 'POST':
        empleado.delete()
        messages.success(request, 'Empleado eliminado exitosamente.')
        return redirect('listar_empleados')
    return render(request, 'eliminar_empleado.html', {'empleado': empleado})

def listar_cajas(request):
    cajas = Caja.objects.all()
    caja_abierta = cajas.filter(fecha_cierre__isnull=True).exists()
    
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)

    return render(request, 'listar_cajas.html', {
        'cajas': cajas, 
        'caja_abierta': caja_abierta,
        'es_admin': empleado.es_admin  
    })


def abrir_caja(request):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    if request.method == 'POST':
        form = AbrirCajaForm(request.POST)
        if form.is_valid():
            caja = form.save(commit=False)
            dni_empleado = request.session.get('empleado_dni')
            empleado = get_object_or_404(Empleado, dni=dni_empleado)
            caja.empleado = empleado
            caja.save()
            messages.success(request, 'Caja abierta correctamente.')
            return redirect('listar_cajas')
    else:
        form = AbrirCajaForm()
    return render(request, 'abrir_caja.html', {'form': form, 'es_admin': empleado.es_admin})

def cerrar_caja(request, id_caja):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    caja = get_object_or_404(Caja, id_caja=id_caja)

    if request.method == 'POST':
        dni_empleado = request.session.get('empleado_dni')
        empleado = get_object_or_404(Empleado, dni=dni_empleado)

        caja.cerrar_caja(empleado)
        messages.success(request, 'Caja cerrada correctamente.')
        return redirect('listar_cajas')

    return render(request, 'cerrar_caja.html', {'caja': caja, 'es_admin': empleado.es_admin})


def modificar_caja(request, id_caja):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    caja = get_object_or_404(Caja, id_caja=id_caja)

    if request.method == 'POST':
        monto_inicial = request.POST.get('monto_inicial', caja.monto_inicial)
        monto_recaudado = request.POST.get('monto_recaudado', caja.monto_recaudado)

        try:
            monto_inicial = float(monto_inicial)
            monto_recaudado = float(monto_recaudado)
        except ValueError:
            messages.error(request, 'Los montos ingresados deben ser valores numéricos.')
            return redirect('modificar_caja', id_caja=id_caja)

        caja.monto_inicial = monto_inicial
        caja.monto_recaudado = monto_recaudado

        caja.monto_final = caja.monto_inicial + caja.monto_recaudado
        
        caja.save()

        messages.success(request, 'Montos actualizados y monto final recalculado exitosamente.')
        return redirect('listar_cajas')

    return render(request, 'modificar_caja.html', {'caja': caja, 'es_admin': empleado.es_admin})


def eliminar_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)

    if request.method == 'POST':
        caja.delete()
        messages.success(request, 'Caja eliminada exitosamente.')
        return redirect('listar_cajas')

    return render(request, 'eliminar_caja.html', {'caja': caja})

def listar_servicios(request):
    servicios = Servicios.objects.all()
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)

    context = {
        'servicios': servicios,
        'es_admin': empleado.es_admin, 
    }
    return render(request, 'listar_servicios.html', context)

def crear_servicio(request):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    if request.method == 'POST':
        form = ServiciosForm(request.POST, request.FILES)
        if form.is_valid():
            form.save() 
            messages.success(request, 'Servicio creado exitosamente.')
            return redirect('listar_servicios')
    else:
        form = ServiciosForm()
    return render(request, 'crear_servicio.html', {'form': form, 'es_admin': empleado.es_admin })

def modificar_servicio(request, id_servicio):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    if request.method == 'POST':
        form = ServiciosForm(request.POST, request.FILES, instance=servicio) 
        if form.is_valid():
            form.save()
            return redirect('listar_servicios')
    else:
        form = ServiciosForm(instance=servicio)
    return render(request, 'modificar_servicio.html', {'form': form, 'es_admin': empleado.es_admin})

def eliminar_servicio(request, id_servicio):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    if request.method == 'POST':
        servicio.delete()
        return redirect('listar_servicios')
    return render(request, 'eliminar_servicio.html', {'servicio': servicio})
    
def listar_turnos(request):
    turnos = Turno.objects.all()
    servicios_x_turno = ServicioXTurno.objects.select_related('id_turno', 'id_servicio').all()
    empleados_x_turno = EmpleadoXTurno.objects.select_related('id_turno', 'dni_emp').all()

    dni_empleado = request.session.get('empleado_dni')
    empleado = Empleado.objects.get(dni=dni_empleado)

    context = {
        'turnos': turnos,
        'servicios_x_turno': servicios_x_turno,
        'empleados_x_turno': empleados_x_turno,
        'es_admin': empleado.es_admin, 
    }
    return render(request, 'listar_turnos.html', context)

def crear_registro_turno(request):

    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)

    if request.method == 'POST':
        servicio_id = request.POST.get('servicio_id')
        empleado_id = request.POST.get('empleado_id')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')

     # Crear el objeto Turno y guardarlo
        turno = Turno.objects.create(fecha=fecha, hora=hora, estado_turno=True)

     # Verificar si se ha seleccionado un servicio y crear la relación
        if servicio_id:
            ServicioXTurno.objects.create(id_servicio_id=servicio_id, id_turno=turno)

     # Verificar si se ha seleccionado un empleado y crear la relación
        if empleado_id:
            EmpleadoXTurno.objects.create(dni_emp_id=empleado_id, id_turno=turno)

        messages.success(request, 'Registro creado exitosamente.')
        return redirect('listar_turnos')

    servicios = Servicios.objects.all()
    empleados = Empleado.objects.all()
    return render(request, 'crear_registro_turno.html', {'servicios': servicios, 'empleados': empleados, 'es_admin': empleado.es_admin})

from django.core.exceptions import ValidationError

def modificar_registro_turno(request, turno_id):
    turno = get_object_or_404(Turno, id_turno=turno_id)
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)

    servicio_actual = ServicioXTurno.objects.filter(id_turno=turno).first()
    empleado_actual = EmpleadoXTurno.objects.filter(id_turno=turno).first()

    if request.method == 'POST':
        nuevo_servicio_id = request.POST.get('id_servicio')
        nuevo_empleado_id = request.POST.get('id_empleado')

        nueva_fecha = request.POST.get('fecha')
        nueva_hora = request.POST.get('hora')

        # Actualizar el estado del turno desde el select
        estado_turno = request.POST.get('estado_turno') == 'True'  # Verifica el valor del select

        # Actualizar el turno
        turno.fecha = nueva_fecha
        turno.hora = nueva_hora
        turno.estado_turno = estado_turno  # Asigna el nuevo valor
        turno.save()

        # Actualizar o crear el servicio relacionado con el turno
        if servicio_actual:
            servicio_actual.id_servicio_id = nuevo_servicio_id
            servicio_actual.save()
        else:
            ServicioXTurno.objects.create(id_servicio_id=nuevo_servicio_id, id_turno=turno)

        # Actualizar o crear el empleado relacionado con el turno
        if empleado_actual:
            empleado_actual.dni_emp_id = nuevo_empleado_id
            empleado_actual.save()
        else:
            EmpleadoXTurno.objects.create(dni_emp_id=nuevo_empleado_id, id_turno=turno)

        messages.success(request, 'El turno ha sido actualizado correctamente.')
        return redirect('listar_turnos')

    servicios = Servicios.objects.all()
    empleados = Empleado.objects.all()

    return render(request, 'modificar_registro_turno.html', {
        'turno': turno,
        'servicios': servicios,
        'empleados': empleados,
        'servicio_actual': servicio_actual.id_servicio if servicio_actual else None,
        'empleado_actual': empleado_actual.dni_emp if empleado_actual else None,
        'es_admin': empleado.es_admin
    })




def eliminar_registro_turno(request, turno_id):
    turno = Turno.objects.get(id_turno=turno_id)

    if request.method == 'POST':
        turno.delete()
        messages.success(request, 'Registro eliminado exitosamente.')
        return redirect('listar_turnos')

    return render(request, 'eliminar_registro_turno.html', {'turno': turno})

def listar_clientes(request):
    clientes = Cliente.objects.all()
    
    dni_empleado = request.session.get('empleado_dni')
    empleado = Empleado.objects.get(dni=dni_empleado)
    
    context = {
        'clientes': clientes,
        'es_admin': empleado.es_admin,
    }
    return render(request, 'listar_clientes.html', context)


def listar_ventas(request):
    ventas = Venta.objects.all()

    dni_empleado = request.session.get('empleado_dni')
    empleado = Empleado.objects.get(dni=dni_empleado)

    context = {
        'ventas': ventas,
        'es_admin': empleado.es_admin, 
    }
    return render(request, 'listar_ventas.html', context)


def crear_venta(request):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    if request.method == "POST":
        caja_abierta = Caja.objects.filter(estado=True).first()  
        if caja_abierta:
            form = VentaForm(request.POST)
            if form.is_valid():
                venta = form.save(commit=False)
                venta.id_caja = caja_abierta  
                venta.fecha_venta = timezone.now().date()  
                venta.hs_venta = timezone.now().time() 
                venta.save() 
                messages.success(request, "Venta registrada exitosamente.")
                return redirect('listar_ventas') 
        else:
            messages.error(request, "No se puede registrar la venta, la caja está cerrada.")
            return redirect('crear_venta')
    else:
        form = VentaForm()
    return render(request, 'crear_venta.html', {'form': form, 'es_admin': empleado.es_admin})

def modificar_venta(request, venta_id):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    venta = get_object_or_404(Venta, id_venta=venta_id)

    if request.method == 'POST':
        nuevo_estado = request.POST.get('estado_venta')
        venta.estado_venta = nuevo_estado
        venta.save()
        messages.success(request, 'Estado de la venta modificado exitosamente.')
        return redirect('listar_ventas')

    return render(request, 'modificar_venta.html', {'venta': venta, 'es_admin': empleado.es_admin})

def eliminar_venta(request, venta_id):
    venta = get_object_or_404(Venta, id_venta=venta_id)

    if request.method == 'POST':
        venta.delete()
        messages.success(request, 'Venta eliminada exitosamente.')
        return redirect('listar_ventas')

    return render(request, 'eliminar_venta.html', {'venta': venta})

def ver_reserva(request, reserva_id):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    reserva = Reservas.objects.get(id_reserva=reserva_id)
    return render(request, 'ver_reserva.html', {'reserva': reserva, 'es_admin': empleado.es_admin})

def ver_detalle_venta(request, venta_id):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    detalles_venta = DetalleVenta.objects.filter(id_venta=venta_id)  # Obtiene todos los detalles para una venta
    return render(request, 'lista_detalle_ventas.html', {'detalles_ventas': detalles_venta, 'es_admin': empleado.es_admin})

def registrar_ventas_pendientes():
    if Caja.objects.filter(estado=True).exists():
        ventas_pendientes = Venta.objects.all()
        for venta_pendiente in ventas_pendientes:
            # Registrar cada venta pendiente como una venta normal
            venta = Venta(
                id_caja=Caja.objects.filter(estado=True).first(),
                fecha_venta=venta_pendiente.fecha_venta,
                hs_venta=venta_pendiente.hs_venta,
                monto_total=venta_pendiente.monto_total,
                estado_venta=0  # Marcarlas como completadas
            )
            venta.save()

            # Registrar el detalle de la venta
            detalle_venta = DetalleVenta(
                id_venta=venta,
                id_reserva=venta_pendiente.id_reserva,
                metodo_pago=venta_pendiente.metodo_pago,
                monto_subtotal=venta_pendiente.monto_subtotal
            )
            detalle_venta.save()

        ventas_pendientes.delete()  # Limpiar ventas pendientes una vez registradas

def modificar_detalle_venta(request, detalle_id):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    detalle = get_object_or_404(DetalleVenta, id_detalle_venta=detalle_id)

    if request.method == 'POST':
        form = DetalleVentaForm(request.POST, request.FILES, instance=detalle)
        if form.is_valid():
            form.save()
            # Redirige a la lista de detalles de ventas asociada a esta venta
            return redirect('lista_detalle_ventas', detalle.id_venta.id_venta)  # Pasa el id de la venta
    else:
        form = DetalleVentaForm(instance=detalle)

    return render(request, 'modificar_detalle_venta.html', {'form': form, 'detalle': detalle, 'es_admin': empleado.es_admin})


def modificar_estado_reserva(request, reserva_id):
    dni_empleado = request.session.get('empleado_dni')
    empleado = get_object_or_404(Empleado, dni=dni_empleado)
    reserva = get_object_or_404(Reservas, id_reserva=reserva_id)

    # Inicializar el formulario
    form = EstadoReservaForm(instance=reserva)  # Asignar el formulario con la reserva existente

    if request.method == 'POST':
        form = EstadoReservaForm(request.POST, instance=reserva)  # Volver a asignar el formulario con los datos POST
        if form.is_valid():
            form.save()
            return redirect('ver_reserva', reserva_id=reserva.id_reserva)  # Redirige a la vista de ver reserva

    # No hay necesidad de asignar 'form' nuevamente aquí porque ya se ha hecho arriba
    return render(request, 'modificar_estado_reserva.html', {'form': form, 'reserva': reserva, 'es_admin': empleado.es_admin})

