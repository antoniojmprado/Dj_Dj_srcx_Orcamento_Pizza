from django.contrib import admin
# Aqui ele busca as tabelas do seu models.py para fazer o vínculo
from .models import (
    TransportadoraFrete, 
    DetalhesFrete, 
    ItensFrete, 
    LogTransportadora, 
    TabelaFreteTransportadora
)

# 1. Painel TransportadoraFrete
@admin.register(TransportadoraFrete)
class TransportadoraFreteAdmin(admin.ModelAdmin):
    list_display = ('transportadora', 'estado_sigla', 'estado', 'prazo', 'frete_peso')
    list_filter = ('regiao', 'estado_sigla', 'transportadora')
    search_fields = ('transportadora', 'estado', 'estado_sigla')
    list_editable = ('prazo',)
    ordering = ('estado_sigla', 'transportadora')

# 2. Inline de Itens do Frete
class ItensFreteInline(admin.TabularInline):
    model = ItensFrete
    extra = 0
    readonly_fields = ('comprimento', 'largura', 'altura', 'qt_pacotes', 'qt_unidades', 'volume_item')
    can_delete = False

# 3. Painel DetalhesFrete
@admin.register(DetalhesFrete)
class DetalhesFreteAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'cidade', 'uf_coluna', 'peso_informado', 'data_hora')
    list_filter = ('uf_coluna', 'data_hora')
    search_fields = ('id', 'cliente', 'cidade')
    date_hierarchy = 'data_hora'
    inlines = [ItensFreteInline]
    readonly_fields = ('id', 'cliente', 'cep_destino', 'cidade', 'uf_coluna', 'peso_informado', 'valor_nf', 'data_hora', 'logradouro', 'bairro', 'total_pacotes', 'total_unidades', 'total_volume', 'icms')

# 4. Painel LogTransportadora
@admin.register(LogTransportadora)
class LogTransportadoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'frete_id', 'transportadora_nome', 'valor_antigo', 'valor_novo', 'usuario', 'data_alteracao')
    list_filter = ('transportadora_nome', 'data_alteracao', 'usuario')
    search_fields = ('transportadora_nome', 'usuario', 'frete_id')
    date_hierarchy = 'data_alteracao'
    
    def has_add_permission(self, request): return False
    def has_change_permission(self, request, obj=None): return False
    def has_delete_permission(self, request, obj=None): return False

# 5. Painel TabelaFreteTransportadora
@admin.register(TabelaFreteTransportadora)
class TabelaFreteTransportadoraAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome_transportadora', 'regiao', 'valor_frete', 'frete_unidade') 
    search_fields = ('nome_transportadora',)