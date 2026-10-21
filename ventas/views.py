# ventas/views.py
"""Vistas de la app ventas — W07 (lectura) + W08 (escritura) + W09 (permisos)."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import DeleteView, DetailView, ListView

from .forms import DetalleVentaForm, VentaForm
from .models import Venta


# ── Lectura (W07) ────────────────────────────────────────────────────
class VentaListView(ListView):
    """Lista paginada de ventas, más recientes primero."""

    model               = Venta
    template_name       = 'ventas/lista.html'
    context_object_name = 'ventas'
    paginate_by         = 20

    def get_queryset(self):
        return Venta.objects.select_related('cliente').order_by('-fecha')


class VentaDetailView(DetailView):
    """Detalle de una venta con sus líneas."""

    model               = Venta
    template_name       = 'ventas/detalle.html'
    context_object_name = 'venta'
    pk_url_kwarg        = 'venta_id'

    def get_queryset(self):
        return (
            Venta.objects
            .select_related('cliente')
            .prefetch_related('detalles__producto')
        )


# ── Escritura con permisos (W09) ─────────────────────────────────────
@login_required
@permission_required('ventas.add_venta', raise_exception=True)
def crear_venta(request):
    """Crea una venta con una línea de detalle (2 formularios).

    Los decoradores se revisan de arriba hacia abajo:
        @login_required       → sin sesión: redirige a /accounts/login/
        @permission_required  → con sesión sin 'add_venta': HTTP 403
    """
    venta_form   = VentaForm(request.POST or None)
    detalle_form = DetalleVentaForm(request.POST or None)

    if request.method == 'POST':
        if venta_form.is_valid() and detalle_form.is_valid():
            venta         = venta_form.save()
            detalle       = detalle_form.save(commit=False)
            detalle.venta = venta
            detalle.save()
            messages.success(
                request,
                f'Venta #{venta.pk} registrada. Total: ${venta.total:.2f}'
            )
            return redirect('ventas:detalle', venta_id=venta.pk)

    return render(request, 'ventas/crear.html', {
        'venta_form':   venta_form,
        'detalle_form': detalle_form,
    })


class VentaDeleteView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    """Borrado de venta (detalles en CASCADE). Sin permiso → 403."""

    model               = Venta
    template_name       = 'ventas/eliminar.html'
    pk_url_kwarg        = 'venta_id'
    success_url         = reverse_lazy('ventas:lista')
    permission_required = 'ventas.delete_venta'

    def form_valid(self, form):
        pk       = self.object.pk
        response = super().form_valid(form)
        messages.success(self.request, f'Venta #{pk} eliminada.')
        return response
