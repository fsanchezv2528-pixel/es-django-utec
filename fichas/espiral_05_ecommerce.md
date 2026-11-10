# Ficha de Sistematización — Espiral 5
## ERP Django · Espiral E5: E-commerce y Pagos

| Campo | Contenido |
|---|---|
| **Número de espiral** | 5 |
| **Nombre del ciclo** | E-commerce y Pagos |
| **Semanas** | W13 – W15 |
| **Fecha de inicio** | ___/___/_____ |
| **Fecha de cierre** | 09/11/2026 |
| **Responsable** | Felipe Sánchez Vázquez |
| **Asesor** | MC. Román Fernando López González |

## 1. Objetivo del ciclo
Implementar el canal de e-commerce completo: catálogo público filtrable,
carrito de compras en sesión, proceso de pago con Stripe y confirmación
automática vía webhook con descuento de stock.

## 2. Tareas realizadas

| # | Tarea | Estado | Semana |
|---|---|---|---|
| 1 | App catalogo + django-filter | ✅ | W13 |
| 2 | CatalogoView pública con filtros | ✅ | W13 |
| 3 | Carrito en sesión (5 vistas) | ✅ | W13 |
| 4 | Context processor carrito_info | ✅ | W13 |
| 5 | Templates catálogo + carrito | ✅ | W13 |
| 6 | pip install stripe | ✅ | W14 |
| 7 | CheckoutView con PaymentIntent | ✅ | W14 |
| 8 | Template checkout.html con Stripe.js | ✅ | W14 |
| 9 | pago_exitoso + pago_error | ✅ | W14 |
| 10 | items_snapshot en Pedido + migración 0003 | ✅ | W15 |
| 11 | Webhook endpoint con verificación de firma | ✅ | W15 |
| 12 | Descuento de stock con F() | ✅ | W15 |
| 13 | Tests con mock (Stripe + webhook) | ✅ | W15 |

## 3. Evidencias
- Sitio desplegado: https://felipelxng.onrender.com/catalogo/
- Webhook verificado en local con Stripe CLI (`stripe listen`)
- Tests: Ran 157 tests → OK
- Pedido 'pendiente' → 'pagado' via webhook verificado en /admin/
- Pedido 'pendiente' → 'cancelado' con tarjeta de rechazo (4000 0000 0000 9995)
- Stock decrementado verificado en /admin/productos/

## 4. Criterios de aceptación

| Criterio | Estado |
|---|---|
| GET /catalogo/ sin auth → 200 | ✅ |
| Filtro por nombre/categoría/precio | ✅ |
| Agregar/remover/actualizar carrito | ✅ |
| Tarjeta 4242 → pago exitoso | ✅ |
| Webhook payment_intent.succeeded → Pedido 'pagado' | ✅ |
| Stock decrementado con F() (atómico) | ✅ |
| Firma inválida → 400 | ✅ |
| 157 tests OK | ✅ |

## 5. Problemas encontrados
1. **Red bloqueada.** La red del aula bloqueaba GitHub y Stripe
   (`Failed to connect to github.com:443`, `Connection to api.stripe.com
   timed out`). Se resolvió cambiando de red para el push y para la CLI.
2. **Llaves de Stripe sin configurar.** El `.env` tenía `sk_test_...` y
   `pk_test_...` de ejemplo y daba `Invalid API Key`. Se pegaron las
   llaves reales del sandbox en `STRIPE_SECRET_KEY` y
   `STRIPE_PUBLISHABLE_KEY`.
3. **Plantilla vacía.** `pago_error.html` pesaba 0 bytes y la página salía
   en blanco. Se completó con el contenido de la guía.
4. **Librería `stripe` dañada.** Con `stripe==7.8.0` el pago fallaba con
   `'NoneType' object has no attribute 'Secret'`. Se reinstaló y se
   actualizó a `stripe==16.1.0`; las pruebas siguieron pasando.
5. **Stripe CLI nueva.** La versión 1.55.9 exige `--events` en
   `stripe listen`. Se usó
   `--events payment_intent.succeeded,payment_intent.payment_failed`.

## 6. Lecciones aprendidas
1.
2.
3.

## 7. Tiempo total invertido

| Categoría | Horas |
|---|---|
| Diseño | |
| Implementación | |
| Pruebas | |
| Documentación | |
| **Total Espiral 5** | |
