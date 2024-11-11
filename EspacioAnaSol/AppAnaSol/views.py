from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from .models import Caja, Empleado, Servicios, ServicioXTurno, Turno, EmpleadoXTurno, Cliente, Cliente, Turno, Reservas, Servicios, Venta,DetalleVenta
from .forms import LoginForm, EmpleadoForm, ServiciosForm, TurnoForm,  MultipleTurnoForm, ClienteForm, VentaForm 
from django.http import HttpResponse
from django.core import management
from django.utils import timezone
from django.http import HttpResponseRedirect
from django.http import JsonResponse
import os
def obtener_empleado_autenticado(request):
    dni_empleado = request.session.get('empleado_dni')
    return get_object_or_404(Empleado, dni=dni_empleado)

def pagina_caja(request):
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'caja.html', {'cajas_abiertas': cajas_abiertas, 'es_admin': empleado.es_admin  })

def pagina_clientes(request):
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'clientes.html', {'cajas_abiertas': cajas_abiertas, 'es_admin': empleado.es_admin})

def pagina_empleados(request):
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'empleados.html', {'cajas_abiertas': cajas_abiertas, 'es_admin': empleado.es_admin})

def pagina_servicios(request):
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'servicios.html', {'cajas_abiertas': cajas_abiertas, 'es_admin': empleado.es_admin})

def pagina_turnos(request):
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'turnos.html', {'cajas_abiertas': cajas_abiertas, 'es_admin': empleado.es_admin})

def pagina_ventas(request):
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'ventas.html', {'cajas_abiertas': cajas_abiertas, 'es_admin': empleado.es_admin})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            dni = form.cleaned_data['dni']
            contraseña = form.cleaned_data['contraseña']
            print(f'DNI: {dni}, Contraseña: {contraseña}')
            ...
            try:
                empleado = Empleado.objects.get(dni=dni)
                if empleado.verificar_contraseña(contraseña):
                    request.session['empleado_dni'] = empleado.dni
                    return redirect('pagina_principal') 
                else:
                    messages.error(request, 'DNI o contraseña incorrectos.')
            except Empleado.DoesNotExist:
                messages.error(request, 'DNI o contraseña no existen.')
    else:
        form = LoginForm()

    return render(request, 'login.html', {'form': form})

def logout_view(request):
    if 'empleado_dni' in request.session:
        del request.session['empleado_dni']
        messages.success(request, 'Has cerrado sesión correctamente.')
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
    if 'empleado_dni' not in request.session:
        return redirect('login')  
    empleado = obtener_empleado_autenticado(request)

    return render(request, 'pagina_principal.html', {
        'cajas_abiertas': cajas_abiertas,
        'es_admin': empleado.es_admin
    })


@admin_required
def list_empleados(request):
    empleados = Empleado.objects.all()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'list_empleados.html', {'empleados': empleados, 'es_admin': empleado.es_admin})

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

    return render(request, 'abrir_caja.html')



from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render

@requerir_autenticacion
def list_cajas(request):
    # Obtener el valor de filtro seleccionado o establecer "hoy" por defecto
    date_filter = request.GET.get('date_filter', 'today')

    # Obtener todas las cajas y filtrar por el rango de fechas
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()
    empleado = obtener_empleado_autenticado(request) 

    # Filtrar por el rango de fechas seleccionado
    if date_filter == 'today':
        start_date = timezone.now().date()
        cajas = cajas.filter(fecha_apertura__date=start_date)
    elif date_filter == 'week':
        start_date = timezone.now().date() - timedelta(days=timezone.now().weekday())
        end_date = start_date + timedelta(days=6)
        cajas = cajas.filter(fecha_apertura__date__range=(start_date, end_date))
    elif date_filter == 'month':
        start_date = timezone.now().replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        cajas = cajas.filter(fecha_apertura__date__range=(start_date, end_date))
    # "all" se usa para mostrar todos los registros (sin filtro adicional)

    # Calcula el monto total para cada caja
    for caja in cajas:
        monto_recaudado = caja.monto_recaudado if caja.monto_recaudado else 0
        caja.monto_total = caja.monto_inicial + monto_recaudado

    return render(request, 'list_cajas.html', {
        'cajas': cajas,
        'cajas_abiertas': cajas_abiertas,
        'es_admin': empleado.es_admin,
        'date_filter': date_filter  # Pasamos el valor de filtro al template
    })



