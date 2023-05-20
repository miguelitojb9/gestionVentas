from django.urls import path
from .views import Home, ventas_diarias

urlpatterns = [

    path('', Home.as_view(), name='descargar_excel'),
    path('ventas_diarias/', ventas_diarias, name='ventas_diarias'),

]
