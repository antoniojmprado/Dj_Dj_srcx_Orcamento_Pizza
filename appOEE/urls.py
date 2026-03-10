from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from appOEE import views

urlpatterns = [
    path('', views.home, name='home'),
    path('apresentacao/', views.apresentacao, name='apresentacao'),

    path('total_dias_horasParadas/', views.total_dias_horasParadas, name='total_dias_horasParadas'),

    path('resumo_paralisacoes/', views.resumo_paralisacoes,name='resumo_paralisacoes'),
    path('detalhe_paralisacoes/', views.detalhe_paralisacoes,name='detalhe_paralisacoes'),
    
    path('paradas_maquina/', views.paradas_maquina, name='paradas_maquina'),
    path('paradas_por_dia_maquina/', views.paradas_por_dia_maquina, name='paradas_por_dia_maquina'),
    path('tipo_parada/', views.tipo_parada, name='tipo_parada'),  
    path('motivo_parada/', views.motivo_parada, name='motivo_parada'),
    path('oee_maquina/', views.oee_maquina, name='oee_maquina'),
    
    path('cadastra_ocorrencia/', views.cadastra_ocorrencia, name='cadastra_ocorrencia'),
    path('oee_por_maquina/', views.oee_por_maquina, name='oee_por_maquina'),
    path('oee_parque_diario/', views.oee_parque_diario, name='oee_parque_diario'), 
    path('paradas_parque_diario/', views.paradas_parque_diario,
         name='paradas_parque_diario'),
    path('ocorrencia/<int:pk>/', views.detalhe_ocorrencia,name='detalhe_ocorrencia'),
    path('listar_paralis/', views.listar_paralis, name='listar_paralis'),
    path('oee_parque_acumulado/', views.oee_parque_acumulado, name='oee_parque_acumulado'),
    path('oee_global_duponthtml/', views.oee_global_duponthtml, name='oee_global_duponthtml'),

    path('oee_acum_maquina/', views.oee_acum_maquina, name='oee_acum_maquina'),
    path('ranking_oee/', views.ranking_oee, name='ranking_oee'),
    path('relatorio_ocorrencias/', views.relatorio_ocorrencias, name='relatorio_ocorrencias'),
    path('dashboard_financeiro/', views.dashboard_roce, name='dashboard_roce'), 
    path('prejuizos_financeiros/', views.prejuizos_financeiros, name='prejuizos_financeiros'),
    path('prejuizos_custos_maquina/', views.prejuizos_custos_maquina, name='prejuizos_custos_maquina'),
    path('prejuizos_maquina/', views.prejuizos_maquina, name='prejuizos_maquina'),
    
    path('detalhes_waterfall/', views.detalhes_waterfall, name='detalhes_waterfall'),
    path('simulador/', views.simulador, name='simulador'),
]
