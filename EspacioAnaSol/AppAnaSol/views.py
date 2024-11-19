from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from .models import Caja, Empleado, ServicioXTurno, EmpleadoXTurno, Cliente, Turno, Reservas, Servicios, Venta, Reservas, DetalleVenta
from .forms import LoginForm, EmpleadoForm, ServiciosForm, ClienteForm, TurnoForm
from django.http import HttpResponse
from django.core import management
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse
from decimal import Decimal
import os
import json

def obtener_empleado_autenticado(request):
    dni_empleado = request.session.get('empleado_dni')
    return get_object_or_404(Empleado, dni=dni_empleado)

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            contraseña = form.cleaned_data['contraseña']
            try:
                empleado = Empleado.objects.get(dni=dni)
                if empleado.verificar_contraseña(contraseña):
                    request.session['empleado_dni'] = empleado.dni
                    messages.success(request, '¡Entraste a la Interfaz para Empleados! ¡Bienvenido a Espacio Ana Sol!')
                    return redirect('pagina_principal') 
                else:
                    messages.error(request, '¡DNI o Contraseña incorrectos, vuelva a intentarlo!')
            except Empleado.DoesNotExist:
                messages.error(request, '¡Empleado inexistente!')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if 'empleado_dni' in request.session:
        del request.session['empleado_dni']
        messages.success(request, '¡Saliste de Espacio Ana Sol, adiós!')
    else:
        messages.warning(request, 'No estabas autenticado.')
    return redirect('login')
