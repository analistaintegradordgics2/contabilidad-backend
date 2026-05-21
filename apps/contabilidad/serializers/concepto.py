from rest_framework import serializers
from apps.contabilidad.models.concepto import Concepto
from apps.utils.history import getHistorymodel

class ConceptosSerializer(serializers.ModelSerializer):
    
    codigo_nombre = serializers.SerializerMethodField()

    def get_codigo_nombre(self, obj):
        return f"{obj.codigo or ''} - {obj.nombre or ''}"

    class Meta:
        model = Concepto
        fields = (
            "id",
            "codigo",
            "nombre",
            "detalle",
            "codigo_nombre",
        )

class ConceptoHistorySerializer(serializers.ModelSerializer):

    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            {'db': 'codigo', 'label': 'Código'},
            {'db': 'nombre', 'label': 'Nombre'},
            {'db': 'detalle', 'label': 'Detalle'},
            {'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        list_principal = getHistorymodel(obj, campos,'')
        
        return list_principal

    class Meta:
        model = Concepto
        fields = (
            'id',
            'history')
        