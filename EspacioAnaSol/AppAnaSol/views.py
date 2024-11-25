from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from .models import Caja, Empleado, ServicioXTurno, EmpleadoXTurno, Cliente, Turno, Reservas, Servicios, Venta, Reservas, DetalleVenta
from .forms import EmpleadoForm, ServiciosForm, ClienteForm, TurnoForm, MetodoPagoForm
from django.core import management
from django.utils import timezone
from django.http import HttpResponseRedirect, JsonResponse, HttpResponse
from django.db.models import Count
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
                # Obtener el empleado por DNI
                empleado = Empleado.objects.get(dni=dni)
                
                # Verificar la contraseña
                if empleado.verificar_contraseña(contraseña):
                    # Guardar DNI del empleado en la sesión
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
        return empleado
    except Empleado.DoesNotExist:
        return None

def requerir_autenticacion(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'empleado_dni' not in request.session:
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
    empleados = Empleado.objects.all()

    # Pasar las contraseñas en texto plano a la plantilla
    for empleado in empleados:
        empleado.contraseña_original = empleado.contraseña_original or "No establecida"

    empleado_autenticado = obtener_empleado_autenticado(request)
    return render(request, 'list_empleados.html', {
        'empleados': empleados,
        'es_admin': empleado_autenticado.es_admin
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
    if request.method == "POST":
        form = EmpleadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('list_empleados')
    else:
        form = EmpleadoForm()
    return render(request, 'add_empleado.html', {'form': form, 'es_admin': empleado.es_admin})

@admin_required
@requerir_autenticacion
def update_empleado(request, dni):
    empleado_autenticado = obtener_empleado_autenticado(request)
    empleado = get_object_or_404(Empleado, dni=dni)

    if request.method == "POST":
        nombre = request.POST.get('nombre')
        apellido = request.POST.get('apellido')
        domicilio = request.POST.get('domicilio')
        correo_electronico = request.POST.get('correo_electronico')
        numero_telefono = request.POST.get('numero_telefono')
        contraseña = request.POST.get('contraseña')  # Obtén la contraseña en texto claro
        estado_empleado = request.POST.get('estado_empleado')
        es_admin = request.POST.get('es_admin') == 'True' 

        # Validar que los campos obligatorios no estén vacíos
        if not nombre or not apellido or not correo_electronico:
            # Retornar error si algún campo obligatorio está vacío
            return render(request, 'update_empleado.html', {
                'empleado': empleado,
                'es_admin': empleado_autenticado.es_admin,
                'error': 'Por favor, complete todos los campos obligatorios.'
            })

        # Si la contraseña se modificó, actualizamos el campo cifrado y en texto claro
        if contraseña:
            empleado.set_password(contraseña)  # Cifra la nueva contraseña
            empleado.contraseña_original = contraseña  # Guarda la contraseña en texto claro

        # Actualiza los otros campos
        empleado.nombre = nombre
        empleado.apellido = apellido
        empleado.domicilio = domicilio
        empleado.correo_electronico = correo_electronico
        empleado.numero_telefono = numero_telefono
        empleado.estado_empleado = estado_empleado
        empleado.es_admin = es_admin

        empleado.save()

        return redirect('list_empleados')

    # Si es GET, se pasa la contraseña sin cifrar para mostrarla en el formulario
    return render(request, 'update_empleado.html', {
        'empleado': empleado,
        'contraseña_original': empleado.contraseña_original,
        'es_admin': empleado_autenticado.es_admin
    })

def guardar_empleado(request, empleado_id):
    empleado = get_object_or_404(Empleado, pk=empleado_id)
    if request.method == "POST":
        contraseña = request.POST.get("contraseña")

        if contraseña:
            # Guardar la contraseña en texto plano
            empleado.contraseña_original = contraseña

            # Cifrar y guardar la contraseña en el campo encriptado
            empleado.password = make_password(contraseña)

        # Guardar otros datos
        empleado.nombre = request.POST.get("nombre")
        empleado.apellido = request.POST.get("apellido")
        empleado.save()

        return redirect("list_empleados")

@login_required
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

@login_required
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

@login_required
@requerir_autenticacion
def cerrar_caja(request, id_caja):
    caja = Caja.objects.get(id_caja=id_caja)
    empleado = obtener_empleado_autenticado(request)
    if request.method == 'POST':
        caja.cerrar_caja(obtener_empleado_autenticado(request)) 
        return redirect('list_cajas')

    return render(request, 'cerrar_caja.html', {'caja': caja, 'es_admin': empleado.es_admin})

@login_required
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

@admin_required
@requerir_autenticacion
def delete_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)
    if request.method == "POST":
        caja.delete()
        messages.success(request, 'Caja eliminada con éxito.')
        return redirect('list_cajas')
    
    return render(request, 'delete_caja.html', {'caja': caja})

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
        form = ServiciosForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio agregado con éxito.')
            return redirect('list_servicios')
    else:
        form = ServiciosForm()
        print(form.errors)
    return render(request, 'add_servicio.html', {'form': form, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})


@login_required
@requerir_autenticacion
def update_servicio(request, id_servicio):
    servicio = get_object_or_404(Servicios, id_servicio=id_servicio)
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
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

    return render(request, 'update_servicio.html', {'servicio': servicio, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})

@login_required
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
            # Guardar el ID del cliente en la sesión para usarlo en la vista de Turno
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

    return render(request, 'registrar_turno.html', {'form': form, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})

@login_required
@requerir_autenticacion
def cancelar_registro(request):
    request.session.pop('cliente_id', None)  # Limpiar datos de sesión si existen
    return redirect('list_turnos')

# Listar turnos
@login_required
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
            'empleados': empleado,
        })

    context = {
        'turnos_data': turnos_data,
        'cajas_abiertas': cajas_abiertas,
        'es_admin': empleado.es_admin
    }
    
    return render(request, 'list_turnos.html', context)


