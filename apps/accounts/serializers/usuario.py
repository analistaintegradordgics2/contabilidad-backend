from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.conf import settings
from django.db.models import F, Value
from django.db.models.functions import Concat
from rest_framework import serializers

from apps.parametros.models.parametrizacion import Parametros
from apps.personas.models.persona import Persona

UserModel = get_user_model()


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

    info_persona = serializers.SerializerMethodField()
    logoempresa = serializers.SerializerMethodField()
    firma = serializers.SerializerMethodField()
    n_completo = serializers.SerializerMethodField()

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

    def get_firma(self, obj):
        persona = getattr(obj, 'user_persona', None)

        if not persona:
            return None

        archivo = persona.archivos.filter(tipo='firma_persona').first()

        if archivo:
            dominio = Parametros.objects.filter(parametro='dominio_empresa').first()
            return f"{dominio.valor.lower()}media/{archivo.src}"

        return None

    def get_n_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip()

    class Meta:
        model = UserModel
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


class UsuariosSerializer(serializers.ModelSerializer):

    new_password = serializers.CharField(default=None, read_only=True)
    repeat_password = serializers.CharField(default=None, read_only=True)
    isPwd = serializers.BooleanField(default=True, read_only=True)
    isPwdN = serializers.BooleanField(default=True, read_only=True)

    archivo = serializers.SerializerMethodField('get_archivo', read_only=True)
    def get_archivo(self, obj):
        try:
            persona = Persona.objects.filter(usuario_id=obj.id).first()
            archivo = persona.archivos.filter(delete=None, tipo="PERFIL").values(
                "content_type_id", "id", "name", "object_id", "tipo", "src",
                url=Concat(Value(settings.MEDIA_URL), F('src'))
            ).first()
            if archivo is not None:
                return archivo
            return {"id": None, "url": None}
        except Exception:
            return {"id": None, "url": None}

    n_completo = serializers.SerializerMethodField('get_n_completo', read_only=True)
    def get_n_completo(self, obj):
        try:
            return f"{obj.first_name} {obj.last_name}".strip()
        except Exception:
            return ""

    estado = serializers.SerializerMethodField('get_estado', read_only=True)
    def get_estado(self, obj):
        try:
            return "Activo" if obj.is_active else "Inactivo"
        except Exception:
            return ""

    # permisos_casos = serializers.SerializerMethodField('get_permisos_casos', read_only=True)
    # def get_permisos_casos(self, obj):
    #     user_perm_ids = set(obj.user_permissions.values_list('id', flat=True))
    #     data_permisos = Permission.objects.filter(
    #         codename__in=[
    #             "view_ver_casos",
    #             "view_crear_casos",
    #             "view_crear_seguimientos_casos",
    #             "view_finalizar_casos",
    #             "view_todas_las_notificaciones",
    #             "view_menu_arriendos_pagos_anular_pagos",
    #             "view_editar_casos"
    #         ]
    #     ).order_by("id")

    #     return [
    #         {
    #             "id": item.id,
    #             "nombre": item.name,
    #             "select": item.id in user_perm_ids
    #         }
    #         for item in data_permisos
    #     ]

    permisos_ingreso_sistema = serializers.SerializerMethodField('get_permisos_ingreso_sistema', read_only=True)
    def get_permisos_ingreso_sistema(self, obj):
        user_perm_ids = set(obj.user_permissions.values_list('id', flat=True))
        data_permisos = Permission.objects.filter(
            codename__in=["view_ingreso_sin_restriccion_horario"]
        ).order_by("id")

        return [
            {
                "id": item.id,
                "nombre": item.name,
                "select": item.id in user_perm_ids
            }
            for item in data_permisos
        ]

    class Meta:
        model = UserModel
        fields = (
            'id', 'username', 'first_name', 'new_password', 'repeat_password',
            'isPwd', 'isPwdN', 'archivo', 'last_name', 'email', 'is_active',
            'n_completo', 'estado', 'permisos_ingreso_sistema'
        )
