"""Management command para crear los 3 grupos de acceso del ERP.

Uso:
    python manage.py crear_grupos

    Gerente  → acceso completo a las apps del ERP
    Vendedor → registrar ventas, consultar productos y clientes
    Almacén  → gestionar inventario de productos

Se puede correr las veces que sea: crea o actualiza los grupos.
"""
from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

APPS_ERP = ['clientes', 'proveedores', 'productos', 'ventas', 'configuracion']


def _permisos(app_label, modelos, acciones):
    """Permisos <accion>_<modelo> de una app.

    Ej.: _permisos('ventas', ['venta'], ['add', 'view'])
         → ventas.add_venta, ventas.view_venta
    """
    return Permission.objects.filter(
        content_type__app_label=app_label,
        codename__in=[f'{a}_{m}' for m in modelos for a in acciones],
    )


class Command(BaseCommand):
    help = 'Crea o actualiza los 3 grupos de acceso del ERP'

    def _grupo(self, nombre, permisos):
        grupo, creado = Group.objects.get_or_create(name=nombre)
        permisos = permisos.distinct()
        grupo.permissions.set(permisos)
        self.stdout.write(self.style.SUCCESS(
            f'  ✅ {nombre} — {permisos.count()} permisos asignados '
            f'({"creado" if creado else "actualizado"})'
        ))

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING(
            '\nConfigurando grupos de acceso del ERP...\n'
        ))

        # GERENTE: add/change/delete/view de todas las apps del ERP
        self._grupo('Gerente', Permission.objects.filter(
            content_type__app_label__in=APPS_ERP
        ))

        # VENDEDOR: operar ventas, consultar productos y clientes
        self._grupo('Vendedor',
            _permisos('ventas', ['venta', 'detalleventa'], ['add', 'view'])
            | _permisos('productos', ['producto'], ['view'])
            | _permisos('clientes', ['cliente'], ['view'])
        )

        # ALMACÉN: gestionar inventario
        self._grupo('Almacén',
            _permisos('productos', ['producto', 'categoria'], ['add', 'change', 'view'])
            | _permisos('proveedores', ['proveedor'], ['view'])
        )

        self.stdout.write(self.style.SUCCESS(
            '\n🎉 Grupos configurados exitosamente.\n'
            'Asigna usuarios desde /admin/ → Usuarios → Grupos.\n'
        ))
