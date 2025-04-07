from django.shortcuts import render, get_object_or_404, redirect
from .models import Sala, Estado , GeneroPelicula ,Horarios, Usuario# Asegúrate de importar tus modelos
from .forms import EstadoForm, GeneroPeliculaForm , HorarioForm
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import ftplib
import os
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.conf import settings
from datetime import datetime
from django.urls import reverse
from django.shortcuts import redirect
from functools import wraps
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import login_required  # Añade esta línea al inicio
from .models import Cartelera
from django.shortcuts import render, redirect, get_object_or_404
from .models import Horarios
from .forms import HorarioForm
from datetime import datetime
from django.utils.timezone import make_aware

def logout_view(request):
    # Limpia el token en la BD
    if 'usuario_id' in request.session:
        try:
            user = Usuario.objects.get(id=request.session['usuario_id'])
            user.token_sesion = None
            user.save()
        except Usuario.DoesNotExist:
            pass
            
    request.session.flush()
    return redirect('index')

def home(request):
    generos = GeneroPelicula.objects.all()
    estado_activo = Estado.objects.get(strDescripcion="activo")
    
    # Obtener carteleras activas con sus relaciones
    carteleras = Cartelera.objects.filter(
        idEstado=estado_activo
    ).select_related(
        'idPelicula',
        'idPelicula__idGenero',
        'idHorarios'
    ).order_by('idHorarios__dteFechaInicio', 'HorarioInicio')
    
    return render(request, 'peliculas/home.html', {
        'generos': generos,
        'carteleras': carteleras
    })
import secrets
from datetime import datetime, timedelta
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.conf import settings
from .models import Usuario

def index(request):
    # Redirige si ya está autenticado
    if 'usuario_id' in request.session and 'token_sesion' in request.session:
        try:
            user = Usuario.objects.get(id=request.session['usuario_id'])
            if user.token_sesion == request.session['token_sesion']:
                return redirect('admin_dashboard')
        except Usuario.DoesNotExist:
            pass

    # Manejo de intentos fallidos
    ip = request.META.get('REMOTE_ADDR', '')
    intentos = cache.get(f'login_attempts_{ip}', 0)
    
    if intentos >= 3:  # Límite de intentos
        cache.set(f'login_blocked_{ip}', True, timeout=300)  # Bloqueo por 5 minutos
        return render(request, 'index.html', {
            'error': 'Demasiados intentos. Espere 5 minutos.'
        })

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()[:45]  # Limita longitud
        password = request.POST.get('password', '')[:128]  # Limita longitud

        try:
            if cache.get(f'login_blocked_{ip}'):
                return render(request, 'index.html', {
                    'error': 'Cuenta temporalmente bloqueada. Intente más tarde.'
                })

            user = Usuario.objects.get(strNombre=username)
            
            # Validación de credenciales
            if user.strPwd == password and user.idEstado.strDescripcion.lower() == 'activo':
                # Generar token único
                token = secrets.token_urlsafe(64)
                
                # Actualizar sesión
                request.session.cycle_key()
                request.session['usuario_id'] = user.id
                request.session['token_sesion'] = token
                request.session['ip_address'] = ip
                request.session['user_agent'] = request.META.get('HTTP_USER_AGENT', '')[:255]
                request.session.set_expiry(settings.SESSION_COOKIE_AGE)  # Usar configuración global
                
                # Actualizar usuario
                user.token_sesion = token
                user.ultimo_login = datetime.now()
                user.save()
                
                # Resetear contador de intentos
                cache.delete(f'login_attempts_{ip}')
                
                return redirect('admin_dashboard')
            else:
                # Incrementar intentos fallidos
                cache.set(f'login_attempts_{ip}', intentos + 1, timeout=300)
                raise Usuario.DoesNotExist
                
        except Usuario.DoesNotExist:
            # Registro seguro de error
            print(f"Intento fallido para usuario: {username} desde IP: {ip}")
            return render(request, 'index.html', {
                'error': 'Credenciales inválidas o cuenta inactiva'
            })

    return render(request, 'index.html')

def admin_dashboard(request):
    return render(request, 'admin_dashboard.html')

# Vista para listar los estados
def listar_estados(request):
    estados = Estado.objects.all()
    return render(request, 'peliculas/listar_estados.html', {'estados': estados})

# Vista para crear un nuevo estado
def crear_estado(request):
    if request.method == 'POST':
        form = EstadoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_estados')  # Redirige a la lista de estados
    else:
        form = EstadoForm()
    return render(request, 'peliculas/crear_estado.html', {'form': form})

# Vista para eliminar un estado
def eliminar_estado(request, pk):
    estado = get_object_or_404(Estado, pk=pk)
    estado.delete()
    return redirect('listar_estados')


def admin_estado(request):
    estados = Estado.objects.all()
    if request.method == 'POST':
        if 'create' in request.POST:
            # Crear un nuevo estado
            form = EstadoForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin_estado')
        elif 'delete' in request.POST:
            # Eliminar un estado
            estado_id = request.POST.get('id')
            estado = get_object_or_404(Estado, id=estado_id)
            estado.delete()
            return redirect('admin_estado')
    else:
        form = EstadoForm()

    return render(request, 'peliculas/admin_estado.html', {'estados': estados, 'form': form})



