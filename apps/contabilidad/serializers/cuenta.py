from rest_framework import serializers
from apps.contabilidad.models.cuenta import *
from apps.utils.history import getHistorymodel

# Si prefieres nombres más claros en el modelo nuevo
class MayorSerializer(serializers.ModelSerializer):
    codigo_nombre = serializers.SerializerMethodField()

    def get_codigo_nombre(self, obj):
        return f"{obj.codigo} - {obj.nombre}" if obj.codigo and obj.nombre else None

    class Meta:
        model = Mayor
        fields = (
            "id",
            "codigo",
            "nombre",
            "tipo",
            "estado",
            "maneja_nits",
            "maneja_base",
            "maneja_ccosto",
            "cuenta_cxc",
            "cuenta_cxp",
            "flujocaja",
            "naturaleza",
            "nittercero",
            "codigo_nombre"
        )

class MayorHistorySerializer(serializers.ModelSerializer):

    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            {'db': 'codigol', 'label': 'Código'},
            {'db': 'nombrel', 'label': 'Nombre'},
            {'db': 'tipo', 'label': 'Tipo'},
            {'db': 'estado', 'label': 'Estado'},
            {'db': 'nits', 'label': 'Nits'},
            {'db': 'base', 'label': 'Base'},
            {'db': 'porcentajeret', 'label': '% Retención'},
            {'db': 'ccosto', 'label': 'Centro de costo'},
            {'db': 'cxc', 'label': 'Cuenta por cobrar'},
            {'db': 'cxp', 'label': 'Cuenta por pagar'},
            {'db': 'flujocaja', 'label': 'Flujo de caja'},
            {'db': 'naturaleza', 'label': 'Naturaleza'},
            {'db': 'naturaleza', 'label': 'Naturaleza'},
            {'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        list_principal = getHistorymodel(obj, campos,'')
        
        return list_principal

    class Meta:
        """Meta class."""
        model = Mayor
        fields = (
            'history',
        )
