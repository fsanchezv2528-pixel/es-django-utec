"""Suite de pruebas W11 — ImageField, validador y API media.

Ejecutar con:
    python manage.py test tests.test_w11_media --verbosity=2

Resultado esperado: Ran 8 tests ... OK
"""
import io
import os
from decimal import Decimal

from PIL import Image

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient, APITestCase

from productos.models     import Categoria, Producto
from productos.validators import validar_imagen_producto


def _imagen(nombre='img.jpg', formato='JPEG', content_type='image/jpeg',
            size=(100, 100)) -> SimpleUploadedFile:
    buf = io.BytesIO()
    Image.new('RGB', size, color='teal').save(buf, format=formato)
    buf.seek(0)
    return SimpleUploadedFile(nombre, buf.read(), content_type=content_type)


def _archivo_invalido() -> SimpleUploadedFile:
    return SimpleUploadedFile(
        'notimage.exe', b'\x00\x01fake binary content\xff\xfe',
        content_type='application/octet-stream'
    )


def _borrar_imagenes():
    for prod in Producto.objects.exclude(imagen=''):
        if prod.imagen:
            try:
                os.remove(prod.imagen.path)
            except (FileNotFoundError, NotImplementedError, ValueError):
                pass


# ── Validador ─────────────────────────────────────────────────────────
class ValidadorImagenTest(TestCase):

    def test_imagen_jpeg_valida_pasa(self):
        validar_imagen_producto(_imagen())

    def test_imagen_png_valida_pasa(self):
        validar_imagen_producto(_imagen('img.png', 'PNG', 'image/png'))

    def test_archivo_no_imagen_lanza_error(self):
        with self.assertRaises(ValidationError) as ctx:
            validar_imagen_producto(_archivo_invalido())
        self.assertIn('no permitido', str(ctx.exception).lower())

    def test_imagen_muy_grande_lanza_error(self):
        archivo = _imagen()
        archivo.size = 6 * 1024 * 1024   # simular 6 MB
        with self.assertRaises(ValidationError) as ctx:
            validar_imagen_producto(archivo)
        self.assertIn('5 mb', str(ctx.exception).lower())


# ── Modelo ────────────────────────────────────────────────────────────
class ProductoImagenModelTest(TestCase):

    def setUp(self):
        self.cat = Categoria.objects.create(nombre='Cat Media')

    def tearDown(self):
        _borrar_imagenes()

    def test_producto_sin_imagen_es_valido(self):
        prod = Producto.objects.create(
            nombre='Sin imagen', precio=Decimal('100.00'), stock=5, categoria=self.cat
        )
        self.assertFalse(bool(prod.imagen))

    def test_producto_puede_guardarse_con_imagen(self):
        prod = Producto(
            nombre='Con imagen', precio=Decimal('200.00'), stock=3,
            categoria=self.cat, imagen=_imagen()
        )
        prod.save()
        self.assertTrue(bool(prod.imagen))
        self.assertIn('productos/', prod.imagen.name)


# ── API ───────────────────────────────────────────────────────────────
class ProductoAPIImagenTest(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.cat    = Categoria.objects.create(nombre='Cat API')

    def tearDown(self):
        _borrar_imagenes()

    def test_api_devuelve_imagen_url_none_sin_imagen(self):
        prod = Producto.objects.create(
            nombre='Sin img API', precio=Decimal('100.00'), stock=5, categoria=self.cat
        )
        r = self.client.get(f'/api/productos/{prod.pk}/')
        self.assertEqual(r.status_code, 200)
        self.assertIsNone(r.json().get('imagen_url'))

    def test_api_devuelve_imagen_url_con_imagen(self):
        prod = Producto(
            nombre='Con img API', precio=Decimal('300.00'), stock=2,
            categoria=self.cat, imagen=_imagen()
        )
        prod.save()
        r = self.client.get(f'/api/productos/{prod.pk}/')
        self.assertEqual(r.status_code, 200)
        url = r.json().get('imagen_url')
        self.assertIsNotNone(url)
        self.assertTrue(url.startswith('http'))
        self.assertIn('productos/', url)
