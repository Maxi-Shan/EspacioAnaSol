from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from django.utils.timezone import now
from datetime import timedelta, datetime
from .models import Caja, Empleado, ServicioXTurno, EmpleadoXTurno, Cliente, Turno, Reservas, Servicios, Venta, Reservas, DetalleVenta
from .forms import ServiciosForm, ClienteForm, TurnoForm, MetodoPagoForm, EmpleadoForm
from django.core import management
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.db.models import Count, Sum
import os
import json

def login(request):
    dni_error = ''
    contraseña_error = ''

    if request.method == 'POST':
        dni = request.POST.get('dni')
        contraseña = request.POST.get('contraseña')

        if not dni or not contraseña:
            if not dni:
                dni_error = 'Por favor, ingrese su DNI.'
            if not contraseña:
                contraseña_error = 'La contraseña no puede estar vacía.'
        else:
            try:

                empleado = Empleado.objects.get(dni=dni)


                if empleado.estado_empleado in ['suspendido', 'despedido']:
                    dni_error = 'Estás suspendido.'
                    return redirect('login')

                if empleado.contraseña == contraseña: 

                    request.session['empleado_dni'] = empleado.dni
                    messages.success(request, '¡Entraste a la Interfaz para Empleados! ¡Bienvenido a Espacio Ana Sol!')
                    return redirect('pagina_principal')
                else:
                    contraseña_error = 'Contraseña incorrecta.'
            except Empleado.DoesNotExist:
                dni_error = 'Empleado inexistente.'

    return render(request, 'login.html', {'dni_error': dni_error, 'contraseña_error': contraseña_error})


def logout(request):
    if 'empleado_dni' in request.session:
        del request.session['empleado_dni']
        messages.success(request, '¡Sesión cerrada correctamente!')
    else:
        messages.warning(request, 'No estabas autenticado.')
    return redirect('login')


def obtener_empleado_autenticado(request):
    dni_cifrado = request.session.get('empleado_dni')
    if not dni_cifrado:
        return None
    try:
        empleado = Empleado.objects.get(dni=dni_cifrado)


        if empleado.estado_empleado in ['suspendido', 'despedido']:
            return None  
        return empleado
    except Empleado.DoesNotExist:
        return None