@login_required
@requerir_autenticacion
def modificar_turno(request, turno_id):
    empleado = obtener_empleado_autenticado(request)
    turno = get_object_or_404(Turno, id_turno=turno_id)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
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
        'es_admin': empleado.es_admin, 
        'cajas_abiertas': cajas_abiertas,
    })

@login_required
@requerir_autenticacion
def eliminar_turno(request, turno_id):
    turno = get_object_or_404(Turno, id_turno=turno_id)
    turno.delete()
    return redirect('list_turnos')

@login_required
@requerir_autenticacion
def list_clientes(request):
    empleado = obtener_empleado_autenticado(request)
    clientes = Cliente.objects.all() 
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    return render(request, 'list_clientes.html', {'clientes': clientes, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})

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
def list_ventas(request):
    ventas = Venta.objects.all()
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    return render(request, 'list_ventas.html', {'ventas': ventas, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})

@login_required
@requerir_autenticacion
def modificar_metodo_pago(request, venta_id):
    # Obtener la venta y el detalle de la venta relacionado con la venta
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
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

@login_required
@requerir_autenticacion
def list_reservas(request):
    reservas = Reservas.objects.all()
    empleado = obtener_empleado_autenticado(request)
    cajas_abiertas = Caja.objects.filter(estado=True).exists()
    return render(request, 'list_reservas.html', {'reservas': reservas, 'es_admin': empleado.es_admin, 'cajas_abiertas': cajas_abiertas,})

from django.http import JsonResponse
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from .models import Turno, ServicioXTurno, Reservas, Venta, DetalleVenta, Caja
import json
from decimal import Decimal

# Alias para confirmar específicamente turnos
def confirmar_turno(request):
    return gestionar_turno(request, accion='confirmar')

