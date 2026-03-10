from django.contrib import admin
from django.contrib.admin.widgets import AdminSplitDateTime
from django import forms
from .models import *

#from .models import Horas_turno, Turnos_dia, Empresa, Maquina, Motivo, Tipo_parada, Ocorrencia, Calc_roce

from .models import MaquinaFinancas
from .models import ParametroFinanceiro
from .models import Waterfall


@admin.register(MaquinaFinancas)
class MaquinaFinancasAdmin(admin.ModelAdmin):
    list_display = ('maquina', 'valor_reposicao', 'custo_minuto', 'dias_sem', 'horas_turno', 'sem_mes', 'turnos_dia', 'horas_mes', 'minutos_mes')
    # Permite editar direto na lista
    list_editable = ('valor_reposicao', 'horas_turno','turnos_dia','dias_sem','sem_mes')

@admin.register(Horas_turno)
class Horas_turnoAdmin(admin.ModelAdmin):
    list_display = ('id', 'qt_horas_turno')


@admin.register(Turnos_dia)
class Turnos_diaAdmin(admin.ModelAdmin):
    list_display = ('id', 'qt_turnos_dia')

@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)


@admin.register(Maquina)
class MaquinaAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome')
    search_fields = ('nome',)


@admin.register(Motivo)
class MotivoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nome', 'tipo_parada_id')
    search_fields = ('nome', 'tipo_parada_id')


@admin.register(Tipo_parada)
class Tipo_paradaAdmin(admin.ModelAdmin):
    list_display = ('id', 'descricao')
    search_fields = ('descricao',)


class OcorrenciaAdminForm(forms.ModelForm):
    class Meta:
        model = Ocorrencia
        fields = '__all__'
        widgets = {
            'data_fim': AdminSplitDateTime(),
        }


@admin.register(Ocorrencia)
class OcorrenciaAdmin(admin.ModelAdmin):
    form = OcorrenciaAdminForm

    readonly_fields = ('data_inicio',)

    list_display = (
        'id',
        'empresa',
        'data_inicio',
        'data_fim',
        'tempo_parado_formatado',
        'maquina',
        'motivo',
        'tipo_parada', 
    )

    list_filter = (
        'empresa',
        'maquina',
        'motivo',
        'tipo_parada',
        'data_inicio',
    )

    search_fields = (
        'empresa__nome',
        'maquina__nome',
        'motivo__nome',
    )

    date_hierarchy = 'data_inicio'


@admin.register(ParametroFinanceiro)
class ParametroFinanceiroAdmin(admin.ModelAdmin):
    list_display = ('faturamento_grupo', 'quantidade_pessoas',
                    'percentual_empresa_estudo')


@admin.register(Waterfall)
class Waterfall(admin.ModelAdmin):
    list_display = ('fat_bruto', 'perda_oee', 'fat_real',
                    'cust_var', 'cust_fixo', 'res_contab', 'perda_disp', 'perda_perf', 'perda_quali', 'cust_inefic', 'res_contab', 'hr_paralis','minutos_mes')
