from django.shortcuts import render


def index(request):
    context = {
        'titulo': 'Ventas',
        'descripcion': 'Ciclo de ventas, pedidos y facturación.',
        'espiral': 'Espiral 3 · W07',
    }
    return render(request, 'ventas/index.html', context)