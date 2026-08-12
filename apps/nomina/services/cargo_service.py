from django.db import transaction
from apps.nomina.models.contratos import Cargo

from apps.parametros.services.empresa_service import EmpresaService
from apps.utils.render import Render

class CargoService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(validated_data, instancia=None, user=None):
        """
        Crea o actualiza un Cargo.
        Recibe validated_data de un serializer — las FKs ya vienen como instancias.
        """
        if instancia:
            validated_data['um'] = user
            for attr, value in validated_data.items():
                setattr(instancia, attr, value)
            instancia.save()
            return instancia
        else:
            validated_data['uc'] = user
            return Cargo.objects.create(**validated_data)

    @staticmethod
    def imprimir(request_data):
        nombre = "cargos"

        empresa = EmpresaService.obtener_datos_empresa()

        data = request_data

        params = {
            'empresa': empresa,
            'data': data
        }

        pdf = Render.render_pdfkit('pdf/nomina/cargos.html', params, nombre)

        return pdf