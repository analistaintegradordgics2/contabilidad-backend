from rest_framework import serializers
from apps.contabilidad.models.parametros import CentroCostos
from apps.utils.history import getHistorymodel

class CentroCostosSerializer(serializers.ModelSerializer):

    class Meta:
        model = CentroCostos
        fields = '__all__'

        