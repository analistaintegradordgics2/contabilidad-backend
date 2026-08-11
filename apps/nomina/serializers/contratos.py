from rest_framework import serializers

from apps.utils.history import getHistorymodel

from apps.nomina.models.contratos import Cargo

class CargoModelSerializer(serializers.ModelSerializer):
    
    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            {'db': 'nombre', 'label': 'Nombre'},
            {'db': 'estado', 'label': 'Estado'},
            {'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        list_principal = getHistorymodel(obj, campos)
        
        return list_principal

    class Meta:
        """Meta class."""
        model = Cargo
        fields = ("id", "nombre", "estado", "uc", "um", "history")