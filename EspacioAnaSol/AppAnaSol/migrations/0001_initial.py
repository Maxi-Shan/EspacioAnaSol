# Generated by Django 5.0.6 on 2024-10-13 04:47

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('id_cliente', models.AutoField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('apellido', models.CharField(blank=True, max_length=255, null=True)),
                ('correo_electronico', models.CharField(blank=True, max_length=255, null=True)),
                ('numero_telefono', models.CharField(blank=True, max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('dni', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(blank=True, max_length=255, null=True)),
                ('apellido', models.CharField(blank=True, max_length=255, null=True)),
                ('domicilio', models.CharField(blank=True, max_length=255, null=True)),
                ('correo_electronico', models.CharField(blank=True, max_length=255, null=True)),
                ('numero_telefono', models.CharField(blank=True, max_length=20, null=True)),
                ('contraseña', models.CharField(blank=True, max_length=255, null=True)),
                ('estado_empleado', models.BooleanField(default=True)),
                ('es_admin', models.BooleanField(default=False)),
            ],
        ),
        migrations.CreateModel(
            name='Servicios',
            fields=[
                ('id_servicio', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_del_servicio', models.CharField(max_length=255)),
                ('descripcion_del_servicio', models.TextField(blank=True, null=True)),
                ('duracion', models.CharField(blank=True, max_length=255, null=True)),
                ('precio_del_servicio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('valor_sello', models.DecimalField(decimal_places=2, max_digits=10)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='servicios/')),
            ],
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id_turno', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateField(blank=True, null=True)),
                ('hora', models.TimeField(blank=True, null=True)),
                ('estado_turno', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Caja',
            fields=[
                ('id_caja', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_apertura', models.DateTimeField(auto_now_add=True)),
                ('fecha_cierre', models.DateTimeField(blank=True, null=True)),
                ('monto_inicial', models.DecimalField(decimal_places=2, max_digits=10)),
                ('monto_recaudado', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('monto_final', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('estado', models.BooleanField(default=True)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cajas_abiertas', to='AppAnaSol.empleado')),
                ('empleado_cierre', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='cajas_cerradas', to='AppAnaSol.empleado')),
            ],
        ),
        migrations.CreateModel(
            name='Reservas',
            fields=[
                ('id_reserva', models.AutoField(primary_key=True, serialize=False)),
                ('id_cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.cliente')),
                ('id_servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.servicios')),
                ('id_turno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.turno')),
            ],
        ),
        migrations.CreateModel(
            name='ServicioXTurno',
            fields=[
                ('id_serv_x_tur', models.AutoField(primary_key=True, serialize=False)),
                ('id_servicio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.servicios')),
                ('id_turno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.turno')),
            ],
        ),
        migrations.CreateModel(
            name='EmpleadoXTurno',
            fields=[
                ('id_emp_x_tur', models.AutoField(primary_key=True, serialize=False)),
                ('dni_emp', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.empleado')),
                ('id_turno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.turno')),
            ],
        ),
        migrations.CreateModel(
            name='Venta',
            fields=[
                ('id_venta', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_venta', models.DateField(blank=True, null=True)),
                ('hs_venta', models.TimeField(blank=True, null=True)),
                ('monto_total', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado_venta', models.IntegerField(choices=[(0, 'Completada'), (1, 'En Proceso')])),
                ('id_caja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.caja')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id_detalle_venta', models.AutoField(primary_key=True, serialize=False)),
                ('metodo_pago', models.CharField(blank=True, max_length=255, null=True)),
                ('monto_subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('comprobante', models.ImageField(blank=True, null=True, upload_to='detalleventa/')),
                ('estado_reserva', models.BooleanField(default=True)),
                ('id_reserva', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.reservas')),
                ('id_venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.venta')),
            ],
        ),
    ]