def requerir_autenticacion(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'empleado_dni' not in request.session:
            return redirect('login')
        
        empleado = obtener_empleado_autenticado(request)
        if not empleado:
            return redirect('login')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def admin_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        empleado = obtener_empleado_autenticado(request)
        if not empleado or not empleado.es_admin:
            return redirect('pagina_principal')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


@login_required
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
@requerir_autenticacion
def list_empleados(request):
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    empleados = Empleado.objects.all()

    # Pasar las contraseñas en texto plano a la plantilla
    for empleado in empleados:
        empleado.contraseña_original = empleado.contraseña_original or "No establecida"

    empleado_autenticado = obtener_empleado_autenticado(request)
    return render(request, 'list_empleados.html', {
        'empleados': empleados,
        'es_admin': empleado.es_admin, 
        'cajas_abiertas': cajas_abiertas
    })

@login_required
@requerir_autenticacion
def list_cajas(request):
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()

    today = timezone.now().date()


    filtro = request.GET.get('rango_fecha', 'hoy') 

    if filtro == 'hoy':
        cajas = Caja.objects.filter(fecha_apertura__date=today).order_by('-fecha_apertura')
    elif filtro == 'semana':
        start_of_week = today - timedelta(days=today.weekday()) 
        end_of_week = start_of_week + timedelta(days=6) 
        cajas = Caja.objects.filter(fecha_apertura__date__range=[start_of_week, end_of_week]).order_by('-fecha_apertura')
    elif filtro == 'mes':
        start_of_month = today.replace(day=1)
        end_of_month = today.replace(day=28) + timedelta(days=4)  
        cajas = Caja.objects.filter(fecha_apertura__date__range=[start_of_month, end_of_month]).order_by('-fecha_apertura')
    else:
        cajas = Caja.objects.all().order_by('-fecha_apertura')

    cajas_abiertas = cajas.filter(estado=True).exists() 
    empleado = obtener_empleado_autenticado(request)

    for caja in cajas:
        monto_recaudado = caja.monto_recaudado if caja.monto_recaudado else 0
        caja.monto_total = caja.monto_inicial + monto_recaudado  

    return render(request, 'list_cajas.html', {
        'cajas': cajas,
        'cajas_abiertas': cajas_abiertas,
        'es_admin': empleado.es_admin,
        'filtro': filtro 
    })

def ventas_por_caja(request, id_caja):
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    caja = get_object_or_404(Caja, id_caja=id_caja)
    ventas = Venta.objects.filter(id_caja=caja).order_by('-fecha_venta')

    context = {
        'caja': caja,
        'ventas': ventas,
        'es_admin': empleado.es_admin, 
        'cajas_abiertas': cajas_abiertas
    }
    return render(request, 'ventas_por_caja.html', context)


@login_required
@requerir_autenticacion
def list_turnos(request):
    empleado = obtener_empleado_autenticado(request)

    estado = request.GET.get('estado', 'Pendiente')  
    rango_fecha = request.GET.get('rango_fecha', 'hoy') 

    # Filtrar turnos por fecha
    hoy = now().date()
    if rango_fecha == 'hoy':
        turnos = Turno.objects.filter(fecha=hoy).order_by('-fecha', '-hora')
    elif rango_fecha == 'semana':
        inicio_semana = hoy - timedelta(days=hoy.weekday())  
        fin_semana = inicio_semana + timedelta(days=6) 
        turnos = Turno.objects.filter(fecha__range=[inicio_semana, fin_semana]).order_by('-fecha', '-hora')
    elif rango_fecha == 'mes':
        turnos = Turno.objects.filter(fecha__month=hoy.month, fecha__year=hoy.year).order_by('-fecha', '-hora')
    elif rango_fecha == 'todo':
        turnos = Turno.objects.all().order_by('-fecha', '-hora')  # No filtrar por fecha
    else:
        turnos = Turno.objects.all().order_by('-fecha', '-hora')

    # Filtrar por estado de turno
    if estado != 'todos':
        turnos = turnos.filter(estado_turno=estado)

    # Obtener datos adicionales para cada turno
    turnos_data = []
    for turno in turnos:
        empleados = EmpleadoXTurno.objects.filter(id_turno=turno).select_related('dni_emp')
        servicios = ServicioXTurno.objects.filter(id_turno=turno).select_related('id_servicio')

        empleado_nombres = ', '.join([f"{emp.dni_emp.nombre} {emp.dni_emp.apellido}" for emp in empleados])
        servicio_nombres = ', '.join([servicio.id_servicio.nombre_del_servicio for servicio in servicios])

        turnos_data.append({
            'turno': turno,
            'empleados': empleado_nombres,
            'servicios': servicio_nombres,
            'id_cliente': turno.id_cliente if turno.id_cliente else None,
            'diseño_uñas': turno.diseño_uñas,
            'senia_comprobante': turno.senia_comprobante,
        })

    context = {
        'turnos_data': turnos_data,
        'cajas_abiertas': Caja.objects.filter(estado=True).exists(),
        'es_admin': empleado.es_admin,
        'estado_actual': estado,
        'rango_fecha_actual': rango_fecha, 
    }

    return render(request, 'list_turnos.html', context)

@login_required
@requerir_autenticacion
def list_ventas(request):
    today = timezone.now().date()
    start_of_day = timezone.make_aware(datetime.combine(today, datetime.min.time()))
    end_of_day = start_of_day + timedelta(days=1)

    ventas = Venta.objects.filter(fecha_venta__gte=start_of_day, fecha_venta__lt=end_of_day).order_by('-hs_venta')

    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    
    return render(request, 'list_ventas.html', {
        'ventas': ventas,
        'es_admin': empleado.es_admin,
        'cajas_abiertas': cajas_abiertas,
    })



@login_required
@requerir_autenticacion
def list_clientes(request):
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()

    # Obtener filtros de la solicitud GET
    rango_fecha = request.GET.get('rango_fecha', 'hoy')  # Por defecto 'hoy'

    # Filtrar clientes por fecha
    hoy = now().date()
    if rango_fecha == 'hoy':
        clientes = Cliente.objects.filter(fecha_registro__date=hoy).order_by('-fecha_registro')
    elif rango_fecha == 'semana':
        inicio_semana = hoy - timedelta(days=hoy.weekday())  # Lunes de esta semana
        fin_semana = inicio_semana + timedelta(days=7)  # Domingo de esta semana
        clientes = Cliente.objects.filter(fecha_registro__date__range=[inicio_semana, fin_semana]).order_by('-fecha_registro')
    elif rango_fecha == 'mes':
        clientes = Cliente.objects.filter(fecha_registro__month=hoy.month, fecha_registro__year=hoy.year).order_by('-fecha_registro')
    elif rango_fecha == 'todo':
        clientes = Cliente.objects.all().order_by('-fecha_registro')  # No filtrar por fecha
    else:
        clientes = Cliente.objects.all().order_by('-fecha_registro')

    cajas_abiertas = Caja.objects.filter(estado=True).exists()

    return render(request, 'list_clientes.html', {
        'clientes': clientes,
        'es_admin': empleado.es_admin,
        'cajas_abiertas': cajas_abiertas,
        'rango_fecha_actual': rango_fecha,  
    })

@login_required
@requerir_autenticacion
def ventas_por_caja(request, id_caja):
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    caja = get_object_or_404(Caja, id_caja=id_caja)


    ventas = Venta.objects.filter(id_caja=caja).order_by('-hs_venta')

    return render(request, 'ventas_por_caja.html', {
        'caja': caja,
        'ventas': ventas,
        'es_admin': empleado.es_admin,
        'cajas_abiertas': cajas_abiertas,
    })


@admin_required
@requerir_autenticacion
def delete_empleado(request, dni):
    empleado = get_object_or_404(Empleado, dni=dni)
    if request.method == "POST":
        empleado.delete()
        return redirect('list_empleados')
    return render(request, 'delete_confirm.html', {'empleado': empleado})

@admin_required
@requerir_autenticacion
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
@requerir_autenticacion
def add_empleado(request):
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    if request.method == "POST":
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_empleados')
    else:
        form = EmpleadoForm()
    return render(request, 'add_empleado.html', {'form': form, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas})

@admin_required
@requerir_autenticacion
def update_empleado(request, dni):
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
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

    return render(request, 'update_empleado.html', {'empleado': empleado, 'cajas_abiertas': cajas_abiertas,})



@login_required
@requerir_autenticacion
def abrir_caja(request):
    empleado = obtener_empleado_autenticado(request)
    if request.method == 'POST':
        monto_inicial = request.POST.get('monto_inicial')

        errores = {} 

        if not monto_inicial:
            errores['monto_inicial'] = 'El monto inicial es obligatorio.'
        else:
            try:
                monto_inicial = float(monto_inicial)  
            except ValueError:
                errores['monto_inicial'] = 'El monto inicial debe ser un número válido.'

        if errores:
            return render(request, 'abrir_caja.html', {
                'errores': errores,
                'monto_inicial': monto_inicial if not 'monto_inicial' in errores else None,
                'es_admin': empleado.es_admin
            })

        dni_empleado = request.session.get('empleado_dni')  
        try:
            empleado = Empleado.objects.get(dni=dni_empleado)
        except Empleado.DoesNotExist:
            return render(request, 'abrir_caja.html', {'error': 'Empleado no encontrado.'})

        hora_actual = timezone.localtime(timezone.now())  

        # Crea la nueva caja
        nueva_caja = Caja(
            empleado=empleado,
            monto_inicial=monto_inicial,
            estado=True, 
            fecha_apertura=hora_actual  
        )
        nueva_caja.save()

        return redirect('list_cajas')

    return render(request, 'abrir_caja.html', {
        'es_admin': empleado.es_admin
    })




@login_required
@requerir_autenticacion
def cerrar_caja(request, id_caja):
    caja = Caja.objects.get(id_caja=id_caja)
    empleado = obtener_empleado_autenticado(request)
    if request.method == 'POST':
        caja.cerrar_caja(obtener_empleado_autenticado(request)) 
        return redirect('list_cajas')

    return render(request, 'cerrar_caja.html', {'caja': caja, 'es_admin': empleado.es_admin})

@admin_required
@requerir_autenticacion
def update_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
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
    
    return render(request, 'update_caja.html', {'caja': caja, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})

@login_required
@requerir_autenticacion
def list_reservas(request):
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    

    estado_reserva = request.GET.get('estado_reserva', '')  
    rango_fecha = request.GET.get('rango_fecha', 'hoy') 
    

    reservas = Reservas.objects.all()
    if estado_reserva:
        reservas = reservas.filter(estado_reserva=estado_reserva)
    

    hoy = now().date()
    if rango_fecha == 'hoy':
        reservas = reservas.filter(fecha_registro__date=hoy).order_by('-fecha_registro')
    elif rango_fecha == 'semana':
        inicio_semana = hoy - timedelta(days=hoy.weekday())  
        fin_semana = inicio_semana + timedelta(days=6)  
        reservas = reservas.filter(fecha_registro__range=[inicio_semana, fin_semana]).order_by('-fecha_registro')
    elif rango_fecha == 'mes':
        reservas = reservas.filter(fecha_registro__month=hoy.month, fecha_registro__year=hoy.year).order_by('-fecha_registro')
    else:
        reservas = reservas.order_by('-fecha_registro')  
    
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    return render(request, 'list_reservas.html', {
        'reservas': reservas,
        'es_admin': empleado.es_admin,
        'cajas_abiertas': cajas_abiertas,
        'estado_reserva_actual': estado_reserva,
        'rango_fecha_actual': rango_fecha
    })


@login_required
@requerir_autenticacion
def list_servicios(request):
    servicios = Servicios.objects.all()
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    return render(request, 'list_servicios.html', {'servicios': servicios, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})

@login_required
@requerir_autenticacion
def add_servicio(request):
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    if request.method == 'POST':
        nombre_del_servicio = request.POST.get('nombre_del_servicio')
        descripcion_del_servicio = request.POST.get('descripcion_del_servicio')
        duracion = request.POST.get('duracion')
        precio_del_servicio = request.POST.get('precio_del_servicio')
        senia = request.POST.get('senia')
        imagen = request.FILES.get('imagen')

        errores = {}


        if not nombre_del_servicio:
            errores['nombre_del_servicio'] = 'El nombre del servicio es obligatorio.'
        if not precio_del_servicio:
            errores['precio_del_servicio'] = 'El precio del servicio es obligatorio.'
        if not senia:
            errores['senia'] = 'El valor de la seña es obligatorio.'
        if not duracion:
            errores['duracion'] = 'La duración es obligatoria.'


        try:
            if float(precio_del_servicio) <= 0:
                errores['precio_del_servicio'] = 'El precio debe ser un valor positivo.'
        except ValueError:
            errores['precio_del_servicio'] = 'El precio debe ser un número válido.'
        
        try:
            if float(senia) <= 0:
                errores['senia'] = 'El valor de la seña debe ser un valor positivo.'
        except ValueError:
            errores['senia'] = 'El valor de la seña debe ser un número válido.'

        if errores:
            return render(request, 'add_servicio.html', {
                'errores': errores,
                'form': request.POST,
                'es_admin': empleado.es_admin,
                'cajas_abiertas': cajas_abiertas,
            })


        servicio = Servicios(
            nombre_del_servicio=nombre_del_servicio,
            descripcion_del_servicio=descripcion_del_servicio,
            duracion=duracion,
            precio_del_servicio=precio_del_servicio,
            senia=senia,
            imagen=imagen,
        )
        servicio.save()
        messages.success(request, 'Servicio agregado con éxito.')
        return redirect('list_servicios')
    
    return render(request, 'add_servicio.html', {'form': None, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas})


@login_required
@requerir_autenticacion
def modificar_servicio(request, id_servicio):
    empleado = obtener_empleado_autenticado(request)
    if not empleado:
        messages.error(request, "No se pudo obtener el empleado.")
        return redirect('login')  # O donde desees redirigir en caso de que no se pueda obtener el empleado
    
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)

    # Verificar si el empleado es admin
    print("Empleado es admin:", empleado.es_admin)
    print("Caja abierta:", cajas_abiertas)

    if request.method == 'POST':

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

    return render(request, 'update_servicio.html', {
        'servicio': servicio,
        'es_admin': empleado.es_admin,
        'cajas_abiertas': cajas_abiertas
    })



