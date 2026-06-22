from apps.parametros.models.parametrizacion import Parametros

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

        return {
            'nombre': cls._get_parametro('nombre_empresa'),
            'nit': cls._get_parametro('nit_empresa'),
            'direccion': cls._get_parametro('direccion_empresa'),
            'telefono': cls._get_parametro('telefono_empresa'),
            'email': cls._get_parametro('email_empresa'),
            'logo': f'{dominio}media/iconos/{logo}' if dominio and logo else ''
        }