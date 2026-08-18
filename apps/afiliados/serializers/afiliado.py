from rest_framework import serializers
from apps.personas.models.persona import PersonaTipoPersona, Persona
from apps.afiliados.models import Afiliado
from apps.afiliados.serializers.causacion import AfiliadoConceptoCausacionSerializer

import pdb

class AfiliadoResumenSerializer(serializers.ModelSerializer):

    class Meta:
        model = Afiliado
        # fields = '__all__'
        exclude = ('created', 'modified', 'delete', 'uc', 'um')

    def to_representation(self, instance):
        if not instance:
            return {}
        representation = super().to_representation(instance)
        
        if getattr(instance, 'tipo_contrato', None):
            representation['tipo_contrato'] = {
                'id': instance.tipo_contrato.id,
                'nombre': instance.tipo_contrato.nombre
            }
            
        if getattr(instance, 'aplicativo', None):
            representation['aplicativo'] = {
                'id': instance.aplicativo.id,
                'nombre': instance.aplicativo.nombre
            }
        
        if getattr(instance, 'persona', None):
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
            
        return representation

class AfiliadoModelSerializer(AfiliadoResumenSerializer):
    conceptos_causacion = serializers.ListField(
        child=serializers.DictField(),
        write_only=True,
        required=False
    )

    def to_representation(self, instance):
        if not instance:
            return {}
        representation = super().to_representation(instance)
        
        if self.context.get('conceptos_facturar', False):
            #Incluir solo los conceptos con marca facturar
            conceptos_causacion = instance.afiliado_concepto_causacion.filter(facturar=True)
        else:
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
            afiliado_obj = obj.afiliado_persona.first()
            if not afiliado_obj:
                return {}
            return AfiliadoModelSerializer(afiliado_obj).data
        except Exception:
            return {}
    
    tipospersonas = serializers.SerializerMethodField('get_tipos_personas', read_only=True)
    def get_tipos_personas(self, obj):
        try:
            return PersonaTipoPersona.objects.filter(persona_id=obj.id).values('tipo_persona__nombre')
        except Exception:
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