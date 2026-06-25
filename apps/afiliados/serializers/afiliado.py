from rest_framework import serializers
from apps.personas.models.persona import PersonaTipoPersona, Persona
from apps.afiliados.models import Afiliado
from apps.afiliados.serializers.causacion import AfiliadoConceptoCausacionSerializer

import pdb

class AfiliadoModelSerializer(serializers.ModelSerializer):
    conceptos_causacion = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    class Meta:
        model = Afiliado
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        
        if instance.tipo_contrato:
            representation['tipo_contrato'] = {
                'id': instance.tipo_contrato.id,
                'nombre': instance.tipo_contrato.nombre
            }
            
        if instance.aplicativo:
            representation['aplicativo'] = {
                'id': instance.aplicativo.id,
                'nombre': instance.aplicativo.nombre
            }
        
        if instance.persona:
            telefonos = list(instance.persona.telefonos_personas.exclude(eliminado=True).values('id', 'valor'))
            direccion = instance.persona.direcciones_personas.exclude(eliminado=True).first()
            ciudad = None
            if direccion and direccion.ciudad:
                ciudad = direccion.ciudad.nombre
            representation['persona'] = {
                'id': instance.persona.id,
                'documento': instance.persona.documento,
                'n_completo': instance.persona.n_completo,
                'email': instance.persona.email,
                'telefonos': telefonos,
                'ciudad': ciudad
            }
            
        conceptos_causacion = instance.afiliado_concepto_causacion
        if conceptos_causacion.exists():
            representation['conceptos_causacion'] = AfiliadoConceptoCausacionSerializer(
                conceptos_causacion, 
                many=True
            ).data
        else:
            representation['conceptos_causacion'] = []
            
        return representation

class AfiliadoListSerializer(serializers.ModelSerializer):

    afiliado = serializers.SerializerMethodField('get_afiliado', read_only=True)
    def get_afiliado(self, obj):
        try:
            return AfiliadoModelSerializer(obj.afiliado_persona.first()).data
        except:
            return {}
    
    tipospersonas = serializers.SerializerMethodField('get_tipos_personas', read_only=True)
    def get_tipos_personas(self, obj):
        try:
            return PersonaTipoPersona.objects.filter(persona_id=obj.id).values('tipo_persona__nombre')
        except:
            return {}

    class Meta:
        model = Persona
        fields = (
            'id',
            'documento',
            'n_completo',
            'email',
            'tipospersonas',
            'afiliado'
        )