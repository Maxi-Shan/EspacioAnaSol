from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.files.storage import default_storage
from django.conf import settings
from django.contrib import messages
from django.utils import timezone
from .models import Caja, Empleado, Servicios, ServicioXTurno, Turno, EmpleadoXTurno, Cliente, Venta, DetalleVenta, Reservas, D_VentaXServicio
from .forms import LoginForm, EmpleadoForm, ServiciosForm, TurnoForm, ClienteForm,  MultipleTurnoForm
from django.http import HttpResponse
from django.core import management
from django.utils import timezone
from django.http import HttpResponseRedirect
import os

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

def logout_view(request):
    # Eliminar la clave de sesión para cerrar la sesión
    if 'empleado_dni' in request.session:
        del request.session['empleado_dni']
        messages.success(request, 'Has cerrado sesión correctamente.')
    else:
        messages.warning(request, 'No estabas autenticado.')
    
    # Redirigir al usuario a la página de inicio de sesión
    return redirect('login')

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
    empleado = obtener_empleado_autenticado(request)
    es_admin = empleado.es_admin
    if request.method == 'POST':
        # Esta parte se queda igual, pero debes asegurarte de que la lógica de cierre de caja esté correcta
        caja.cerrar_caja(obtener_empleado_autenticado(request))  # Aquí se usa el empleado que cierra la caja
        return redirect('list_cajas')

    return render(request, 'cerrar_caja.html', {'caja': caja, 'es_admin': es_admin,})

@admin_required
def update_caja(request, id_caja):
    caja = get_object_or_404(Caja, id_caja=id_caja)
    empleado = obtener_empleado_autenticado(request)
    es_admin = empleado.es_admin
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
    
    return render(request, 'update_caja.html', {'caja': caja, 'es_admin': es_admin,})

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
    # Obtener el empleado autenticado
    empleado = obtener_empleado_autenticado(request)

    # Verificar si el empleado es admin
    es_admin = empleado.es_admin

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

    return render(request, 'add_turno.html', {'form': form, 'es_admin': es_admin,})

# Listar turnos
@requerir_autenticacion
def list_turnos(request):
    turnos = Turno.objects.all().prefetch_related('empleadoxturno_set', 'servicioxturno_set')  # Carga los turnos y sus relaciones

    empleado = obtener_empleado_autenticado(request)
    es_admin = empleado.es_admin

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

    return render(request, 'list_turnos.html', {'turnos_data': turnos_data, 'es_admin': es_admin,})

# Modificar un turno
@requerir_autenticacion
def update_turno(request, turno_id):
    turno = get_object_or_404(Turno, id_turno=turno_id)
    empleado = obtener_empleado_autenticado(request)

    # Verificar si el empleado es admin
    es_admin = empleado.es_admin

    if request.method == 'POST':
        form = TurnoForm(request.POST, instance=turno)
        if form.is_valid():
            form.save()
            messages.success(request, 'Turno actualizado correctamente.')
            return redirect('list_turnos')
    else:
        form = TurnoForm(instance=turno)

    return render(request, 'update_turno.html', {'form': form, 'turno': turno, 'es_admin': es_admin,})

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
    empleado = obtener_empleado_autenticado(request)

    # Verificar si el empleado es admin
    es_admin = empleado.es_admin
    return render(request, 'list_clientes.html', {'clientes': clientes, 'es_admin': es_admin,})

@login_required
@admin_required
def backup_database(request):
    # Define el nombre del archivo de respaldo con la fecha actual
    timestamp = timezone.now().strftime('%Y-%m-%d_%H-%M-%S')
    backup_filename = f'backup_{timestamp}.json'
    backup_path = os.path.join('backups', backup_filename)

    # Crear la carpeta de backups si no existe
    os.makedirs('backups', exist_ok=True)

    # Ejecuta el comando de dumpdata para exportar toda la base de datos en formato JSON
    with open(backup_path, 'w') as backup_file:
        management.call_command('dumpdata', stdout=backup_file)
    
    # Enviar un mensaje de éxito al usuario
    messages.success(request, f'Copia de seguridad realizada con éxito: {backup_filename}')

    # Opcional: enviar el archivo de respaldo como respuesta para descarga
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

        # Guardar el archivo de copia de seguridad temporalmente
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        with default_storage.open(backup_path, 'wb+') as destination:
            for chunk in backup_file.chunks():
                destination.write(chunk)

        # Restaurar la base de datos usando el archivo de copia de seguridad
        try:
            management.call_command('loaddata', backup_path)
            messages.success(request, 'La base de datos se ha restaurado correctamente.')
        except Exception as e:
            messages.error(request, f'Error al restaurar la base de datos: {str(e)}')
        finally:
            # Eliminar el archivo después de la restauración para mantener seguridad
            os.remove(backup_path)

        return HttpResponseRedirect(request.path_info)

    return render(request, 'restore_database.html')

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from .forms import ClienteForm, ReservasForm
from .models import Cliente, Reservas, Venta, DetalleVenta, D_VentaXServicio, Caja, Servicios

