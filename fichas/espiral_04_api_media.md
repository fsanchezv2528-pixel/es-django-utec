# Ficha de Sistematización — Espiral 4
## ERP Django · Espiral E4: API REST y Media

| Campo | Contenido |
|---|---|
| **Número de espiral** | 4 |
| **Nombre del ciclo** | API REST y Media |
| **Semanas** | W10 – W12 |
| **Fecha de inicio** | ___/___/_____ |
| **Fecha de cierre** | ___/___/_____ |
| **Responsable** | Felipe Sánchez Vázquez |
| **Asesor** | MC. Román Fernando López González |

## 1. Objetivo del ciclo
Exponer el ERP como API REST con autenticación por token, gestionar
imágenes de productos y generar documentos (factura PDF e inventario Excel).

## 2. Tareas realizadas

| # | Tarea | Estado | Semana |
|---|---|---|---|
| 1 | rest_framework.authtoken + REST_FRAMEWORK | ✅ | W10 |
| 2 | Serializers × 5 entidades | ✅ | W10 |
| 3 | API Views + /api/ + token | ✅ | W10 |
| 4 | ImageField + validador MIME/tamaño | ✅ | W11 |
| 5 | imagen_url en la API + preview en admin | ✅ | W11 |
| 6 | django-storages listo para S3 | ✅ | W11 |
| 7 | Factura PDF | ✅ | W12 |
| 8 | Exportación Excel con openpyxl | ✅ | W12 |

## 3. Evidencias
- URL pública: https://es-django-utec.onrender.com
- API: /api/productos/ · /api/auth/token/
- Tests: Ran 131 tests → OK

## 4. Problemas encontrados
1. El equipo del aula no tiene Docker ni WSL2 y no se tienen permisos de
   administrador → el PDF usa xhtml2pdf, el respaldo que la guía W12 documenta.
2. Conexión intermitente a GitHub → se resolvió cambiando de red.

## 5. Lecciones aprendidas
1.
2.
3.
