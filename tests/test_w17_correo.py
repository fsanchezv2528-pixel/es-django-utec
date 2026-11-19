"""Suite de pruebas W17 — Correos transaccionales con django-anymail.

Usa el backend locmem (en memoria) para capturar correos sin enviarlos.
Los correos enviados se almacenan en django.core.mail.outbox.
"""
from decimal import Decimal

from django.core import mail
from django.test import TestCase, override_settings

from clientes.models      import Cliente
from configuracion.models import ConfiguracionERP
from productos.models     import Categoria, Producto
from ventas.models        import Pedido
from ventas.tasks         import (
    enviar_confirmacion_pedido,
    verificar_stock_bajo,
)

EMAIL_SETTINGS = {
    'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
    'CELERY_TASK_ALWAYS_EAGER': True,
    'CELERY_TASK_EAGER_PROPAGATES': True,
    'ADMINS': [('Admin Test', 'admin@test.com')],
    'DEFAULT_FROM_EMAIL': 'test@erp.com',
}


def _crear_pedido_pagado(correo_enviado=False) -> Pedido:
    """Crea un Pedido en estado 'pagado' para los tests."""
    ConfiguracionERP.get_instance()
    n    = Pedido.objects.count()
    cat  = Categoria.objects.create(nombre=f'Cat-{n}')
    prod = Producto.objects.create(
        nombre='Producto Test', precio=Decimal('100.00'),
        stock=5, categoria=cat
    )
    cli  = Cliente.objects.create(
        nombre='Cliente Test', correo=f'cliente{n}@test.com'
    )
    return Pedido.objects.create(
        numero_pedido  = f'PED-TEST-{n:03d}',
        cliente        = cli,
        estado         = 'pagado',
        total_pagado   = Decimal('116.00'),
        correo_enviado = correo_enviado,
        items_snapshot = [
            {
                'producto_id': prod.pk,
                'nombre':      prod.nombre,
                'cantidad':    2,
                'precio':      str(prod.precio),
            }
        ],
    )


@override_settings(**EMAIL_SETTINGS)
class EnviarConfirmacionTest(TestCase):
    """Tests del envío del correo de confirmación de pedido."""

    def setUp(self):
        mail.outbox = []

    def test_correo_enviado_a_cliente(self):
        pedido = _crear_pedido_pagado()
        enviar_confirmacion_pedido.delay(pedido.pk)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(pedido.cliente.correo, mail.outbox[0].to)

    def test_correo_asunto_contiene_numero_pedido(self):
        pedido = _crear_pedido_pagado()
        enviar_confirmacion_pedido.delay(pedido.pk)

        self.assertIn(pedido.numero_pedido, mail.outbox[0].subject)

    def test_correo_cuerpo_html_contiene_total(self):
        pedido = _crear_pedido_pagado()
        enviar_confirmacion_pedido.delay(pedido.pk)

        mensaje = mail.outbox[0]
        alternativas = [
            body for body, mime in mensaje.alternatives
            if mime == 'text/html'
        ]
        self.assertEqual(len(alternativas), 1)
        self.assertIn(str(pedido.total_pagado), alternativas[0])

    def test_correo_marca_correo_enviado_true(self):
        pedido = _crear_pedido_pagado()
        self.assertFalse(pedido.correo_enviado)

        enviar_confirmacion_pedido.delay(pedido.pk)

        pedido.refresh_from_db()
        self.assertTrue(pedido.correo_enviado)

    def test_correo_no_duplicado_si_ya_enviado(self):
        pedido = _crear_pedido_pagado(correo_enviado=True)
        enviar_confirmacion_pedido.delay(pedido.pk)

        self.assertEqual(len(mail.outbox), 0)

    def test_tarea_devuelve_skip_si_ya_enviado(self):
        pedido = _crear_pedido_pagado(correo_enviado=True)
        resultado = enviar_confirmacion_pedido.delay(pedido.pk).get()

        self.assertEqual(resultado['estado'], 'skip')

    def test_segunda_ejecucion_no_duplica_correo(self):
        """Dos ejecuciones seguidas (webhook + vista) envían un solo correo."""
        pedido = _crear_pedido_pagado()
        enviar_confirmacion_pedido.delay(pedido.pk)
        enviar_confirmacion_pedido.delay(pedido.pk)

        self.assertEqual(len(mail.outbox), 1)


@override_settings(**EMAIL_SETTINGS)
class AlertaStockTest(TestCase):
    """Tests del correo de alerta de stock bajo."""

    def setUp(self):
        mail.outbox = []
        ConfiguracionERP.get_instance()

    def test_alerta_enviada_si_hay_stock_bajo(self):
        cat = Categoria.objects.create(nombre='Cat Alert')
        Producto.objects.create(
            nombre='Stock Bajo', precio=Decimal('50.00'),
            stock=2, categoria=cat
        )
        verificar_stock_bajo.delay(umbral=5)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('admin@test.com', mail.outbox[0].to)

    def test_alerta_contiene_nombre_producto(self):
        cat = Categoria.objects.create(nombre='Cat Alert2')
        Producto.objects.create(
            nombre='Teclado Escaso', precio=Decimal('200.00'),
            stock=1, categoria=cat
        )
        verificar_stock_bajo.delay(umbral=5)

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Teclado Escaso', mail.outbox[0].body)

    def test_no_alerta_si_todo_ok(self):
        cat = Categoria.objects.create(nombre='Cat OK')
        Producto.objects.create(
            nombre='Bien surtido', precio=Decimal('100.00'),
            stock=20, categoria=cat
        )
        verificar_stock_bajo.delay(umbral=5)

        self.assertEqual(len(mail.outbox), 0)