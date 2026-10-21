from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from apps.accounts.models import RegistroIngreso

class CustomTokenSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        # Agregar info del usuario
        data['user'] = {
            "id": self.user.id,
            "username": self.user.username,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
        }

        data['status'] = 200

        return data

class RegistroIngresoSerializer(serializers.ModelSerializer):
    usuario_nombre = serializers.CharField(source='usuario.username', read_only=True)

    class Meta:
        model = RegistroIngreso
        fields = ('id', 'usuario', 'usuario_nombre', 'fecha_ingreso', 'direccion_ip', 'agente_usuario')
        read_only_fields = fields
