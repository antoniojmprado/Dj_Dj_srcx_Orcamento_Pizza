from django.contrib import admin

from appOrcam.models import ConfiguracaoRateio, Orcamento, Chapa, ParametrosOrcamento


@admin.register(Chapa)
class ChapaAdmin(admin.ModelAdmin):
    list_display = ('id', 'largura_cm', 'comprimento_cm', 'custo_m2')
    search_fields = ('nome',)


@admin.register(ConfiguracaoRateio)
class ConfiguracaoRateioAdmin(admin.ModelAdmin):
    # Exibe as informações principais na lista
    list_display = ('maquina', 'percentual_producao', 'producao_un_hora')

    # Permite editar a velocidade diretamente na lista para ser mais rápido
    list_editable = ('producao_un_hora',)
    

@admin.register(ParametrosOrcamento)
class ParametrosOrcamentoAdmin(admin.ModelAdmin):
    # Isso impede que você crie vários registros; você só edita um.
    def has_add_permission(self, request):
        return not ParametrosOrcamento.objects.exists()

@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    # 1. Trava os campos para o formulário não sobrescrever o cálculo do Python
    readonly_fields = ('preco_final_unitario',
                       'perda_material', 'data_criacao')

    # 2. Configura o que aparece na 'vitrine' (lista de orçamentos)
    list_display = (
        'cliente',
        'produto_nome',
        'quantidade',
        'maquina_impressao',
        'preco_final_unitario',
        'perda_material_formatada'  # Usando sua função de formatação aqui
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
            'fields': ('chapa_ideal', 'chapa_utilizada', 'maquina_impressao', 'maquina_corte', 'margem_real')
        }),
        ('Resultados (Calculados Automaticamente)', {
            'fields': ('preco_final_unitario', 'perda_material')
        }),
    )

    list_filter = ('maquina_impressao', 'data_criacao')
    search_fields = ('cliente', 'produto_nome')

    def perda_material_formatada(self, obj):
        return f"R$ {obj.perda_material:.2f}"
    perda_material_formatada.short_description = 'Perda de Papelão'
