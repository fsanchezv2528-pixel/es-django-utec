# productos/serializers.py
"""Serializers de la app productos — W10 + W11 (imagen_url)."""
from rest_framework import serializers

from .models import Categoria, Producto


class CategoriaSerializer(serializers.ModelSerializer):
    """Serializer de Categoria — todos los campos del modelo."""

    class Meta:
        model            = Categoria
        fields           = '__all__'
        read_only_fields = ['id']


class ProductoSerializer(serializers.ModelSerializer):
    """Serializer de Producto con nombres legibles y URL absoluta de imagen."""

    categoria_nombre = serializers.CharField(source='categoria.nombre', read_only=True)
    proveedor_nombre = serializers.CharField(
        source='proveedor.nombre', read_only=True, allow_null=True, default=None
    )
    imagen_url = serializers.SerializerMethodField()

    class Meta:
        model  = Producto
        fields = [
            'id', 'nombre', 'precio', 'stock',
            'categoria', 'categoria_nombre',
            'proveedor', 'proveedor_nombre',
            'activo', 'imagen', 'imagen_url', 'creado',
        ]
        read_only_fields = ['id', 'creado']
        extra_kwargs = {
            'imagen': {'required': False, 'allow_null': True},
        }

    def get_imagen_url(self, obj: Producto) -> str | None:
        """URL absoluta de la imagen, o None si el producto no tiene."""
        if not obj.imagen:
            return None
        request = self.context.get('request')
        if request:
            return request.build_absolute_uri(obj.imagen.url)
        return obj.imagen.url
