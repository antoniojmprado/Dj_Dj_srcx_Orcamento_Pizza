from django.urls import path
from appOrcam import views

urlpatterns = [
    path('', views.inicial, name='inicial'),
    path('orcamento/<int:pk>/', views.imprimir_orcamento,name='imprimir_orcamento'),
    path('modelForm/', views.form_modelForm, name='form_modelForm'),
    path('listar_orcamentos/', views.listar_orcamentos, name='listar_orcamentos'),
    # path('home/', views.home, name='home'),
    # Exemplo: http://127.0.0.1:8000/orcamento/27/
    # path('', views.form_modelForm, name='form_modelForm'),

]