def requerir_autenticacion(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'empleado_dni' not in request.session:
            return redirect('login') 
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        empleado = obtener_empleado_autenticado(request)
        if not empleado.es_admin:
            return redirect('pagina_principal')  
        return view_func(request, *args, **kwargs)
    return _wrapped_view



@requerir_autenticacion
def pagina_principal(request):
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()  
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'pagina_principal.html', {
        'cajas_abiertas': cajas_abiertas,
        'es_admin': empleado.es_admin,
        'nombre': empleado
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
        empleado.estado_empleado = estado_empleado
        empleado.es_admin = es_admin == 'True'  
        empleado.save()
        return redirect('list_empleados')

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
def update_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    
    if request.method == "POST":
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        domicilio = request.POST.get('domicilio')
        correo_electronico = request.POST.get('correo_electronico')
        numero_telefono = request.POST.get('numero_telefono')
        contraseña = request.POST.get('contraseña')
        estado_empleado = request.POST.get('estado_empleado')
        es_admin = request.POST.get('es_admin') == 'True' 

        if not nombre or not apellido or not correo_electronico:
            messages.error(request, "Los campos 'Nombre', 'Apellido' y 'Correo Electrónico' son obligatorios.")
            return render(request, 'update_empleado.html', {'empleado': empleado})

        empleado.nombre = nombre
        empleado.apellido = apellido
        empleado.domicilio = domicilio
        empleado.correo_electronico = correo_electronico
        empleado.numero_telefono = numero_telefono
        empleado.contraseña = contraseña
        empleado.estado_empleado = estado_empleado
        empleado.es_admin = es_admin

        empleado.save()

        return redirect('list_empleados')

    return render(request, 'update_empleado.html', {'empleado': empleado})



@requerir_autenticacion
def abrir_caja(request):
    empleado = obtener_empleado_autenticado(request)
    if request.method == 'POST':
        monto_inicial = request.POST.get('monto_inicial')

        try:
            monto_inicial = float(monto_inicial)  # Convierte a float
        except ValueError:
            return render(request, 'abrir_caja.html', {'error': 'Monto inicial no válido.'})

        # Obtener el empleado autenticado
        dni_empleado = request.session.get('empleado_dni')  # Obtener el dni del empleado desde la sesión
        try:
            empleado = Empleado.objects.get(dni=dni_empleado)
        except Empleado.DoesNotExist:
            return render(request, 'abrir_caja.html', {'error': 'Empleado no encontrado.'})

        # Obtener la hora actual ajustada a la zona horaria configurada en Django
        hora_actual = timezone.localtime(timezone.now())  # Hora local con la zona horaria configurada

        # Crea la nueva caja
        nueva_caja = Caja(
            empleado=empleado,
            monto_inicial=monto_inicial,
            estado=True,  # Caja abierta
            fecha_apertura=hora_actual  # Asigna la hora de apertura
        )
        nueva_caja.save()

        return redirect('list_cajas')

    return render(request, 'abrir_caja.html', {
        'es_admin': empleado.es_admin
    })



@requerir_autenticacion
def list_cajas(request):
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists() 
    empleado = obtener_empleado_autenticado(request) 

    for caja in cajas:
        monto_recaudado = caja.monto_recaudado if caja.monto_recaudado else 0
        caja.monto_total = caja.monto_inicial + monto_recaudado  

    return render(request, 'list_cajas.html', {
        'cajas': cajas,
        'cajas_abiertas': cajas_abiertas,
        'es_admin': empleado.es_admin
    })


@requerir_autenticacion
def cerrar_caja(request, id_caja):
    caja = Caja.objects.get(id_caja=id_caja)
    empleado = obtener_empleado_autenticado(request)
    if request.method == 'POST':
        caja.cerrar_caja(obtener_empleado_autenticado(request)) 
        return redirect('list_cajas')

    return render(request, 'cerrar_caja.html', {'caja': caja, 'es_admin': empleado.es_admin})

def update_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)
    empleado = obtener_empleado_autenticado(request)
    if request.method == "POST":
        monto_inicial = request.POST.get('monto_inicial')

        if monto_inicial:
            monto_inicial = monto_inicial.replace(',', '.') 

        try:
            caja.monto_inicial = float(monto_inicial)
            caja.save()
            messages.success(request, 'Caja modificada con éxito.')
            return redirect('list_cajas')
        except ValueError:
            messages.error(request, 'Monto inicial no válido. Asegúrese de ingresar un número válido.')
    
    return render(request, 'update_caja.html', {'caja': caja, 'es_admin': empleado.es_admin})


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
    return render(request, 'list_servicios.html', {'servicios': servicios, 'es_admin': empleado.es_admin})


@requerir_autenticacion
def add_servicio(request):
    empleado = obtener_empleado_autenticado(request)
    if request.method == 'POST':
        form = ServiciosForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio agregado con éxito.')
            return redirect('list_servicios')
    else:
        form = ServiciosForm()
        print(form.errors)
    return render(request, 'add_servicio.html', {'form': form, 'es_admin': empleado.es_admin})


@requerir_autenticacion
def update_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    empleado = obtener_empleado_autenticado(request)
    if request.method == 'POST':
        # Verifica los datos que están llegando
        nombre_del_servicio = request.POST.get('nombre_del_servicio')
        descripcion_del_servicio = request.POST.get('descripcion_del_servicio')
        duracion = request.POST.get('duracion')
        precio_del_servicio = request.POST.get('precio_del_servicio')
        senia = request.POST.get('senia')

        print("Datos recibidos:", nombre_del_servicio, descripcion_del_servicio, duracion, precio_del_servicio, senia)

        if not nombre_del_servicio or not precio_del_servicio or not senia:
            messages.error(request, "El nombre, el precio y el valor sello son obligatorios.")
            return render(request, 'update_servicio.html', {'servicio': servicio})

        servicio.nombre_del_servicio = nombre_del_servicio
        servicio.descripcion_del_servicio = descripcion_del_servicio
        servicio.duracion = duracion
        servicio.precio_del_servicio = precio_del_servicio
        servicio.senia = senia

        if 'imagen' in request.FILES:
            servicio.imagen = request.FILES['imagen']

        servicio.save()
        messages.success(request, 'Servicio actualizado con éxito.')
        return redirect('list_servicios')

    return render(request, 'update_servicio.html', {'servicio': servicio, 'es_admin': empleado.es_admin})



@requerir_autenticacion
def delete_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado con éxito.')
        return redirect('list_servicios')
    return render(request, 'delete_servicio.html', {'servicio': servicio})

@requerir_autenticacion
def registrar_cliente(request):
    empleado = obtener_empleado_autenticado(request)
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()
            # Guardar el ID del cliente en la sesión para usarlo en la vista de Turno
            request.session['cliente_id'] = cliente.id_cliente
            return redirect('registrar_turno')
    else:
        form = ClienteForm()
    return render(request, 'registrar_cliente.html', {'form': form, 'es_admin': empleado.es_admin})

@requerir_autenticacion
def registrar_turno(request):
    cliente_id = request.session.get('cliente_id')
    empleado = obtener_empleado_autenticado(request)
    if not cliente_id:
        return redirect('registrar_cliente')

    if request.method == "POST":
        form = TurnoForm(request.POST, request.FILES)  # Importante: Agregar request.FILES aquí
        if form.is_valid():
            # Guardar el turno con commit=False para no guardar inmediatamente
            turno = form.save(commit=False)
            turno.id_cliente_id = cliente_id  # Asociar el cliente automáticamente
            turno.estado_turno = "Pendiente"  # Estado predeterminado como "Pendiente"
            turno.save()

            # Obtener el empleado y servicio del formulario
            empleado = form.cleaned_data['id_empleado']
            servicio = form.cleaned_data['id_servicio']
            
            # Crear registros en las tablas intermedias
            EmpleadoXTurno.objects.create(dni_emp=empleado, id_turno=turno)
            ServicioXTurno.objects.create(id_servicio=servicio, id_turno=turno)

            # Limpiar datos de sesión
            del request.session['cliente_id']
            return redirect('list_turnos')
    else:
        form = TurnoForm()

    return render(request, 'registrar_turno.html', {'form': form, 'es_admin': empleado.es_admin})

@requerir_autenticacion
def cancelar_registro(request):
    request.session.pop('cliente_id', None)  # Limpiar datos de sesión si existen
    return redirect('list_turnos')

# Listar turnos
@requerir_autenticacion
def list_turnos(request):
    empleado = obtener_empleado_autenticado(request)
    turnos = Turno.objects.select_related('id_cliente').prefetch_related('empleadoxturno_set', 'servicioxturno_set')
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    turnos = Turno.objects.all()

    turnos_data = []
    for turno in turnos:
        # Obtener los empleados y servicios relacionados con cada turno
        empleados = EmpleadoXTurno.objects.filter(id_turno=turno).select_related('dni_emp')
        servicios = ServicioXTurno.objects.filter(id_turno=turno).select_related('id_servicio')

        empleado_nombres = ', '.join([f"{emp.dni_emp.nombre} {emp.dni_emp.apellido}" for emp in empleados])
        servicio_nombres = ', '.join([servicio.id_servicio.nombre_del_servicio for servicio in servicios])

        # Añadir los datos de cada turno a la lista turnos_data
        turnos_data.append({
            'turno': turno,
            'empleados': empleado_nombres,
            'servicios': servicio_nombres,
            'id_cliente': turno.id_cliente if turno.id_cliente else None,  # Aseguramos que exista el cliente
            'diseño_uñas': turno.diseño_uñas,
            'senia_comprobante': turno.senia_comprobante,  # Añadido para mostrar la imagen del comprobante
            'cajas_abiertas': cajas_abiertas,
            'turnos_data': turnos,
        })

    context = {
        'turnos_data': turnos_data,
        'cajas_abiertas': cajas_abiertas
    }
    
    return render(request, 'list_turnos.html', context)


@requerir_autenticacion
def modificar_turno(request, turno_id):
    empleado = obtener_empleado_autenticado(request)
    turno = get_object_or_404(Turno, id_turno=turno_id)

    if request.method == "POST":
        empleado_id = request.POST.get('empleado')
        servicio_id = request.POST.get('servicio')
        diseño_uñas = request.FILES.get('diseño_uñas')
        senia_comprobante = request.FILES.get('senia_comprobante')

        # Actualizar el turno con los nuevos datos
        turno.id_empleado_id = empleado_id  # Asignar empleado
        turno.save()

        # Si se selecciona un servicio, actualizar la relación ServicioXTurno
        if servicio_id:
            # Eliminar los servicios actuales del turno (si existen)
            ServicioXTurno.objects.filter(id_turno=turno).delete()

            # Crear una nueva relación de servicio para el turno
            ServicioXTurno.objects.create(id_servicio_id=servicio_id, id_turno=turno)

        # Actualizar los archivos si fueron proporcionados
        if diseño_uñas:
            turno.diseño_uñas = diseño_uñas
        if senia_comprobante:
            turno.senia_comprobante = senia_comprobante

        turno.save()

        # Redirigir al listado de turnos o a una página de confirmación
        return redirect('list_turnos')

    # Obtener todos los empleados y servicios para mostrarlos en el formulario
    empleados = Empleado.objects.all()
    servicios = Servicios.objects.all()  # Asegúrate de que se obtienen todos los servicios

    # Obtener el servicio actual asociado al turno (si existe)
    servicios_asociados = ServicioXTurno.objects.filter(id_turno=turno)

    return render(request, 'modificar_turno.html', {
        'turno': turno,
        'empleados': empleados,
        'servicios': servicios,
        'servicios_asociados': servicios_asociados,
        'es_admin': empleado.es_admin
    })

@requerir_autenticacion
def eliminar_turno(request, turno_id):
    turno = get_object_or_404(Turno, id_turno=turno_id)
    turno.delete()
    return redirect('list_turnos')


@requerir_autenticacion
def list_clientes(request):
    empleado = obtener_empleado_autenticado(request)
    clientes = Cliente.objects.all() 
    return render(request, 'list_clientes.html', {'clientes': clientes, 'es_admin': empleado.es_admin})


@requerir_autenticacion
def backup_database(request):
    timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_filename = f'backup_{timestamp}.json'
    backup_path = os.path.join('backups', backup_filename)

    os.makedirs('backups', exist_ok=True)

    with open(backup_path, 'w') as backup_file:
        management.call_command('dumpdata', stdout=backup_file)

    messages.success(request, f'Copia de seguridad realizada con éxito: {backup_filename}')

    with open(backup_path, 'r') as f:
        response = HttpResponse(f.read(), content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="{backup_filename}"'
        return response
    

@requerir_autenticacion
def restore_database(request):
    if request.method == 'POST' and request.FILES['backup_file']:
        backup_file = request.FILES['backup_file']
        backup_path = os.path.join(settings.MEDIA_ROOT, 'backups', backup_file.name)

        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        with default_storage.open(backup_path, 'wb+') as destination:
            for chunk in backup_file.chunks():
                destination.write(chunk)

        try:
            management.call_command('loaddata', backup_path)
            messages.success(request, 'La base de datos se ha restaurado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al restaurar la base de datos: {str(e)}')
        finally:
            os.remove(backup_path)

        return HttpResponseRedirect(request.path_info)

    return render(request, 'restore_database.html')

@requerir_autenticacion
def list_ventas(request):
    ventas = Venta.objects.all()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'list_ventas.html', {'ventas': ventas, 'es_admin': empleado.es_admin})

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Venta, DetalleVenta
from .forms import MetodoPagoForm

def modificar_metodo_pago(request, venta_id):
    # Obtener la venta y el detalle de la venta relacionado con la venta
    venta = get_object_or_404(Venta, id_venta=venta_id)
    detalle_venta = get_object_or_404(DetalleVenta, id_venta=venta)

    if request.method == 'POST':
        form = MetodoPagoForm(request.POST, instance=detalle_venta)
        if form.is_valid():
            # Asignamos la venta actual a id_venta para asegurar que se mantenga la relación
            detalle_venta.id_venta = venta
            form.save()
            messages.success(request, 'Método de pago modificado correctamente.')
            return redirect('list_ventas')
    else:
        form = MetodoPagoForm(instance=detalle_venta)

    return render(request, 'modificar_metodo_pago.html', {
        'form': form,
        'venta': venta,
    })



@requerir_autenticacion
def detalle_venta(request, id_venta):
    venta = get_object_or_404(Venta, id_venta=id_venta)
    detalle_venta = DetalleVenta.objects.filter(id_venta=venta).first()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'detalle_venta.html', {'venta': venta, 'detalle_venta': detalle_venta, 'es_admin': empleado.es_admin})

