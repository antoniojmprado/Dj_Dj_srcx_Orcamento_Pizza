from django import forms
from django.apps import apps
from .models import Orcamento, Chapa  # Mudamos de ProdutoPadrao para Chapa


class OrcamentoForm(forms.ModelForm):

    selecionar_produto_padrao = forms.ModelChoiceField(
        queryset=Chapa.objects.all(),
        required=False,
        label="Características do Produto",
        empty_label="--- Selecione um produto para preencher automático ---",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Orcamento
        fields = [
            'selecionar_produto_padrao', 'cliente', 'produto_nome',
            'categoria_produto',  # ADICIONE ESTE CAMPO AQUI
            'quantidade', 'unidades_chapa', 'maquina_impressao',
            'maquina_corte', 'chapa_projeto', 'chapa_utilizada',
            'margem_real', 'custo_frete_unitario'
        ]

        widgets = {
            # Deixamos a categoria como um campo escondido (Hidden)
            # Assim o usuário não vê, mas o Django "carrega" o campo no save()
            'categoria_produto': forms.HiddenInput(),

            'quantidade': forms.TextInput(attrs={'class': 'mask-inteiro', 'placeholder': '0'}),
            'unidades_chapa': forms.TextInput(attrs={'class': 'mask-inteiro', 'placeholder': '1'}),
            'margem_real': forms.TextInput(attrs={'class': 'mask-decimal', 'placeholder': '0,00'}),
            'custo_frete_unitario': forms.TextInput(attrs={'class': 'mask-money', 'placeholder': '0,00'}),
        }

    def __init__(self, *args, **kwargs):
        super(OrcamentoForm, self).__init__(*args, **kwargs)

        # Lógica de filtros das máquinas (OEE)
        try:
            # Em vez de buscar o modelo de forma genérica, vamos garantir 
            # que o queryset aponte para o modelo correto
            from appOEE.models import Maquina  # Importe direto se possível
            
            self.fields['maquina_impressao'].queryset = Maquina.objects.filter(impressora=True)
            self.fields['maquina_corte'].queryset = Maquina.objects.filter(corte=True)
            # o campo 'chapa_projeto' pareça desabilitado e o usuário não consiga clicar nele, mas como ele tecnicamente não está com o atributo disabled, o navegador enviará o ID para o Django normalmente.
            self.fields['chapa_projeto'].widget.attrs['style'] = 'pointer-events: none; background-color: #e9ecef;'
            self.fields['chapa_projeto'].widget.attrs['tabindex'] = '-1'
        except Exception as e:
            # No deploy, é bom imprimir o erro no log para você saber o que houve
            print(f"Erro ao carregar máquinas no form: {e}")
