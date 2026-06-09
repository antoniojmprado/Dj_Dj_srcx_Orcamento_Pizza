from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from appQuali import views

# A blindagem do aplicativo: todas as rotas agora pertencem a este grupo
app_name = 'appQuali'

urlpatterns = [
    path('', views.home, name='home'), 
    path('data_primeiro_registro/', views.data_primeiro_registro, name='data_primeiro_registro'),
    path('data_ultimo_registro/', views.data_ultimo_registro, name='data_ultimo_registro'),
    path('reclamacao/excluir/<int:pk>/', views.reclamacao_delete_sql, name='reclamacao_delete_sql'),
    path('reclam_cliente/', views.reclam_cliente, name='reclam_cliente'),
    
    path('qt_reclamantes/', views.qt_reclamantes, name='qt_reclamantes'),
    path('maioresReclamantes/', views.maioresReclamantes, name='maioresReclamantes'),
    path('week_modal/', views.week_modal, name='week_modal'),
    
    path('reclamacoes_list/', views.reclamacoes_list, name='reclamacoes_list'),
    
    path('defeitosPorMes/', views.defeitosPorMes, name='defeitosPorMes'),
    path('defeitosPorDiaHistorico30/', views.defeitosPorDiaHistorico30, name='defeitosPorDiaHistorico30'),
    path('defeitosPorTipoMaisFrequentes/', views.defeitosPorTipoMaisFrequentes, name='defeitosPorTipoMaisFrequentes'),
    path('selecionaMesAno/', views.selecionaMesAno, name='selecionaMesAno'),
    path('defeitoMesEscolhido/', views.defeitoMesEscolhido, name='defeitoMesEscolhido'),
    path('defeitosPorMaisFrequentesMesAnterior/', views.defeitosPorMaisFrequentesMesAnterior, name='defeitosPorMaisFrequentesMesAnterior'),
    path('defeitosPorSemana/', views.defeitosPorSemana, name='defeitosPorSemana'),
    path('listaDefeitos/', views.listaDefeitos, name='listaDefeitos'), 
    path('grafico_defeitos/', views.grafico_defeitos, name='grafico_defeitos'),
    
    path('tiposDefeitosPorSemana/', views.tiposDefeitosPorSemana, name='tiposDefeitosPorSemana'),
]

# Deixamos a verificação de MEDIA aqui, mas lembre-se que em produção (Nginx) 
# ele assumirá o controle de servir os áudios e vídeos de forma robusta.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )