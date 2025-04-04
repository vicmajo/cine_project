from django.http import HttpResponse

def prueba_error(request):
    raise ValueError("Este es un error de prueba")
