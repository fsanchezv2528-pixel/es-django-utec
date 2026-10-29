# Sprint 3 Retrospective — ERP Django
## Semanas W10–W12 · Espiral 4: API REST y Media

**Responsable:** Felipe Sánchez Vázquez

## ¿Qué funcionó bien? (Keep)
1. Las vistas genéricas de DRF dieron una API completa con poco código.
2. El validador de imágenes revisa el tipo real del archivo, no la extensión.
3. El motor de PDF quedó desacoplado: usa WeasyPrint si existe y xhtml2pdf si no.

## ¿Qué mejorar? (Improve)
1. Instalar Docker/WSL2 requiere permisos de administrador que el equipo
   del aula no tiene; hay que coordinarlo con el laboratorio.
2. Las imágenes en Render se pierden en cada deploy (disco efímero);
   falta configurar un bucket S3.
3. Problemas de red al hacer push: tener a mano el hotspot del celular.

## Acción de mejora (Kaizen) para Sprint 4
> "Antes de cada sesión verificaré la conexión a GitHub y que Render
>  despliegue correctamente."

## Velocidad del Sprint 3

| HU | Pts plan. | Pts ent. |
|---|---|---|
| HU-E4-01 Listar productos vía API | 2 | 2 |
| HU-E4-02 Crear productos con token | 3 | 3 |
| HU-E4-03 API clientes/proveedores/ventas | 3 | 3 |
| HU-E4-04 Subir imagen de producto | 3 | 3 |
| HU-E4-05 Imagen en la API | 2 | 2 |
| HU-E4-06 Factura en PDF | 5 | 5 |
| HU-E4-07 Exportar inventario a Excel | 3 | 3 |
| **Total** | **21** | **21** |