@requerir_autenticacion
def delete_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    if request.method == 'POST':
        servicio.delete()
        messages.success(request, 'Servicio eliminado con éxito.')
        return redirect('list_servicios')
    return render(request, 'delete_servicio.html', {'servicio': servicio})

@login_required
@requerir_autenticacion
def registrar_cliente(request):
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():
            cliente = form.save()

            request.session['cliente_id'] = cliente.id_cliente
            return redirect('registrar_turno')
    else:
        form = ClienteForm()
    return render(request, 'registrar_cliente.html', {'form': form, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})

@login_required
@requerir_autenticacion
def registrar_turno(request):
    cliente_id = request.session.get('cliente_id')
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    if not cliente_id:
        return redirect('registrar_cliente')

    if request.method == "POST":
        form = TurnoForm(request.POST, request.FILES)
        if form.is_valid():

            turno = form.save(commit=False)
            turno.id_cliente_id = cliente_id 
            turno.estado_turno = "Pendiente" 
            turno.save()

            empleado = form.cleaned_data['id_empleado']
            servicio = form.cleaned_data['id_servicio']

            EmpleadoXTurno.objects.create(dni_emp=empleado, id_turno=turno)
            ServicioXTurno.objects.create(id_servicio=servicio, id_turno=turno)

            # Limpiar datos de sesión
            del request.session['cliente_id']
            return redirect('list_turnos')
    else:
        form = TurnoForm()

    return render(request, 'registrar_turno.html', {'form': form, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})

