from rest_framework import serializers
from apps.contabilidad.models.cuenta import *
from apps.utils.history import getCombinedHistory

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
            "codigo_nombre"
        )

class MayorHistorySerializer(serializers.ModelSerializer):

    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            {'db': 'codigo', 'label': 'Código'},
            {'db': 'nombre', 'label': 'Nombre'},
            {'db': 'tipo', 'label': 'Tipo'},
            {'db': 'estado', 'label': 'Estado'},
            {'db': 'naturaleza', 'label': 'Naturaleza'},
            {'db': 'maneja_nits', 'label': 'Maneja Nits'},
            {'db': 'maneja_base', 'label': 'Maneja Base'},
            {'db': 'maneja_ccosto', 'label': 'Centro de costo'},
            {'db': 'cuenta_cxc', 'label': 'Cuenta por cobrar'},
            {'db': 'cuenta_cxp', 'label': 'Cuenta por pagar'},
            {'db': 'flujocaja', 'label': 'Flujo de caja'},
            {'db': 'history_date', 'label': 'fecha_bitacora'},
            {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username'}
        ]

        list_principal = getCombinedHistory(obj=obj, campos_principal=campos, tipo='Cuenta Contable')

        return list_principal

    class Meta:
        """Meta class."""
        model = Mayor
        fields = (
            'history',
        )
