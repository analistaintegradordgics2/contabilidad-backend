from rest_framework import serializers
from django.shortcuts import get_object_or_404
from apps.personas.models.persona import *
from apps.public.models import Archivo
import pdb
from apps.personas.serializers.contacto import *

class PersonaTributarioSerializer(serializers.ModelSerializer):
    
    reteiva = serializers.BooleanField(default=False)
    reteica = serializers.BooleanField(default=False)
    retefuente = serializers.BooleanField(default=False)
    autoretenedor = serializers.BooleanField(default=False)
    gran_contribuyente = serializers.BooleanField(default=False)
    no_contribuyente = serializers.BooleanField(default=False)

    class Meta:
        model = PersonaTributario
        fields = '__all__'


class PersonaConyugeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaConyuge
        fields = '__all__'

class PersonLaboralSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonaLaboral
        fields = '__all__'

class PersonaModelSerializer(serializers.ModelSerializer):

    ciudad_nombre = serializers.CharField(source='ciudad_expedicion.nombre', read_only=True)
    tipo_documento_nombre = serializers.CharField(source='tipo_documento.nombre', read_only=True)
    rsocial = serializers.CharField(source='n_completo', read_only=True)

    uc_id = serializers.IntegerField(read_only=False, allow_null=True, required=False)
    um_id = serializers.IntegerField(read_only=False, allow_null=True, required=False)

    telefonos = TelefonoModelSerializer(many=True,read_only=True,source='telefonos_personas')
    direcciones = DirecionModelSerializer(many=True,read_only=True,source='direcciones_personas')
    tributario = serializers.SerializerMethodField()
    conyuge = PersonaConyugeSerializer(read_only=True)
    # conyuge = PersonLaboralSerializer(read_only=True)

    class Meta:
        """Meta class."""
        model = Persona
        fields = '__all__'
    
    def get_tributario(self, obj):

        try:

            tributario = obj.personatributario

            return PersonaTributarioSerializer(
                tributario
            ).data

        except PersonaTributario.DoesNotExist:

            return PersonaTributarioSerializer().data


class ArchivoPersonaSerializer(serializers.Serializer):
    src = serializers.FileField()

    def validate(self, validated_data):
        validated_data['name'] = validated_data['src'].name
        self.context['archivo'] = validated_data
        return validated_data

    def save(self, **kwargs):
        obj_persona = get_object_or_404(Persona, pk=kwargs['persona_id'])
        t1 = Archivo(content_object=obj_persona, uc=kwargs['uc'], tipo=kwargs['tipo'], **self.context['archivo'])
        t1.save()
        return obj_persona.archivos.all()

    class Meta:
        """Meta class."""
        fields = ('name', 'src')




