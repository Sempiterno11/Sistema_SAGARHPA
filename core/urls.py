from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# Importamos directamente tus funciones para no usar el prefijo "views."
from oficios.views import (
    lista_oficios, registrar_oficio, archivo_muerto, 
    generar_pdf_oficios, tablero_control, asignar_area, asignar_empleado, responder_oficio, historial_oficios
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    
    # 1. El Inicio (Tablero)
    path('', tablero_control, name='lista_oficios'), 
    
    # 2. Registro (Asegúrate que este nombre coincida con el botón verde)
    path('registrar/', registrar_oficio, name='registrar_oficio'),
    
    # 3. Acciones
    path('asignar-area/<int:oficio_id>/', asignar_area, name='asignar_area'),
    path('asignar-empleado/<int:oficio_id>/', asignar_empleado, name='asignar_empleado'),
    
    # 4. Otros
    path('archivo-muerto/', archivo_muerto, name='archivo_muerto'),
    path('reporte-pdf/', generar_pdf_oficios, name='generar_pdf_oficios'),
    path('responder-oficio/<int:oficio_id>/', responder_oficio, name='responder_oficio'),
    path('historial/', historial_oficios, name='historial_oficios')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)