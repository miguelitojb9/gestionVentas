from django import forms
from app.ventas.models import VentaDiaria, Asistencia, Trabajador, Local, GastosDiario
from django.core.exceptions import ValidationError


class VentaDiariaForm(forms.ModelForm):
    class Meta:
        model = VentaDiaria
        fields = ('local','producto', 'cantidad_entrada', 'cantidad_merma', 'fecha', 'cantidad_venta',)

        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'producto': forms.Select(attrs={'class': 'form-control'}),
            'cantidad': forms.NumberInput(attrs={'min': 1}),
            'precio_venta': forms.NumberInput(attrs={'min': 0}),
            'precio_costo': forms.NumberInput(attrs={'min': 0}),
        }


class GastosDiariaForm(forms.ModelForm):
    class Meta:
        model = GastosDiario
        fields = ('local', 'fecha', 'monto', 'concepto', 'descripcion',)

        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
            'concepto': forms.Select(attrs={'class': 'form-control'}),

        }


class AsistenciaDiariaForm(forms.ModelForm):
    class Meta:
        model = Asistencia
        fields = ['trabajador', 'fecha', 'local']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Agregar la clase de Bootstrap al campo de selección de trabajador
        self.fields['trabajador'].widget.attrs.update({'class': 'form-control col-3 '})
        if 'initial' in kwargs:
            local = kwargs['initial'].get('local')
            try:
                local_id = local.id
                self.fields['trabajador'].queryset = Trabajador.objects.filter(local_id=local_id)
            except (ValueError, TypeError):
                pass
        elif self.instance.pk:
            self.fields['trabajador'].queryset = self.instance.local.trabajadores_set.order_by('nombre')
    #
    # def clean(self):
    #     cleaned_data = super().clean()
    #     trabajador = cleaned_data.get('trabajador')
    #     local = cleaned_data.get('local')
    #     if trabajador and local:
    #         if trabajador.local != local:
    #             raise ValidationError('El trabajador seleccionado no pertenece a este local')
    #


class TrabajadorForm(forms.ModelForm):
    class Meta:
        model = Trabajador
        fields = ['nombre', 'salario_basico', 'local']

