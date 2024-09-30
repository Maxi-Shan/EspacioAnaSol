from django.db import models
from django.utils import timezone

class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    correo_electronico = models.CharField(max_length=255)
    numero_telefono = models.CharField(max_length=20)

    def __str__(self):
        return f'{self.nombre} {self.apellido}'
    pass

class Turno(models.Model):
    id_turno = models.AutoField(primary_key=True)
    fecha = models.DateField()
    hora = models.TimeField()
    estado_turno = models.BooleanField()

    def __str__(self):
        return f'Turno {self.id_turno} - {self.fecha} {self.hora}'

class Servicios(models.Model):
    id_servicio = models.AutoField(primary_key=True)
    nombre_del_servicio = models.CharField(max_length=255)
    descripcion_del_servicio = models.CharField(max_length=255)
    categoria_del_servicio = models.CharField(max_length=255)
    precio_del_servicio = models.DecimalField(max_digits=10, decimal_places=2)
    nota_adicional = models.TextField()
    imagen = models.ImageField(upload_to='servicios/', blank=True, null=True)  

    def __str__(self):
        return self.nombre_del_servicio

class Empleado(models.Model):
    dni = models.IntegerField(primary_key=True)
    nombre = models.CharField(max_length=255)
    apellido = models.CharField(max_length=255)
    domicilio = models.CharField(max_length=255)
    correo_electronico = models.CharField(max_length=255)
    numero_telefono = models.CharField(max_length=20)
    contraseña = models.CharField(max_length=255)
    estado_empleado = models.BooleanField(default=True)
    es_admin = models.BooleanField(default=False)

    def __str__(self):
        return self.nombre

class Caja(models.Model):
    id_caja = models.AutoField(primary_key=True)
    empleado = models.ForeignKey(Empleado, on_delete=models.CASCADE)
    fecha_apertura = models.DateTimeField(null=True, blank=True)
    fecha_cierre = models.DateTimeField(null=True, blank=True)
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    monto_recaudado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_final = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def abrir_caja(self):
        self.fecha_apertura = timezone.now()
        self.save()

    def cerrar_caja(self):
        self.fecha_cierre = timezone.now()
        self.save()

    def __str__(self):
        return f"Caja ID: {self.id_caja} - Empleado: {self.empleado.nombre}"

class Venta(models.Model):
    id_venta = models.AutoField(primary_key=True)
    id_caja = models.ForeignKey(Caja, on_delete=models.CASCADE)
    fecha_venta = models.DateField()
    hs_venta = models.TimeField()
    monto_inicial = models.DecimalField(max_digits=10, decimal_places=2)
    estado_venta = models.BooleanField()

    def __str__(self):
        return f'Venta {self.id_venta} - {self.fecha_venta} {self.hs_venta}'

class DetalleVenta(models.Model):
    id_detalle_venta = models.AutoField(primary_key=True)
    id_cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    id_turno = models.ForeignKey(Turno, on_delete=models.CASCADE)
    id_venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    metodo_pago = models.CharField(max_length=255)
    monto_subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    nota_adicional = models.TextField()

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
