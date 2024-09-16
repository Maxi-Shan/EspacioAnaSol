from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def servicios(request):
    return render(request,'elegir_servicio.html')