from django.urls import path
from appOrcam import views

urlpatterns = [
    # não necessariamente 'home'. Pode ser index, main whatever...
    path('home/', views.home, name='home'),
    # Exemplo: http://127.0.0.1:8000/orcamento/27/
    path('orcamento/<int:pk>/', views.imprimir_orcamento,name='imprimir_orcamento'),
    # path('modelForm/', views.form_modelForm, name='form_modelForm'),
    path('', views.form_modelForm, name='form_modelForm'),

]
