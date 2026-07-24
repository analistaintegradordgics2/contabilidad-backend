from rest_framework import serializers

from apps.contabilidad.models.parametros import EstadoFactElectro

class EstadosFactSerializer(serializers.ModelSerializer):
    class Meta:
        """Meta class."""
        model = EstadoFactElectro
        fields = '__all__'