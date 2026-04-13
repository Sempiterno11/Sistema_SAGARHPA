from django.db import models

# TABLA NUEVA: Para registrar las oficinas
class Area(models.Model):
    id_area = models.CharField(max_length=10, unique=True, verbose_name="ID de Área") # Ej: GAN01
    nombre = models.CharField(max_length=100)
    titular = models.CharField(max_length=100)

    def __str__(self):
        return f"[{self.id_area}] {self.nombre}"
    
class Empleado(models.Model):
    nombre = models.CharField(max_length=150)
    puesto = models.CharField(max_length=100)
    # Conectamos al empleado con su área (ej. Juan es de Ganadería)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, related_name='empleados')

    def __str__(self):
        return f"{self.nombre} - {self.puesto}"

# TU TABLA ACTUALIZADA: Le agregamos campos de Turno y Respuesta
class Oficio(models.Model):
    # --- 1. DATOS DE RECEPCIÓN (Ventanilla) ---
    numero_oficio = models.CharField(max_length=100, unique=True)
    asunto = models.TextField()
    remitente = models.CharField(max_length=200)
    fecha_recepcion = models.DateField()
    archivo_pdf = models.FileField(upload_to='oficios_pdfs/', null=True, blank=True)

    # --- 2. DATOS DE TURNADO (Jefe a Área) ---
    area_destino = models.ForeignKey(Area, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Turnado a Área")
    instruccion = models.TextField(blank=True, null=True, verbose_name="Instrucción de Turno")
    fecha_turnado = models.DateTimeField(auto_now_add=True, null=True)

    # --- 3. DATOS DE ASIGNACIÓN (Secretaria a Empleado) ---
    asignado_a = models.ForeignKey(Empleado, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Persona que resuelve")
    instruccion_interna = models.TextField(blank=True, null=True, verbose_name="Instrucción de la Secretaría")

    # --- 4. DATOS DE RESPUESTA (Cierre del proceso) ---
    respuesta_pdf = models.FileField(upload_to='respuestas_pdfs/', null=True, blank=True)
    fecha_respuesta = models.DateField(null=True, blank=True)

    # --- 5. CONTROL DE ESTADOS (El "Semáforo" del proceso) ---
    ESTADO_CHOICES = [
        ('RECIBIDO', 'Recibido en Ventanilla'),
        ('TURNADO', 'Turnado a Área'),
        ('EN_PROCESO', 'Asignado a Empleado'),
        ('FINALIZADO', 'Respondido / Archivado'),
    ]
    estado = models.CharField(
        max_length=20, 
        choices=ESTADO_CHOICES, 
        default='RECIBIDO'
    )

    def __str__(self):
        return f"{self.numero_oficio} - {self.estado}"