@requerir_autenticacion
def cerrar_caja(request, id_caja):
    caja = Caja.objects.get(id_caja=id_caja)
    if request.method == 'POST':
        caja.cerrar_caja(obtener_empleado_autenticado(request)) 
        return redirect('list_cajas')

    return render(request, 'cerrar_caja.html', {'caja': caja})

@requerir_autenticacion
def update_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)

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
    return render(request, 'list_servicios.html', {'servicios': servicios, 'es_admin': empleado.es_admin})


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
        # Verifica los datos que están llegando
        nombre_del_servicio = request.POST.get('nombre_del_servicio')
        descripcion_del_servicio = request.POST.get('descripcion_del_servicio')
        duracion = request.POST.get('duracion')
        precio_del_servicio = request.POST.get('precio_del_servicio')
        valor_sello = request.POST.get('valor_sello')

        print("Datos recibidos:", nombre_del_servicio, descripcion_del_servicio, duracion, precio_del_servicio, valor_sello)

        if not nombre_del_servicio or not precio_del_servicio or not valor_sello:
            messages.error(request, "El nombre, el precio y el valor sello son obligatorios.")
            return render(request, 'update_servicio.html', {'servicio': servicio})

        servicio.nombre_del_servicio = nombre_del_servicio
        servicio.descripcion_del_servicio = descripcion_del_servicio
        servicio.duracion = duracion
        servicio.precio_del_servicio = precio_del_servicio
        servicio.valor_sello = valor_sello

        if 'imagen' in request.FILES:
            servicio.imagen = request.FILES['imagen']

        servicio.save()
        messages.success(request, 'Servicio actualizado con éxito.')
        return redirect('list_servicios')

    return render(request, 'update_servicio.html', {'servicio': servicio})



@requerir_autenticacion
def delete_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado con éxito.')
        return redirect('list_servicios')
    return render(request, 'delete_servicio.html', {'servicio': servicio})


@requerir_autenticacion
def add_turno(request):
    if request.method == 'POST':
        form = MultipleTurnoForm(request.POST)
        if form.is_valid():
            fecha = form.cleaned_data['fecha']
            servicio = form.cleaned_data['servicio']

            horas = [
                form.cleaned_data['hora1'],
                form.cleaned_data['hora2'],
                form.cleaned_data['hora3'],
                form.cleaned_data['hora4'],
            ]

            empleados = [
                form.cleaned_data['empleado1'],
                form.cleaned_data['empleado2'],
                form.cleaned_data['empleado3'],
                form.cleaned_data['empleado4'],
            ]

            for i in range(4):
                turno = Turno.objects.create(
                    fecha=fecha,
                    hora=horas[i],
                    estado_turno='Disponible',
                    # No pasamos id_cliente, dejará que sea NULL
                )
                EmpleadoXTurno.objects.create(dni_emp=empleados[i], id_turno=turno)
                ServicioXTurno.objects.create(id_servicio=servicio, id_turno=turno)

            messages.success(request, 'Cuatro turnos creados correctamente.')
            return redirect('list_turnos')
        else:
            messages.error(request, 'Por favor, completa el formulario correctamente.')
    else:
        form = MultipleTurnoForm()

    return render(request, 'add_turno.html', {'form': form})

# Listar turnos
@requerir_autenticacion
def list_turnos(request):
    # Obtener todos los turnos junto con el cliente asociado
    turnos = Turno.objects.select_related('id_cliente').prefetch_related('empleadoxturno_set', 'servicioxturno_set')
    empleado = obtener_empleado_autenticado(request)

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
            'es_admin': empleado.es_admin
        })
    
    # Pasar los datos a la plantilla
    return render(request, 'list_turnos.html', {
        'turnos_data': turnos_data
    })
    

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

