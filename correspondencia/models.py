from django.db import models

class Oficio(models.Model):
    numero_oficio = models.CharField(max_length=100, unique=True, verbose_name="Número de Oficio")
    remitente = models.CharField(max_length=200)
    destinatario = models.CharField(max_length=200)
    asunto = models.CharField()
    fecha_emision = models.DateField()  
    fecha_recepcion = models.DateField(auto_now_add=True)
    archivo_pdf = models.FileField(upload_to='oficios_pdfs/', null=True, blank=True)

    def __str__(self):
        return self.numero_oficio 