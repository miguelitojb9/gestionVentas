from django.contrib import admin
from django.core.paginator import Paginator
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe

from app.ventas.forms import VentaDiariaForm, AsistenciaDiariaForm, TrabajadorForm
from app.ventas.models import Local, Producto, PrecioVenta, VentaDiaria, Trabajador, Nomina, Asistencia
from django.db.models import Max
from django.utils import timezone
from django.db import models
from django.shortcuts import render

from datetime import datetime, timedelta
from django.db.models import ExpressionWrapper, Sum, F, FloatField
from django.db.models.functions import Coalesce


class VentaDiariaInline(admin.TabularInline):
    model = VentaDiaria
    extra = 1
    can_delete = True
    show_change_link = True
    form = VentaDiariaForm


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    # ... list_display, search_fields, inlines ...
    list_display = ('nombre', 'ventas_por_local', 'trabajador_por_local', 'asistencia_por_local', 'nomina_por_local')
    search_fields = ('nombre',)

    # date_hierarchy = 'fecha'  # Agregar el filtro de fecha
    # inlines = [VentaDiariaInline]  # Agregar la funcionalidad de edición en línea

    def ventas_por_local(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:ventas_por_local", args=[obj.id]),
            'Registrar ventas diarias'
        ))

    def asistencia_por_local(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:asistencia_por_local", args=[obj.id]),
            'Registrar asistencia diarias'
        ))

    def trabajador_por_local(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:trabajador_por_local", args=[obj.id]),
            'Registrar Trabajador'
        ))

    def nomina_por_local(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:nomina_por_local", args=[obj.id]),
            'Calcular Nomina'
        ))

    ventas_por_local.short_description = 'Ventas diarias'
    asistencia_por_local.short_description = 'Asistencia diarias'
    nomina_por_local.short_description = 'Nomina diarias'

    def ventas_por_local_view(self, request, local_id):
        local = get_object_or_404(Local, id=local_id)
        ventas = VentaDiaria.objects.filter(local=local)

        # Obtener una lista de fechas distintas en orden descendente
        fechas = ventas.dates('fecha', 'day', order='DESC')

        # Crear un diccionario de ventas por fecha para cada fecha distinta
        ventas_por_fecha = {}
        ganacia_total = 0
        for fecha in fechas:
            # Filtramos las ventas por fecha
            ventas_fecha = ventas.filter(fecha=fecha)
            # Total Importe por ventas
            total_importe_venta = sum(s.importe_precio_venta for s in ventas_fecha)
            # Total importe por precio costo
            total_importe_costo = sum(s.importe_precio_costo for s in ventas_fecha)
            # Ganancia en el dia
            ganancia_dia = total_importe_venta - total_importe_costo
            # Creamos la tupla con el queryset y los otros valores
            ventas_por_fecha[fecha] = (ventas_fecha, total_importe_venta, total_importe_costo, ganancia_dia)

            ganacia_total += ganancia_dia

        if request.method == 'POST':
            form = VentaDiariaForm(request.POST)
            if form.is_valid():
                venta = form.save(commit=False)
                venta.local = local
                venta.save()
                fecha = venta.fecha.strftime('%Y-%m-%d')
                return redirect('admin:ventas_por_local', local_id=local_id)
        else:
            ultima_fecha = VentaDiaria.objects.filter(local=local).aggregate(Max('fecha'))[
                'fecha__max']
            form = VentaDiariaForm(initial={'local': local, 'fecha': ultima_fecha or timezone.now()})

        form.fields['local'].widget.attrs['hidden'] = True  # Ocultar el campo 'local'

        context = {
            'local': local,
            'local_id': local_id,
            'ventas_por_fecha': ventas_por_fecha,
            'ganacia_total': ganacia_total,
            'form': form
        }

        return render(request, 'admin/ventas_por_local.html', context)

    def asistencia_por_local_view(self, request, local_id):
        local = get_object_or_404(Local, id=local_id)
        asistencia = Asistencia.objects.filter(local=local)

        # Obtener una lista de fechas distintas en orden descendente
        fechas = asistencia.dates('fecha', 'day', order='DESC')

        # Crear un diccionario de ventas por fecha para cada fecha distinta
        asistencia_por_fecha = {}
        ganacia_total = 0
        for fecha in fechas:
            # Filtramos las asistencia por fecha
            asistencia_fecha = asistencia.filter(fecha=fecha)
            # Creamos la tupla con el queryset y los otros valores
            cant_trabajadores_fecha = Asistencia.objects.filter(local=local, fecha=fecha).count()
            asistencia_por_fecha[fecha] = (asistencia_fecha, cant_trabajadores_fecha)

        if request.method == 'POST':
            form = AsistenciaDiariaForm(request.POST)
            if form.is_valid():
                asis = form.save(commit=False)
                asis.local = local
                asis.save()
                return redirect('admin:asistencia_por_local', local_id=local_id)
        else:
            ultima_fecha = Asistencia.objects.filter(local=local).aggregate(Max('fecha'))[
                'fecha__max']
            form = AsistenciaDiariaForm(initial={'local': local, 'fecha': ultima_fecha or timezone.now()})

        form.fields['local'].widget.attrs['hidden'] = True  # Ocultar el campo 'local'
        form.fields['local'].label = False  # Ocultar el label del campo 'local'
        form.fields['fecha'].label = False  # Ocultar el label del campo 'local'

        cant_trabajadores = Trabajador.objects.filter(local=local).count()

        context = {
            'local': local,
            'local_id': local_id,
            'form': form,
            'asistencia_por_fecha': asistencia_por_fecha,
            'cant_trabajadores': cant_trabajadores,

            # 'page_obj': page_obj, 'paginator': paginator
        }

        return render(request, 'admin/asistencia_por_local.html', context)

    def trabajador_por_local_view(self, request, local_id):
        local = get_object_or_404(Local, id=local_id)
        trabajador = Trabajador.objects.filter(local=local)

        if request.method == 'POST':
            form = TrabajadorForm(request.POST)
            if form.is_valid():
                form.instance.local = local
                form.save()
                return redirect('admin:trabajador_por_local', local_id=local_id)
        else:
            form = TrabajadorForm(initial={'local': local})

        form.fields['local'].widget.attrs['hidden'] = True  # Ocultar el campo 'local'
        form.fields['local'].label = False  # Ocultar el label del campo 'local'

        cant_trabajadores = Trabajador.objects.filter(local=local).count()

        context = {
            'local': local,
            'local_id': local_id,
            'form': form,
            'trabajadors': trabajador,
            'cant_trabajadores': cant_trabajadores,

            # 'page_obj': page_obj, 'paginator': paginator
        }

        return render(request, 'admin/trabajador_por_local.html', context)

    def nomina_por_local_view(self, request, local_id):
        local = get_object_or_404(Local, id=local_id)
        # obtener las fechas de los últimos 7 días
        hoy = datetime.today().date()
        # fechas = [hoy - timedelta(days=i) for i in range(7)]
        ventas = VentaDiaria.objects.filter(local=local)
        fechas = ventas.dates('fecha', 'day', order='DESC')

        # recopilar los datos de ventas diarias, asistencias, y totales de importe para cada fecha y local
        datos_por_fecha = {}
        for fecha in fechas:
            datos_por_fecha[fecha] = {}
            venta_diaria = VentaDiaria.objects.filter(fecha=fecha, local=local).select_related('local', 'producto')
            total_importe_ventas = venta_diaria.aggregate(total_ventas=
                                                          Sum(F('cantidad_venta') * F('precio_venta_producto')))[
                'total_ventas']
            total_importe_costo = venta_diaria.aggregate(total_costo=
                                                         Sum(F('cantidad_venta') * F('precio_costo_producto')))[
                'total_costo']
            ganancia = (total_importe_ventas - total_importe_costo)
            if ganancia > 15000:
                ganancia = 0.06 * ganancia
            else:
                ganancia = 0
            asistencias = Asistencia.objects.filter(fecha=fecha, local=local).select_related('trabajador').annotate(
                salario_total=ExpressionWrapper(F('trabajador__salario_basico') + ganancia,
                                                output_field=FloatField()),

            )
            trabajadores_salarios = Asistencia.objects.filter(local=local).values('trabajador__nombre').annotate(
                salario_total=ExpressionWrapper(F('trabajador__salario_basico') + ganancia, output_field=FloatField())
            ).annotate(
                total_salario=Coalesce(Sum('salario_total'), 0, output_field=FloatField())
            ).values('trabajador__nombre', 'total_salario')

            # Creamos la tupla con el queryset y los otros valores
            # ventas_por_fecha[fecha] = (ventas_fecha, total_importe_venta, total_importe_costo, ganancia_dia)
            datos_por_fecha[fecha] = (venta_diaria, asistencias, (total_importe_ventas - total_importe_costo))
            cant_trabajadores = Trabajador.objects.filter(local=local).count()

            # enviar los datos recopilados al template
            context = {
                'fechas': fechas,
                'local': local,
                'datos_por_fecha': datos_por_fecha,
                'cant_trabajadores': cant_trabajadores,
                'trabajadores_salarios': trabajadores_salarios,
            }

        return render(request, 'admin/nomina_por_local.html', context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('local/<int:local_id>/ventas/', self.admin_site.admin_view(self.ventas_por_local_view),
                 name='ventas_por_local'),
            path('local/<int:local_id>/asistencia/', self.admin_site.admin_view(self.asistencia_por_local_view),
                 name='asistencia_por_local'),

            path('local/<int:local_id>/trabajador/', self.admin_site.admin_view(self.trabajador_por_local_view),
                 name='trabajador_por_local'),

            path('local/<int:local_id>/nomina/', self.admin_site.admin_view(self.nomina_por_local_view),
                 name='nomina_por_local'),
        ]
        return my_urls + urls


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('precio', 'nombre')