@admin_required
@requerir_autenticacion
def cancelar_registro(request):
    request.session.pop('cliente_id', None)  
    return redirect('list_turnos')


@requerir_autenticacion
def modificar_turno(request, turno_id):
    empleado = obtener_empleado_autenticado(request)
    turno = get_object_or_404(Turno, id_turno=turno_id)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    if request.method == "POST":
        empleado_id = request.POST.get('empleado')


        turno.id_empleado_id = empleado_id  
        turno.save()

        return redirect('list_turnos')

    empleados = Empleado.objects.all()

    return render(request, 'modificar_turno.html', {
        'turno': turno,
        'empleados': empleados,
        'es_admin': empleado.es_admin,  
        'cajas_abiertas': cajas_abiertas,
    })



@login_required
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
    
@login_required
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




@login_required
@requerir_autenticacion
def modificar_metodo_pago(request, venta_id):
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    venta = get_object_or_404(Venta, id_venta=venta_id)
    detalle_venta_list = DetalleVenta.objects.filter(id_venta=venta)
    
    if detalle_venta_list.count() == 1:

        detalle_venta = detalle_venta_list.first()
    elif detalle_venta_list.count() > 1:

        detalle_venta = detalle_venta_list.first()  
    else:

        messages.error(request, "No se encontraron detalles de venta para esta venta.")
        return redirect('list_ventas')

    if request.method == 'POST':
        form = MetodoPagoForm(request.POST, instance=detalle_venta)
        if form.is_valid():

            detalle_venta.id_venta = venta
            form.save()
            messages.success(request, 'Método de pago modificado correctamente.')
            return redirect('list_ventas')
    else:
        form = MetodoPagoForm(instance=detalle_venta)

    return render(request, 'modificar_metodo_pago.html', {
        'form': form,
        'venta': venta,
        'cajas_abiertas': cajas_abiertas,
    })


