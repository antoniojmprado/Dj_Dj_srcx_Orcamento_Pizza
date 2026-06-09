from django import forms
from django.core.exceptions import ValidationError
from .models import Reclamacoes
from .models import SemanAno
from .widgets import MultipleFileInput
from .utils import capitalize_pt
from datetime import date



class MultipleFileField(forms.FileField):
    widget = MultipleFileInput

    def clean(self, data, initial=None):
        if not data:
            return []
        if isinstance(data, (list, tuple)):
            return data
        return [data]


class ReclamacoesForm(forms.ModelForm):
    arquivos = MultipleFileField(
        required=False,
        help_text="Você pode selecionar vários arquivos"
    )

    class Meta:
        model = Reclamacoes
        fields = [
            'cliente', 'descricao', 'id_defeito',
            'vendedora', 'id_produto', 'id_tecnol',
            'id_empresa', 'comentarios'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'
            # field.widget.attrs['autocomplete'] = 'off'

    def clean_nome(self):
        cliente = self.cleaned_data['cliente']
        return capitalize_pt(cliente)
    
    
class SemanAnoForm(forms.ModelForm):

    class Meta:
        model = SemanAno
        fields = ['ano', 'semana',]



    
