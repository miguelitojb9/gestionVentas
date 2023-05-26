# Generated by Django 4.2.1 on 2023-05-24 03:32

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Local',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Producto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=255)),
                ('categoria', models.CharField(choices=[('1', 'Elaborados'), ('2', 'No Elaborados')], default='1', max_length=255)),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='VentaDiaria',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('cantidad_entrada', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cantidad_disponible', models.IntegerField(default=0)),
                ('cantidad_merma', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('cantidad_venta', models.IntegerField(default=0)),
                ('precio_costo_producto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('importe_precio_costo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('precio_venta_producto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('importe_precio_venta', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.local')),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.producto')),
            ],
            options={
                'ordering': ['fecha'],
            },
        ),
        migrations.CreateModel(
            name='Trabajador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=50)),
                ('salario_basico', models.DecimalField(decimal_places=2, max_digits=10)),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.local')),
            ],
        ),
        migrations.CreateModel(
            name='PrecioVenta',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('precio', models.DecimalField(decimal_places=2, max_digits=10)),
                ('activo', models.BooleanField(default=True)),
                ('producto', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.producto')),
            ],
        ),
        migrations.CreateModel(
            name='Nomina',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('salario_devengado', models.DecimalField(decimal_places=2, max_digits=10)),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('total_nomina', models.DecimalField(decimal_places=2, max_digits=10)),
                ('trabajador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.trabajador')),
            ],
        ),
        migrations.CreateModel(
            name='GastosDiario',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('monto', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('concepto', models.CharField(choices=[('1', 'Electricidad'), ('2', 'Arrendamiento'), ('3', 'Otros')], default='3', max_length=255)),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ventas.local')),
            ],
        ),
        migrations.CreateModel(
            name='Asistencia',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fecha', models.DateField(default=django.utils.timezone.now)),
                ('local', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.local')),
                ('trabajador', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='ventas.trabajador')),
            ],
        ),
        migrations.AddConstraint(
            model_name='precioventa',
            constraint=models.UniqueConstraint(condition=models.Q(('activo', True)), fields=('producto',), name='unique_active_price'),
        ),
    ]
