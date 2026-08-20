import pdb

from django.db import transaction
from apps.nomina.models.entidades import Entidad, EntidadCentroCosto
from apps.personas.models.persona import Persona
from apps.personas.services.persona_service import PersonaService
from apps.utils.funciones import Funciones

from apps.parametros.services.empresa_service import EmpresaService

from apps.utils.render import Render

class EntidadService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(validated_data, user, instancia=None):
        """
        Crea o actualiza una Entidad con su Persona asociada y centros de costos.
        Recibe validated_data de un serializer — las FKs ya vienen como instancias.
        """
        persona_data = validated_data.pop('data_persona', {})
        entidad_centro_costo = validated_data.pop('centro_costos', [])

        persona_data['estado'] = 1 if validated_data.get('estado', False) else 2
        persona_data['tipos_persona'] = persona_data['tipo_persona']
        persona = PersonaService.crear_o_actualizar({'persona': persona_data}, user.id)
        validated_data['personas'] = persona

        if instancia:
            for attr, value in validated_data.items():
                setattr(instancia, attr, value)
            instancia.save()
            entidad = instancia
        else:
            validated_data['uc'] = user
            validated_data['um'] = user
            entidad = Entidad.objects.create(**validated_data)

        # Manejar centros de costo
        enticcosto = EntidadCentroCosto.objects.filter(entidad_id=entidad.id)

        if not enticcosto.exists():
            for item in entidad_centro_costo:
                EntidadCentroCosto.objects.create(
                    entidad=entidad,
                    centro_costos=item.get('centro_costos'),
                    mayor_cta_debito=item.get('mayor_cta_debito'),
                    mayor_cta_credito=item.get('mayor_cta_credito'),
                    eliminado=item.get('eliminado', False),
                    uc=user
                )
        else:
            for item in entidad_centro_costo:
                if item.get('id') is None:
                    EntidadCentroCosto.objects.create(
                        entidad=entidad,
                        centro_costos=item.get('centro_costos'),
                        mayor_cta_debito=item.get('mayor_cta_debito'),
                        mayor_cta_credito=item.get('mayor_cta_credito'),
                        eliminado=item.get('eliminado', False),
                        uc=user
                    )
                else:
                    ec = EntidadCentroCosto.objects.get(pk=item['id'])
                    ec.um = user
                    ec.entidad = entidad
                    ec.centro_costos = item.get('centro_costos')
                    ec.mayor_cta_debito = item.get('mayor_cta_debito')
                    ec.mayor_cta_credito = item.get('mayor_cta_credito')
                    ec.eliminado = item.get('eliminado', False)
                    ec.save()

        return entidad

    def imprimir(request_data):

        data = request_data

        nombre = "cargos"

        empresa = EmpresaService.obtener_datos_empresa()

        params = {
            'empresa': empresa,
            'data': data["data"],
            'filtros': data["filtros"]
        }

        return Render.render_pdfkit('pdf/nomina/entidades.html', params, nombre)

    def exportar(request_data):
        model = []
        data = request_data
        name_file = "ENTIDADES"

        if data["filtros"]["tipo_entidades_id"] != None :
            name_file = "{} - TIPO ENTIDAD: {} ".format(name_file, data["data"][0]["tipo_entidad_nombre"])
        
        if data["filtros"]["entidad_centro_costos_entidad__centro_costos_id"] != None :
            name_file = "{} - CENTRO COSTO: {} ".format(name_file, data["data"][0]["centro_costo"])
        
        for item in data["data"] :
            params = {
                'identificacion': item["persona"]["documento"],
                'nombre': item["persona"]["n_completo"],
                'tipo_entidad': item["tipo_entidad_nombre"],
            }

            if data["filtros"]["entidad_centro_costos_entidad__centro_costos_id"] != None :
                params["centro_costo"] = item["centro_costo"]
                params["cta_debito"] = item["mayor_cta_debito"]
                params["cta_credito"] = item["mayor_cta_credito"]
            
            params["estado"] = item["estado"]

            model.append(params)
        
        return Render.export_excel(model, name_file)