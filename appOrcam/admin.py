import django
from django.urls import reverse
from django.contrib import admin
from django.utils.html import format_html
from appOrcam.models import ConfiguracaoRateio, Custo_frete, Custo_tinta, Orcamento, Chapa


@admin.register(Chapa)
class ChapaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'largura_cm', 'comprimento_cm',
                    'tipo_papelao', 'custo_m2', 'gramatura_kg_m2', 
                    'larg_apara_m', 'preco_apara_kg')
    
    list_editable = ('nome', 'largura_cm', 'comprimento_cm','tipo_papelao',
                     'custo_m2', 'gramatura_kg_m2', 'larg_apara_m', 'preco_apara_kg')
    search_fields = ('nome',)


@admin.register(ConfiguracaoRateio)
class ConfiguracaoRateioAdmin(admin.ModelAdmin):
    # Exibe as informações principais na lista
    list_display = ('maquina', 'percentual_producao', 'producao_un_hora')

    # Permite editar a velocidade diretamente na lista para ser mais rápido
    list_editable = ('producao_un_hora',)
    

@admin.register(Custo_tinta)
class Custo_tintaAdmin(admin.ModelAdmin):
    # Isso impede que você crie vários registros; você só edita um.
    def has_add_permission(self, request):
        return not Custo_tinta.objects.exists()
    

@admin.register(Custo_frete)
class Custo_freteAdmin(admin.ModelAdmin):
    # Isso impede que você crie vários registros; você só edita um.
    def has_add_permission(self, request):
        return not Custo_frete.objects.exists()


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):

    def imprimir_orcamento_btn(self, obj):
        # Gerar o link para a página de impressão do orçamento
        url = reverse('imprimir_orcamento', kwargs={'pk': obj.pk})
        return format_html('<a href="{}" target="_blank">Imprimir PDF</a>', url)
    
    
    # 1. Trava os campos para o formulário não sobrescrever o cálculo do Python
    readonly_fields = ('preco_final_unitario', 
                       'data_criacao', 'resumo_composicao', 'imprimir_orcamento_btn')  # Adicione o campo do botão aqui

    # 2. Configura o que aparece na 'vitrine' (lista de orçamentos)
    list_display = (
        'id',
        'cliente',
        'produto_nome',
        'quantidade',
        'unidades_chapa',
        'maquina_impressao',
        'preco_final_unitario',
        'perda_material_formatada',  # Usando sua função de formatação aqui
        'resumo_composicao',
        'imprimir_orcamento_btn',  # Botão para imprimir o orçamento em PDF
    )

    # 3. Mantém seus filtros e busca
    list_filter = ('maquina_impressao', 'data_criacao')
    search_fields = ('cliente', 'produto_nome')

    # 4. Sua função de formatação (mantida conforme seu código)
    def perda_material_formatada(self, obj):
        return f"R$ {obj.perda_material:.2f}"
    perda_material_formatada.short_description = 'Perda de Papelão'

    # 5. Organização visual do formulário de preenchimento
    fieldsets = (
        ('Dados do Cliente', {
            'fields': ('cliente', 'produto_nome', 'quantidade')
        }),
        ('Configuração de Produção', {
            'fields': ('chapa_projeto', 'chapa_utilizada', 'unidades_chapa', 'maquina_impressao', 'maquina_corte', 'margem_real')
        }),
        ('Valor do frete por unidade ("Frete por Unidade" no calculador de Fretes)', {
            'fields': ('custo_frete_unitario',)
        }),
        ('Resultados (Calculados Automaticamente)', {
            'fields': ('preco_final_unitario', 'perda_material', 'resumo_composicao')
        }),
    )

    list_filter = ('maquina_impressao', 'data_criacao')
    search_fields = ('cliente', 'produto_nome')

    def perda_material_formatada(self, obj):
        return f"R$ {obj.perda_material:.2f}"
    perda_material_formatada.short_description = 'Perda de Papelão'
    
         