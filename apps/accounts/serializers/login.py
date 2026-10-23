from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.accounts.models import RegistroIngreso

from apps.accounts.serializers.usuario import UserFindSerializer

class CustomTokenSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        # Agregar info del usuario
        data['user'] = UserFindSerializer(self.user).data

        data['status'] = 200

        return data

class RegistroIngresoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = RegistroIngreso
        fields = ('id', 'usuario', 'usuario_nombre', 'fecha_ingreso', 'direccion_ip', 'agente_usuario')
        read_only_fields = fields