# Eliminar un turno
@requerir_autenticacion
def delete_turno(request, turno_id):
    turno = get_object_or_404(Turno, id_turno=turno_id)  
    if request.method == 'POST':
        turno.delete()  
        messages.success(request, 'Turno eliminado correctamente.')
        return redirect('list_turnos') 

    return render(request, 'delete_turno_confirm.html', {'turno': turno}) 

def list_clientes(request):
    clientes = Cliente.objects.all() 
    return render(request, 'list_clientes.html', {'clientes': clientes})

@login_required
@admin_required
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
    
@login_required
@admin_required
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
def registrar_cliente(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST)
        if cliente_form.is_valid():
            cliente = cliente_form.save()
            request.session['id_cliente'] = cliente.id_cliente  # Guardamos el id del cliente en la sesión
            return redirect('registrar_reserva')
    else:
        cliente_form = ClienteForm()
    return render(request, 'registrar_cliente.html', {'form': cliente_form})

@requerir_autenticacion
def registrar_reserva(request):
    id_cliente = request.session.get('id_cliente')
    cliente = Cliente.objects.get(id_cliente=id_cliente)

    if request.method == 'POST':
        servicio_id = request.POST.get('servicio')
        fecha = request.POST.get('fecha')
        hora = request.POST.get('hora')
        metodo_pago = request.POST.get('metodo_pago')
        diseño_uñas = request.FILES.get('diseño_uñas')  # Imagen opcional
        comprobante = request.FILES.get('comprobante')  # Archivo opcional

        if servicio_id and fecha and hora and metodo_pago:
            servicio = Servicios.objects.get(id_servicio=servicio_id)
            turno = Turno.objects.filter(fecha=fecha, hora=hora, estado_turno='Disponible').first()

            if turno:
                # Asignar imagen de diseño de uñas al turno si existe
                if diseño_uñas:
                    turno.diseño_uñas = diseño_uñas
                    turno.save()

                # Crear la reserva
                reserva = Reservas.objects.create(
                    id_cliente=cliente,
                    id_turno=turno,
                    id_serv_x_tur=ServicioXTurno.objects.get(id_servicio=servicio, id_turno=turno),
                    estado_reserva='pendiente'
                )

                # Cambiar el estado del turno a 'Pendiente'
                turno.estado_turno = 'Pendiente'
                turno.save()

                # Crear la venta solo aquí
                caja_abierta = Caja.objects.filter(estado=True).first()
                if not caja_abierta:
                    return render(request, 'error.html', {'error': 'No hay ninguna caja abierta. No se puede registrar la venta.'})

                venta = Venta.objects.create(
                    id_cliente=cliente,
                    id_caja=caja_abierta,
                    fecha_venta=timezone.now().date(),
                    hs_venta=timezone.now().time(),
                    monto_total=servicio.valor_sello,
                    estado_venta=1
                )

                # Crear el detalle de la venta
                DetalleVenta.objects.create(
                    id_venta=venta,
                    id_reserva=reserva,
                    metodo_pago=metodo_pago,
                    monto_subtotal=servicio.valor_sello,
                    comprobante=comprobante if metodo_pago == 'Transferencia' and comprobante else None,
                    estado_reserva=reserva.estado_reserva
                )

                # Redirigir a la confirmación de la reserva
                return redirect('confirmar_reserva', reserva_id=reserva.id_reserva)

    if 'fecha' in request.GET:
        fecha = request.GET['fecha']
        turnos = Turno.objects.filter(fecha=fecha, estado_turno__in=['Disponible', 'Cancelado'])
        horas_disponibles = [turno.hora for turno in turnos]
        return JsonResponse({'horas': horas_disponibles})

    servicios = Servicios.objects.all()
    return render(request, 'registrar_reserva.html', {
        'servicios': servicios
    })

