from apps.afiliados.serializers.afiliado import AfiliadoModelSerializer
from rest_framework import serializers

class CuponSinGenerarModelSerializer(AfiliadoModelSerializer):
    pass

class CuponGeneradoModelSerializer(serializers.ModelSerializer):
    pass