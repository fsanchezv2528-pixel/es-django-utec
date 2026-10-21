# Sprint 2 Retrospective — ERP Django
## Semanas W07–W09 · Espiral 3: CRUD Web y Autenticación

**Fecha:** 20/10/2026
**Responsable:** Felipe Sánchez Vázquez

## ¿Qué funcionó bien? (Keep)
1. select_related() en W07 evitó queries N+1 desde el inicio.
2. reverse_lazy() en los CBV evitó el error ImproperlyConfigured.
3. El management command crear_grupos permite configurar roles
   en producción sin tocar el admin.

## ¿Qué mejorar? (Improve)
1. Documentar el orden de LoginRequiredMixin + PermissionRequiredMixin.
2. Agregar un template 403.html con el diseño del ERP.
3. Revisar los tests viejos cada vez que cambian vistas o templates
   (los tests de W02 fallaron al reemplazar index.html por lista.html).

## Acción de mejora (Kaizen) para Sprint 3
> "En el Sprint 3 (DRF), documentaré los endpoints con docstrings
>  desde el inicio, no al final."

## Velocidad del Sprint 2

| HU | Pts plan. | Pts ent. |
|---|---|---|
| HU-E3-01 Lista productos | 2 | 2 |
| HU-E3-02 Detalle producto | 2 | 2 |
| HU-E3-03 Listas clientes y proveedores | 2 | 2 |
| HU-E3-04 Detalle venta con líneas | 3 | 3 |
| HU-E3-05 Crear y editar productos | 3 | 3 |
| HU-E3-06 Registrar ventas | 5 | 5 |
| HU-E3-07 Eliminar con confirmación | 2 | 2 |
| HU-E3-08 Autenticación login/logout | 3 | 3 |
| HU-E3-09 3 roles con permisos | 5 | 5 |
| **Total** | **27** | **27** |

**Velocidad Sprint 2:** 27 puntos
**Velocidad acumulada (S0+S1+S2):** 58 puntos
