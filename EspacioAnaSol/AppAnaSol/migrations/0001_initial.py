# Generated by Django 5.0.6 on 2024-09-15 04:37

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
                ('nombre', models.CharField(max_length=255)),
                ('apellido', models.CharField(max_length=255)),
                ('correo_electronico', models.CharField(max_length=255)),
                ('numero_telefono', models.CharField(max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='Empleado',
            fields=[
                ('dni', models.IntegerField(primary_key=True, serialize=False)),
                ('nombre', models.CharField(max_length=255)),
                ('apellido', models.CharField(max_length=255)),
                ('domicilio', models.CharField(max_length=255)),
                ('correo_electronico', models.CharField(max_length=255)),
                ('numero_telefono', models.CharField(max_length=20)),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='imagenes/')),
                ('contraseña', models.CharField(blank=True, max_length=255, null=True)),
                ('estado_empleado', models.BooleanField(default=True)),
            ],
        ),
        migrations.CreateModel(
            name='Servicios',
            fields=[
                ('id_servicio', models.AutoField(primary_key=True, serialize=False)),
                ('nombre_del_servicio', models.CharField(max_length=255)),
                ('descripcion_del_servicio', models.CharField(max_length=255)),
                ('categoria_del_servicio', models.CharField(max_length=255)),
                ('precio_del_servicio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nota_adicional', models.TextField()),
                ('imagen', models.ImageField(blank=True, null=True, upload_to='servicios/')),
            ],
        ),
        migrations.CreateModel(
            name='Turno',
            fields=[
                ('id_turno', models.AutoField(primary_key=True, serialize=False)),
                ('fecha', models.DateField()),
                ('hora', models.TimeField()),
                ('estado_turno', models.BooleanField()),
            ],
        ),
        migrations.CreateModel(
            name='Caja',
            fields=[
                ('id_caja', models.AutoField(primary_key=True, serialize=False)),
                ('fecha_apertura', models.DateTimeField(blank=True, null=True)),
                ('fecha_cierre', models.DateTimeField(blank=True, null=True)),
                ('monto_inicial', models.DecimalField(decimal_places=2, max_digits=10)),
                ('monto_recaudado', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('monto_final', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('empleado', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.empleado')),
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
                ('fecha_venta', models.DateField()),
                ('hs_venta', models.TimeField()),
                ('monto_inicial', models.DecimalField(decimal_places=2, max_digits=10)),
                ('estado_venta', models.BooleanField()),
                ('id_caja', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.caja')),
            ],
        ),
        migrations.CreateModel(
            name='DetalleVenta',
            fields=[
                ('id_detalle_venta', models.AutoField(primary_key=True, serialize=False)),
                ('metodo_pago', models.CharField(max_length=255)),
                ('monto_subtotal', models.DecimalField(decimal_places=2, max_digits=10)),
                ('nota_adicional', models.TextField()),
                ('id_cliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.cliente')),
                ('id_turno', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.turno')),
                ('id_venta', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='AppAnaSol.venta')),
            ],
        ),
    ]
