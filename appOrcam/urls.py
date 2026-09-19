from django.urls import include, path
from appOrcam import views

urlpatterns = [
    path('orcamento/<int:pk>/', views.orcamento_pdf, name='imprimir_orcamento'),  # Como deve estar no seu urls.py
    path('listar_roteiros_producao/<int:pk>/',views.listar_roteiros_producao, name='listar_roteiros_producao'),
    path('modelForm/', views.form_modelForm, name='form_modelForm'),
    path('listar_orcamentos/', views.listar_orcamentos, name='listar_orcamentos'),
    path('get_chapa_detalhes/<int:chapa_id>/', views.get_chapa_detalhes, name='get_chapa_detalhes'),
    path('listar_roteiros_producao/', views.listar_roteiros_producao, name='listar_roteiros_producao'),

    path('memoria_calculo_view/', views.memoria_calculo_view, name='memoria_calculo_view'),
    
    path('orcamento_pdf_view/<int:pk>/', views.orcamento_pdf,name='orcamento_pdf_view'),
    path('frete/', include('appFrete.urls')),
        
    path('orcamento/<int:pk>/simulacao/', views.simulacoes_orcamentos, name='simulacoes_orcamentos'),

    path('simulador/', views.simulador_orcamento, name='simulador_orcamento'),

    path('api/simulador/', views.api_simulador_dinamico, name='api_simulador_dinamico'),

# 1º Passo: Vitrine Escura
    path('', views.pagina_inicial_demo, name='pagina_inicial'), 
    
    # 2º Passo: Tela Vermelha (A ponte que mata o WhatsApp)
    path('acesso/', views.tela_vermelha_demo, name='tela_vermelha'), 
    
    # 3º Passo: O Motor de Orçamento
    path('orcamento/', views.calcular_orcamento, name='calcular_orcamento'),
    path('api/consulta-cep/<str:cep_digitado>/', views.consulta_cep_local, name='consulta_cep_local'),

    path('painel_fila_vendas/', views.painel_fila_vendas, name='painel_fila_vendas'),
    path('vendas/puxar/', views.puxar_proximo_lead, name='puxar_proximo_lead'),
    path('vendas/atendimento/<int:lead_id>/', views.detalhe_atendimento, name='detalhe_atendimento'),
    path('vendas/meus-atendimentos/', views.meus_atendimentos, name='meus_atendimentos'),
    path('vendas/atualizar-status/<int:lead_id>/<str:novo_status>/', views.atualizar_status_lead, name='atualizar_status_lead'),

    path('logout/', views.sair_sistema, name='logout_vendedor'),
]
