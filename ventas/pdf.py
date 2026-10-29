# ventas/pdf.py
"""Conversión HTML → PDF para el ERP — W12.

Motor:
    1. WeasyPrint, si está instalado y tiene sus librerías nativas
       (Docker / Linux). Es el motor oficial de la guía W12.
    2. xhtml2pdf como respaldo (Windows sin Docker). La guía W12 lo
       documenta como fallback para equipos donde Docker no es viable.
"""
import io
import os

from django.conf import settings
from django.contrib.staticfiles import finders


def _link_callback(uri, rel):
    """Convierte /media/... y /static/... en rutas de archivo para xhtml2pdf."""
    media_url  = settings.MEDIA_URL or '/media/'
    static_url = settings.STATIC_URL or '/static/'
    if uri.startswith(media_url):
        ruta = os.path.join(settings.MEDIA_ROOT, uri[len(media_url):])
    elif uri.startswith(static_url):
        relativa = uri[len(static_url):]
        ruta = finders.find(relativa) or os.path.join(settings.STATIC_ROOT, relativa)
    else:
        return uri
    return ruta if ruta and os.path.isfile(ruta) else uri


def html_a_pdf(html: str, base_url: str | None = None) -> tuple[bytes, str]:
    """Genera el PDF y devuelve (bytes, nombre_del_motor)."""
    try:
        import weasyprint
        pdf = weasyprint.HTML(string=html, base_url=base_url).write_pdf()
        return pdf, 'weasyprint'
    except (ImportError, OSError):
        pass   # sin WeasyPrint o sin sus librerías nativas → respaldo

    from xhtml2pdf import pisa
    buffer = io.BytesIO()
    resultado = pisa.CreatePDF(
        html, dest=buffer, encoding='utf-8', link_callback=_link_callback
    )
    if resultado.err:
        raise RuntimeError('xhtml2pdf no pudo generar el PDF')
    return buffer.getvalue(), 'xhtml2pdf'