@login_required
@requerir_autenticacion
def detalle_venta(request, id_venta):
    venta = get_object_or_404(Venta, id_venta=id_venta)
    detalle_venta = DetalleVenta.objects.filter(id_venta=venta).first()
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    empleado = obtener_empleado_autenticado(request)
    return render(request, 'detalle_venta.html', {'venta': venta, 'detalle_venta': detalle_venta, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})


def confirmar_turno(request):
    return gestionar_turno(request, accion='confirmar')

def gestionar_turno(request, accion):
    if request.method == 'POST':
        data = json.loads(request.body)  
        turnos_ids = data.get('turnos') 
        action = data.get('action')  

        if not turnos_ids:
            return JsonResponse({'success': False, 'message': 'No se seleccionaron turnos.'})

        caja_activa = Caja.objects.filter(estado=True).first()

        if not caja_activa:
            return JsonResponse({'success': False, 'message': 'No hay una caja abierta para realizar la acción.'})

        for turno_id in turnos_ids:
            try:
                turno = Turno.objects.get(id_turno=turno_id)

                if action == 'confirmar':

                    turno.estado_turno = 'Confirmado'
                    turno.save()


                    servicio_x_turno = ServicioXTurno.objects.filter(id_turno=turno).first()
                    if not servicio_x_turno:
                        return JsonResponse({'success': False, 'message': f'No se encontró un servicio asociado al turno {turno_id}.'})

                    reserva = Reservas.objects.create(
                        id_cliente=turno.id_cliente,
                        id_turno=turno,
                        id_serv_x_tur=servicio_x_turno,
                        estado_reserva='Confirmada'
                    )

                    precio_servicio = servicio_x_turno.id_servicio.precio_del_servicio
                    senia = servicio_x_turno.id_servicio.senia
                    monto_subtotal = (precio_servicio * senia) / 100


                    venta = Venta.objects.create(
                        id_caja=caja_activa,
                        id_cliente=turno.id_cliente,
                        monto_total=monto_subtotal
                    )

                    DetalleVenta.objects.create(
                        id_venta=venta,
                        id_reserva=reserva,
                        metodo_pago='Tranferencia',
                        monto_subtotal=monto_subtotal
                    )


                    send_mail(
                        'Confirmación de Turno',
                        f'Hola {turno.id_cliente.nombre}, tu turno ha sido confirmado para el día {turno.fecha} a las {turno.hora}.',
                        'anasolespacio@gmail.com',
                        [turno.id_cliente.correo_electronico],
                        fail_silently=False,
                    )

                elif action == 'cancelar':

                    turno.estado_turno = 'Cancelado'
                    turno.save()

                    send_mail(
                        'Cancelación de Turno',
                        f'Hola {turno.id_cliente.nombre}, lamentamos informarte que tu turno para el día {turno.fecha} a las {turno.hora} ha sido cancelado.',
                        'anasolespacio@gmail.com',
                        [turno.id_cliente.correo_electronico],
                        fail_silently=False,
                    )

            except Turno.DoesNotExist:
                return JsonResponse({'success': False, 'message': f'El turno con ID {turno_id} no existe.'})

        return JsonResponse({'success': True, 'message': f'Turno(s) {accion} correctamente.'})

    return JsonResponse({'success': False, 'message': 'Método no permitido.'})


