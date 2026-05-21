from rest_framework import serializers

from apps.personas.models.contacto import TipoContacto, Telefono, Direccion, DatosContactoPersona, DatosContactoPersonaPersonas
from apps.parametros.serializers.ubicacion import CiudadModelSerializer


class DatosContactoPersonaSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class."""
        model = DatosContactoPersona
        fields = "__all__"

class DatosContactoPersonaPersonasSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class."""
        model = DatosContactoPersonaPersonas
        fields = "__all__"

class TipoContactoModelSerializer(serializers.ModelSerializer):
    """EstadoCivil model serializer."""

    class Meta:
        """Meta class."""
        model = TipoContacto
        fields = ('id', 'nombre')


class DirecionModelSerializer(serializers.ModelSerializer):

    uc_id = serializers.IntegerField(read_only=False, allow_null=True, required=False)
    um_id = serializers.IntegerField(read_only=False, allow_null=True, required=False)
    
    direccion_ciudad = serializers.SerializerMethodField('get_direccion_ciudad', read_only=True)
    def get_direccion_ciudad(self, obj):  
        try:          
            return CiudadModelSerializer(obj.ciudad).data
        except:
            return {}

    class Meta:
        ordering = ['-id']
        model = Direccion
        fields = (
            "id",
            "persona",
            "tipo",
            "barrio",
            "ciudad",
            "descripcion",
            "codigo_postal",
            "incluir_a_factura",
            "direccion_ciudad",
            "uc_id",
            "um_id",
            "eliminado",
            "usar_en_portales",
        )


class TelefonoModelSerializer(serializers.ModelSerializer):

    uc_id = serializers.IntegerField(read_only=False, allow_null=True,required=False)
    um_id = serializers.IntegerField(read_only=False, allow_null=True,required=False)

    class Meta:
        ordering = ['-id']
        model = Telefono
        fields = (
            "id",
            "persona",
            "tipo",
            "valor",
            "sms",
            "prefijo",
            "uc_id",
            "um_id",
            "eliminado",
            "usar_en_portales"
        )
