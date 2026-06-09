from django.contrib import admin  # type: ignore
from django import forms
from appQuali.models import Empresa, Produtos, TiposDefeitos, Reclamacoes, ReclamacoesArquivo
from import_export.admin import ImportExportModelAdmin
from django.conf.locale.es import formats as es_formats


class TiposDefeitosAdmin(admin.ModelAdmin):
    list_display = ('id', 'tipo_defeito',)
    # parameter_name = 'TiposDefeitos'

class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('id', 'empresa',)
    
class ProdutosAdmin(admin.ModelAdmin):
    list_display = ('id', 'produto',)
    

class ReclamacoesAdmin(admin.ModelAdmin):
    list_display = ('id', 'data_reclam', 'cliente', 'descricao',
                    'id_defeito', 'id_produto', 'id_tecnol', 'id_empresa', 'data_atualiza',)
    list_filter = ['id_tecnol', 'id_defeito']
    

    

admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Produtos, ProdutosAdmin)
admin.site.register(Reclamacoes, ReclamacoesAdmin)
admin.site.register(TiposDefeitos, TiposDefeitosAdmin)
admin.site.register(ReclamacoesArquivo)