@login_required
def gestionar_turno(request, accion):
    if request.method == 'POST':
        data = json.loads(request.body)  # Leer el cuerpo JSON de la solicitud
        turnos_ids = data.get('turnos')  # IDs de los turnos seleccionados
        action = data.get('action')  # "confirmar" o "cancelar"

        if not turnos_ids:
            return JsonResponse({'success': False, 'message': 'No se seleccionaron turnos.'})

        for turno_id in turnos_ids:
            try:
                turno = Turno.objects.get(id_turno=turno_id)

                if action == 'confirmar':
                    # Actualizar estado del turno y crear una reserva
                    turno.estado_turno = 'Confirmado'
                    turno.save()

                    # Obtener el servicio asociado al turno
                    servicio_x_turno = ServicioXTurno.objects.filter(id_turno=turno).first()
                    if not servicio_x_turno:
                        return JsonResponse({'success': False, 'message': f'No se encontró un servicio asociado al turno {turno_id}.'})

                    # Crear reserva asociada al turno
                    reserva = Reservas.objects.create(
                        id_cliente=turno.id_cliente,
                        id_turno=turno,
                        id_serv_x_tur=servicio_x_turno,
                        estado_reserva='En Proceso'
                    )

                    # Crear registro de venta asociado a la reserva
                    precio_servicio = servicio_x_turno.id_servicio.precio_del_servicio
                    senia = servicio_x_turno.id_servicio.senia
                    monto_subtotal = (precio_servicio * senia) / 100

                    # Obtener la caja activa (supone que hay una caja abierta única)
                    caja_activa = Caja.objects.filter(estado=True).first()
                    if not caja_activa:
                        return JsonResponse({'success': False, 'message': 'No hay una caja abierta para registrar la venta.'})

                    # Crear la venta
                    venta = Venta.objects.create(
                        id_caja=caja_activa,
                        id_cliente=turno.id_cliente,
                        monto_total=monto_subtotal
                    )

                    # Crear el detalle de venta
                    DetalleVenta.objects.create(
                        id_venta=venta,
                        id_reserva=reserva,
                        metodo_pago='Tranferencia',  # Se puede modificar según corresponda
                        monto_subtotal=monto_subtotal
                    )

                    # Enviar correo de confirmación
                    send_mail(
                        'Confirmación de Turno',
                        f'Hola {turno.id_cliente.nombre}, tu turno ha sido confirmado para el día {turno.fecha} a las {turno.hora}.',
                        'anasolespacio@gmail.com',
                        [turno.id_cliente.correo_electronico],
                        fail_silently=False,
                    )

                elif action == 'cancelar':
                    # Actualizar estado del turno a "cancelado"
                    turno.estado_turno = 'Cancelado'
                    turno.save()

                    # Enviar correo de cancelación
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
            # Leer el cuerpo JSON de la solicitud
            data = json.loads(request.body)

            # Obtener la acción
            accion = data.get('accion')
            if accion not in ['confirmar', 'cancelar']:
                return JsonResponse({"error": "Acción no válida"}, status=400)

            # Obtener la reserva correspondiente
            reserva = get_object_or_404(Reservas, id_reserva=reserva_id)
            
            # Obtener el empleado asociado al turno de la reserva
            empleado_turno = EmpleadoXTurno.objects.filter(id_turno=reserva.id_turno).first()
            if not empleado_turno:
                return JsonResponse({"error": "No se encuentra el empleado asociado al turno."}, status=400)

            # Verificar si la caja está abierta para el empleado
            caja_abierta = Caja.objects.filter(empleado=empleado_turno.dni_emp, estado=True).last()
            if not caja_abierta:
                return JsonResponse({"error": "Realice la Apertura de caja para realizar esta acción"}, status=400)

            # Acciones para confirmar o cancelar la reserva
            if accion == 'confirmar':
                # Obtener el servicio y los montos
                servicio = reserva.id_serv_x_tur.id_servicio
                monto_subtotal = (servicio.precio_del_servicio * servicio.senia) / 100
                monto_total_adicional = servicio.precio_del_servicio - monto_subtotal

                # Verificar si ya existe una venta para este cliente en la caja abierta
                venta_existente = Venta.objects.filter(
                    id_caja=caja_abierta,
                    id_cliente=reserva.id_cliente
                ).last()

                if venta_existente:
                    # Si la caja de la venta existente es la misma, actualizar el monto
                    if venta_existente.id_caja == caja_abierta:
                        venta_existente.monto_total += monto_total_adicional
                        venta_existente.save()
                    else:
                        # Si es otra caja, crear una nueva venta
                        venta_existente = Venta.objects.create(
                            id_caja=caja_abierta,
                            id_cliente=reserva.id_cliente,
                            monto_total=monto_total_adicional
                        )
                else:
                    # Si no hay una venta existente, crear una nueva
                    venta_existente = Venta.objects.create(
                        id_caja=caja_abierta,
                        id_cliente=reserva.id_cliente,
                        monto_total=monto_total_adicional
                    )

                # Crear un detalle de venta asociado
                DetalleVenta.objects.create(
                    id_venta=venta_existente,
                    id_reserva=reserva,
                    metodo_pago='Tranferencia',
                    monto_subtotal=monto_total_adicional
                )

                # Actualizar el estado de la reserva a 'terminada'
                reserva.estado_reserva = 'Terminada'
                reserva.save()

                return JsonResponse({"success": "Se confirmó la reserva como terminada exitosamente"})

            elif accion == 'cancelar':
                # Actualizar el estado de la reserva a 'cancelada'
                reserva.estado_reserva = 'Cancelada'
                reserva.save()

                return JsonResponse({"success": "Se canceló la reserva exitosamente"})

        except json.JSONDecodeError:
            return JsonResponse({"error": "JSON malformado"}, status=400)
    return JsonResponse({"error": "Método no permitido"}, status=405)


@login_required
@requerir_autenticacion
def inicio(request):
   
    return render(request,'index.html')
    #return HttpResponse("<h1>hola feos<h1>")

@login_required
@requerir_autenticacion
def gturno(request):
    servicios = (
        ServicioXTurno.objects.values('id_servicio__nombre_del_servicio')
        .annotate(total=Count('id_turno'))
        .order_by('-total')
    )

    # Preparar los datos para Chart.js
    labels = [servicio['id_servicio__nombre_del_servicio'] for servicio in servicios]
    data = [servicio['total'] for servicio in servicios]

    context = {
        'labels': labels,
        'data': data,
    }
    return render(request,'graficos/grafico_turno.html',context)
    #return HttpResponse("<h1>hola feos<h1>")

@login_required
@requerir_autenticacion
def gventas(request):
    ventas_por_metodo = (
        DetalleVenta.objects.values('metodo_pago')
        .annotate(total=Count('id_detalle_venta'))
        .order_by('-total')
    )

    # Preparar los datos para Chart.js
    labels = [venta['metodo_pago'] if venta['metodo_pago'] else 'Desconocido' for venta in ventas_por_metodo]
    data = [venta['total'] for venta in ventas_por_metodo]

    context = {
        'labels': labels,
        'data': data,
    }
    
    return render(request, 'graficos/grafico_ventas.html',context)