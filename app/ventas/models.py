from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Max
from django.utils.translation import gettext_lazy as _
from datetime import datetime


class Local(models.Model):
    nombre = models.CharField(max_length=255)

    def __str__(self):
        return self.nombre


class Trabajador(models.Model):
    nombre = models.CharField(max_length=50)
    salario_basico = models.DecimalField(max_digits=10, decimal_places=2)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)


    def __str__(self):
        return self.nombre


class Nomina(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    salario_devengado = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateField(default=timezone.now)
    total_nomina = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Nomina de {self.trabajador.nombre} - {self.fecha.strftime("%b %Y")}'


class Asistencia(models.Model):
    trabajador = models.ForeignKey(Trabajador, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    local = models.ForeignKey(Local, on_delete=models.CASCADE)

    def clean(self):
        if self.trabajador.local != self.local:
            raise ValidationError('El trabajador seleccionado no pertenece a este local')
        # validar que no exista otra venta diaria con el mismo producto, fecha y local
        asistencia_existente = Asistencia.objects.filter(local=self.local, trabajador=self.trabajador, fecha=self.fecha).first()
        if asistencia_existente and asistencia_existente.pk != self.pk:
            raise ValidationError('Ya existe una asistencia diaria para este producto, fecha y local')

    def __str__(self):
        return f'Asistencia de {self.trabajador.nombre} - {self.fecha.strftime("%d %b %Y")}'


class Producto(models.Model):
    nombre = models.CharField(max_length=255)
    categoria = models.CharField(max_length=255, choices=[
        ('1', 'Elaborados'),
        ('2', 'No Elaborados'),

    ], default='1')
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return self.nombre


class PrecioVenta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['producto'], condition=models.Q(activo=True), name='unique_active_price'),
        ]

    def __str__(self):
        return f"{self.producto} - {self.precio}"

    def clean(self):
        super().clean()
        # if PrecioVenta.objects.filter(producto=self.producto, activo=True).exists():
        #     raise ValidationError('No se encontró ningún precio de venta activo para el producto actual')

    def save(self, *args, **kwargs):
        if self.activo:
            PrecioVenta.objects.filter(producto=self.producto, activo=True).exclude(id=self.id).update(activo=False)
        super().save(*args, **kwargs)


class GastosDiario(models.Model):
    local = models.ForeignKey(Local, on_delete=models.PROTECT)
    fecha = models.DateField(default=timezone.now)  # Agregar un campo de fecha
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    concepto = models.CharField(max_length=255, choices=[
        ('1', 'Electricidad'),
        ('2', 'Arrendamiento'),
        ('3', 'Otros'),

    ], default='3')
    descripcion = models.TextField(max_length=255,null=True,blank=True )

    def clean(self):
        super().clean()
        # Validar que en el mes solo puede existir un gasto por concepto de electricidad
        if self.concepto == '1':
            electricidad_gastos = GastosDiario.objects.filter(
                local=self.local,
                fecha__year=self.fecha.year,
                fecha__month=self.fecha.month,
                concepto='1'
            )
            if self.pk:
                electricidad_gastos = electricidad_gastos.exclude(pk=self.pk)
            if electricidad_gastos.exists():
                raise ValidationError(_('Ya existe un gasto por concepto de electricidad en este mes.'))

        # Validar que el campo descripción no sea nulo si el concepto es de otros
        if self.concepto == '3' and not self.descripcion:
            raise ValidationError(_('Debe proporcionar una descripción para el gasto de "Otros".'))

        # Validar que el concepto de arrendamiento sea quincenal
        if self.concepto == '2':
            if self.fecha.day <= 15:
                fecha_inicio_quincena = datetime(self.fecha.year, self.fecha.month, 1)
                fecha_fin_quincena = datetime(self.fecha.year, self.fecha.month, 15)
            else:
                fecha_inicio_quincena = datetime(self.fecha.year, self.fecha.month, 16)
                fecha_fin_quincena = datetime(self.fecha.year, self.fecha.month, self.fecha.day)

            gastos_arrendamiento = GastosDiario.objects.filter(
                local=self.local,
                concepto='2',
                fecha__range=[fecha_inicio_quincena, fecha_fin_quincena]
            )

            if gastos_arrendamiento.exists():
                raise ValidationError(_('Solo se puede registrar un gasto quincenal por concepto de {}.'.format(
                    self.get_concepto_display())))

            # Validar que el monto sea mayor que cero
            if self.monto <= 0:
                raise ValidationError(_('El monto debe ser mayor que cero en este local.'))



class VentaDiaria(models.Model):
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)  # Agregar un campo de fecha
    cantidad_entrada = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_disponible = models.IntegerField(default=0)
    cantidad_merma = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad_venta = models.IntegerField(default=0)
    precio_costo_producto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    importe_precio_costo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    precio_venta_producto = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    importe_precio_venta = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.local} - {self.producto}"


    def clean(self):
        # validar que no exista otra venta diaria con el mismo producto, fecha y local
        venta_existente = VentaDiaria.objects.filter(local=self.local, producto=self.producto, fecha=self.fecha).first()
        if venta_existente and venta_existente.pk != self.pk:
            raise ValidationError('Ya existe una venta diaria para este producto, fecha y local')

    def actualizar_valores(self):
        venta_anterior = VentaDiaria.objects.filter(local=self.local, producto=self.producto,
                                                    fecha__lt=self.fecha).order_by('-fecha').first()
        if venta_anterior:
            self.cantidad_disponible = venta_anterior.cantidad_disponible + self.cantidad_entrada
        else:
            self.cantidad_disponible = self.cantidad_entrada

        self.precio_costo_producto = self.producto.precio
        self.importe_precio_costo = Decimal(self.cantidad_venta) * self.precio_costo_producto
        precio_venta = PrecioVenta.objects.filter(producto=self.producto, activo=True).last()
        self.precio_venta_producto = precio_venta.precio if precio_venta else 0
        self.importe_precio_venta = Decimal(self.cantidad_venta) * self.precio_venta_producto
        self.cantidad_disponible -= (Decimal(self.cantidad_venta) + self.cantidad_merma)

    def actualizar_cantidad_venta(self, nueva_cantidad_venta):
        self.cantidad_venta = nueva_cantidad_venta
        self.actualizar_valores()
        self.save()

    def save(self, *args, **kwargs):
        # calcular los valores de la venta diaria
        venta_anterior = VentaDiaria.objects.filter(local=self.local, producto=self.producto,
                                                    fecha__lt=self.fecha).order_by('-fecha').first()
        if venta_anterior:
            self.cantidad_disponible = venta_anterior.cantidad_disponible + self.cantidad_entrada
        else:
            self.cantidad_disponible = self.cantidad_entrada

        self.precio_costo_producto = self.producto.precio
        self.importe_precio_costo = Decimal(self.cantidad_venta) * self.precio_costo_producto
        precio_venta = PrecioVenta.objects.filter(producto=self.producto, activo=True).last()
        self.precio_venta_producto = precio_venta.precio if precio_venta else 0
        self.importe_precio_venta = Decimal(self.cantidad_venta) * self.precio_venta_producto
        self.cantidad_disponible -= (Decimal(self.cantidad_venta) + Decimal(self.cantidad_merma))

        # llamar al método save del padre para guardar el objeto
        super(VentaDiaria, self).save(*args, **kwargs)

    class Meta:
        ordering = ['fecha']
