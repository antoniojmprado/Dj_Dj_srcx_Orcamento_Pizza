from appOrcam import views
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('orcam/', include('appOrcam.urls')),
    path('oee/', include('appOEE.urls')),
    # A nova linha que liga o Frete:
    path('frete/', include('appFrete.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
