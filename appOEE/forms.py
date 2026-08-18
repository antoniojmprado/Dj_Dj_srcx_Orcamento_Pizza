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
