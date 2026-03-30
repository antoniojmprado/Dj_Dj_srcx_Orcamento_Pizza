from django import forms
from django.apps import apps
from .models import Orcamento


class OrcamentoForm(forms.ModelForm):
    class Meta:
        model = Orcamento
        fields = [
            'cliente', 'produto_nome', 'quantidade',
            'unidades_chapa', 'maquina_impressao', 'maquina_corte',
            'chapa_projeto', 'chapa_utilizada',
            'margem_real','custo_frete_unitario'
        ]
        widgets = {
            # Números Inteiros (Quantidade e Unidades por Chapa)
            'quantidade': forms.TextInput(attrs={'class': 'mask-inteiro', 'placeholder': '0'}),
            'unidades_chapa': forms.TextInput(attrs={'class': 'mask-inteiro', 'placeholder': '1'}),

            # Números Decimais (Margem e Frete)
            'margem_real': forms.TextInput(attrs={'class': 'mask-decimal', 'placeholder': '0,00'}),
            'custo_frete_unitario': forms.TextInput(attrs={'class': 'mask-money', 'placeholder': '0,00'}),
        }

    def __init__(self, *args, **kwargs):
        super(OrcamentoForm, self).__init__(*args, **kwargs)

        # Filtro de Segurança: Só mostra máquinas que imprimem (1 no MySQL)
        try:
            # Pegamos o modelo do appOEE de forma dinâmica
            Maquina = apps.get_model('appOEE', 'Maquina')

            # Aplicamos o filtro booleano (True = 1)
            # Isso vai tirar Century e Boca de Sapo da lista de impressão automaticamente
            self.fields['maquina_impressao'].queryset = Maquina.objects.filter(impressora=True)
            self.fields['maquina_corte'].queryset = Maquina.objects.filter(corte=True)
        except Exception:
            # Se algo falhar na inicialização, o formulário não trava o site
            pass
