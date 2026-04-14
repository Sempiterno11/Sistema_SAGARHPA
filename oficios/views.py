from django.shortcuts import render, get_object_or_404
from .models import Oficio, Area, Empleado
from django.db import models
from .forms import OficioForm
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from datetime import datetime
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa  
from django.utils import timezone
from django.db.models import Q

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
    
    return render(request, 'modals/registro_oficio.html', {'form': form})

@login_required
def archivo_muerto(request):
    anio_actual = datetime.now().year
    oficios = Oficio.objects.exclude(fecha_recepcion__year=anio_actual).order_by('-fecha_recepcion')
    return render(request, 'oficios/lista_oficios.html', {'oficios': oficios, 'titulo_pagina': 'Archivo historico (Años anteriores)'})

@login_required
def generar_pdf_oficios(request):
    # 1. Capturamos los mismos filtros que el tablero por si quieres reporte filtrado
    query = request.GET.get('q', '')
    area_id = request.GET.get('area', '')

    # 2. Filtramos la base de datos (solo los pendientes para el reporte de trabajo)
    oficios = Oficio.objects.exclude(estado='FINALIZADO')

    if query:
        oficios = oficios.filter(
            Q(numero_oficio__icontains=query) |
            Q(remitente__icontains=query) |
            Q(asunto__icontains=query)
        )
    
    if area_id:
        oficios = oficios.filter(area_destino_id=area_id)

    oficios = oficios.order_by('-fecha_recepcion')

    # 3. Preparar el PDF
    template_path = 'oficios/reporte_pdf.html' # Asegúrate que el archivo esté aquí
    context = {
        'oficios': oficios,
        'fecha': datetime.now(),
        'titulo': 'Reporte de Oficios Pendientes'
    }    
    
    response = HttpResponse(content_type='application/pdf')
    # Esto hace que se abra en el navegador en lugar de descargarse directo
    response['Content-Disposition'] = 'inline; filename="reporte_sagarhpa.pdf"'
    
    template = get_template(template_path)
    html = template.render(context)
    
    pisa_status = pisa.CreatePDF(html, dest=response)   
    
    if pisa_status.err:
        return HttpResponse('Error al generar el reporte PDF', status=400)
    return response

@login_required
def tablero_control(request):
    # --- NUEVO: Capturamos los filtros del buscador ---
    query = request.GET.get('q', '')
    area_id = request.GET.get('area', '')

    # 1. RECIBIDOS: Apenas entraron
    recibidos_count = Oficio.objects.filter(estado='RECIBIDO').count()

    # 2. EN PROCESO: Turnados o En Proceso
    en_proceso_count = Oficio.objects.filter(
        Q(estado='TURNADO') | Q(estado='EN_PROCESO')
    ).count()

    # 3. RESPONDIDOS/FINALIZADOS
    finalizados_count = Oficio.objects.filter(estado='FINALIZADO').count()

    # 4. LA LISTA PARA LA TABLA (Con Filtros Aplicados)
    pendientes = Oficio.objects.exclude(estado='FINALIZADO')

    # Si el usuario escribió algo en el buscador
    if query:
        pendientes = pendientes.filter(
            Q(numero_oficio__icontains=query) |
            Q(remitente__icontains=query) |
            Q(asunto__icontains=query)
        )

    # Si el usuario seleccionó un área específica
    if area_id:
        pendientes = pendientes.filter(area_destino_id=area_id)

    # Ordenamos después de filtrar
    pendientes = pendientes.order_by('-fecha_recepcion')

    # 5. HISTORIAL RÁPIDO
    recientes = Oficio.objects.all().order_by('-id')[:5]

    context = {
        'pendientes': pendientes,
        'recibidos_count': recibidos_count,
        'en_proceso_count': en_proceso_count,
        'finalizados_count': finalizados_count,
        'total_pendientes': pendientes.count(), # Ahora cuenta los filtrados
        'recientes': recientes,
        # --- NUEVO: Enviamos estas variables al HTML ---
        'todas_las_areas': Area.objects.all(),
        'query': query,
        'area_filtro': area_id,
    }
    
    return render(request, 'tablero_control.html', context)

@login_required
def asignar_area(request, oficio_id):
    oficio = get_object_or_404(Oficio, id=oficio_id)
    from .models import Area
    areas = Area.objects.all()

    if request.method == 'POST':
        area_id = request.POST.get('area_seleccionada')
        indicacion = request.POST.get('instruccion')
        
        oficio.area_destino_id = area_id
        oficio.instruccion = indicacion
        oficio.estado = 'TURNADO'  
        oficio.save()
        
        # CAMBIO AQUÍ: Usamos el nombre que tienes en el navbar
        return redirect('lista_oficios') 

    return render(request, 'asignar_area.html', {
        'oficio': oficio,
        'areas': areas
    })

@login_required
def asignar_empleado(request, oficio_id):
    oficio = get_object_or_404(Oficio, id=oficio_id)
    from .models import Empleado
    
    empleados_del_area = Empleado.objects.filter(area=oficio.area_destino)

    if request.method == 'POST':
        empleado_id = request.POST.get('empleado_id')
        nota_interna = request.POST.get('instruccion_interna')
        
        oficio.asignado_a_id = empleado_id
        oficio.instruccion_interna = nota_interna
        oficio.estado = 'EN_PROCESO'
        oficio.save()

        # CAMBIO AQUÍ: Usamos el nombre que tienes en el navbar
        return redirect('lista_oficios')

    return render(request, 'oficios/asignar_empleado.html', {
        'oficio': oficio, 
        'empleados': empleados_del_area
    })

@login_required
def responder_oficio(request, oficio_id):
    # 1. Buscamos el oficio
    oficio = get_object_or_404(Oficio, id=oficio_id)
    
    if request.method == 'POST':
        # 2. Extraemos el archivo PDF de la respuesta
        archivo = request.FILES.get('archivo_respuesta')
        
        if archivo:
            # 3. Actualizamos los campos de respuesta y cerramos el ciclo
            oficio.respuesta_pdf = archivo
            oficio.fecha_respuesta = timezone.now().date()
            oficio.estado = 'FINALIZADO' 
            oficio.save()
            
            # 4. Mandamos al usuario de vuelta al tablero (donde ya no aparecerá como pendiente)
            return redirect('lista_oficios')
            
    return render(request, 'modals/responder_oficio.html', {'oficio': oficio})

@login_required
def historial_oficios(request):
    # Traemos solo los que ya tienen respuesta
    finalizados = Oficio.objects.filter(estado='FINALIZADO').order_by('-fecha_respuesta')
    
    return render(request, 'historial.html', {'finalizados': finalizados})
