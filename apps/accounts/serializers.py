from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from django.db.models import F, Value
from django.db.models.functions import Concat
from apps.parametros.models.parametrizacion import Parametros

User = get_user_model()

class UserFindSerializer(serializers.ModelSerializer):
    user_persona = serializers.SlugRelatedField(
        many=False,
        read_only=True,
        slug_field='id'
    )

    user_permissions = serializers.SlugRelatedField(
        many=True,
        read_only=True,
        slug_field='codename'
    )

    # groups = GrupoPermissionsSerializer(many=True, read_only=True)

    info_persona = serializers.SerializerMethodField()
    logoempresa = serializers.SerializerMethodField()
    # departamento = serializers.SerializerMethodField()
    firma = serializers.SerializerMethodField()

    def get_info_persona(self, obj):
        persona = getattr(obj, 'user_persona', None)

        if not persona:
            return {
                "documento": 'Sin Asignar',
                "fecha_nacimiento": 'Sin Asignar'
            }

        archivo = persona.archivos.filter(
            delete=None,
            tipo="PERFIL"
        ).annotate(
            url=Concat(Value(settings.MEDIA_URL), F('src'))
        ).values(
            "content_type_id", "id", "name", "object_id", "tipo", "src", "url"
        ).first()

        return {
            "id": persona.id,
            "documento": persona.documento,
            "fecha_nacimiento": persona.fecha_nacimiento or 'Sin Asignar',
            "archivo": archivo
        }

    def get_logoempresa(self, obj):
        nombre = Parametros.objects.filter(parametro='nombre_logo_empresa').first()
        dominio = Parametros.objects.filter(parametro='dominio_empresa').first()

        if nombre and nombre.valor:
            return f"{dominio.valor}media/iconos/{nombre.valor}"
        return None

    # def get_departamento(self, obj):
    #     obj_dep = UsuariosDepartamentos.objects.filter(user_id=obj.id).first()

    #     if obj_dep:
    #         return {
    #             "id": obj_dep.departamento_id,
    #             "nombre": obj_dep.departamento.nombre,
    #         }
    #     return None

    def get_firma(self, obj):
        persona = getattr(obj, 'user_persona', None)

        if not persona:
            return None

        archivo = persona.archivos.filter(tipo='firma_persona').first()

        if archivo:
            dominio = Parametros.objects.filter(parametro='dominio_empresa').first()
            return f"{dominio.valor.lower()}media/{archivo.src}"

        return None
    
    n_completo= serializers.SerializerMethodField()
    def get_n_completo(self, obj):
        n_completo = f"{obj.first_name} {obj.last_name}"
        return n_completo

    class Meta:
        model = User
        fields = (
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'is_superuser',
            'user_permissions',
            'user_persona',
            'info_persona',
            'logoempresa',
            'firma',
            'n_completo'
        )

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

