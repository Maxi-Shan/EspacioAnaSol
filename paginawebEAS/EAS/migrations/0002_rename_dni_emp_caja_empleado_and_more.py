# Generated by Django 5.0.6 on 2024-09-04 14:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('EAS', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='caja',
            old_name='dni_emp',
            new_name='empleado',
        ),
        migrations.RenameField(
            model_name='caja',
            old_name='fecha_hora_cierre',
            new_name='fecha_apertura',
        ),
        migrations.RemoveField(
            model_name='caja',
            name='fecha_hora_apertura',
        ),
        migrations.AddField(
            model_name='caja',
            name='fecha_cierre',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='caja',
            name='monto_final',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='caja',
            name='monto_recaudado',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='contraseña',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='estado_empleado',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='imagen',
            field=models.ImageField(blank=True, null=True, upload_to='imagenes/'),
        ),
    ]