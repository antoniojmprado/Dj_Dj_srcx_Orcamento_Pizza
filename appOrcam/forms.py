from django import forms                 
from django.core.exceptions import ValidationError
from django.utils import timezone


class OrcamentoForm(forms.ModelForm):

    class Meta:  # Em vez de passar a classe diretamente, você pode importar aqui dentro
        from .models import Orcamento
        model = Orcamento
        fields = "__all__"

