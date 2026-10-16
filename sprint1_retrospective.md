# Sprint 1 Retrospective — ERP Django
## Semanas W04–W06 · Espiral 2: Modelado de Datos y ORM

**Fecha:** 16/10/2026

> Borrador: tuve dificultades en el .txt

## ¿Qué funcionó bien? (Keep)
1. Diseñar el diagrama ER y documentar las decisiones antes de escribir código evitó rehacer modelos en W05.
2. Los tests desde W04 (43) hasta W05 (55) dieron confianza para migrar sin romper lo anterior.
3. Jazzmin mejora significativamente la UX del admin.

## ¿Qué mejorar? (Improve)
1. Revisar las dependencias de cada modelo antes de correr `check` (el `ImageField` de ConfiguracionERP exigía Pillow y bloqueó las migraciones hasta instalarla).
2. Ejecutar `full_clean()` en los tests desde el principio (no solo `save()`).
3. Hacer el push a GitHub con tiempo: una falla de red retrasó el cierre de W05.

## Acción de mejora (Kaizen) para Sprint 2
> "En el Sprint 2, voy a instalar y registrar en requirements.txt cualquier
>  dependencia nueva antes de correr check o migrate, y voy a probar la
>  conexión a GitHub antes de la hora de cierre."

## Velocidad del Sprint 1

| HU | Puntos planificados | Puntos entregados |
|---|---|---|
| HU-E2-01 Diagrama ER aprobado | 3 | 3 |
| HU-E2-02 Modelo Cliente | 2 | 2 |
| HU-E2-03 Modelo Proveedor | 2 | 2 |
| HU-E2-04 Modelo Categoria | 1 | 1 |
| HU-E2-05 Modelo Producto | 3 | 3 |
| HU-E2-06 Modelos Venta + Detalle | 5 | 5 |
| HU-E2-07 Suite ≥ 15 tests | 3 | 3 |
| HU-E2-08 Admin con Jazzmin | 2 | 2 |
| **Total** | **21** | **21** |

**Velocidad del equipo Sprint 1:** 21 puntos
**Velocidad acumulada (S0 + S1):** 31 puntos
