# clientes/views.py
"""Vistas de la app clientes — W07 (lectura) + W08 (escritura) + W09 (permisos)."""
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import ProtectedError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView, DeleteView, DetailView, ListView, UpdateView
)

from .forms import ClienteForm
from .models import Cliente


# ── Lectura (W07) ────────────────────────────────────────────────────
class ClienteListView(ListView):
    """Lista paginada de clientes activos."""

    model               = Cliente
    template_name       = 'clientes/lista.html'
    context_object_name = 'clientes'
    paginate_by         = 20

    def get_queryset(self):
        return Cliente.objects.filter(activo=True).order_by('nombre')


class ClienteDetailView(DetailView):
    """Detalle de un cliente con sus últimas ventas."""

    model               = Cliente
    template_name       = 'clientes/detalle.html'
    context_object_name = 'cliente'
    pk_url_kwarg        = 'cliente_id'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['ventas'] = self.object.ventas.order_by('-fecha')[:10]
        return ctx


# ── Escritura (W08) ──────────────────────────────────────────────────
class ClienteCreateView(LoginRequiredMixin, CreateView):
    """Alta de cliente."""

    model         = Cliente
    form_class    = ClienteForm
    template_name = 'clientes/crear.html'
    success_url   = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f'Cliente "{self.object.nombre}" creado exitosamente.'
        )
        return response


class ClienteUpdateView(LoginRequiredMixin, UpdateView):
    """Edición de cliente."""

    model         = Cliente
    form_class    = ClienteForm
    template_name = 'clientes/editar.html'
    pk_url_kwarg  = 'cliente_id'
    success_url   = reverse_lazy('clientes:lista')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request, f'Cliente "{self.object.nombre}" actualizado.'
        )
        return response


# ── Borrado con permiso (W09) ────────────────────────────────────────
class ClienteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Borrado de cliente. Sin sesión → login; sin permiso → 403."""

    model               = Cliente
    template_name       = 'clientes/eliminar.html'
    pk_url_kwarg        = 'cliente_id'
    success_url         = reverse_lazy('clientes:lista')
    permission_required = 'clientes.delete_cliente'

    def form_valid(self, form):
        nombre = self.object.nombre
        try:
            response = super().form_valid(form)
        except ProtectedError:
            messages.error(
                self.request,
                f'No se puede eliminar "{nombre}": tiene ventas. '
                f'Desactívalo en su lugar.'
            )
            return redirect('clientes:detalle', cliente_id=self.object.pk)
        messages.success(self.request, f'Cliente "{nombre}" eliminado.')
        return response
