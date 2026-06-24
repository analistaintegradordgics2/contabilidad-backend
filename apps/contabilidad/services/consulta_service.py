from rest_framework.response import Response
from django.db import transaction
from apps.common_db.db import execute_procedure
from rest_framework import status
from apps.contabilidad.models.cuenta import Mayor
from .saldo_service import SaldosService
from apps.contabilidad.models.parametros import CentroCostos
from apps.contabilidad.serializers.centrocostos import CentroCostosSerializer
from apps.contabilidad.models.saldo import SaldosNits, Saldos
from django.db.models import Sum
from apps.parametros.services.empresa_service import EmpresaService
from apps.utils.render import Render
from apps.parametros.models.parametrizacion import Parametros, Mes
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
                    # pdb.set_trace()
                    params = [
                        mayordesde.codigo,
                        mayorhasta.codigo,
                        persona_param,
                        model['año'],
                        model['mesini'],
                        model['mesfin'],
                        model['concepto'],
                    ]
                    # pdb.set_trace()
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
        filmesfin = SaldosService._obtener_campo_saldo_fin(model['mesfin'])
        querySaldos = ""
        
        if model['tipo'] == 1 or model['tipo'] == 3 :
            querySaldos = SaldosNits.objects.filter(mayor_id=mayorid, anio=anio).aggregate(Sum(filmesini), Sum(filmesfin)).values()
        elif model['tipo'] == 2 :
            querySaldos = SaldosNits.objects.filter(mayor_id=mayorid, personas_id=personaid, anio=anio).aggregate(Sum(filmesini), Sum(filmesfin)).values()
        elif model['tipo'] == 4 :
            querySaldos = SaldosNits.objects.filter(personas_id=personaid, anio=anio).aggregate(Sum(filmesini)).values()

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

    def centro_costos():

        query = CentroCostos.objects.filter(estado__iexact="activo").order_by('codigo')

        data = CentroCostosSerializer(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)
    
    @staticmethod
    def filtro_balance_general(model):
        try:
            with transaction.atomic():
                sql = """
                    select json_agg(json_build_object(
                        'codigo', codigo,
                        'nombre', nombre,
                        'parcial', parcial,
                        'total', total,
                        'color', color,
                        'tipo_cuenta',tipo_cuenta)) 
                    from getbalgeneral (%s,%s,%s);"""
                
                params = [
                    model['tipo'],
                    model['año'],
                    model['mesini']
                ]
                resultado = execute_procedure(sql=sql, params=params)
                if resultado[0][0] != None:
                    return resultado[0][0]
                else:
                    return []
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def imprimir_consulta_balance_general(model):
        data = ConsultaService.filtro_balance_general(model)
        empresa = EmpresaService.obtener_datos_empresa()

        nombre = "consultabalancegeneral"
        totales = {
            'parcial': 0,
            'total': 0,
        }

        for item in data:
            item['parcial'] = 0 if item['parcial'] == None else item['parcial']
            item['total'] = 0 if item['total'] == None else item['total']

            totales['parcial'] = totales['parcial'] + item['parcial']
            totales['total'] = totales['total'] + item['total']
        
        params = {
            'data': data,
            'empresa': empresa,
            'model': model,
            'totales': totales
        }
        pdf = Render.render_pdfkit('pdf/contabilidad/consultabalancegeneral.html', params, nombre)
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

    @staticmethod
    def filtro_aux_banco(model):
        try:
            with transaction.atomic():
                sql = """
                    select json_agg(json_build_object(
                        'id', id,
                        'tipo', tipo,
                        'numero', numero,
                        'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                        'fechac', to_char(date(fechac), 'dd/mm/yyyy'),
                        'docref', docref,
                        'idconc', idconc,
                        'nrocg', nrocg,
                        'detalle', detalle,
                        'cedula', cedula,
                        'persona', persona,
                        'valor_db', valor_db,
                        'valor_cr', valor_cr,
                        'color', color,
                        'fuentes_id', fuentes_id,
                        'saldo',saldo,
                        'order_insercion',order_insercion)) from getauxiliarbancos (%s, %s, %s, %s);
                    """
                params = [
                    model['año'],
                    model['mesini'],
                    model['mesfin'],
                    model['codigo']
                ]
                resultado = execute_procedure(sql=sql, params=params)
        except Exception:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
        if resultado and resultado[0] is not None:
            return resultado[0][0]
        return []

    @staticmethod
    def consulta_saldos_aux_banco(model):
        mayorid = model['codigo']
        anio = model['año']
        filmesini = SaldosService._obtener_campo_saldo_inicio(model['mesini'])
        filmesfin = SaldosService._obtener_campo_saldo_fin(model['mesfin'])
        
        return Saldos.objects.filter(mayor_id=mayorid, anio=anio).aggregate(Sum(filmesini), Sum(filmesfin)).values()

    @staticmethod
    def exportar_consulta_filtro_aux_banco(request_data):
        sumas = request_data["sumas"]
        modelo = request_data["model"]
        model = []

        for item in request_data["data"]:
            ConsultaAuxiliarFormatter._procesar_detalles(item, 'exportar')

            model.append(
                ConsultaAuxiliarFormatter._armar_movimiento_bancos(
                    item['tipo'],
                    item['numero'],
                    item['fecha'],
                    item['fechac'],
                    item['nrocg'],
                    item['docref'],
                    item['detalle'],
                    item['cedula'],
                    item['persona'],
                    item['valor_db'],
                    item['valor_cr'],
                    item['saldo'],
                )
            )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_bancos(
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "SALDO ANTERIOR",
                sumas["saldoinidb"],
                sumas["saldoinicr"],
                None,
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_bancos(
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "MOVIMIENTOS",
                sumas["summovdb"],
                sumas["summovcr"],
                None,
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_bancos(
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                None,
                "NUEVO SALDO",
                sumas["saldofindb"],
                sumas["saldofincr"],
                None,
            )
        )

        dataReturn = Render.export_excel(model, 'CONSULTA DE AUXILIAR POR BANCOS: {} - {}'.format(
            modelo["codigonom"]["nombre1"], modelo["nommayor"]))

        return dataReturn

    @staticmethod
    def imprimir_consulta_aux_banco(request_data):
        data = ConsultaService.filtro_aux_banco(request_data['model'])
        sumas = request_data["sumas"]
        for item in data:
            item = ConsultaAuxiliarFormatter._procesar_detalles(item, 'imprimir')
        
        empresa = EmpresaService.obtener_datos_empresa()

        nombre = "consultasauxbanco"
        params = {
            'data': data,
            'empresa': empresa,
            'model': request_data['model'],
            'sumas': sumas
        }

        pdf = Render.render_pdfkit('pdf/contabilidad/consultasauxbanco.html', params, nombre)
        return pdf
    
    @staticmethod
    def exportar_consulta_balance_general(request_data):
        numero = NumeroA()
        request_data['model']['mesfin'] = numero.mes_letra(
            "0{}".format(request_data['model']['mesfin']) if request_data['model']['mesfin'] < 10 else str(
                request_data['model']['mesfin']))
        model = []

        totales = {
            'parcial': 0,
            'total': 0,
        }

        for item in request_data['data']:
            item['parcial'] = 0 if item['parcial'] == None else item['parcial']
            item['total'] = 0 if item['total'] == None else item['total']

            totales['parcial'] = totales['parcial'] + item['parcial']
            totales['total'] = totales['total'] + item['total']

            model.append({
                'codigo': item['codigo'],
                'nombre': item['nombre'],
                'parcial': item['parcial'],
                'total': item['total']
            })

        model.append({
            'codigo': None,
            'nombre': None,
            'parcial': totales['parcial'],
            'total': totales['total']
        })

        dataReturn = Render.export_excel(model, 'INFORME DE BALANCE GENERAL AÑO: {} - MES: {}'.format(
            request_data['model']['año'], request_data['model']['mesfin']))

        return dataReturn

    @staticmethod
    def filtro_balance_prueba(model):
        try:
            sql = """
                select json_agg(json_build_object(
                    'codigo', codigo,
                    'nombre', nombre,
                    'saldoi', saldoi,
                    'debitos', debitos,
                    'creditos', creditos,
                    'saldof', saldof,
                    'color', color,
                    'codigo_id', codigo_id)) 
                from getbalprueba (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s);"""
            
            params = [
                model['tipo'],
                model['año'],
                model['mesini'],
                1 if model['vernit'] == True else 0,
                model['codigonom']['codigo1'] if model['codigonom']['codigo1'] != None else '',
                model['codigonom']['codigo2'] if model['codigonom']['codigo2'] != None else '',
                1 if model['vercusinmov'] == True else 0,
                model['mesfin'],
                model['consolidado'],
                model['niif']
            ]
            resultado = execute_procedure(sql=sql, params=params)
            if resultado[0][0] != None:
                return resultado[0][0]
            else:
                return []
        except:
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
    
    @staticmethod
    def imprimir_consulta_balance_prueba(request_data):
        data = ConsultaService.filtro_balance_prueba(request_data['model'])
        empresa = EmpresaService.obtener_datos_empresa()

        nombre = "consultabalanceprueba"

        params = {
            'data': data,
            'empresa': empresa,
            'model': request_data['model'],
            'totales': request_data["totales"]
        }

        pdf = Render.render_pdfkit('pdf/contabilidad/consultabalanceprueba.html', params, nombre)
        return pdf
    
    @staticmethod
    def exportar_consulta_balance_prueba(request_data):
        model = []
        totales = request_data["totales"]

        for item in request_data['datos'] :
            model.append(
                ConsultaAuxiliarFormatter._armar_movimiento_cajaprueba(
                    item['codigo'], 
                    item['nombre'], 
                    item['saldoi'], 
                    item['debitos'], 
                    item['creditos'], 
                    item['saldof']
                )
            )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_cajaprueba(
                None, "TOTAL", 
                totales["totales"]["inicial"], totales["totales"]["debito"], 
                totales["totales"]["credito"], totales["totales"]["final"]
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_cajaprueba(
                None, "INGRESOS", 
                totales["ingresos"]["inicial"], totales["ingresos"]["debito"], 
                totales["ingresos"]["credito"], totales["ingresos"]["final"]
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_cajaprueba(
                None, "GASTOS", 
                totales["gastos"]["inicial"], totales["gastos"]["debito"], 
                totales["gastos"]["credito"], totales["gastos"]["final"]
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_cajaprueba(
                None, "RESULTADOS", 
                totales["resultados_uno"]["ingr_gast_sin"], totales["resultados_uno"]["ingr_gast_deb"], 
                totales["resultados_uno"]["ingr_gast_cr"], totales["resultados_uno"]["ingr_gast_sfi"]
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_cajaprueba(
                None, "TOTAL ACTIVOS", 
                totales["activos"]["inicial"], totales["activos"]["debito"], 
                totales["activos"]["credito"], totales["activos"]["final"]
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_cajaprueba(
                None, "TOTAL PASIVO + PATRIMONIO", 
                totales["total_pasivo_patrimonio"]["inicial"], totales["total_pasivo_patrimonio"]["debito"], 
                totales["total_pasivo_patrimonio"]["credito"], totales["total_pasivo_patrimonio"]["final"]
            )
        )

        model.append(
            ConsultaAuxiliarFormatter._armar_movimiento_cajaprueba(
                None, "RESULTADO", 
                totales["resultado_dos"]["inicial"], totales["resultado_dos"]["debito"], 
                totales["resultado_dos"]["credito"], totales["resultado_dos"]["final"]
            )
        )
        request_data['tipo'] = 8
        nombreinforme = ConsultaAuxiliarFormatter._get_nombre_informe(request_data)
        dataReturn = Render.export_excel(model, nombreinforme)
        return dataReturn


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
        elif request_data['tipo'] == 8:
            mes_ini = Mes.objects.get(id=request_data['mes_ini'])
            mes_fin = Mes.objects.get(id=request_data['mes_fin'])
            nombreinforme = 'CONSULTA DE BALANCE DE PRUEBA' + ' AÑO: ' + str(
            request_data['anio']) + ' - ' + 'MES: ' + str(mes_ini.nombre) + ' HASTA ' + str(mes_fin.nombre)

        return nombreinforme
    
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

    def _armar_movimiento_bancos(tipo, numero, fecha, fecha_cg, nro_cg, doc_ref, detalle, nit, persona, debito, credito, saldo):
        return {
            'tipo': tipo or '',
            'numero': numero or '',
            'fecha': fecha or '',
            'fecha_cg': fecha_cg or '',
            'nro_cg': '' if nro_cg in [None, 'NULL'] else nro_cg,
            'doc_ref': doc_ref or '',
            'detalle': detalle or '',
            'nit': nit or '',
            'persona': persona or '',
            'debito': debito if debito is not None else '',
            'credito': credito if credito is not None else '',
            'saldo': saldo if saldo is not None else '',
        }
    
    def _armar_movimiento_cajaprueba(codigo, nombre, saldo_inicial, debitos, creditos, saldo_final):
        numero = NumeroA()
        return {
            'codigo': codigo or '',
            'nombre': nombre or '',
            'saldo_inicial': numero.numero_a_positivo(saldo_inicial) or '',
            'debitos': numero.numero_a_positivo(debitos) or '',
            'creditos': numero.numero_a_positivo(creditos) or '',
            'saldo_final': numero.numero_a_positivo(saldo_final) or '',
        }