@admin.register(PrecioVenta)
class PrecioVentaAdmin(admin.ModelAdmin):
    list_display = ('producto', 'precio', 'activo')


# @admin.register(VentaDiaria)
class VentaDiariaAdmin(admin.ModelAdmin):
    form = VentaDiariaForm
    list_display = ('local', 'producto', 'fecha', 'cantidad_venta', 'importe_precio_venta', 'importe_precio_costo')
    list_filter = ('local', 'fecha', 'producto')
    date_hierarchy = 'fecha'
    ordering = ('-fecha', 'local', 'producto')
    readonly_fields = (
        'precio_costo_producto', 'importe_precio_costo', 'precio_venta_producto', 'importe_precio_venta',
        'local_nombre')

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.select_related('local', 'producto')
        return qs

    def local_nombre(self, obj):
        return obj.local.nombre

    local_nombre.short_description = 'Local'
    local_nombre.admin_order_field = 'local__nombre'

    def get_total_importe_venta(self, queryset):
        return queryset.aggregate(total_importe_venta=Sum('importe_precio_venta'))['total_importe_venta']

    def get_total_importe_costo(self, queryset):
        return queryset.aggregate(total_importe_costo=Sum('importe_precio_costo'))['total_importe_costo']


# @admin.register(Trabajador)
class TrabajadorAdmin(admin.ModelAdmin):
    list_display = ['nombre', 'salario_basico', ]
    list_filter = ['local']


# @admin.register(Nomina)
class NominaAdmin(admin.ModelAdmin):
    list_display = ['trabajador', 'salario_devengado', 'fecha', 'total_nomina', ]


# @admin.register(Asistencia)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['trabajador', 'fecha']
    list_filter = ['local', 'fecha']
