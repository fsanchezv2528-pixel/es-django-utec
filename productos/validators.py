# productos/validators.py
"""Validadores de archivos de imagen para la app productos — W11.

Valida:
    - Tamaño máximo (5 MB)
    - Tipo real del archivo por sus primeros bytes (no por la extensión)
    - Que Pillow pueda abrirlo (imagen no corrupta)
"""
import filetype
from PIL import Image

from django.core.exceptions import ValidationError

MAX_IMAGE_SIZE = 5 * 1024 * 1024   # 5 MB

FORMATOS_MIME_PERMITIDOS = {'image/jpeg', 'image/png', 'image/webp'}


def validar_imagen_producto(archivo) -> None:
    """Valida un archivo subido como imagen de producto.

    Raises:
        ValidationError: si el archivo es muy grande, no es JPEG/PNG/WEBP
                         o está corrupto.
    """
    # Una imagen ya guardada (al editar sin subir otra) ya se validó
    # cuando se subió: no se vuelve a leer del disco.
    if getattr(archivo, '_committed', False):
        return

    # 1. Tamaño
    if archivo.size > MAX_IMAGE_SIZE:
        raise ValidationError(
            f'La imagen supera el tamaño máximo permitido de 5 MB. '
            f'Tamaño recibido: {archivo.size / (1024 * 1024):.1f} MB.'
        )

    # 2. Tipo real por "magic bytes"
    archivo.seek(0)
    cabecera = archivo.read(512)
    archivo.seek(0)

    tipo = filetype.guess(cabecera)
    if tipo is None or tipo.mime not in FORMATOS_MIME_PERMITIDOS:
        mime_detectado = tipo.mime if tipo else 'desconocido'
        raise ValidationError(
            f'Tipo de archivo no permitido: {mime_detectado}. '
            f'Solo se aceptan: JPEG, PNG, WEBP.'
        )

    # 3. Que Pillow lo pueda abrir
    archivo.seek(0)
    try:
        Image.open(archivo).verify()
    except Exception as exc:
        raise ValidationError(
            f'El archivo no es una imagen válida o está corrupto: {exc}'
        )
    finally:
        archivo.seek(0)   # para que Django pueda guardar el archivo completo
