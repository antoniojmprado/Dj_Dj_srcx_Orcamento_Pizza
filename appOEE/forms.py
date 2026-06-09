from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone


class OcorrenciaForm(forms.ModelForm):

    data_fim = forms.DateTimeField(
        required=False,
        input_formats=['%Y-%m-%dT%H:%M'],
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }
        )
    )

    class Meta:  # Em vez de passar a classe diretamente, você pode importar aqui dentro
        from .models import Ocorrencia
        model = Ocorrencia
        fields = [
            'data_fim',
            'empresa',
            'maquina',
            'motivo',
            'qualidade',
            'performance'
        ]


# class Calc_roceForm(forms.ModelForm):

#     class Meta:
#         model = Calc_roce
#         fields = [
#             'valor_ativos',
#             'deprec_ano_porc',
#             'manut_mes',
#             'qt_pessoas',
#             'salario_medio',
#             'encargos_porc',
#             'benef_porc',
#             'outros_porc',
#             'horas_turno',
#             'dia_mes',
#             'turnos_dia',
#             'mes_ano',
#             'disponibilidade',
#             'qualidade',
#             'performance',
#         ]