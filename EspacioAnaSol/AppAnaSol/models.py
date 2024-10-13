from django.db import models
from django.utils import timezone
from django.db.models import Sum

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    apellido = models.CharField(max_length=255, blank=True, null=True)
    correo_electronico = models.CharField(max_length=255, blank=True, null=True)
    numero_telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    pass

class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    fecha = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    estado_turno = models.BooleanField(default=True)

    def __str__(self):
        return f'Turno {self.id_turno} - {self.fecha} {self.hora}'

class Servicios(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre_del_servicio = models.CharField(max_length=255)
    descripcion_del_servicio = models.TextField(blank=True, null=True)
    duracion = models.CharField(max_length=255, blank=True, null=True)
    precio_del_servicio = models.DecimalField(max_digits=10, decimal_places=2)
    valor_sello = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)

    def __str__(self):
        return self.nombre_del_servicio

    def __str__(self):
        return self.nombre_del_servicio

class Empleado(models.Model):
    dni = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255, blank=True, null=True)
    apellido = models.CharField(max_length=255, blank=True, null=True)
    domicilio = models.CharField(max_length=255, blank=True, null=True)
    correo_electronico = models.CharField(max_length=255, blank=True, null=True)
    numero_telefono = models.CharField(max_length=20, blank=True, null=True)
    contraseña = models.CharField(max_length=255, blank=True, null=True)
    estado_empleado = models.BooleanField(default=True)
    es_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class Caja(models.Model):
    id_caja = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE, related_name='cajas_abiertas')
    fecha_apertura = models.DateTimeField(auto_now_add=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    monto_recaudado = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    empleado_cierre = models.ForeignKey(Empleado, null=True, blank=True, on_delete=models.SET_NULL, related_name='cajas_cerradas')
    estado = models.BooleanField(default=True)

    def cerrar_caja(self, empleado):
        self.fecha_cierre = timezone.now()
        self.empleado_cierre = empleado
        
        # Calcular el monto recaudado basado en las ventas
        total_ventas = Venta.objects.filter(id_caja=self).aggregate(total=Sum('monto_total'))['total'] or 0
        self.monto_recaudado = total_ventas
        
        # Calcular el monto final
        self.monto_final = self.monto_inicial + self.monto_recaudado
        
        self.estado = False  # Marcar la caja como cerrada
        self.save()

    def __str__(self):
        return f'Caja {self.id_caja} - Estado: {"Abierta" if self.estado else "Cerrada"}'


class Venta(models.Model):
    ESTADO_VENTA_CHOICES = [
        (0, 'Completada'),
        (1, 'En Proceso'),
    ]
    
    id_venta = models.AutoField(primary_key=True)
    id_caja = models.ForeignKey(Caja, on_delete=models.CASCADE)
    fecha_venta = models.DateField(null=True, blank=True)
    hs_venta = models.TimeField(null=True, blank=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado_venta = models.IntegerField(choices=ESTADO_VENTA_CHOICES)

    def __str__(self):
        return f'Venta {self.id_venta} - {self.fecha_venta} {self.hs_venta}'

class Reservas(models.Model):
    id_reserva = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)
    id_servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)

    def __str__(self):
        return

class DetalleVenta(models.Model):
    id_detalle_venta = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    id_reserva = models.ForeignKey(Reservas, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=255, null=True, blank=True)
    monto_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    comprobante = models.ImageField(upload_to='detalleventa/', blank=True, null=True)
    estado_reserva = models.BooleanField(default=True)

    def __str__(self):
        return f'Detalle Venta {self.id_detalle_venta} - Venta {self.id_venta.id_venta}'

class EmpleadoXTurno(models.Model):
    id_emp_x_tur = models.AutoField(primary_key=True)
    dni_emp = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)

    def __str__(self):
        return f'Empleado {self.dni_emp.nombre} - Turno {self.id_turno.id_turno}'

class ServicioXTurno(models.Model):
    id_serv_x_tur = models.AutoField(primary_key=True)
    id_servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)

    def __str__(self):
        return f'Servicio {self.id_servicio.nombre_servicio} - Turno {self.id_turno.id_turno}'

