"""Suite de pruebas W13 — Catálogo público y carrito de compras.

Ejecutar con:
    python manage.py test tests.test_w13_ecommerce --verbosity=2

Resultado esperado: Ran 9 tests ... OK
"""
from decimal import Decimal

from django.test import TestCase
from django.urls import reverse

from productos.models import Categoria, Producto


class CatalogoPublicoTest(TestCase):

    def setUp(self):
        cat = Categoria.objects.create(nombre='Electrónica')
        Producto.objects.create(nombre='Laptop', precio=Decimal('10000.00'), stock=5, categoria=cat)
        Producto.objects.create(nombre='Mouse', precio=Decimal('250.00'), stock=20, categoria=cat)
        Producto.objects.create(nombre='Producto Inactivo', precio=Decimal('100.00'),
                                stock=5, categoria=cat, activo=False)

    def _nombres(self, **params):
        r = self.client.get(reverse('catalogo:catalogo'), params)
        self.assertEqual(r.status_code, 200)
        return [p.nombre for p in r.context['productos']]

    def test_catalogo_accesible_sin_auth(self):
        r = self.client.get(reverse('catalogo:catalogo'))
        self.assertEqual(r.status_code, 200)

    def test_catalogo_solo_muestra_activos(self):
        nombres = self._nombres()
        self.assertIn('Laptop', nombres)
        self.assertNotIn('Producto Inactivo', nombres)

    def test_catalogo_filtro_por_nombre(self):
        nombres = self._nombres(nombre='lapt')
        self.assertIn('Laptop', nombres)
        self.assertNotIn('Mouse', nombres)

    def test_catalogo_filtro_por_precio_max(self):
        nombres = self._nombres(precio_max=500)
        self.assertIn('Mouse', nombres)
        self.assertNotIn('Laptop', nombres)


class CarritoTest(TestCase):

    def setUp(self):
        cat = Categoria.objects.create(nombre='Cat')
        self.prod = Producto.objects.create(nombre='Teclado', precio=Decimal('350.00'),
                                            stock=10, categoria=cat)

    def _agregar(self, cantidad):
        self.client.post(reverse('catalogo:agregar', args=[self.prod.pk]), {'cantidad': cantidad})

    def _carrito(self):
        return self.client.get(reverse('catalogo:carrito'))

    def test_carrito_vacio_al_inicio(self):
        r = self._carrito()
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context['items'], [])

    def test_agregar_producto_incrementa_carrito(self):
        self._agregar(2)
        items = self._carrito().context['items']
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]['cantidad'], 2)

    def test_agregar_mismo_producto_acumula_cantidad(self):
        self._agregar(1)
        self._agregar(3)
        self.assertEqual(self._carrito().context['items'][0]['cantidad'], 4)

    def test_carrito_calcula_total_correcto(self):
        self._agregar(2)
        self.assertEqual(self._carrito().context['total'], Decimal('700.00'))

    def test_remover_producto_lo_elimina(self):
        self._agregar(1)
        self.client.post(reverse('catalogo:remover', args=[self.prod.pk]))
        self.assertEqual(self._carrito().context['items'], [])
