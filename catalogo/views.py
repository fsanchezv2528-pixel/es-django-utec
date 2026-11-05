# catalogo/views.py
"""Catálogo público y carrito de compras en sesión — W13.

Estructura del carrito en la sesión (todo serializable a JSON):
    request.session['carrito'] = {
        '1': {'nombre': 'Laptop', 'precio': '10000.00', 'cantidad': 2,
              'imagen': 'productos/laptop.jpg'},
    }
    - La clave es str(producto.pk): JSON solo admite claves de texto.
    - El precio se guarda como str: Decimal no es serializable a JSON.
"""

import stripe
from django.conf import settings
from django.contrib.auth.decorators import login_required

from ventas.models import Pedido
from .checkout_utils import (
    calcular_totales,
    generar_numero_pedido,
    obtener_o_crear_cliente,
)

# Configurar la clave secreta de Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

from decimal import Decimal

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.generic import ListView

from productos.models import Producto

from .filters import ProductoFilter

MAX_CANTIDAD = 99


# ── CATÁLOGO ──────────────────────────────────────────────────────────
class CatalogoView(ListView):
    """Catálogo público con filtros. No requiere iniciar sesión."""

    model               = Producto
    template_name       = 'catalogo/catalogo.html'
    context_object_name = 'productos'
    paginate_by         = 12

    def get_queryset(self):
        qs = (
            Producto.objects
            .select_related('categoria', 'proveedor')
            .filter(activo=True)
            .order_by('nombre')
        )
        self.filtro = ProductoFilter(self.request.GET, queryset=qs)
        return self.filtro.qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['filtro'] = self.filtro
        # Parámetros de filtro sin "page", para armar los enlaces de paginación
        params = self.request.GET.copy()
        params.pop('page', None)
        ctx['filtros_query'] = params.urlencode()
        return ctx


# ── CARRITO: utilidades ───────────────────────────────────────────────
def _obtener_carrito(request) -> dict:
    return request.session.get('carrito', {})


def _guardar_carrito(request, carrito: dict) -> None:
    request.session['carrito'] = carrito
    request.session.modified   = True


def _leer_cantidad(request, defecto: int = 1) -> int:
    """Lee 'cantidad' del POST sin tronar si viene vacía o con texto."""
    try:
        return int(request.POST.get('cantidad', defecto))
    except (TypeError, ValueError):
        return defecto


def _redirigir_seguro(request, defecto: str):
    """Regresa a 'next' solo si apunta a este mismo sitio (evita open redirect)."""
    destino = request.POST.get('next') or request.META.get('HTTP_REFERER')
    if destino and url_has_allowed_host_and_scheme(
        destino, allowed_hosts={request.get_host()}, require_https=request.is_secure()
    ):
        return redirect(destino)
    return redirect(defecto)


# ── CARRITO: vistas ───────────────────────────────────────────────────
def ver_carrito(request):
    """Muestra el carrito con subtotales y total (precios como Decimal)."""
    items = []
    total = Decimal('0.00')
    for prod_id, datos in _obtener_carrito(request).items():
        precio   = Decimal(datos['precio'])
        cantidad = int(datos['cantidad'])
        subtotal = precio * cantidad
        total   += subtotal
        items.append({
            'prod_id':  prod_id,
            'nombre':   datos['nombre'],
            'precio':   precio,
            'cantidad': cantidad,
            'subtotal': subtotal,
            'imagen':   datos.get('imagen'),
        })
    return render(request, 'catalogo/carrito.html', {'items': items, 'total': total})


def agregar_al_carrito(request, producto_id: int):
    """Agrega un producto o suma su cantidad. Solo POST (protegido con CSRF)."""
    if request.method != 'POST':
        return redirect('catalogo:catalogo')

    producto = get_object_or_404(Producto, pk=producto_id, activo=True)
    carrito  = _obtener_carrito(request)
    clave    = str(producto_id)
    cantidad = max(1, _leer_cantidad(request))

    if clave in carrito:
        carrito[clave]['cantidad'] = min(MAX_CANTIDAD, carrito[clave]['cantidad'] + cantidad)
    else:
        carrito[clave] = {
            'nombre':   producto.nombre,
            'precio':   str(producto.precio),
            'cantidad': min(MAX_CANTIDAD, cantidad),
            'imagen':   producto.imagen.name if getattr(producto, 'imagen', None) else None,
        }

    _guardar_carrito(request, carrito)
    messages.success(request, f'"{producto.nombre}" agregado al carrito.')
    return _redirigir_seguro(request, 'catalogo:catalogo')


