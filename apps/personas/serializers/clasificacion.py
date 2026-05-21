from rest_framework import serializers
from apps.personas.models.clasificacion import TipoDocumento, Genero, EstadoCivil, TipoPersona
from apps.personas.models.persona import PersonaTipoPersona


class TipoDocumentoModelSerializer(serializers.ModelSerializer):
    """Tipo documento model serializer."""

    class Meta:
        """Meta class."""
        model = TipoDocumento
        fields = (
            'id',
            'nombre'
        )

class GeneroModelSerializer(serializers.ModelSerializer):
    """Genero model serializer."""

    class Meta:
        """Meta class."""
        model = Genero
        fields = ('id', 'nombre')


class EstadoCivilModelSerializer(serializers.ModelSerializer):
    """EstadoCivil model serializer."""

    class Meta:
        """Meta class."""
        model = EstadoCivil
        fields = ('id', 'nombre')


class TipoPersonaSerializer(serializers.ModelSerializer):

    tipo_persona_nombre = serializers.SerializerMethodField('get_tipo_persona', read_only=True)
    def get_tipo_persona(self, obj):        
        return obj.tipo_persona.nombre

    color = serializers.SerializerMethodField('get_color', read_only=True)
    def get_color(self, obj):  
        try:          
            return obj.tipo_persona.color
        except:
            return ""
    class Meta:
        """Meta class."""
        model = PersonaTipoPersona
        fields = ('id','tipo_persona', 'persona','tipo_persona_nombre','color')



class TipoPersonaModelSerializer(serializers.ModelSerializer):
    class Meta:
        ordering = ['-id']
        model = TipoPersona
        fields = (
            "id",
            "nombre",
        )
