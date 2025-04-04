"""
URL configuration for cine project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from peliculas import views  # Asegúrate de importar tus vistas

urlpatterns = [
    path('', views.home, name='home'),
    path('index', views.index, name='index'),
    path('admin/', admin.site.urls),  # Esto es para el panel admin
    path('estado/', views.admin_estado, name='admin_estado'),
    path('peliculas/', include('peliculas.urls')),
        # Ruta para el CRUD de Estado
    # Otras rutas de tu proyecto
]
