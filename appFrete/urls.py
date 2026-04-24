from django.urls import path
from . import views

# O 'app_name' é o sobrenome que usamos no HTML: {% url 'appFrete:calcular_frete' %}
# Ele é importante para evitar conflitos de nomes entre diferentes apps
# Quando você define app_name = 'appFrete', você está dizendo ao Django: "Todas as URLs que eu criar aqui dentro pertencem à família appFrete".

app_name = 'appFrete'

urlpatterns = [
    
    path('', views.calcular_frete_view, name='calcular_frete_view'),

    # Lista de todos os fretes salvos (Onde está o DataTables)
    path('lista_fretes', views.lista_fretes, name='lista_fretes'),

    # Visualizar um frete específico (O que o botão do olho chama)
    # <int:pk> é o ID do frete que você salvou no banco
    path('resultado/<int:pk>/', views.calcular_frete_view, name='result_transps'),

    # # Rota para a exclusão via AJAX
    # path('excluir-frete/<int:pk>/', views.excluir_frete, name='excluir_frete'),
]