def registrar_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST, request.FILES)
        if form.is_valid():
            cliente = form.save()
            request.session['cliente_id'] = cliente.id_cliente
            return redirect('seleccionar_servicio', cliente_id=cliente.id_cliente)
    else:
        form = ClienteForm()
    return render(request, 'registrar_cliente.html', {'form': form})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .forms import ReservasForm
from .models import Cliente, Reservas

@requerir_autenticacion
def seleccionar_servicio(request, cliente_id):
    # Obtener el cliente correspondiente
    cliente = get_object_or_404(Cliente, id_cliente=cliente_id)
    
    if request.method == 'POST':
        form = ReservasForm(request.POST)
        if form.is_valid():
            # Crear la reserva pero sin guardarla de inmediato
            reserva = form.save(commit=False)
            reserva.id_cliente = cliente  # Asociar el cliente a la reserva
            reserva.estado_reserva = 'En Proceso'  # Definir el estado inicial
            reserva.save()  # Guardar la reserva en la base de datos
            
            # Guardar el cliente en la sesión para los siguientes pasos
            request.session['cliente_id'] = cliente_id
            
            messages.success(request, 'Reserva realizada con éxito. Redirigiendo a confirmación.')
            return redirect('confirmar_registro')  # Redirige a la página de confirmación

        else:
            messages.error(request, 'Hubo un error en el formulario. Por favor, verifica los datos ingresados.')
    else:
        form = ReservasForm()

    return render(request, 'seleccionar_servicio.html', {'form': form, 'cliente': cliente})


from django.contrib import messages
from django.utils import timezone
from .models import Caja, Venta, DetalleVenta, D_VentaXServicio, Reservas

@requerir_autenticacion
def confirmar_registro(request):
    cliente_id = request.session.get('cliente_id')
    reserva = Reservas.objects.filter(id_cliente=cliente_id, estado_reserva='En Proceso').first()

    if request.method == "POST":
        # Verifica si hay una caja abierta (estado=True)
        caja_abierta = Caja.objects.filter(estado=True).first()  # Busca una caja abierta (estado=True)
        
        if not caja_abierta:
            messages.error(request, 'No hay ninguna caja abierta. Abre una caja antes de confirmar la venta.')
            return redirect('pagina_principal')

        # Si hay una caja abierta, procede con el registro de la venta y detalles
        venta = Venta.objects.create(
            id_caja=caja_abierta,
            id_cliente=reserva.id_cliente,
            fecha_venta=timezone.now().date(),
            hs_venta=timezone.now().time(),
            monto_total=0.0,  # Cambiar al monto real si se calcula
            estado_venta=1  # Estado "En Proceso"
        )

        DetalleVenta.objects.create(
            id_venta=venta,
            id_reserva=reserva,
            metodo_pago='Efectivo',  # Cambiar según tu lógica de pago
            monto_subtotal=0.0,  # Cambiar al monto real
            estado_reserva='Confirmado'
        )

        D_VentaXServicio.objects.create(
            id_d_venta=venta,
            id_servicio=reserva.id_servicio
        )

        # Actualizar el estado de la reserva y limpiar la sesión
        reserva.estado_reserva = 'confirmado'
        reserva.save()
        del request.session['cliente_id']

        return redirect('list_ventas')
    
    return render(request, 'confirmar_registro.html', {'reserva': reserva})


def cancelar_registro(request):
    if 'cliente_id' in request.session:
        del request.session['cliente_id']
    if 'reserva_id' in request.session:
        del request.session['reserva_id']
    messages.info(request, 'Registro cancelado.')
    return redirect('pagina_principal')

def list_ventas(request):
    ventas = Venta.objects.all()
    return render(request, 'list_ventas.html', {'ventas': ventas})

def detalle_venta(request, venta_id):
    detalles_venta = DetalleVenta.objects.filter(id_venta=venta_id)
    return render(request, 'detalle_venta.html', {'detalles_venta': detalles_venta})