def convertir_fecha(fecha_str):
    """ Convierte la fecha de entrada en d/m/Y h:i A a un objeto datetime válido. """
    try:
        return make_aware(datetime.strptime(fecha_str, "%d/%m/%Y %I:%M %p"))
    except ValueError:
        return None  # Retorna None si hay un error en la conversión

def admin_horarios(request):
    horarios = Horarios.objects.all()
    form = HorarioForm()
    horario_a_editar = None  

    # Capturar el ID del horario a editar desde la URL
    horario_id = request.GET.get('edit')
    if horario_id:
        horario_a_editar = get_object_or_404(Horarios, id=horario_id)
        form = HorarioForm(instance=horario_a_editar)

    if request.method == 'POST':
        horario_id = request.POST.get('horario_id')
        fecha_inicio = request.POST.get('dteFechaInicio', '').strip()
        fecha_fin = request.POST.get('dteFechaFin', '').strip()

        # Convertir fechas si están presentes
        fecha_inicio = convertir_fecha(fecha_inicio) if fecha_inicio else None
        fecha_fin = convertir_fecha(fecha_fin) if fecha_fin else None

        if fecha_inicio and fecha_fin:
            if horario_id:  # Si hay ID, es una edición
                horario_a_editar = get_object_or_404(Horarios, id=horario_id)
                horario_a_editar.dteFechaInicio = fecha_inicio
                horario_a_editar.dteFechaFin = fecha_fin
                horario_a_editar.save()
            else:  # Si no hay ID, es una creación
                Horarios.objects.create(dteFechaInicio=fecha_inicio, dteFechaFin=fecha_fin)

            return redirect('admin_horarios')

        elif 'delete' in request.POST:
            horario_id = request.POST.get('id')
            horario = get_object_or_404(Horarios, id=horario_id)
            horario.delete()
            return redirect('admin_horarios')

    return render(request, 'peliculas/admin_horarios.html', {
        'horarios': horarios,
        'form': form,
        'horario_a_editar': horario_a_editar
    })



from django.shortcuts import render, redirect, get_object_or_404
from .models import GeneroPelicula
from .forms import GeneroPeliculaForm
def admin_generos(request):
    generos = GeneroPelicula.objects.all()
    genero_a_editar = None  

    # Capturar el ID del género a editar desde la URL
    genero_id = request.GET.get('edit')
    if genero_id:
        genero_a_editar = get_object_or_404(GeneroPelicula, id=genero_id)

    if request.method == 'POST':
        if 'create' in request.POST:
            form = GeneroPeliculaForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect('admin_generos')

        elif 'update' in request.POST:
            genero_id = request.POST.get('genero_id')
            genero_a_editar = get_object_or_404(GeneroPelicula, id=genero_id)
            form = GeneroPeliculaForm(request.POST, instance=genero_a_editar)
            if form.is_valid():
                form.save()
                return redirect('admin_generos')

        elif 'delete' in request.POST:
            genero_id = request.POST.get('id')
            genero = get_object_or_404(GeneroPelicula, id=genero_id)
            genero.delete()
            return redirect('admin_generos')

    return render(request, 'peliculas/admin_generos.html', {
        'generos': generos,
        'genero_a_editar': genero_a_editar
    })


def admin_salas(request):
    salas = Sala.objects.all()
    estados = Estado.objects.all()

    if request.method == 'POST':
        id_sala = request.POST.get('id')
        descripcion = request.POST.get('strDescripcion')
        cantidad_asientos = request.POST.get('intCantidadAcientos')
        id_estado = request.POST.get('idestad')

        estado = get_object_or_404(Estado, id=id_estado)

        if id_sala:  # Si tiene ID, es una actualización
            sala = get_object_or_404(Sala, id=id_sala)
            sala.strDescripcion = descripcion
            sala.intCantidadAcientos = cantidad_asientos
            sala.idEstado= estado
            sala.save()
        else:  # Si no tiene ID, es una nueva sala
            Sala.objects.create(
                strDescripcion=descripcion,
                intCantidadAcientos=cantidad_asientos,
                idEstado=estado
            )

        return redirect('admin_salas')

    return render(request, 'peliculas/admin_salas.html', {'salas': salas, 'estados': estados})


def eliminar_sala(request, sala_id):
    sala = get_object_or_404(Sala, id=sala_id)
    sala.delete()
    return redirect('admin_salas')

from django.shortcuts import render, redirect, get_object_or_404
from ftplib import FTP
from django.conf import settings
from .models import Pelicula
from .forms import PeliculaForm

# Función para subir imágenes al servidor FTP y retornar la URL completa

def subir_imagen_ftp(archivo, nombre_destino):
    try:
        ftp = FTP(settings.FTP_HOST, timeout=10)
        ftp.login(settings.FTP_USER, settings.FTP_PASS)
        ftp.cwd(settings.FTP_DIR)

        with archivo.open("rb") as f:
            ftp.storbinary(f"STOR {nombre_destino}", f)

        ftp.quit()
        return f"{settings.FTP_URL}/{nombre_destino}"
    except Exception as e:
        print(f"Error subiendo archivo FTP: {e}")
        return None

