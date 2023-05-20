from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from decimal import Decimal
from django.db.models import Max



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
    fecha = models.DateField(default=timezone.now())
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


class VentaDiaria(models.Model):
    local = models.ForeignKey(Local, on_delete=models.CASCADE)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now())  # Agregar un campo de fecha
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

    def get_total_importe_venta(self, queryset):
        return sum(s.importe_precio_venta for s in queryset)

    def get_total_importe_costo(self, queryset):
        return sum(s.importe_precio_costo for s in queryset)
