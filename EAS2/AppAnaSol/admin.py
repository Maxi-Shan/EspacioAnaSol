from django.contrib import admin
from django.core.mail import send_mail
from django.utils.html import format_html
from .models import Turno, Empleado, EmpleadoXTurno, Reservas, DetalleVenta, Servicios
from django.http import HttpResponseRedirect

class TurnoAdmin(admin.ModelAdmin):
    list_display = ('id_turno', 'cliente_nombre', 'empleado', 'fecha', 'hora', 'diseño_uñas', 'mostrar_comprobante')

    def cliente_nombre(self, obj):
        return f"{obj.id_cliente.nombre} {obj.id_cliente.apellido}" if obj.id_cliente else "Sin cliente"
    cliente_nombre.short_description = 'Cliente'

    def empleado(self, obj):
        empleado_x_turno = EmpleadoXTurno.objects.filter(id_turno=obj).first()
        return empleado_x_turno.dni_emp.nombre if empleado_x_turno and empleado_x_turno.dni_emp else "Sin empleado"
    empleado.short_description = 'Empleado'

    def mostrar_diseño_uñas(self, obj):
        if obj.diseño_uñas:
            return format_html(
                '<img src="{}" style="max-width: 100px; max-height: 100px;" />',
                obj.diseño_uñas.url
            )
        return "No hay diseño de uñas"
    mostrar_diseño_uñas.short_description = 'Diseño de Uñas'

    def mostrar_comprobante(self, obj):
        reserva = Reservas.objects.filter(id_turno=obj).first()
        if reserva:
            detalle_venta = DetalleVenta.objects.filter(id_reserva=reserva).first()
            if detalle_venta and detalle_venta.comprobante:
                return format_html(f'<a href="{detalle_venta.comprobante.url}" target="_blank">Ver comprobante</a>')
        return "Sin comprobante"
    mostrar_comprobante.short_description = 'Comprobante'

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # Convertir turno a reserva si el estado es 'confirmado'
        if obj.estado_turno == 'confirmado':
            reserva = obj.convertir_a_reserva()
            if reserva:
                self.message_user(request, f"Turno confirmado y guardado en Reservas con ID {reserva.id_reserva}")
            else:
                self.message_user(request, "No se pudo crear la reserva", level='error')

    actions = ['confirmar_turnos', 'cancelar_turnos']

    # Acción para confirmar turnos y convertirlos a reservas
    @admin.action(description='Confirmar turnos seleccionados y enviar correo')
    def confirmar_turnos(self, request, queryset):
        for turno in queryset:
            if turno.estado_turno in ['pendiente', 'cancelado']:
                turno.estado_turno = 'confirmado'
                turno.save()
                reserva = turno.convertir_a_reserva()

                if reserva:
                    turno.delete()
                    cliente = turno.id_cliente
                    send_mail(
                    'Confirmación de tu turno en AnaSol',
                    f'Hola {cliente.nombre}, tu turno ha sido confirmado para el {{ fecha_turno }} a las {{ fecha_hora }}. ¡Gracias por elegirnos!',
                    'anasolespacio@gmail.com',
                    [cliente.correo_electronico],
                    fail_silently=False,
                )
                self.message_user(request, f'Correo de confirmación enviado a {cliente.correo_electronico}')
            return HttpResponseRedirect(request.get_full_path())

    @admin.action(description='Cancelar turnos seleccionados y enviar correo')
    def cancelar_turnos(self, request, queryset):
        for turno in queryset:
            if turno.estado_turno in ['pendiente', 'confirmado']:
                turno.estado_turno = 'cancelado'
                turno.save()

                cliente = turno.id_cliente
                send_mail(
                    'Cancelación de tu turno en AnaSol',
                    f'Hola {cliente.nombre}, lamentamos informarte que tu turno para el {turno.fecha} a las {turno.hora} ha sido cancelado. Por favor, contáctanos para más información.',
                    'anasolespacio@gmail.com',
                    [cliente.correo_electronico],
                    fail_silently=False,
                )
                self.message_user(request, f'Correo de cancelación enviado a {cliente.correo_electronico}')

        return HttpResponseRedirect(request.get_full_path())

    actions = [confirmar_turnos, cancelar_turnos]

class ReservasAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'cliente_nombre', 'id_serv_x_tur', 'estado_reserva')

    def cliente_nombre(self, obj):
        return f"{obj.id_cliente.nombre} {obj.id_cliente.apellido}" if obj.id_cliente else "Sin cliente"
    cliente_nombre.short_description = 'Cliente'

    @admin.action(description='Cancelar reservas seleccionadas y enviar correo')
    def cancelar_reservas(self, request, queryset):
        for reserva in queryset:
            if reserva.estado_reserva == 'confirmada':
                reserva.estado_reserva = 'cancelada'
                reserva.save()

                cliente = reserva.id_cliente
                send_mail(
                    'Cancelación de tu reserva en AnaSol',
                    f'Hola {cliente.nombre}, lamentamos informarte que tu reserva ha sido cancelada. Contáctanos para reprogramarla o para más información.',
                    'anasolespacio@gmail.com',
                    [cliente.correo_electronico],
                    fail_silently=False,
                )
                self.message_user(request, f'Correo de cancelación enviado a {cliente.correo_electronico}')

    actions = [cancelar_reservas]


class EmpleadoAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'apellido', 'domicilio', 'correo_electronico', 'numero_telefono', 'contraseña', 'estado_empleado', 'es_admin']
    search_fields = ['nombre', 'apellido']
    list_filter = ['nombre', 'apellido']
    ordering = ['nombre']


admin.site.register(Empleado, EmpleadoAdmin)
admin.site.register(EmpleadoXTurno)
admin.site.register(Turno, TurnoAdmin)
admin.site.register(Reservas, ReservasAdmin)
admin.site.register(Servicios)

