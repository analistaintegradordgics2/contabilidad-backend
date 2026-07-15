from apps.parametros.models.parametrizacion import Parametros
import os
from django.conf import settings

class EmpresaService:

    @staticmethod
    def _get_parametro(nombre):
        parametro = Parametros.objects.filter(
            parametro=nombre
        ).first()

        return parametro.valor if parametro else ''

    @classmethod
    def obtener_datos_empresa(cls):
        dominio = cls._get_parametro('dominio_empresa')
        logo = cls._get_parametro('nombre_logo_empresa')

        logo_url = ''

        if dominio and logo:
            ruta_logo = os.path.join(settings.MEDIA_ROOT, 'iconos', logo)

            if os.path.isfile(ruta_logo):
                logo_url = f'{dominio}media/iconos/{logo}'

        return {
            'nombre': cls._get_parametro('nombre_empresa'),
            'nit': cls._get_parametro('nit_empresa'),
            'direccion': cls._get_parametro('direccion_empresa'),
            'telefono': cls._get_parametro('telefono_empresa'),
            'email': cls._get_parametro('email_empresa'),
            'logo': logo_url
        }