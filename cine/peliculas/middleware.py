import traceback
import logging
from django.core.mail import mail_admins
logger = logging.getLogger(__name__)

class ExceptionLoggingMiddleware:
    """Middleware para capturar errores y enviarlos por correo."""
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            # Obtener detalles del error
            error_traceback = traceback.format_exc()
            error_message = f"Error: {str(e)}\n\nDetalles:\n{error_traceback}"
            logger.error(error_message)  # Registrar el error en logs
            
            # Enviar correo a los administradores
            mail_admins(
                subject="⚠️ ERROR en la Aplicación Django",
                message=error_message
            )
            
            raise e  # Relanzar la excepción para que Django la maneje