@csrf_exempt
def actualizar_reserva(request, reserva_id):
    if request.method == 'POST':
        try:

            data = json.loads(request.body)


            accion = data.get('accion')
            if accion not in ['confirmar', 'cancelar']:
                return JsonResponse({"error": "Acción no válida"}, status=400)


            reserva = get_object_or_404(Reservas, id_reserva=reserva_id)
            

            empleado_turno = EmpleadoXTurno.objects.filter(id_turno=reserva.id_turno).first()
            if not empleado_turno:
                return JsonResponse({"error": "No se encuentra el empleado asociado al turno."}, status=400)

            caja_abierta = Caja.objects.filter(estado=True).last()

            if accion == 'confirmar':

                servicio = reserva.id_serv_x_tur.id_servicio
                monto_subtotal = (servicio.precio_del_servicio * servicio.senia) / 100
                monto_total_adicional = servicio.precio_del_servicio - monto_subtotal


                venta_existente = Venta.objects.filter(
                    id_caja=caja_abierta,
                    id_cliente=reserva.id_cliente
                ).last()

                if venta_existente:

                    if venta_existente.id_caja == caja_abierta:
                        venta_existente.monto_total += monto_total_adicional
                        venta_existente.save()
                    else:

                        venta_existente = Venta.objects.create(
                            id_caja=caja_abierta,
                            id_cliente=reserva.id_cliente,
                            monto_total=monto_total_adicional
                        )
                else:

                    venta_existente = Venta.objects.create(
                        id_caja=caja_abierta,
                        id_cliente=reserva.id_cliente,
                        monto_total=monto_total_adicional
                    )


                DetalleVenta.objects.create(
                    id_venta=venta_existente,
                    id_reserva=reserva,
                    metodo_pago='Tranferencia',
                    monto_subtotal=monto_total_adicional
                )


                reserva.estado_reserva = 'Terminada'
                reserva.save()

                return JsonResponse({"success": "Se confirmó la reserva como terminada exitosamente"})

            elif accion == 'cancelar':

                reserva.estado_reserva = 'Cancelada'
                reserva.save()

                return JsonResponse({"success": "Se canceló la reserva exitosamente"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON malformado"}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@requerir_autenticacion
def inicio(request):
   
    return render(request,'index.html')


@requerir_autenticacion
def gturno(request):
    servicios = (
        ServicioXTurno.objects.values('id_servicio__nombre_del_servicio')
        .annotate(total=Count('id_turno'))
        .order_by('-total')
    )


    labels = [servicio['id_servicio__nombre_del_servicio'] for servicio in servicios]
    data = [servicio['total'] for servicio in servicios]

    context = {
        'labels': labels,
        'data': data,
    }
    return render(request,'graficos/grafico_turno.html',context)




@requerir_autenticacion
def gventas(request):
    ventas_por_metodo = (
        DetalleVenta.objects.values('metodo_pago')
        .annotate(total=Count('id_detalle_venta'))
        .order_by('-total')
    )

    labels = [venta['metodo_pago'] if venta['metodo_pago'] else 'Desconocido' for venta in ventas_por_metodo]
    data = [venta['total'] for venta in ventas_por_metodo]

    context = {
        'labels': labels,
        'data': data,
    }
    
    return render(request, 'graficos/grafico_ventas.html',context)

def gcaja(request):
    data = Caja.objects.values('empleado_nombre', 'empleado_apellido').annotate(
        total_recaudado=Sum('monto_final')
    ).order_by('-total_recaudado')

    empleados = [f"{d['empleado_nombre']} {d['empleado_apellido']}" for d in data]

    montos = [float(d['total_recaudado'] or 0) for d in data]

    return render(request, 'graficos/grafico_caja.html', {'empleados': empleados, 'montos': montos})

