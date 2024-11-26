from decimal import Decimal, ROUND_HALF_UP
from django.shortcuts import render, redirect, get_object_or_404
from .models import Turno, Cliente, EmpleadoXTurno, ServicioXTurno, Empleado, Servicios
from .forms import ClienteForm, TurnoForm, ComprobanteForm
from django.utils.timezone import now  

def base(request):
    return render(request, 'base.html')

def tutorial(request):
    return render(request, 'tutorial.html')

def servicios(request):
    servicios = Servicios.objects.all()
    return render(request, 'elegir_servicio.html', {'servicios': servicios})

def elegir_turno(request, servicio):
    servicio_obj = get_object_or_404(Servicios, nombre_del_servicio=servicio)

    if request.method == 'POST':
        turno_form = TurnoForm(request.POST)
        cliente_form = ClienteForm(request.POST)

        if turno_form.is_valid() and cliente_form.is_valid():
            nombre = cliente_form.cleaned_data['nombre']
            apellido = cliente_form.cleaned_data['apellido']
            numero_telefono = cliente_form.cleaned_data['numero_telefono']
            correo_electronico = cliente_form.cleaned_data['correo_electronico']

            empleado_dni = turno_form.cleaned_data['empleado'].dni
            fecha = turno_form.cleaned_data['fecha']
            hora = turno_form.cleaned_data['hora']

            request.session['turno_data'] = {
                'fecha': str(fecha),
                'hora': str(hora),
                'nombre': nombre,
                'apellido': apellido,
                'numero_telefono': numero_telefono,
                'correo_electronico': correo_electronico,
                'servicio': servicio_obj.nombre_del_servicio,
                'empleado_dni': empleado_dni
            }

            return redirect('confirmacion_turno', servicio_nombre=servicio_obj.nombre_del_servicio)
    else:
        turno_form = TurnoForm()
        cliente_form = ClienteForm()

    return render(request, 'elegir_turno.html', {
        'turno_form': turno_form,
        'cliente_form': cliente_form,
        'servicio': servicio_obj
    })



def confirmacion_turno(request, servicio_nombre):
    turno_data = request.session.get('turno_data', {})

    if not turno_data:
        return redirect('elegir_turno', servicio=servicio_nombre)

    servicio = get_object_or_404(Servicios, nombre_del_servicio__icontains=servicio_nombre)

    valor_reserva = (servicio.precio_del_servicio * servicio.senia) / 100
    valor_reserva_redondeado = valor_reserva.quantize(Decimal('0.00'), rounding=ROUND_HALF_UP)

    nombre = turno_data.get('nombre')
    apellido = turno_data.get('apellido')
    numero_telefono = turno_data.get('numero_telefono')
    correo_electronico = turno_data.get('correo_electronico')

    if request.method == 'POST':
        form = ComprobanteForm(request.POST, request.FILES)
        
        if form.is_valid():
            diseño_uñas = form.cleaned_data['diseño_uñas']
            senia_comprobante = form.cleaned_data['senia_comprobante']

            # Crear o recuperar el cliente
            cliente, created = Cliente.objects.get_or_create(
                nombre=nombre,
                apellido=apellido,
                numero_telefono=numero_telefono,
                correo_electronico=correo_electronico,
                defaults={'fecha_registro': now()}
            )

            # Crear el nuevo Turno con los datos recibidos
            nuevo_turno = Turno.objects.create(
                id_cliente=cliente,
                fecha=turno_data['fecha'],
                hora=turno_data['hora'],
                diseño_uñas=diseño_uñas,
                estado_turno='pendiente',
                fecha_registro=now()  # Registrar la fecha actual del turno
            )

            # Crear la relación entre el servicio y el turno
            ServicioXTurno.objects.create(
                id_servicio=servicio,
                id_turno=nuevo_turno
            )

            # Guardar el comprobante de la senia
            nuevo_turno.senia_comprobante = senia_comprobante
            nuevo_turno.save()

            # Asignar el empleado al turno
            empleado = get_object_or_404(Empleado, dni=turno_data['empleado_dni'])
            EmpleadoXTurno.objects.create(dni_emp=empleado, id_turno=nuevo_turno)

            # Limpiar la sesión
            del request.session['turno_data']
            return redirect('procesando_reserva', pk=nuevo_turno.pk)
    else:
        form = ComprobanteForm()

    context = {
        'servicio': servicio,
        'turno_data': turno_data,
        'nombre': nombre,
        'apellido': apellido,
        'numero_telefono': numero_telefono,
        'correo_electronico': correo_electronico,
        'form': form,
        'valor_reserva': valor_reserva_redondeado,
    }

    return render(request, 'confirmacion_turno.html', context)


def procesando_reserva(request, pk):
    turno = get_object_or_404(Turno, pk=pk)

    # Si se detecta una actualización (refresh), redirige a la página base.
    if request.method == "GET" and 'refresh' in request.META.get('HTTP_CACHE_CONTROL', '').lower():
        return redirect('inicio')

    return render(request, 'procesando_reserva.html', {'turno': turno})


def tiempo_agotado(request):
    # Si se detecta una actualización (refresh), redirige a la página de inicio.
    if request.method == "GET" and 'refresh' in request.META.get('HTTP_CACHE_CONTROL', '').lower():
        return redirect('inicio')

    return render(request, 'tiempo_agotado.html')


def mostrar_turnos(request):
    fecha = request.GET.get('fecha')
    
    horarios_totales = ['09:00', '11:00', '18:00', '20:00']
    
    if fecha:
        turnos_reservados = Turno.objects.filter(fecha=fecha).values_list('hora', flat=True)
        
        turnos_reservados_horas = [turno.strftime("%H:%M") for turno in turnos_reservados]
        
        turnos_disponibles = [hora for hora in horarios_totales if hora not in turnos_reservados_horas]
    else:
        turnos_disponibles = []
        turnos_reservados_horas = []

    return render(request, 'mostrar_turnos.html', {
        'fecha': fecha,
        'turnos_disponibles': turnos_disponibles,
        'turnos_reservados_horas': turnos_reservados_horas,
        'horarios_totales': horarios_totales
    })
