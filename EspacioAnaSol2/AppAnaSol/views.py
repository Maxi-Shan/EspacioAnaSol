from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .forms import ClienteForm
from .models import Turno, Servicios, Reservas, Caja, Venta, DetalleVenta
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json

def inicio(request):
    return render(request, 'inicio.html')

def seleccionar_servicio(request):
    servicios = Servicios.objects.all()
    if request.method == 'POST':
        servicio_id = request.POST.get('servicio_id')
        return redirect('seleccionar_turno', servicio_id=servicio_id) 
    return render(request, 'seleccionar_servicio.html', {'servicios': servicios})



def seleccionar_turno(request, servicio_id):
    turnos = Turno.objects.filter(estado_turno=True, servicioxturno__id_servicio=servicio_id)

    fechas_ocupadas = [turno.fecha.strftime('%Y-%m-%d') for turno in turnos]

    horas_ocupadas = {}
    for turno in turnos:
        fecha_str = turno.fecha.strftime('%Y-%m-%d')
        if fecha_str not in horas_ocupadas:
            horas_ocupadas[fecha_str] = []
        horas_ocupadas[fecha_str].append(turno.hora.strftime('%H:%M'))  

    return render(request, 'seleccionar_turno.html', {
        'fechas_ocupadas': fechas_ocupadas,
        'horas_ocupadas': json.dumps(horas_ocupadas),  
        'servicio_id': servicio_id  
    })



def obtener_horas(request):
    fecha = request.GET.get('fecha')
    if fecha:
        turnos = Turno.objects.filter(fecha=fecha)
        horas = [turno.hora.strftime('%H:%M') for turno in turnos]
    else:
        horas = []

    return JsonResponse({'horas': horas})

def registrar_cliente(request, servicio_id):
    fecha = request.GET.get('fecha')
    hora = request.GET.get('hora')

    if not fecha or not hora:
        return redirect('seleccionar_turno', servicio_id=servicio_id)

    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST, request.FILES)  # Agregar request.FILES para manejar la imagen
        if cliente_form.is_valid():
            cliente = cliente_form.save()

            # Buscar o crear el turno basado en la fecha y hora seleccionadas
            turno, created = Turno.objects.get_or_create(
                fecha=fecha,
                hora=hora,
                defaults={'estado_turno': True}
            )

            # Guardar reserva
            servicio = Servicios.objects.get(id_servicio=servicio_id)
            reserva = Reservas(
                id_cliente=cliente,
                id_turno=turno,
                id_servicio=servicio,
                estado_reserva='en_proceso'  # Estado automático
            )
            reserva.save()

            # Verificar si la caja está abierta
            caja_abierta = Caja.objects.filter(estado=True).first()

            if caja_abierta:
                # Registrar venta
                venta = Venta(
                    id_caja=caja_abierta,
                    fecha_venta=timezone.now().date(),
                    hs_venta=timezone.now().time(),
                    monto_total=servicio.precio_del_servicio,
                    estado_venta=0  # Completada
                )
                venta.save()

                # Registrar detalle de la venta
                detalle_venta = DetalleVenta(
                    id_venta=venta,
                    id_reserva=reserva,
                    metodo_pago='Transferencia',  # Ajustar según el caso
                    monto_subtotal=servicio.precio_del_servicio,
                    comprobante=request.FILES.get('comprobante')  # Guardar la imagen
                )
                detalle_venta.save()

            return redirect('inicio')  # Redirigir a la página de inicio
    else:
        cliente_form = ClienteForm()

    # Obtener el servicio para mostrarlo en el formulario
    servicio = Servicios.objects.get(id_servicio=servicio_id)

    return render(request, 'registrar_cliente.html', {
        'form': cliente_form,
        'servicio_id': servicio_id,
        'fecha': fecha,
        'hora': hora,
        'servicio': servicio,  # Pasar el servicio para mostrarlo en la plantilla
    })
