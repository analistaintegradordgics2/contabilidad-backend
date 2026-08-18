from rest_framework import serializers

from datetime import datetime

from apps.utils.history import getHistorymodel

from apps.nomina.models.entidades import Entidad, EntidadCentroCosto, TipoEntidad

class EntidadCentroCostoSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        """Meta class."""
        model = EntidadCentroCosto
        fields = ("id", "centro_costos", "entidad", "mayor_cta_credito", "mayor_cta_debito", "eliminado", "uc", "um")
        read_only_fields = ("entidad",)

class EntidadSerializer(serializers.ModelSerializer):

    data_persona = serializers.DictField(write_only=True)
    centro_costos = EntidadCentroCostoSerializer(write_only=True, many=True)
    
    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            {'db': 'personas_id', 'label': 'persona', 'nombre_relacion': 'n_completo'},
            {'db': 'tipo_entidad_id', 'label': 'tipo_entidad', 'nombre_relacion': 'nombre'},
            {'db': 'estado', 'label': 'Estado'},
            {'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        campos_enticcosto = [
            {'db': 'centro_costos_id', 'label': 'centro_costo', 'nombre_relacion': 'nombre'},
            {'db': 'mayor_cta_credito_id', 'label': 'cta_credito', 'nombre_relacion': 'codigo'},
            {'db': 'mayor_cta_debito_id', 'label': 'cta_debito', 'nombre_relacion': 'codigo'},
            {'db': 'eliminado', 'label': 'Eliminado centro costo', 'identificar_registro': 'centro_costos', 'nombre_relacion': 'nombre'},
            {'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        list_principal = getHistorymodel(obj, campos)
        obj_enticcosto = EntidadCentroCosto.objects.filter(entidad_id=obj.id)

        for item in obj_enticcosto:
            list_hijos = getHistorymodel(item, campos_enticcosto)
            list_principal += list_hijos

        list_principal = sorted(list_principal, key=lambda x: datetime.strptime(x['fecha_bitacora'],"%d/%m/%Y %H:%M" ), reverse=True)
        
        return list_principal
    
    centro_costo = serializers.SerializerMethodField('get_centro_costo', read_only=True)
    def get_centro_costo(self, obj):
        try :
            filtros = {
                "entidad_id": obj.id,
                "eliminado": False,
                "centro_costos_id": self.context["filtros"]["entidad_centro_costos_entidad__centro_costos_id"]
            }
            enti = EntidadCentroCosto.objects.filter(**filtros).first()
            return "{} - {}".format(enti.centro_costos.codigo, enti.centro_costos.nombre)
        except :
            None
    
    mayor_cta_debito = serializers.SerializerMethodField('get_mayor_cta_debito', read_only=True)
    def get_mayor_cta_debito(self, obj):
        try :
            filtros = {
                "entidad_id": obj.id,
                "eliminado": False,
                "centro_costos_id": self.context["filtros"]["entidad_centro_costos_entidad__centro_costos_id"]
            }
            enti = EntidadCentroCosto.objects.filter(**filtros).first()
            return "{} - {}".format(enti.mayor_cta_debito.codigo, enti.mayor_cta_debito.nombre)
        except :
            None

    mayor_cta_credito = serializers.SerializerMethodField('get_mayor_cta_credito', read_only=True)
    def get_mayor_cta_credito(self, obj):
        try :
            filtros = {
                "entidad_id": obj.id,
                "eliminado": False,
                "centro_costos_id": self.context["filtros"]["entidad_centro_costos_entidad__centro_costos_id"]
            }
            enti = EntidadCentroCosto.objects.filter(**filtros).first()
            return "{} - {}".format(enti.mayor_cta_credito.codigo, enti.mayor_cta_credito.nombre)
        except :
            None

    entidad_centro_costos = serializers.SerializerMethodField('get_entidad_centro_costos', read_only=True)
    def get_entidad_centro_costos(self, obj):
        model = []
        for item in EntidadCentroCosto.objects.filter(entidad_id=obj.id, eliminado=False) :
            model.append({
                "id": item.id,
                "centro_costos": item.centro_costos_id,
                "centro_costos_nombre": "{} - {}".format(item.centro_costos.codigo, item.centro_costos.nombre),
                "mayor_cta_debito": item.mayor_cta_debito_id,
                "mayor_cta_credito": item.mayor_cta_credito_id,
                "mayor_cta_debito_nombre": "{} - {}".format(item.mayor_cta_debito.codigo, item.mayor_cta_debito.nombre),
                "mayor_cta_credito_nombre": "{} - {}".format(item.mayor_cta_credito.codigo, item.mayor_cta_credito.nombre),
                "eliminado": item.eliminado
            })
        
        return model
    
    tipo_entidad_nombre = serializers.SerializerMethodField('get_tipo_entidad_nombre', read_only=True)
    def get_tipo_entidad_nombre(self, obj):
        try :
            return obj.tipo_entidad.nombre
        except :
            return None
    
    persona = serializers.SerializerMethodField('get_persona', read_only=True)
    def get_persona(self, obj):
        from apps.personas.serializers.persona import PersonaModelSerializer
        return PersonaModelSerializer(obj.personas).data
    
    persona_nombre = serializers.SerializerMethodField('get_persona_nombre', read_only=True)
    def get_persona_nombre(self, obj):
        try :
            return obj.personas.n_completo
        except :
            return None

    class Meta:
        """Meta class."""
        model = Entidad
        fields = ("id", "personas", "tipo_entidad", "estado", "uc", "um", "history", "estado", "tipo_entidad_nombre", "centro_costo", "mayor_cta_debito", "mayor_cta_credito", "entidad_centro_costos", "persona", "persona_nombre", "data_persona", "centro_costos")

class TipoEntidadSerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta class."""
        model = TipoEntidad
        fields = ("id", "nombre", "estado")