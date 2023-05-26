from django.contrib import admin
from django.shortcuts import get_object_or_404, redirect
from django.urls import path, reverse
from django.utils.safestring import mark_safe
from app.ventas.forms import VentaDiariaForm, AsistenciaDiariaForm, TrabajadorForm, GastosDiariaForm
from app.ventas.models import Local, Producto, PrecioVenta, VentaDiaria, Trabajador, Asistencia, GastosDiario
from django.db.models import Max
from django.utils import timezone
from django.shortcuts import render

import datetime
from decimal import Decimal
from django.db.models import ExpressionWrapper, F, FloatField, Sum
from django.core.paginator import Paginator


class VentaDiariaInline(admin.TabularInline):
    model = VentaDiaria
    extra = 1
    can_delete = True
    show_change_link = True
    form = VentaDiariaForm


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    # ... list_display, search_fields, inlines ...
    list_display = ('nombre', 'ventas_por_local', 'gastos_por_local', 'asistencia_por_local', 'trabajador_por_local',
                    'nomina_por_local')
    search_fields = ('nombre',)

    # date_hierarchy = 'fecha'  # Agregar el filtro de fecha
    # inlines = [VentaDiariaInline]  # Agregar la funcionalidad de edición en línea

    def ventas_por_local(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:ventas_por_local", args=[obj.id]),
            'Registrar ventas diarias'
        ))

    def gastos_por_local(self, obj):
        return mark_safe('<a href="{}">{}</a>'.format(
            reverse("admin:gastos_por_local", args=[obj.id]),
            'Registrar gastos diarios'
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
    gastos_por_local.short_description = 'Gastos diarios'
    asistencia_por_local.short_description = 'Asistencia diarias'
    nomina_por_local.short_description = 'Nomina diarias'

    def ventas_por_local_view(self, request, local_id):
        local = get_object_or_404(Local, id=local_id)
        # Obtener la fecha actual
        fecha_actual = datetime.datetime.now()

        # Determinar si estamos en la primera o segunda quincena
        if fecha_actual.day <= 15:
            # Estamos en la primera quincena
            fecha_inicio_quincena = datetime.datetime(fecha_actual.year, fecha_actual.month, 1)
            fecha_fin_quincena = datetime.datetime(fecha_actual.year, fecha_actual.month, 15)
        else:
            # Estamos en la segunda quincena
            ultimo_dia_mes = 31 \
                if fecha_actual.month in [1, 3, 5, 7, 8, 10, 12] else 30 \
                if fecha_actual.month in [4, 6, 9, 11] else 29 \
                if (fecha_actual.year % 4 == 0 and fecha_actual.year % 100 != 0) or fecha_actual.year % 400 == 0 \
                else 28

            fecha_inicio_quincena = datetime.datetime(fecha_actual.year, fecha_actual.month, 16)
            fecha_fin_quincena = datetime.datetime(fecha_actual.year, fecha_actual.month,
                                                   min(ultimo_dia_mes, 30))  # Obtener la fecha actual
        fecha_actual = datetime.datetime.now()
        ventas = VentaDiaria.objects.filter(local=local, fecha__gte=fecha_inicio_quincena,
                                            fecha__lte=fecha_fin_quincena)
        fechas = ventas.dates('fecha', 'day', order="DESC")
        # Crear un diccionario de ventas por fecha para cada fecha distinta
        ventas_por_fecha = {}
        ganacia_total = 0
        for fecha in fechas:
            # Filtramos las ventas por fecha
            ventas_fecha = ventas.filter(fecha=fecha).order_by('-fecha')
            # Total Importe por ventas
            total_importe_venta = sum(s.importe_precio_venta for s in ventas_fecha)
            # Total importe por precio costo
            total_importe_costo = sum(s.importe_precio_costo for s in ventas_fecha)
            # Ganancia en el dia
            ganancia_dia = total_importe_venta - total_importe_costo
            # Creamos la tupla con el queryset y los otros valores
            queryset = ventas_fecha.order_by('-fecha')
            paginator = Paginator(queryset, 10)
            page_number = request.GET.get('page')
            page_obj = paginator.get_page(page_number)
            ventas_por_fecha[fecha] = (page_obj, total_importe_venta, total_importe_costo, ganancia_dia)

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

    def gastos_por_local_view(self, request, local_id):
        local = get_object_or_404(Local, id=local_id)
        gastos = GastosDiario.objects.filter(local=local)

        # Obtener una lista de fechas distintas en orden descendente
        fechas = gastos.dates('fecha', 'day', order="DESC")

        # Crear un diccionario de ventas por fecha para cada fecha distinta
        ventas_por_fecha = {}
        gastos_total = 0

        for fecha in fechas:
            # Filtramos las ventas por fecha
            gastos_fecha = gastos.filter(fecha=fecha).order_by('fecha')
            gastos_electricidad = gastos_fecha.filter(concepto='1')
            gastos_arrendamiento = gastos_fecha.filter(concepto='2')
            gastos_otros = gastos_fecha.filter(concepto='3')
            total_gastos_electricidad = sum(s.monto for s in gastos_electricidad)
            total_gastos_arrendamiento = sum(s.monto for s in gastos_arrendamiento)
            total_gastos_otros = sum(s.monto for s in gastos_otros)
            total_gastos_dia = total_gastos_electricidad + total_gastos_arrendamiento + total_gastos_otros
            ventas_por_fecha[fecha] = (gastos_fecha, gastos_electricidad, total_gastos_electricidad,
                                       gastos_arrendamiento, total_gastos_arrendamiento, gastos_otros,
                                       total_gastos_otros, total_gastos_dia)
            gastos_total += total_gastos_electricidad + total_gastos_arrendamiento + total_gastos_otros

        if request.method == 'POST':
            form = GastosDiariaForm(request.POST)
            if form.is_valid():
                gasto = form.save(commit=False)
                gasto.local = local
                gasto.save()
                fecha = gasto.fecha.strftime('%Y-%m-%d')
                return redirect('admin:gastos_por_local', local_id=local_id)
        else:
            ultima_fecha = GastosDiario.objects.filter(local=local).aggregate(Max('fecha'))[
                'fecha__max']
            form = GastosDiariaForm(initial={'local': local, 'fecha': ultima_fecha or timezone.now()})
            form.fields['local'].label = False  # Ocultar el label del campo 'local'

        form.fields['local'].widget.attrs['hidden'] = True  # Ocultar el campo 'local'

        context = {
            'local': local,
            'local_id': local_id,
            'ventas_por_fecha': ventas_por_fecha,
            'gastos_total': gastos_total,
            'form': form
        }

        return render(request, 'admin/gastos_por_local.html', context)

    def asistencia_por_local_view(self, request, local_id):
        local = get_object_or_404(Local, id=local_id)
        asistencia = Asistencia.objects.filter(local=local)

        # Obtener una lista de fechas distintas en orden descendente
        fechas = asistencia.dates('fecha', 'day')

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
        from datetime import datetime
        local = get_object_or_404(Local, id=local_id)
        # obtener las fechas de los últimos 7 días
        hoy = datetime.today().date()
        # fechas = [hoy - timedelta(days=i) for i in range(7)]
        ventas = VentaDiaria.objects.filter(local=local)
        gastos = GastosDiario.objects.filter(local=local)
        fechas = ventas.dates('fecha', 'day', order='DESC')
        trabajadores = Trabajador.objects.filter(local=local)

        # recopilar los datos de ventas diarias, asistencias, y totales de importe para cada fecha y local
        datos_por_fecha = {}
        cant_trabajadores = {}
        trabajadores_salarios = []
        ganancia_fecha = {}
        asistencias = {}
        ganacia_total = 0
        gastos_total = 0
        for fecha in fechas:
            gastos_fecha = gastos.filter(fecha=fecha).order_by('fecha')
            total_gastos_diario = sum(s.monto for s in gastos_fecha)
            venta_diaria = VentaDiaria.objects.filter(fecha=fecha, local=local).select_related('local', 'producto')
            total_importe_ventas = venta_diaria.aggregate(total_ventas=
                                                          Sum(F('cantidad_venta') * F('precio_venta_producto')))[
                'total_ventas']
            importe_venta_elaborados = venta_diaria.filter(producto__categoria='1').aggregate(total_ventas=
                                                                                              Sum(F(
                                                                                                  'cantidad_venta') * F(
                                                                                                  'precio_venta_producto')))[
                'total_ventas']

            importe_venta_no_elaborados = venta_diaria.filter(producto__categoria='2').aggregate(total_ventas=
                                                                                                 Sum(F(
                                                                                                     'cantidad_venta') * F(
                                                                                                     'precio_venta_producto')))[
                'total_ventas']
            ganancia = total_importe_ventas
            # Filtramos las ventas por fecha
            ventas_fecha = ventas.filter(fecha=fecha)
            # Total importe por precio costo
            total_importe_costo = sum(s.importe_precio_costo for s in ventas_fecha)
            # Ganancia en el dia
            ganancia_dia = total_importe_ventas - total_importe_costo
            ganacia_total += ganancia_dia

            cantidad_trabajadores_dia = Asistencia.objects.filter(fecha=fecha, local=local).select_related(
                'trabajador').distinct().count()

            if ganancia > 15000:
                ganancia -= 15000

                if importe_venta_elaborados:
                    ganancia = (importe_venta_elaborados * Decimal(str('0.06'))) + (
                            (ganancia - importe_venta_elaborados) * Decimal(str('0.02')))
                else:
                    ganancia = ganancia * Decimal(str('0.02'))

                ganancia /= cantidad_trabajadores_dia

            else:
                ganancia = 0
            ganancia_fecha[fecha] = ganancia

            asistencias = Asistencia.objects.filter(fecha=fecha, local=local).select_related('trabajador').annotate(
                salario_devengado_diario=ExpressionWrapper(F('trabajador__salario_basico') + ganancia,
                                                           output_field=FloatField()),
            )

            # trabajadores_salarios

            # Gastos
            gastos_total += total_gastos_diario

            datos_por_fecha[fecha] = (
                venta_diaria, asistencias, ganancia, importe_venta_elaborados, importe_venta_no_elaborados)
            cant_trabajadores = Trabajador.objects.filter(local=local).count()

        a = asistencias
        # determinar remuneracion por trabajador
        salario_total_trabajadores = 0
        for trabajador in trabajadores:
            remuneracion_total = Decimal(str('0'))
            for _, d in datos_por_fecha.items():
                for a in d[1].filter(trabajador=trabajador):
                    remuneracion_total += Decimal(str(a.salario_devengado_diario))
            trabajadores_salarios.append({
                'nombre': trabajador.nombre,
                'total_devengado': remuneracion_total
            }, )
            salario_total_trabajadores += remuneracion_total

        ganancia_temporal = ganacia_total - (salario_total_trabajadores + gastos_total)

        admin_salario = ganancia_temporal * Decimal(str('0.23'))



        context = {
            'fechas': fechas,
            'local': local,
            'datos_por_fecha': datos_por_fecha,
            'cant_trabajadores': cant_trabajadores,
            'trabajadores_salarios': trabajadores_salarios,
            'salario_total_trabajadores': salario_total_trabajadores,
            'ganacia_total': ganacia_total,
            'gastos_total': gastos_total,
            'admin_salario': admin_salario,
            'ganancia_neta': ganancia_temporal - admin_salario,
        }

        return render(request, 'admin/nomina_por_local.html', context)

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('local/<int:local_id>/ventas/', self.admin_site.admin_view(self.ventas_por_local_view),
                 name='ventas_por_local'),
            path('local/<int:local_id>/gastos/', self.admin_site.admin_view(self.gastos_por_local_view),
                 name='gastos_por_local'),
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
    list_display = ('nombre', 'categoria', 'precio',)
    list_filter = ('categoria',)


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


@admin.register(Trabajador)
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


@admin.register(GastosDiario)
class AsistenciaAdmin(admin.ModelAdmin):
    list_display = ['local', 'fecha', 'concepto', 'monto']
