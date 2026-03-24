from django import forms
from .models import Oficio

class OficioForm(forms.ModelForm):
    class Meta:
        model = Oficio
        fields = ['numero_oficio', 'asunto', 'remitente', 'fecha_recepcion', 'archivo_pdf']
        widgets = {
            'fecha_recepcion': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'asunto': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
        }