from django.urls import path
from . import views

# O 'app_name' é o sobrenome que usamos no HTML: {% url 'appFrete:calcular_frete' %}
# Ele é importante para evitar conflitos de nomes entre diferentes apps
# Quando você define app_name = 'appFrete', você está dizendo ao Django: "Todas as URLs que eu criar aqui dentro pertencem à família appFrete".

app_name = 'appFrete'

urlpatterns = [
    path('', views.calcular_frete_view, name='calcular_frete_view'),
]
