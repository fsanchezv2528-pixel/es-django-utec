# catalogo/context_processors.py
"""Inyecta el contador del carrito en TODOS los templates — W13."""


def carrito_info(request) -> dict:
    carrito = request.session.get('carrito', {}) if hasattr(request, 'session') else {}
    return {
        'carrito_total_items':     sum(int(i.get('cantidad', 0)) for i in carrito.values()),
        'carrito_total_productos': len(carrito),
    }
