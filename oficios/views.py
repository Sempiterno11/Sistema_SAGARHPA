from django.shortcuts import render
from .models import Oficio
from django.db import models
from .forms import OficioForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  

@login_required
def lista_oficios(request):
    busqueda = request.GET.get('buscar')
    if busqueda:
        oficios = Oficio.objects.filter(
            models.Q(numero_oficio__icontains=busqueda) | 
            models.Q(asunto__icontains=busqueda)
        )
    else:
        oficios = Oficio.objects.all().order_by('-fecha_recepcion')
    
    return render(request, 'lista_oficios.html', {'oficios': oficios, 'busqueda': busqueda})

def registrar_oficio(request):
    if request.method == 'POST':
        form = OficioForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('lista_oficios')
    else:
        form = OficioForm()
    
    return render(request, 'registrar_oficio.html', {'form': form})

@login_required
def archivo_muerto(request):
    anio_actual = datetime.now().year
    oficios = Oficio.objects.exclude(fecha_recepcion__year=anio_actual).order_by('-fecha_recepcion')
    return render(request, 'oficios/lista_oficios.html', {'oficios': oficios, 'titulo_pagina': 'Archivo historico (Años anteriores)'})

@login_required
def generar_pdf_oficios(request):
    oficios = Oficio.objects.all().order_by('-fecha_recepcion')
    template_path = 'oficios/reporte_pdf.html'
    context = {'oficios': oficios,
               'fecha': datetime.now(),
    }    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="reporte_sagarhpa.pdf"'
    template = get_template(template_path)
    html = template.render(context)
    pisa_status = pisa.CreatePDF(html, dest=response)   
    if pisa_status.err:
        return HttpResponse('Error al generar PDF', status=400)
    return response 