def remover_del_carrito(request, producto_id: int):
    """Elimina un producto del carrito. Solo POST."""
    if request.method != 'POST':
        return redirect('catalogo:carrito')
    carrito = _obtener_carrito(request)
    clave   = str(producto_id)
    nombre  = carrito.get(clave, {}).get('nombre', 'Producto')
    carrito.pop(clave, None)
    _guardar_carrito(request, carrito)
    messages.warning(request, f'"{nombre}" eliminado del carrito.')
    return redirect('catalogo:carrito')


def actualizar_cantidad(request, producto_id: int):
    """Cambia la cantidad. Si es 0 o menos, quita el producto. Solo POST."""
    if request.method != 'POST':
        return redirect('catalogo:carrito')
    carrito  = _obtener_carrito(request)
    clave    = str(producto_id)
    cantidad = _leer_cantidad(request)
    if clave in carrito:
        if cantidad > 0:
            carrito[clave]['cantidad'] = min(MAX_CANTIDAD, cantidad)
        else:
            carrito.pop(clave)
    _guardar_carrito(request, carrito)
    return redirect('catalogo:carrito')


def vaciar_carrito(request):
    """Vacía el carrito. Solo POST."""
    if request.method == 'POST':
        _guardar_carrito(request, {})
        messages.info(request, 'Carrito vaciado.')
    return redirect('catalogo:carrito')

@login_required
def checkout(request):
    """Resumen del carrito y creación de PaymentIntent de Stripe."""
    carrito = _obtener_carrito(request)
    if not carrito:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('catalogo:catalogo')

    totales         = calcular_totales(carrito)
    publishable_key = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == 'POST':
        try:
            cliente = obtener_o_crear_cliente(request.user)

            numero = generar_numero_pedido()
            pedido = Pedido.objects.create(
                numero_pedido = numero,
                cliente       = cliente,
                estado        = 'pendiente',
                total_pagado  = totales['total'],
            )

            monto_centavos = int(totales['total'] * 100)

            intent = stripe.PaymentIntent.create(
                amount          = monto_centavos,
                currency        = 'mxn',
                metadata        = {
                    'pedido_id':  pedido.pk,
                    'pedido_num': pedido.numero_pedido,
                    'cliente':    cliente.nombre,
                },
                idempotency_key = f'pedido-{pedido.pk}',
            )

            return render(request, 'catalogo/checkout.html', {
                'carrito':         carrito,
                'totales':         totales,
                'pedido':          pedido,
                'client_secret':   intent.client_secret,
                'publishable_key': publishable_key,
            })

        except stripe.error.StripeError as exc:
            messages.error(
                request,
                f'Error al conectar con Stripe: {exc.user_message}'
            )
            return redirect('catalogo:pago_error')

        except Exception as exc:
            messages.error(
                request,
                f'Error inesperado en el proceso de pago: {exc}'
            )
            return redirect('catalogo:pago_error')

    return render(request, 'catalogo/checkout.html', {
        'carrito':         carrito,
        'totales':         totales,
        'client_secret':   None,
        'publishable_key': publishable_key,
    })


def pago_exitoso(request, pedido_id: int):
    """Confirmación post-pago: vacía el carrito y muestra el pedido."""
    pedido = get_object_or_404(Pedido, pk=pedido_id)

    _guardar_carrito(request, {})
    messages.success(
        request,
        f'¡Pago exitoso! Tu pedido {pedido.numero_pedido} '
        f'está confirmado. Total: ${pedido.total_pagado}'
    )

    return render(request, 'catalogo/pago_exitoso.html', {
        'pedido': pedido,
    })


def pago_error(request):
    """Vista de error de pago."""
    return render(request, 'catalogo/pago_error.html')
