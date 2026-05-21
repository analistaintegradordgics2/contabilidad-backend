from rest_framework import serializers
import pdb
from apps.parametros.models.ubicacion import Ciudad, Zona, Barrio, TipoVia


class CiudadModelSerializer(serializers.ModelSerializer):
     
    class Meta:
        """Meta class."""
        model = Ciudad
        fields = ('id', 'nombre')

class ZonaModelSerializer(serializers.ModelSerializer):
    ciudad_id = serializers.IntegerField(required=True)
    ciudad    = serializers.SlugRelatedField(
        read_only=True,
        slug_field='nombre'
    )

    class Meta:
        """Meta class."""
        model = Zona
        fields = ('id', 'nombre', 'ciudad_id', 'ciudad')
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['nombre'] = data['nombre'].capitalize() if data['nombre'] else None
        return data
    
    def validate(self, data):
        nombre = data['nombre'].strip().lower()
        ciudad = data['ciudad']

        existe = Zona.objects.filter(
            nombre__iexact=nombre,
            ciudad=ciudad
        ).exclude(id=self.instance.id if self.instance else None)

        if existe.exists():
            raise serializers.ValidationError("La zona ya existe")

        return data


class BarrioModelSerializer(serializers.ModelSerializer):
    zonas_id = serializers.IntegerField(required=True)
    zonas = serializers.SlugRelatedField(
        read_only=True,
        slug_field='nombre'
    )

    ciudad_id = serializers.IntegerField(required=True)
    ciudad = serializers.SlugRelatedField(
        read_only=True,
        slug_field='nombre'
    )
    
    class Meta:
        """Meta class."""
        model = Barrio
        fields = ('id', 'nombre', 'ciudad', 'ciudad_id', 'zonas_id','zonas')

class TipoViaModelSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class."""
        model = TipoVia
        fields = "__all__"
