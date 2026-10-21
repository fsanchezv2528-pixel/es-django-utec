"""Suite de pruebas W08 — Vistas de escritura: Create, Update, Delete.

Actualizado en W09: los usuarios de prueba que borran productos o crean
ventas ahora necesitan el permiso correspondiente (RBAC).

Ejecutar con:
    python manage.py test tests.test_w08_escritura --verbosity=2
"""
from decimal import Decimal

from django.contrib.auth.models import Permission, User
from django.test import TestCase
from django.urls import reverse

from clientes.models    import Cliente
from productos.models   import Categoria, Producto
from proveedores.models import Proveedor
from ventas.models      import Venta


def _dar_permiso(user, app_label, codename):
    user.user_permissions.add(
        Permission.objects.get(content_type__app_label=app_label, codename=codename)
    )


class ProductoEscrituraTest(TestCase):
    """Tests de Create, Update y Delete de Producto."""

    def setUp(self):
        self.user = User.objects.create_user('testuser', password='testpass123')
        _dar_permiso(self.user, 'productos', 'delete_producto')
        self.cat  = Categoria.objects.create(nombre='Cat Test')
        self.prod = Producto.objects.create(
            nombre='Laptop', precio=Decimal('10000.00'),
            stock=5, categoria=self.cat
        )

    def test_crear_sin_auth_redirige_a_login(self):
        r = self.client.get(reverse('productos:crear'))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    def test_editar_sin_auth_redirige_a_login(self):
        r = self.client.get(reverse('productos:editar', args=[self.prod.pk]))
        self.assertEqual(r.status_code, 302)
        self.assertIn('/accounts/login/', r['Location'])

    def test_crear_con_auth_http_200(self):
        self.client.force_login(self.user)
        r = self.client.get(reverse('productos:crear'))
        self.assertEqual(r.status_code, 200)
        self.assertTemplateUsed(r, 'productos/crear.html')

    def test_post_valido_crea_producto(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse('productos:crear'), {
            'nombre':    'Monitor 4K',
            'precio':    '5500.00',
            'stock':     '3',
            'categoria': self.cat.pk,
            'activo':    True,
        })
        self.assertRedirects(r, reverse('productos:lista'))
        self.assertTrue(Producto.objects.filter(nombre='Monitor 4K').exists())

    def test_post_invalido_muestra_errores(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse('productos:crear'), {
            'nombre':    'Producto mal',
            'precio':    '-100.00',
            'stock':     '5',
            'categoria': self.cat.pk,
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn('precio', r.context['form'].errors)
        self.assertFalse(Producto.objects.filter(nombre='Producto mal').exists())

    def test_delete_elimina_producto(self):
        self.client.force_login(self.user)
        pk = self.prod.pk
        r  = self.client.post(reverse('productos:eliminar', args=[pk]))
        self.assertRedirects(r, reverse('productos:lista'))
        self.assertFalse(Producto.objects.filter(pk=pk).exists())


class ClienteEscrituraTest(TestCase):
    """Tests de CreateView de Cliente."""

    def setUp(self):
        self.user = User.objects.create_user('userC', password='pass')

    def test_crear_cliente_sin_auth_redirige(self):
        r = self.client.get(reverse('clientes:crear'))
        self.assertEqual(r.status_code, 302)

    def test_post_valido_crea_cliente(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse('clientes:crear'), {
            'nombre': 'María López',
            'correo': 'maria@test.com',
            'activo': True,
        })
        self.assertRedirects(r, reverse('clientes:lista'))
        self.assertTrue(Cliente.objects.filter(correo='maria@test.com').exists())

    def test_post_correo_duplicado_muestra_error(self):
        Cliente.objects.create(nombre='Ana', correo='dup@test.com')
        self.client.force_login(self.user)
        r = self.client.post(reverse('clientes:crear'), {
            'nombre': 'Otro',
            'correo': 'dup@test.com',
            'activo': True,
        })
        self.assertEqual(r.status_code, 200)
        self.assertIn('correo', r.context['form'].errors)


class ProveedorEscrituraTest(TestCase):
    """Tests de CreateView y DeleteView de Proveedor."""

    def setUp(self):
        self.user = User.objects.create_user('userP', password='pass')
        self.prov = Proveedor.objects.create(nombre='Prov Test', correo='prov@test.com')

    def test_crear_proveedor_sin_auth_redirige(self):
        r = self.client.get(reverse('proveedores:crear'))
        self.assertEqual(r.status_code, 302)

    def test_delete_proveedor_con_auth(self):
        self.client.force_login(self.user)
        pk = self.prov.pk
        r  = self.client.post(reverse('proveedores:eliminar', args=[pk]))
        self.assertRedirects(r, reverse('proveedores:lista'))
        self.assertFalse(Proveedor.objects.filter(pk=pk).exists())


class VentaEscrituraTest(TestCase):
    """Tests de crear_venta."""

    def setUp(self):
        self.user = User.objects.create_user('userV', password='pass')
        _dar_permiso(self.user, 'ventas', 'add_venta')
        cat       = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(
            nombre='P', precio=Decimal('100.00'), stock=5, categoria=cat
        )
        self.cli  = Cliente.objects.create(nombre='C', correo='c@t.com')

    def test_crear_venta_sin_auth_redirige(self):
        r = self.client.get(reverse('ventas:crear'))
        self.assertEqual(r.status_code, 302)

    def test_post_valido_crea_venta(self):
        self.client.force_login(self.user)
        r = self.client.post(reverse('ventas:crear'), {
            'cliente':         self.cli.pk,
            'producto':        self.prod.pk,
            'cantidad':        2,
            'precio_unitario': '100.00',
        })
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Venta.objects.count(), 1)
        self.assertEqual(Venta.objects.first().total, Decimal('200.00'))
