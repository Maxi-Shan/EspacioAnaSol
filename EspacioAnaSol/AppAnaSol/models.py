from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.hashers import make_password
from django.core.validators import EmailValidator, RegexValidator

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    correo_electronico = models.EmailField(max_length=255, validators=[EmailValidator()])
    numero_telefono = models.CharField(max_length=15, validators=[RegexValidator(regex='^[0-9]*$', message='El número de teléfono debe contener solo dígitos.')])

    def _str_(self):
        return f"{self.nombre} {self.apellido}" 


class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, null=True, blank=True, on_delete=models.CASCADE)
    fecha = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    diseño_uñas = models.ImageField(upload_to='diseño_uñas/', blank=True, null=True)
    fecha_registro = models.DateTimeField(blank=True, null=True)
    estado_turno = models.CharField(max_length=20, choices=[
        ('Disponible', 'Disponible'),
        ('Pendiente', 'Pendiente'),
        ('Confirmado', 'Confirmado'),
        ('Cancelado', 'Cancelado'),
    ], default='Disponible') 

    def __str__(self):
        return f'Turno {self.id_turno} - Fecha: {self.fecha} Hora: {self.hora} - Estado: {self.estado_turno}'

    
    def convertir_a_reserva(self):
        if not Reservas.objects.filter(id_turno=self).exists():
            reserva = Reservas.objects.create(id_turno=self, id_cliente=self.id_cliente, estado_turno='Confirmado')
            return reserva
        return None

class Servicios(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre_del_servicio = models.CharField(max_length=255)
    descripcion_del_servicio = models.TextField(blank=True, null=True)
    duracion = models.CharField(max_length=255, blank=True, null=True)
    precio_del_servicio = models.DecimalField(max_digits=10, decimal_places=2)
    valor_sello = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)

    def _str_(self):
        return self.nombre_del_servicio
    
class Empleado(models.Model):
    dni = models.IntegerField(primary_key=True, validators=[RegexValidator(regex='^[0-9]+$', message='El DNI debe contener solo dígitos.')])
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    domicilio = models.CharField(max_length=255, blank=True, null=True)
    correo_electronico = models.EmailField(max_length=255, validators=[EmailValidator()], blank=True, null=True, unique=True)
    numero_telefono = models.CharField(max_length=20, blank=True, null=True, validators=[RegexValidator(regex='^[0-9]*$', message='El número de teléfono debe contener solo dígitos.')])
    contraseña = models.CharField(max_length=128)
    estado_empleado = models.CharField(max_length=10, choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')])
    es_admin = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk:  # Solo al crear el objeto
            self.contraseña = make_password(self.contraseña)
        super().save(*args, **kwargs)

    def verificar_contraseña(self, contraseña):
        return make_password(contraseña, self.contraseña)

    def _str_(self):
        return f"{self.nombre} {self.apellido}"

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
        if not self.estado:
            return  # Ya está cerrada
        self.fecha_cierre = timezone.now()
        self.empleado_cierre = empleado
        total_ventas = Venta.objects.filter(id_caja=self).aggregate(total=Sum('monto_total'))['total'] or 0
        self.monto_recaudado = total_ventas
        self.monto_final = self.monto_inicial + self.monto_recaudado
        self.estado = False  
        self.save()

    def _str_(self):
        return f'Caja {self.id_caja} - Estado: {"Abierta" if self.estado else "Cerrada"}'

class Venta(models.Model):
    ESTADO_VENTA_CHOICES = [
        (0, 'Completada'),
        (1, 'En Proceso'),
        (2, 'No Completada'),
    ]
    id_venta = models.AutoField(primary_key=True)
    id_caja = models.ForeignKey(Caja, on_delete=models.CASCADE)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_venta = models.DateField(null=True, blank=True)
    hs_venta = models.TimeField(null=True, blank=True)
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado_venta = models.IntegerField(choices=ESTADO_VENTA_CHOICES)

    def _str_(self):
        return f'Venta {self.id_venta} - Cliente: {self.id_cliente}'

class EmpleadoXTurno(models.Model):
    id_emp_x_tur = models.AutoField(primary_key=True)
    dni_emp = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)

    def _str_(self):
        return f'Empleado: {self.dni_emp} en Turno: {self.id_turno}'

class ServicioXTurno(models.Model):
    id_serv_x_tur = models.AutoField(primary_key=True)
    id_servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)

    def _str_(self):
        return f'Servicio: {self.id_servicio} en Turno: {self.id_turno}'

class Reservas(models.Model):
    ESTADO_OPCIONES = [
        ('confirmada', 'Confirmada'),
        ('pendiente', 'Pendiente'),
        ('cancelada', 'Cancelada'),
    ]
    id_reserva = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)
    id_serv_x_tur = models.ForeignKey(ServicioXTurno, on_delete=models.CASCADE)
    estado_reserva = models.CharField(max_length=20, choices=ESTADO_OPCIONES, default='Confirmada')

    def _str_(self):
        return f'Reserva {self.id_reserva} - Cliente: {self.id_cliente} - Estado: {self.estado_reserva} - Servicio: {self.id_serv_x_tur.id_servicio}'

class DetalleVenta(models.Model):
    id_detalle_venta = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    id_reserva = models.ForeignKey(Reservas, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=255, null=True, blank=True)
    monto_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    comprobante = models.ImageField(upload_to='detalleventa/', blank=True, null=True)
    estado_reserva = models.CharField(max_length=100)

    def _str_(self):
        return f'Detalle de Venta {self.id_detalle_venta} - Reserva: {self.id_reserva}'