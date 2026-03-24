from django.db import models

class Oficio(models.Model):
    numero_oficio = models.CharField(max_length=100, unique=True)
    asunto = models.TextField()
    remitente = models.CharField(max_length=200)
    fecha_recepcion = models.DateField()
    archivo_pdf = models.FileField(upload_to='oficios_pdfs/', null=True, blank=True)

    def __str__(self):
        return self.numero_oficio