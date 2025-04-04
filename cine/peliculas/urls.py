from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    
    path('index', views.index, name='index'), # pantalla de lohin
    path('', views.admin_dashboard, name='admin_dashboard'),#pantalla a la ingresamos si iniciamos sesion como administrador

# todas las urls dentro del apartado de administrador
    path('estado/', views.admin_estado, name='admin_estado'),
    path('admin/horarios/', views.admin_horarios, name='admin_horarios'),
    path('admin/generos/', views.admin_generos, name='admin_generos'),
    path('listar_peliculas/', views.listar_peliculas, name='listar_peliculas'),
    path('agregar/', views.agregar_pelicula, name='agregar_pelicula'),
    path('editar/<int:id>/', views.editar_pelicula, name='editar_pelicula'),
    path('eliminar/<int:id>/', views.eliminar_pelicula, name='eliminar_pelicula'),

    path('admin/salas/', views.admin_salas, name='admin_salas'),
    path('admin/salas/eliminar/<int:sala_id>/', views.eliminar_sala, name='eliminar_sala'),
 

    path('estados/', views.listar_estados, name='listar_estados'),
    path('crear/', views.crear_estado, name='crear_estado'),
    #path('editar/<int:pk>/', views.editar_estado, name='editar_estado'),
    path('eliminar/<int:pk>/', views.eliminar_estado, name='eliminar_estado'),


    path('admin/cartelera/', views.listar_cartelera, name='listar_cartelera'),
    path('admin/cartelera/agregar/', views.agregar_cartelera, name='agregar_cartelera'),
    path('admin/cartelera/editar/<int:id>/', views.editar_cartelera, name='editar_cartelera'),
    path('admin/cartelera/eliminar/<int:id>/', views.eliminar_cartelera, name='eliminar_cartelera'),
    

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    