from django.db import models
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth.hashers import make_password, check_password
from django.core.validators import EmailValidator, RegexValidator, MaxLengthValidator

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255, validators=[MaxLengthValidator(255)], blank=True, null=True)
    apellido = models.CharField(max_length=255, validators=[MaxLengthValidator(255)], blank=True, null=True)
    correo_electronico = models.EmailField(max_length=255, validators=[EmailValidator()])
    numero_telefono = models.CharField(max_length=15, validators=[RegexValidator(regex='^[0-9]*$', message='El número de teléfono debe contener solo dígitos.')])
    diseño_uñas = models.ImageField(upload_to='diseño_uñas/', blank=True, null=True)

    def __str__(self):
        return f"{self.nombre} {self.apellido}"  # En Cliente


class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    fecha = models.DateField(blank=True, null=True)
    hora = models.TimeField(blank=True, null=True)
    estado_turno = models.CharField(max_length=20, choices=[
        ('reservado', 'Reservado'),
        ('disponible', 'Disponible'),
        ('no_disponible', 'No Disponible'),
    ])

    def __str__(self):
        return f"{self.nombre} {self.apellido}"

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
    
class Empleado(models.Model):
    dni = models.IntegerField(primary_key=True, validators=[RegexValidator(regex='^[0-9]+$', message='El DNI debe contener solo dígitos.')])
    nombre = models.CharField(max_length=255, validators=[MaxLengthValidator(255)], blank=True, null=True)
    apellido = models.CharField(max_length=255, validators=[MaxLengthValidator(255)], blank=True, null=True)
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

    def __str__(self):
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

    def __str__(self):
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

    def __str__(self):
        return 

class EmpleadoXTurno(models.Model):
    id_emp_x_tur = models.AutoField(primary_key=True)
    dni_emp = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)

    def __str__(self):
        return 

class ServicioXTurno(models.Model):
    id_serv_x_tur = models.AutoField(primary_key=True)
    id_servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)

    def __str__(self):
        return 

class Reservas(models.Model):
    ESTADO_OPCIONES = [
        ('Confirmada', 'Confirmada'),
        ('En Proceso', 'En Proceso'),
        ('Cancelada', 'Cancelada'),
    ]
    id_reserva = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    id_serv_x_tur = models.ForeignKey(ServicioXTurno, on_delete=models.CASCADE)
    estado_reserva = models.CharField(max_length=20, choices=ESTADO_OPCIONES, default='En Proceso')

    def __str__(self):
        return 

class DetalleVenta(models.Model):
    id_detalle_venta = models.AutoField(primary_key=True)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    id_reserva = models.ForeignKey(Reservas, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=255, null=True, blank=True)
    monto_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    comprobante = models.ImageField(upload_to='detalleventa/', blank=True, null=True)
    estado_reserva = models.CharField(max_length=100)

    def __str__(self):
        return 

class D_VentaXServicio(models.Model):
    id_d_vent_x_serv = models.AutoField(primary_key=True)
    id_d_venta = models.ForeignKey(DetalleVenta, on_delete=models.CASCADE)
    id_servicio = models.ForeignKey(Servicios, on_delete=models.CASCADE)

    def __str__(self):
        return 
