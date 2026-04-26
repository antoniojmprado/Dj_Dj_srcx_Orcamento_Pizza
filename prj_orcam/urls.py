from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# IMPORTANTE: Importar as views de autenticação do próprio Django
from django.contrib.auth import views as auth_views 

urlpatterns = [
    # 1. Login como porta de entrada (usando o motor do Django)
    path('', auth_views.LoginView.as_view(template_name='appFrete/login.html'), name='login'),
    
    # 2. Painel de Administração
    path('admin/', admin.site.urls),
    
    # 3. Seus Aplicativos (Módulos)
    path('orcam/', include('appOrcam.urls')),
    path('oee/', include('appOEE.urls')),
    path('frete/', include('appFrete.urls')),
]

# Essencial para carregar o CSS/JavaScript em ambiente de teste
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)