@requerir_autenticacion
def list_reservas(request):
    reservas = Reservas.objects.all()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'list_reservas.html', {'reservas': reservas, 'es_admin': empleado.es_admin})

@requerir_autenticacion
def confirmar_turnos(request, accion):
    if request.method == 'POST':
        data = json.loads(request.body)  # Leer el cuerpo JSON de la solicitud
        turnos_ids = data.get('turnos')  # IDs de los turnos seleccionados
        action = data.get('action')  # Acción seleccionada: confirmar o cancelar

        if not turnos_ids:
            return JsonResponse({'success': False, 'message': 'No se seleccionaron turnos.'})

        # Verificar si la caja está abierta
        cajas_abiertas = Caja.objects.filter(estado=True)

        if not cajas_abiertas.exists():
            return JsonResponse({'success': False, 'message': 'Debe hacer abrir una caja para confirmar o cancelar este turno.'})

        caja_abierta = cajas_abiertas.first()  # Suponiendo que solo puede haber una caja abierta

        for turno_id in turnos_ids:
            turno = Turno.objects.get(id_turno=turno_id)

            if action == 'confirmar':
                # Crear reserva
                reserva = Reservas.objects.create(
                    id_cliente=turno.id_cliente,
                    id_turno=turno,
                    estado_reserva='confirmada'
                )

                # Crear venta (con monto_total vacío)
                venta = Venta.objects.create(
                    id_caja=caja_abierta,
                    id_cliente=turno.id_cliente,
                    monto_total=None  # No se define el monto total todavía
                )

                # Crear detalle de venta
                servicio = ServicioXTurno.objects.filter(id_turno=turno).first().id_servicio
                monto_subtotal = servicio.precio_del_servicio * (servicio.senia / 100)

                DetalleVenta.objects.create(
                    id_venta=venta,
                    id_reserva=reserva,
                    monto_subtotal=monto_subtotal,
                )

                # Eliminar el turno después de crear la reserva
                turno.delete()

                # Enviar correo de confirmación
                send_mail(
                    'Confirmación de Turno',
                    f'Hola {reserva.id_cliente.nombre}, tu turno ha sido confirmado para el día {reserva.id_turno.fecha} a las {reserva.id_turno.hora}.',
                    'anasolespacio@gmail.com',
                    [reserva.id_cliente.correo_electronico],
                    fail_silently=False,
                )

            elif action == 'cancelar':
                # Cambiar el estado del turno a cancelado
                turno.estado_turno = 'Cancelado'
                turno.save()

                # Crear venta con monto_total igual al monto_subtotal
                venta = Venta.objects.create(
                    id_caja=caja_abierta,
                    id_cliente=turno.id_cliente,
                    monto_total=None  # No se define el monto total todavía
                )

                # Crear detalle de venta
                servicio = ServicioXTurno.objects.filter(id_turno=turno).first().id_servicio
                monto_subtotal = servicio.precio_del_servicio * (servicio.senia / 100)

                DetalleVenta.objects.create(
                    id_venta=venta,
                    id_reserva=None,  # No se crea reserva en caso de cancelación
                    monto_subtotal=monto_subtotal,
                )

                # Enviar correo de cancelación
                send_mail(
                    'Cancelación de Turno',
                    f'Hola {turno.id_cliente.nombre}, lamentamos informarte que tu turno para el día {turno.fecha} a las {turno.hora} ha sido cancelado.',
                    'anasolespacio@gmail.com',
                    [turno.id_cliente.correo_electronico],
                    fail_silently=False,
                )

            return JsonResponse({'success': True, 'message': f'Turno {accion} correctamente.'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@requerir_autenticacion
def gestionar_turno(request, accion):
    if request.method == 'POST':
        data = json.loads(request.body)  # Leer el cuerpo JSON de la solicitud
        turnos_ids = data.get('turnos')  # IDs de los turnos seleccionados
        action = data.get('action')  # Acción seleccionada: confirmar o cancelar

        if not turnos_ids:
            return JsonResponse({'success': False, 'message': 'No se seleccionaron turnos.'})

        # Verificar si la caja está abierta
        cajas_abiertas = Caja.objects.filter(estado=True)

        if not cajas_abiertas.exists():
            return JsonResponse({'success': False, 'message': 'Debe hacer abrir una caja para confirmar o cancelar este turno.'})

        caja_abierta = cajas_abiertas.first()  # Suponiendo que solo puede haber una caja abierta

        for turno_id in turnos_ids:
            try:
                turno = Turno.objects.get(id_turno=turno_id)

                if action == 'confirmar':
                    # Obtener el servicio asociado al turno
                    servicio_x_turno = ServicioXTurno.objects.filter(id_turno=turno).first()
                    if not servicio_x_turno:
                        return JsonResponse({'success': False, 'message': f'No se encontró el servicio para el turno {turno_id}.'})
                    
                    servicio = servicio_x_turno.id_servicio

                    # Crear reserva
                    reserva = Reservas.objects.create(
                        id_cliente=turno.id_cliente,
                        id_turno=turno,
                        estado_reserva='Confirmada',
                        id_serv_x_tur=servicio_x_turno  # Asegúrate de asignar el servicio correctamente
                    )


                    # Crear venta sin el campo metodo_pago
                    venta = Venta.objects.create(
                        id_caja=caja_abierta,
                        id_cliente=turno.id_cliente,
                        monto_total=0,  # Ahora proporcionamos el monto total
                    )

                    # Calcular monto_subtotal (senia)
                    monto_subtotal = servicio.precio_del_servicio * (Decimal(servicio.senia) / 100)

                    # Crear detalle de venta con metodo_pago
                    DetalleVenta.objects.create(
                        id_venta=venta,
                        id_reserva=reserva,  # Se asocia la reserva al detalle de venta
                        monto_subtotal=monto_subtotal,
                        metodo_pago='Transferencia',  # Método de pago establecido como transferencia
                    )

                    # Actualizar estado del turno a 'confirmado'
                    turno.estado_turno = 'Confirmado'
                    turno.save()

                    # Enviar correo de confirmación
                    send_mail(
                        'Confirmación de Turno',
                        f'Hola {reserva.id_cliente.nombre}, tu turno ha sido confirmado para el día {reserva.id_turno.fecha} a las {reserva.id_turno.hora}.',
                        'anasolespacio@gmail.com',
                        [reserva.id_cliente.correo_electronico],
                        fail_silently=False,
                    )

                elif action == 'cancelar':
                    # Cambiar el estado del turno a 'cancelado'
                    turno.estado_turno = 'Cancelado'
                    turno.save()

                    # Obtener el servicio asociado al turno
                    servicio_x_turno = ServicioXTurno.objects.filter(id_turno=turno).first()
                    if not servicio_x_turno:
                        return JsonResponse({'success': False, 'message': f'No se encontró el servicio para el turno {turno_id}.'})
                    
                    reserva = Reservas.objects.create(
                        id_cliente=turno.id_cliente,
                        id_turno=turno,
                        estado_reserva='Cancelada',
                        id_serv_x_tur=servicio_x_turno  # Asegúrate de asignar el servicio correctamente
                    )

                    servicio = servicio_x_turno.id_servicio

                    # Calcular monto_subtotal (senia)
                    monto_subtotal = servicio.precio_del_servicio * (Decimal(servicio.senia) / 100)

                    # Crear venta con monto_subtotal
                    venta = Venta.objects.create(
                        id_caja=caja_abierta,
                        id_cliente=turno.id_cliente,
                        monto_total=monto_subtotal,  # Proporcionamos el monto subtotal para la cancelación
                    )

                    # Crear detalle de venta con metodo_pago
                    DetalleVenta.objects.create(
                        id_venta=venta,
                        id_reserva=reserva,  # No se crea reserva en caso de cancelación
                        monto_subtotal=monto_subtotal,
                        metodo_pago='Transferencia',  # Método de pago establecido como transferencia
                    )

                    # Enviar correo de cancelación
                    send_mail(
                        'Cancelación de Turno',
                        f'Hola {turno.id_cliente.nombre}, lamentamos informarte que tu turno para el día {turno.fecha} a las {turno.hora} ha sido cancelado.',
                        'anasolespacio@gmail.com',
                        [turno.id_cliente.correo_electronico],
                        fail_silently=False,
                    )

                return JsonResponse({'success': True, 'message': f'Turno {accion} correctamente.'})

            except Turno.DoesNotExist:
                return JsonResponse({'success': False, 'message': f'El turno con ID {turno_id} no existe.'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})

@requerir_autenticacion
def confirmar_o_cancelar_turno(request):
    if request.method == 'POST':
        action = request.POST.get('action')  # Confirmar o cancelar
        turnos = request.POST.getlist('turnos')  # Lista de turnos seleccionados

        # Verificar si la caja está abierta
        caja = Caja.objects.first()  # Suponiendo que hay solo una caja
        if not caja.abierta:
            return JsonResponse({'success': False, 'message': 'Realice la Apertura de Caja para confirmar o cancelar este turno.'})

        # Si la caja está abierta, realizar la acción
        for turno_id in turnos:
            turno = Turno.objects.get(id=turno_id)
            if action == 'confirmar':
                turno.estado_turno = 'confirmado'
            elif action == 'cancelar':
                turno.estado_turno = 'cancelado'
            turno.save()

        return JsonResponse({'success': True, 'message': 'Acción realizada exitosamente.'})
