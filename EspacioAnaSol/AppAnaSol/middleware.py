from .models import Empleado

class EmpleadoMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            dni = request.session.get('empleado_dni')
            if dni:
                try:
                    request.empleado = Empleado.objects.get(dni=dni)
                    print(f'Empleado encontrado: {request.empleado.nombre}')
                except Empleado.DoesNotExist:
                    request.empleado = None
            else:
                request.empleado = None
        else:
            request.empleado = None
        return self.get_response(request)
           
