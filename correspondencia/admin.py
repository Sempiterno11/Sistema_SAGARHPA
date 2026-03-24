from django.contrib import admin
from .models import Oficio  # Importamos tu modelo

@admin.register(Oficio)
class OficioAdmin(admin.ModelAdmin):
    # Esto es para que en el panel se vean estas columnas y sea fácil buscar
    list_display = ('numero_oficio', 'remitente', 'destinatario', 'fecha_emision')
    search_fields = ('numero_oficio', 'asunto', 'remitente')
    list_filter = ('fecha_emision',)