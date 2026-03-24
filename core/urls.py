from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from oficios.views import lista_oficios, registrar_oficio, archivo_muerto, generar_pdf_oficios

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', lista_oficios, name='lista_oficios'),
    path('registrar/', registrar_oficio, name='registrar_oficio'),
    path('archivo_muerto/', archivo_muerto, name='archivo_muerto'),
    path('reporte-pdf/', generar_pdf_oficios, name='generar_pdf_oficios'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
