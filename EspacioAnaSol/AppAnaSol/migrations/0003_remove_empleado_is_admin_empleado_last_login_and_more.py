# Generated by Django 5.0.6 on 2024-09-18 16:58

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('AppAnaSol', '0002_empleado_is_admin_alter_empleado_contraseña_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='empleado',
            name='is_admin',
        ),
        migrations.AddField(
            model_name='empleado',
            name='last_login',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='empleado',
            name='estado_empleado',
            field=models.BooleanField(default=True),
        ),
    ]