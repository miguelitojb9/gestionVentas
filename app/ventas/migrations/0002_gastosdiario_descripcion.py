# Generated by Django 4.2.1 on 2023-05-24 03:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ventas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='gastosdiario',
            name='descripcion',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