@requerir_autenticacion
def confirmar_reserva(request, reserva_id):
    reserva = Reservas.objects.get(id_reserva=reserva_id)
    
    # Verificar si hay una caja abierta
    caja_abierta = Caja.objects.filter(estado=True).first()
    
    if not caja_abierta:
        return render(request, 'error.html', {'error': 'No hay ninguna caja abierta. No se puede registrar la venta.'})
    
    # Obtener el servicio, turno y cliente
    servicio = reserva.id_serv_x_tur.id_servicio
    turno = reserva.id_turno
    cliente = reserva.id_cliente

    # Obtener el detalle de la venta para mostrar el método de pago y comprobante
    detalle_venta = DetalleVenta.objects.filter(id_reserva=reserva).first()
    metodo_pago = detalle_venta.metodo_pago if detalle_venta else "No especificado"
    diseño_uñas = turno.diseño_uñas
    comprobante = detalle_venta.comprobante if detalle_venta and detalle_venta.comprobante else None

    # Si es una solicitud POST, redirigir a la página de venta exitosa
    if request.method == 'POST':
        return redirect('venta_exitosa')  # Asegúrate de que la vista y URL de venta_exitosa estén configuradas
    
    # Renderizar el formulario de confirmación
    return render(request, 'confirmar_reserva.html', {
        'reserva': reserva,
        'servicio': servicio,
        'turno': turno,
        'cliente': cliente,
        'monto_subtotal': servicio.valor_sello,
        'metodo_pago': metodo_pago,
        'diseño_uñas': diseño_uñas,
        'comprobante': comprobante
    })

@requerir_autenticacion
def venta_exitosa(request):
    return render(request, 'venta_exitosa.html')

from django.utils import timezone
from datetime import timedelta
from django.shortcuts import render

@requerir_autenticacion
def list_ventas(request):
    # Obtiene el valor del filtro de fechas o establece "hoy" por defecto
    date_filter = request.GET.get('date_filter', 'today')

    # Filtrar ventas según el rango de fechas seleccionado
    if date_filter == 'today':
        start_date = timezone.now().date()
        ventas = Venta.objects.filter(fecha_venta=start_date)
    elif date_filter == 'week':
        start_date = timezone.now().date() - timedelta(days=timezone.now().weekday())
        end_date = start_date + timedelta(days=6)
        ventas = Venta.objects.filter(fecha_venta__range=(start_date, end_date))
    elif date_filter == 'month':
        start_date = timezone.now().replace(day=1)
        end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(days=1)
        ventas = Venta.objects.filter(fecha_venta__range=(start_date, end_date))
    else:
        ventas = Venta.objects.all()  # Muestra todas las ventas si el filtro es "all"

    # Comprobar si hay cajas abiertas
    cajas = Caja.objects.all()
    cajas_abiertas = cajas.filter(estado=True).exists()
    empleado = obtener_empleado_autenticado(request)

    # Renderizar la plantilla con el filtro aplicado
    return render(request, 'list_ventas.html', {
        'ventas': ventas,
        'cajas_abiertas': cajas_abiertas,
        'es_admin': empleado.es_admin,
        'date_filter': date_filter  # Pasamos el valor de filtro al template
    })


@requerir_autenticacion
def list_detalleventa(request, id_venta):
    # Obtener la venta específica
    venta = get_object_or_404(Venta, id_venta=id_venta)
    
    # Obtener los detalles de venta asociados a la venta
    detalles_venta = DetalleVenta.objects.filter(id_venta=venta)

    empleado = obtener_empleado_autenticado(request)
    
    return render(request, 'list_detalleventa.html', {'venta': venta, 'detalles_venta': detalles_venta, 'es_admin': empleado.es_admin})

@requerir_autenticacion
def detalle_reserva(request, id_reserva):
    reserva = get_object_or_404(Reservas, id_reserva=id_reserva)
    return render(request, 'detalle_reserva.html', {'reserva': reserva})

@requerir_autenticacion
def update_venta(request, id_venta):
    venta = get_object_or_404(Venta, id_venta=id_venta)
    
    if request.method == 'POST':
        form = VentaForm(request.POST, instance=venta)
        if form.is_valid():
            form.save()
            return redirect('list_ventas')  # Redirigir de vuelta a la lista de ventas
    else:
        form = VentaForm(instance=venta)
    
    return render(request, 'update_venta.html', {'form': form, 'venta': venta})