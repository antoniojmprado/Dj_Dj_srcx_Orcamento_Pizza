from django.urls import path
from appOrcam import views

urlpatterns = [
    path('', views.inicial, name='inicial'),
    path('orcamento/<int:pk>/', views.imprimir_orcamento,
         name='imprimir_orcamento'),  # Como deve estar no seu urls.py
    path('listar_roteiros_producao/<int:pk>/',views.listar_roteiros_producao, name='listar_roteiros_producao'),
    path('modelForm/', views.form_modelForm, name='form_modelForm'),
    path('listar_orcamentos/', views.listar_orcamentos, name='listar_orcamentos'),
    path('get-chapa-detalhes/<int:chapa_id>/', views.get_chapa_detalhes, name='get_chapa_detalhes'),
    path('listar_roteiros_producao/', views.listar_roteiros_producao, name='listar_roteiros_producao'),

]
