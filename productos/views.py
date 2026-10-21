# productos/views.py
"""Vistas de la app productos — W07 (lectura) + W08 (escritura) + W09 (permisos)."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import ProductoForm
from .models import Producto


# ── Lectura (W07) ────────────────────────────────────────────────────
class ProductoListView(ListView):
    """Lista paginada de productos activos."""

    model               = Producto
    template_name       = 'productos/lista.html'
    context_object_name = 'productos'
    paginate_by         = 20

    def get_queryset(self):
        return (
            Producto.objects
            .select_related('categoria', 'proveedor')
            .filter(activo=True)
            .order_by('nombre')
        )


class ProductoDetailView(DetailView):
    """Detalle de un producto."""

    model               = Producto
    template_name       = 'productos/detalle.html'
    context_object_name = 'producto'
    pk_url_kwarg        = 'producto_id'

    def get_queryset(self):
        return Producto.objects.select_related('categoria', 'proveedor')


# ── Escritura (W08) ──────────────────────────────────────────────────
class ProductoCreateView(LoginRequiredMixin, CreateView):
    """Alta de producto. LoginRequiredMixin va PRIMERO."""

    model         = Producto
    form_class    = ProductoForm
    template_name = 'productos/crear.html'
    success_url   = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Producto "{self.object.nombre}" creado exitosamente.'
        )
        return response


class ProductoUpdateView(LoginRequiredMixin, UpdateView):
    """Edición de producto."""

    model         = Producto
    form_class    = ProductoForm
    template_name = 'productos/editar.html'
    pk_url_kwarg  = 'producto_id'
    success_url   = reverse_lazy('productos:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f'Producto "{self.object.nombre}" actualizado.'
        )
        return response


# ── Borrado con permiso (W09) ────────────────────────────────────────
class ProductoDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Confirmación y borrado de producto.

    - Sin sesión            → redirige a /accounts/login/
    - Con sesión sin permiso → HTTP 403 Forbidden

    NOTA: no se usa raise_exception = True. Con True, Django devuelve 403
    también a quien NO ha iniciado sesión, en vez de mandarlo al login.
    El comportamiento por defecto ya da 403 al usuario autenticado.
    """

    model               = Producto
    template_name       = 'productos/eliminar.html'
    pk_url_kwarg        = 'producto_id'
    success_url         = reverse_lazy('productos:lista')
    permission_required = 'productos.delete_producto'

    def form_valid(self, form):
        nombre = self.object.nombre
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f'No se puede eliminar "{nombre}": tiene ventas asociadas.'
            )
            return redirect('productos:detalle', producto_id=self.object.pk)
        messages.success(self.request, f'Producto "{nombre}" eliminado.')
        return response
