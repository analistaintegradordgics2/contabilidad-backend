from rest_framework.response import Response
from django.db import transaction
from apps.common_db.db import execute_procedure
from rest_framework import status
from apps.contabilidad.models.cuenta import Mayor
from .saldo_service import SaldosService
from apps.contabilidad.models.saldo import SaldosNits
from django.db.models import Sum
from apps.parametros.services.empresa_service import EmpresaService
from apps.utils.render import Render
from apps.parametros.models.parametrizacion import Parametros
from apps.utils.util import NumeroA, get_ciudad_inmo
from apps.utils.list import lists
from django.conf import settings
from datetime import date, datetime 
from apps.personas.models.persona import Persona
from apps.personas.services.persona_service import PersonaFormatter
from apps.personas.models.contacto import Direccion, Telefono
import os, shutil

import pdb

class ConsultaService:

    @staticmethod
    def filtro_aux(model, filtro=None):
        if model['tipo'] == 1:
            # codigo clasificado por nit
            try:
                with transaction.atomic():
                    sql = """
                        select * from getauxiliarnit(%s, %s, %s, %s, %s, %s);
                    """
                    params = [
                        model['año'],
                        model['mesini'],
                        model['mesfin'],
                        model['codigo'],
                        1 if filtro['incnitsinsal'] == True else 0,
                        1 if filtro['incnitsinmov'] == True else 0,
                    ]
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
            if resultado and resultado[0][0] is not None:
                return resultado[0][0][0]
            return []

        elif model['tipo'] == 2:
            # codigo y nit
            try:
                with transaction.atomic():
                    sql = """
                        select json_agg(json_build_object(
                            'id', id,
                            'tipo', tipo,
                            'numero', numero,
                            'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                            'docref', docref,
                            'concepto', concepto,
                            'detalle', detalle,
                            'valor_db', valor_db,
                            'valor_cr', valor_cr,
                            'saldo', saldo,
                            'color', color,
                            'fuentes_id', fuentes_id,
                            'ordenf', ordenf,
                            'base', base,
                            'mov_id', mov_id,
                            'mayor_id', mayor_id)) from getauxcodnit(%s, %s, %s, %s, %s);
                    """
                    params = [
                        model['codigo'],
                        model['persona'],
                        model['año'],
                        model['mesini'],
                        model['mesfin'],
                    ]
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []

        elif model['tipo'] == 3:
            # codigo
            try:
                with transaction.atomic():
                    if model['ccosto'] == True:
                        sql = """
                            select json_agg(json_build_object(
                                'id', id,
                                'tipo', tipo,
                                'numero', numero,
                                'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                'docref', docref,
                                'concepto', concepto,
                                'nits', nits,
                                'nombre', nombre,
                                'detalle', detalle,
                                'valor_db', valor_db,
                                'valor_cr', valor_cr,
                                'saldo', saldo,
                                'color', color,
                                'fuentes_id', fuentes_id,
                                'orden', orden,
                                'ordenf', ordenf,
                                'centro_costos_id', centro_costos_id,
                                'base', base)) from getauxiliarcodigocc(%s, %s, %s, %s, %s, %s);
                        """
                        params = [
                            model['año'],
                            model['mesini'],
                            model['mesfin'],
                            model['codigonom']['nombre1'] if model['codigonom']['nombre1'] is not None else '0',
                            model['codigonom']['nombre2'] if model['codigonom']['nombre2'] is not None else model['codigonom']['nombre1'],
                            model['idcc'],
                        ]
                    else:
                        if model['rango_fecha'] == False:
                            sql = """
                                select json_agg(json_build_object(
                                    'id', id,
                                    'tipo', tipo,
                                    'numero', numero,
                                    'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                    'docref', docref,
                                    'concepto', concepto,
                                    'nits', nits,
                                    'nombre', nombre,
                                    'detalle', detalle,
                                    'valor_db', valor_db,
                                    'valor_cr', valor_cr,
                                    'saldo', saldo,
                                    'color', color,
                                    'fuentes_id', fuentes_id,
                                    'orden', orden,
                                    'ordenf', ordenf,
                                    'base', base)) from getauxiliarcodigo(%s, %s, %s, %s, %s);
                            """
                            params = [
                                model['año'],
                                model['mesini'],
                                model['mesfin'],
                                model['codigonom']['nombre1'] if model['codigonom']['nombre1'] is not None else '0',
                                model['codigonom']['nombre2'] if model['codigonom']['nombre2'] is not None else model['codigonom']['nombre1'],
                            ]
                        else:
                            sql = """
                                select json_agg(json_build_object(
                                    'id', id,
                                    'tipo', tipo,
                                    'numero', numero,
                                    'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                    'docref', docref,
                                    'concepto', concepto,
                                    'nits', nits,
                                    'nombre', nombre,
                                    'detalle', detalle,
                                    'valor_db', valor_db,
                                    'valor_cr', valor_cr,
                                    'saldo', saldo,
                                    'color', color,
                                    'fuentes_id', fuentes_id,
                                    'orden', orden,
                                    'ordenf', ordenf,
                                    'base', base)) from getauxiliarcodigorango(%s, %s, %s, %s);
                            """
                            params = [
                                model['fechaini'],
                                model['fechafin'],
                                model['codigonom']['nombre1'] if model['codigonom']['nombre1'] is not None else '0',
                                model['codigonom']['nombre2'] if model['codigonom']['nombre2'] is not None else model['codigonom']['nombre1'],
                            ]
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []

        elif model['tipo'] == 4:
            try:
                with transaction.atomic():
                    if model['ccosto'] == True:
                        sql = """
                            select json_agg(json_build_object(
                                'id', id,
                                'tipo', tipo,
                                'numero', numero,
                                'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                'docref', docref,
                                'concepto', concepto,
                                'nits', nits,
                                'detalle', detalle,
                                'valor_db', valor_db,
                                'valor_cr', valor_cr,
                                'saldo', saldo,
                                'color', color,
                                'fuentes_id', fuentes_id,
                                'orden', orden,
                                'ordenf', ordenf,
                                'centro_costos_id', centro_costos_id,
                                'base', base)) from getauxiliarnitcc(%s, %s, %s, %s, %s);
                        """
                        params = [
                            model['año'],
                            model['mesini'],
                            model['mesfin'],
                            model['persona'],
                            model['idcc'],
                        ]
                    else:
                        sql = """
                            select json_agg(json_build_object(
                                'id', id,
                                'tipo', tipo,
                                'numero', numero,
                                'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                'docref', docref,
                                'concepto', concepto,
                                'detalle', detalle,
                                'valor_db', valor_db,
                                'valor_cr', valor_cr,
                                'saldo', saldo,
                                'color', color,
                                'fuentes_id', fuentes_id,
                                'base', base)) from getauxiliarper(%s, %s, %s, %s);
                        """
                        params = [
                            model['año'],
                            model['mesini'],
                            model['mesfin'],
                            model['persona'],
                        ]

                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []

        elif model['tipo'] == 5:
            try:
                with transaction.atomic():
                    sql = """
                        select json_agg(json_build_object(
                            'id', id,
                            'tipo', tipo,
                            'numero', numero,
                            'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                            'docref', docref,
                            'concepto', concepto,
                            'detalle', detalle,
                            'valor_db', valor_db,
                            'valor_cr', valor_cr,
                            'saldo', saldo,
                            'color', color,
                            'fuentes_id', fuentes_id,
                            'observa', observa,
                            'base', base)) from getauxiliarperdet(%s, %s, %s, %s);
                    """
                    params = [
                        model['año'],
                        model['mesini'],
                        model['mesfin'],
                        model['persona'],
                    ]
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []

        elif model['tipo'] == 7:
            # codigo, nit y concepto (persona opcional)
            mayordesde = Mayor.objects.filter(codigo=model['codigonom']['nombre1']).first()
            mayorhasta = (
                Mayor.objects.filter(codigo=model['codigonom']['nombre2']).first()
                if model['codigonom']['nombre2'] is not None
                else mayordesde
            )

            persona_val = model.get('persona', None)
            persona_param = None if (persona_val is None or persona_val == '' or persona_val == 0) else persona_val

            try:
                with transaction.atomic():
                    sql = """
                        select json_agg(json_build_object(
                            'id', id,
                            'tipo', tipo,
                            'numero', numero,
                            'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                            'docref', docref,
                            'concepto', concepto,
                            'detalle', detalle,
                            'valor_db', valor_db,
                            'valor_cr', valor_cr,
                            'saldo', saldo,
                            'color', color,
                            'fuentes_id', fuentes_id,
                            'ordenf', ordenf,
                            'base', base,
                            'mov_id', mov_id,
                            'mayor_id', mayor_id)) from getauxcodnitconc(%s, %s, %s, %s, %s, %s, %s);
                    """
                    params = [
                        mayordesde.codigo,
                        mayorhasta.codigo,
                        persona_param,
                        model['año'],
                        model['mesini'],
                        model['mesfin'],
                        model['concepto'],
                    ]
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []
        
    @staticmethod
    def consulta_saldos_aux(model):
        mayorid = model['codigo']
        personaid = model['persona']
        anio = model['año']
        filmesini = SaldosService._obtener_campo_saldo_inicio(model['mesini'])
        filmesfin = SaldosService._obtener_campo_saldo_inicio(model['mesfin'])
        
        if model['tipo'] == 1 or model['tipo'] == 3 :
            querySaldos = SaldosNits.objects.filter(mayor_id=mayorid, anio=anio).aggregate(Sum(filmesini), Sum(filmesfin)).values()
        elif model['tipo'] == 2 :
            querySaldos = SaldosNits.objects.filter(mayor_id=mayorid, personas_id=personaid, anio=anio).aggregate(Sum(filmesini), Sum(filmesfin)).values()
        elif model['tipo'] == 4 :
            querySaldos = SaldosNits.objects.filter(personas_id=personaid, anio=anio).exclude(mayor_id=838).aggregate(Sum(filmesini)).values()

        return querySaldos
    
    @staticmethod
    def imprimir_consulta_aux(request_data):
        model = request_data['model']
        filtro = request_data['filtro']
        sumas = request_data['sumas']

        data = ConsultaService.filtro_aux(model, filtro)

        for item in data:
            item = ConsultaAuxiliarFormatter._procesar_detalles(item, 'imprimir')
        
        empresa = EmpresaService.obtener_datos_empresa()

        nombre = "consultasaux"
        params = {
            'data': data,
            'empresa': empresa,
            'model': model,
            'sumas': sumas,
            'filtros': filtro
        }

        pdf = Render.render_pdfkit('pdf/contabilidad/consultasaux.html', params, nombre)
        return pdf
    
    @staticmethod
    def exportar_consulta_filtro_aux(request_data):
        model = []
        codigo = None
        if request_data['model'].get('codigonom') != None and request_data['model']['codigonom'].get('nombre1') != None:
            codigo = request_data['model']['codigonom']['nombre1']
        elif request_data['model'].get('codigo') != None:
            codigo = str(request_data['model']['codigo'])
        for item in request_data['data']:
            if request_data["tipo"] in [3,7] and item['id'] == None and item['detalle'] != None and ':::' in item['detalle']:
                codigo = item['detalle'].split(" ")[0]
            
            item = ConsultaAuxiliarFormatter._procesar_detalles(item, 'exportar_excel')

            params = {
                'codigo': '',
                'tipo': item['tipo'],
                'numero': item['numero'],
                'fecha': item['fecha'],
                'doc_ref': item['docref'],
                'concepto': item['concepto'],
            }
            if codigo != None and isinstance(item.get('id'), int) and item['id'] != 99:
                params['codigo'] = codigo

            if request_data["tipo"] == 3:
                params['nit'] = item['nits']
                params['nombre'] = item['nombre']
            
            params['detalle'] = item['detalle']
            params['base'] = item['base']
            params['debito'] = item['valor_db']
            params['credito'] = item['valor_cr']
            params['saldo'] = item['saldo']

            if request_data['filtro']['incbase'] == True:
                params["base"] = item["base"] if item["base"] != None else 0
            model.append(params)
        
        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento(
                None,
                None,
                None,
                None,
                None,
                None,
                "SALDO ANTERIOR",
                request_data["sumas"]["saldoinidb"] if request_data["sumas"]["saldoinidb"] is not None else 0,
                request_data["sumas"]["saldoinicr"] if request_data["sumas"]["saldoinicr"] is not None else 0,
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento(
                None,
                None,
                None,
                None,
                None,
                None,
                "MOVIMIENTOS",
                request_data["sumas"]["summovdb"],
                request_data["sumas"]["summovcr"],
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento(
                None,
                None,
                None,
                None,
                None,
                None,
                "BASE",
                None,
                request_data["sumas"]["summovbase"],
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento(
                None,
                None,
                None,
                None,
                None,
                None,
                "NUEVO SALDO",
                request_data["sumas"]["saldofindb"] if request_data["sumas"]["saldofindb"] is not None else 0,
                request_data["sumas"]["saldoinicr"] if request_data["sumas"]["saldoinicr"] is not None else 0,
            )
        )

        nombreinforme = ConsultaAuxiliarFormatter._get_nombre_informe(request_data)
        
        return Render.export_excel(model, nombreinforme)
            
class ConsultaAuxiliarFormatter:

    def _procesar_detalles(item, tipo_proceso=None):
        if item['detalle'] != None:
            item['detalle'] = item['detalle'].replace("JANUARY", "ENERO")
            item['detalle'] = item['detalle'].replace("FEBRUARY", "FEBRERO")
            item['detalle'] = item['detalle'].replace("MARCH", "MARZO")
            item['detalle'] = item['detalle'].replace("APRIL", "ABRIL")
            item['detalle'] = item['detalle'].replace("MAY", "MAYO")
            item['detalle'] = item['detalle'].replace("JUNE", "JUNIO")
            item['detalle'] = item['detalle'].replace("JULY", "JULIO")
            item['detalle'] = item['detalle'].replace("AUGUST", "AGOSTO")
            item['detalle'] = item['detalle'].replace("SEPTEMBER", "SEPTIEMBRE")
            item['detalle'] = item['detalle'].replace("OCTOBER", "OCTUBRE")
            item['detalle'] = item['detalle'].replace("NOVEMBER", "NOVIEMBRE")
            item['detalle'] = item['detalle'].replace("DECEMBER", "DICIEMBRE")
            # se recorta el texto del detalle si tiene mas de 100 caracteres
            if tipo_proceso == 'imprimir' and len(item['detalle']) > 100:
                item['detalle'] = item['detalle'][:100] + "..."

        return item
    
    def _get_nombre_informe(request_data):
        if request_data['tipo'] == 1:
            nombreinforme = "CONSULTA CÓDIGO: {} - {}".format(request_data["model"]["nommayor"],
                                                              request_data["model"]["codigonom"]["nombre1"])
        elif request_data['tipo'] == 2 or request_data['tipo'] == 6:
            nombreinforme = "CONSULTA CÓDIGO Y NIT: CÓDIGO: {} - NIT: {} - {}".format(
                request_data["model"]["nommayor"], request_data["model"]["ccpersona"],
                request_data["model"]["nompersona"])
        elif request_data['tipo'] == 3:
            nombreinforme = "CONSULTA CÓDIGO: {} - {}".format(request_data["model"]["codigonom"]["nombre1"],
                                                              request_data["model"]["codigonom"]["nombre2"] if
                                                              request_data["model"]["codigonom"]["nombre2"] != None else
                                                              request_data["model"]["codigonom"]["nombre1"])
        elif request_data['tipo'] == 4:
            nombreinforme = "CONSULTA NIT/CUENTA: {} - {}".format(request_data["model"]["ccpersona"],
                                                                  request_data["model"]["nompersona"])
        elif request_data['tipo'] == 5:
            nombreinforme = "CONSULTA NIT: {} - {}".format(request_data["model"]["ccpersona"],
                                                           request_data["model"]["nompersona"])

        return nombreinforme
    
    @staticmethod
    def _armar_movimiento(tipo, numero, ref, fecha, doc_ref, concepto, detalle, debito, credito):
        return {
            'tipo': tipo or '',
            'numero': numero or '',
            'ref': ref or '',
            'fecha': fecha or '',
            'doc_ref': doc_ref or '',
            'concepto': concepto or '',
            'detalle': detalle or '',
            'debito': debito if debito is not None else '',
            'credito': credito if credito is not None else '',
        }