# Vista para listar películas en admin_peliculas.html

def listar_peliculas(request):
    peliculas = Pelicula.objects.all()
    form = PeliculaForm()
    return render(request, 'peliculas/admin_peliculas.html', {'peliculas': peliculas, 'form': form})

import time
# Vista para agregar una película

def agregar_pelicula(request):
    if request.method == 'POST':
        form = PeliculaForm(request.POST, request.FILES)
        
        if form.is_valid():
            try:
                pelicula = form.save(commit=False)

                # Subir imagen al FTP si se proporcionó
                if 'strArchivoFtp' in request.FILES:
                    archivo = request.FILES['strArchivoFtp']
                    # Generar nombre único para el archivo
                    nombre_archivo = f"{int(time.time())}_{archivo.name}"
                    ruta_ftp = subir_imagen_ftp(archivo, nombre_archivo)
                    if ruta_ftp:
                        pelicula.strArchivoFtp = ruta_ftp
                    else:
                        raise ValueError("Error al subir la imagen al FTP")

                pelicula.save()
                return redirect('listar_peliculas')

            except Exception as e:
                print(f"Error al guardar película: {str(e)}")
                # Mantener los datos del formulario en caso de error
                return render(request, 'peliculas/admin_peliculas.html', {
                    'form': form,
                    'error_message': f"Error al guardar: {str(e)}",
                    'modo_edicion': False
                })
        else:
            print("Errores en el formulario:", form.errors)
            return render(request, 'peliculas/admin_peliculas.html', {
                'form': form,
                'modo_edicion': False
            })
    
    # Si es GET
    return render(request, 'peliculas/admin_peliculas.html', {
        'form': PeliculaForm(),
        'modo_edicion': False
    })


# Vista para editar película
# Vista para editar película


def editar_pelicula(request, id):
    pelicula = get_object_or_404(Pelicula, id=id)

    if request.method == 'POST':
        form = PeliculaForm(request.POST, request.FILES, instance=pelicula)
        if form.is_valid():
            pelicula = form.save(commit=False)

            # Si el usuario sube una nueva imagen, se sube al FTP
            if 'strArchivoFtp' in request.FILES:
                archivo = request.FILES['strArchivoFtp']
                ruta_ftp = subir_imagen_ftp(archivo, archivo.name)
                if ruta_ftp:
                    pelicula.strArchivoFtp = ruta_ftp  # Guarda la nueva imagen
            else:
                # Si no se sube una imagen, se mantiene la actual
                pelicula.strArchivoFtp = pelicula.strArchivoFtp  

            pelicula.save()
            return redirect(reverse('listar_peliculas'))
    else:
        form = PeliculaForm(instance=pelicula)

    return render(request, 'peliculas/admin_peliculas.html', {
        'form': form,
        'pelicula': pelicula,
        'modo_edicion': True
    })


# Vista para eliminar película

def eliminar_pelicula(request, id):
    pelicula = get_object_or_404(Pelicula, id=id)
    pelicula.delete()
    return redirect(reverse('listar_peliculas')) 



from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from .models import Cartelera
from .forms import CarteleraForm
import re


# Listar cartelera

def listar_cartelera(request):
    cartelera = Cartelera.objects.all()
    form = CarteleraForm()

    for item in cartelera:
        # Extraer el VIDEO_ID usando expresiones regulares
        match = re.search(r'v=([a-zA-Z0-9_-]+)', item.idPelicula.strVideo)
        if match:
            item.video_id = match.group(1)  # Asignamos el VIDEO_ID extraído
            item.idPelicula.strVideo = f"https://www.youtube.com/embed/{item.video_id}"  # Asignamos la URL embebida
        else:
            item.idPelicula.strVideo = None  # Si no se encuentra el VIDEO_ID, asignamos None

    return render(request, 'peliculas/admin_cartelera.html', {'cartelera': cartelera, 'form': form})


# Agregar cartelera

def agregar_cartelera(request):
    if request.method == 'POST':
        form = CarteleraForm(request.POST)
        if form.is_valid():
            
            form.save()
            return redirect(reverse('listar_cartelera'))
    return redirect(reverse('listar_cartelera'))

# Editar cartelera

def editar_cartelera(request, id):
    cartelera = get_object_or_404(Cartelera, id=id)
    if request.method == 'POST':
        form = CarteleraForm(request.POST, instance=cartelera)
        if form.is_valid():
            form.save()
            return redirect(reverse('listar_cartelera'))
    else:
        form = CarteleraForm(instance=cartelera)
    return render(request, 'peliculas/admin_cartelera.html', {'form': form, 'cartelera': Cartelera.objects.all(), 'modo_edicion': True, 'cartelera_editar': cartelera})

# Eliminar cartelera

def eliminar_cartelera(request, id):
    cartelera = get_object_or_404(Cartelera, id=id)
    cartelera.delete()
    return redirect(reverse('listar_cartelera'))

