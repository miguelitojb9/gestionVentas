"""settings URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView

from app.ventas.admin import LocalAdmin
from app.ventas.views import buscar_productos, eliminar_venta, \
    actualizar_venta_diaria, eliminar_ventas, eliminar_asistencia, actualizar_trabajador, eliminar_trabajador, \
    DescargarExcelVentasDiariasView, DescargarDatosExcelNomina
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', RedirectView.as_view(url='/admin/ventas')),
    path('admin/', admin.site.urls),
    path('', include('app.ventas.urls')),

    path('descargar_excel/', DescargarExcelVentasDiariasView.as_view(), name='descargar_excel'),
    path('descargar_datos_excel_nomina/', DescargarDatosExcelNomina.as_view(), name='descargar_datos_excel_nomina'),
    path('buscar_productos/', buscar_productos, name='buscar_productos'),
    path('actualizar_venta_diaria/', actualizar_venta_diaria, name='actualizar_venta_diaria'),

    path('eliminar_venta/', eliminar_venta, name='eliminar_venta'),

    path('eliminar_ventas/', eliminar_ventas, name='eliminar_ventas'),

    path('eliminar_asistencia/', eliminar_asistencia, name='eliminar_asistencia'),

    path('eliminar_trabajador/', eliminar_trabajador, name='eliminar_trabajador'),
    path('actualizar_trabajador/', actualizar_trabajador, name='actualizar_trabajador'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
