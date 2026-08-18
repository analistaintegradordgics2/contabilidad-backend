import pdb

from apps.utils.render import Render

from django.db import transaction
from django.db.models import Q
from apps.nomina.models.novedades import Novedad, NovedadesCentroCosto
from apps.nomina.models.parametrizacion import BaseLiquidacionNovedad
from apps.utils.funciones import Funciones

from apps.parametros.services.empresa_service import EmpresaService

class NovedadService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(validated_data, user_id, instancia=None):
        """
        Crea o actualiza una Novedad con sus relaciones de centros de costos
        y bases de liquidación. Recibe validated_data de NovedadCreateSerializer.
        - FKs simples ya vienen como instancias (entidad, grupo_nomina, etc.)
        - Anidados: base_liquidacion_empleado, base_liquidacion_empresa, centro_costos
        """
        entidad = validated_data.get('entidad', None)
        centro_costos = validated_data.pop('centro_costos', [])
        base_liquidacion_empleado = validated_data.pop('base_liquidacion_empleado', [])
        base_liquidacion_empresa = validated_data.pop('base_liquidacion_empresa', [])
        if instancia:
            for attr, value in validated_data.items():
                if value is not None:
                    setattr(instancia, attr, value)
            instancia.save()
            novedad = instancia
        else:
            validated_data['uc_id'] = user_id
            novedad = Novedad.objects.create(**validated_data)

        # Manejar centros de costo
        if entidad is not None:
            existentes = NovedadesCentroCosto.objects.filter(
                entidades_centro_costos__entidad_id=entidad.id,
                eliminado=False
            )
            if not existentes.exists():
                for item in centro_costos:
                    if not item['eliminado']:
                        if item['id'] is None:
                            NovedadesCentroCosto.objects.create(
                                centro_costos=item['centro_costos'],
                                novedades=novedad,
                                uc_id=user_id,
                                mayor_cta_debito=item.get('mayor_cta_debito'),
                                mayor_cta_credito=item.get('mayor_cta_credito'),
                                eliminado=item['eliminado']
                            )
                        else:    
                            NovedadesCentroCosto.objects.create(
                                entidades_centro_costos_id=item['id'],
                                novedades=novedad,
                                uc_id=user_id,
                                mayor_cta_debito=item.get('mayor_cta_debito'),
                                mayor_cta_credito=item.get('mayor_cta_credito'),
                                eliminado=item['eliminado']
                            )
            else:
                for item in centro_costos:
                    novedad_ccosto = NovedadesCentroCosto.objects.filter(
                        entidades_centro_costos_id=item['id']
                    ).first()
                    if novedad_ccosto is None:
                        novedad_ccosto = NovedadesCentroCosto(uc_id=user_id)
                    else:
                        novedad_ccosto.um_id = user_id
                    novedad_ccosto.entidades_centro_costos_id = item['id']
                    novedad_ccosto.eliminado = item['eliminado']
                    novedad_ccosto.novedades = novedad
                    novedad_ccosto.mayor_cta_debito = item.get('mayor_cta_debito')
                    novedad_ccosto.mayor_cta_credito = item.get('mayor_cta_credito')
                    novedad_ccosto.save()
        else:
            for item in centro_costos:
                novedad_ccosto = NovedadesCentroCosto.objects.filter(
                    centro_costos=item['centro_costos'],
                    novedades=novedad
                ).first()
                if novedad_ccosto is None:
                    NovedadesCentroCosto.objects.create(
                        centro_costos=item['centro_costos'],
                        mayor_cta_debito=item.get('mayor_cta_debito'),
                        mayor_cta_credito=item.get('mayor_cta_credito'),
                        novedades=novedad,
                        eliminado=item['eliminado'],
                        uc_id=user_id
                    )
                else:
                    novedad_ccosto.mayor_cta_debito = item.get('mayor_cta_debito')
                    novedad_ccosto.mayor_cta_credito = item.get('mayor_cta_credito')
                    novedad_ccosto.eliminado = item['eliminado']
                    novedad_ccosto.um_id = user_id
                    novedad_ccosto.save()

        # Manejar bases de liquidación
        bases_existentes = BaseLiquidacionNovedad.objects.filter(novedades=novedad).exists()

        for item in base_liquidacion_empleado + base_liquidacion_empresa:
            # base_liquidacion ya es instancia gracias a PrimaryKeyRelatedField
            if bases_existentes:
                bl = BaseLiquidacionNovedad.objects.filter(
                    novedades=novedad,
                    base_liquidacion=item['base_liquidacion']
                ).first()
                if bl:
                    bl.um_id = user_id
                    bl.eliminado = item['eliminado']
                    bl.save()
                else:
                    BaseLiquidacionNovedad.objects.create(
                        novedades=novedad,
                        base_liquidacion=item['base_liquidacion'],
                        uc_id=user_id
                    )
            else:
                BaseLiquidacionNovedad.objects.create(
                    novedades=novedad,
                    base_liquidacion=item['base_liquidacion'],
                    uc_id=user_id
                )

        return novedad

    @staticmethod
    def exportar(request_data):
        model = []
        data = request_data
        name_file = "NOVEDADES"

        if data["filtros"]["tipo_novedad_id"] != None :
            name_file = " {} - TIPO DE NOVEDAD: {}".format(name_file, data["data"][0]["tipo_novedad_nombre"])
        
        if data["filtros"]["centro_costos"] != None :
            name_file = " {} - CENTRO COSTO: {}".format(name_file, data["data"][0]["foraneas"]["centro_costo"])

        for item in data["data"] :
            params = {
                'nombre': item["nombre"],
                'tipo_novedad': item["tipo_novedad_nombre"],
                'tipo_valor_novedad': item["tipo_valor_novedad_nombre"],
                'valor': item["valor"],
            }
            if data["filtros"]["centro_costos"] != None :
                params["centro_costo"] = item["foraneas"]["centro_costo"]
                params["cta_debito"] = item["foraneas"]["mayor_cta_debito"]
                params["cta_credito"] = item["foraneas"]["mayor_cta_credito"]
            params["estado"] = item["estado"]

            model.append(params)

        return Render.export_excel(model, name_file)

    @staticmethod
    def imprimir(request_data):
        data = request_data
        nombre = "Novedades"

        empresa = EmpresaService.obtener_datos_empresa()

        params = {
            'empresa': empresa,
            'data': data["data"],
            'filtros': data["filtros"]
        }
        pdf = Render.render_pdfkit('pdf/nomina/novedades.html', params, nombre)

        return pdf