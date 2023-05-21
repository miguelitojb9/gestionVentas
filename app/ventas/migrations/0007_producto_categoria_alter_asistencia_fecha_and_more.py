# Generated by Django 4.0 on 2023-05-20 23:35

import datetime
from django.db import migrations, models
from django.utils.timezone import utc


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0006_alter_asistencia_fecha_alter_ventadiaria_fecha'),
    ]

    operations = [
        migrations.AddField(
            model_name='producto',
            name='categoria',
            field=models.CharField(choices=[(1, 'Elaborados'), (2, 'No Elaborados')], default='Elaborados', max_length=255),
        ),
        migrations.AlterField(
            model_name='asistencia',
            name='fecha',
            field=models.DateField(default=datetime.datetime(2023, 5, 20, 23, 35, 38, 656630, tzinfo=utc)),
        ),
        migrations.AlterField(
            model_name='ventadiaria',
            name='fecha',
            field=models.DateField(default=datetime.datetime(2023, 5, 20, 23, 35, 38, 657629, tzinfo=utc)),
        ),
    ]
