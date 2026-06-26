from django.db import transaction
from apps.common_db.db import execute_procedure
from apps.parametros.services.empresa_service import EmpresaService
from apps.utils.render import Render
from apps.utils.util import NumeroA
from apps.utils.list import lists
from apps.parametros.models.parametrizacion import Mes
from apps.contabilidad.models.parametros import CentroCostos
from apps.contabilidad.models.documento import Mov
import pdb, json

class InformeService:
    @staticmethod
    def filtro_balance_general(model):
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
        
        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)
        
        if resultado[0][0] != None:
            return resultado[0][0]
        else:
            return []
    
    @staticmethod
    def imprimir_consulta_balance_general(model):
        data = InformeService.filtro_balance_general(model)
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
    def exportar_consulta_balance_general(request_data):
        numero = NumeroA()
        request_data['model']['mesfin'] = numero.mes_letra(request_data['model']['mesfin'])
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

        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)
            
        if resultado[0][0] != None:
            return resultado[0][0]
        else:
            return []
    
    @staticmethod
    def imprimir_consulta_balance_prueba(request_data):
        data = InformeService.filtro_balance_prueba(request_data['model'])
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
                InformeFormatter._armar_movimiento_cajaprueba(
                    item['codigo'], 
                    item['nombre'], 
                    item['saldoi'], 
                    item['debitos'], 
                    item['creditos'], 
                    item['saldof']
                )
            )

        model.append(
            InformeFormatter._armar_movimiento_cajaprueba(
                None, "TOTAL", 
                totales["totales"]["inicial"], totales["totales"]["debito"], 
                totales["totales"]["credito"], totales["totales"]["final"]
            )
        )

        model.append(
            InformeFormatter._armar_movimiento_cajaprueba(
                None, "INGRESOS", 
                totales["ingresos"]["inicial"], totales["ingresos"]["debito"], 
                totales["ingresos"]["credito"], totales["ingresos"]["final"]
            )
        )

        model.append(
            InformeFormatter._armar_movimiento_cajaprueba(
                None, "GASTOS", 
                totales["gastos"]["inicial"], totales["gastos"]["debito"], 
                totales["gastos"]["credito"], totales["gastos"]["final"]
            )
        )

        model.append(
            InformeFormatter._armar_movimiento_cajaprueba(
                None, "RESULTADOS", 
                totales["resultados_uno"]["ingr_gast_sin"], totales["resultados_uno"]["ingr_gast_deb"], 
                totales["resultados_uno"]["ingr_gast_cr"], totales["resultados_uno"]["ingr_gast_sfi"]
            )
        )

        model.append(
            InformeFormatter._armar_movimiento_cajaprueba(
                None, "TOTAL ACTIVOS", 
                totales["activos"]["inicial"], totales["activos"]["debito"], 
                totales["activos"]["credito"], totales["activos"]["final"]
            )
        )

        model.append(
            InformeFormatter._armar_movimiento_cajaprueba(
                None, "TOTAL PASIVO + PATRIMONIO", 
                totales["total_pasivo_patrimonio"]["inicial"], totales["total_pasivo_patrimonio"]["debito"], 
                totales["total_pasivo_patrimonio"]["credito"], totales["total_pasivo_patrimonio"]["final"]
            )
        )

        model.append(
            InformeFormatter._armar_movimiento_cajaprueba(
                None, "RESULTADO", 
                totales["resultado_dos"]["inicial"], totales["resultado_dos"]["debito"], 
                totales["resultado_dos"]["credito"], totales["resultado_dos"]["final"]
            )
        )
        request_data['tipo'] = 8
        nombreinforme = InformeFormatter._get_nombre_informe(request_data)
        dataReturn = Render.export_excel(model, nombreinforme)
        return dataReturn
    
    @staticmethod
    def filtro_estado_resultados(model):
        if model.get("estado_resultado_anual", False) :
            sql = """select * from getestadoresultados_anual (%s,%s,%s,%s,%s);"""
            
            params = [
                model['tipo'],
                model['año'],
                1,
                1 if model['ver_nits'] == True else 0,
                2 if model['mesacu'] == True else 2,
            ]
        else:
            sql = """
                select json_agg(json_build_object(
                    'codigo', codigo,
                    'nombre', nombre,
                    'parcial', parcial,
                    'total', total,
                    'color', color,
                    'nits', nits,
                    'codigo_id', codigo_id,
                    'orden', orden,
                    'principal', principal,
                    'occidente', occidente,
                    'costa', costa,
                    'eje', eje,
                    'aprincipal', aprincipal,
                    'aoccidente', aoccidente,
                    'acosta', acosta,
                    'aeje', aeje
                )) from getestadoresultados (%s,%s,%s,%s,%s,%s);"""
            
            params = [
                model['tipo'],
                model['año'],
                model['mesini'],
                1 if model['ver_nits'] == True else 0,
                2 if model['mesacu'] == True else 1,
                model['niif']
            ]
        
        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)

        # Consulta para movimientos por centros de costo
        sql = "select * from getestadoresultadoscc (%s,%s)"
        params= [model['año'], model['mesini'] if model['mesini'] else 1]

        with transaction.atomic():
            resultado_cc = execute_procedure(sql=sql, params=params)

        query = []
        if resultado[0][0] != None:
            if resultado_cc[0][0] != None :
                for item1 in resultado[0][0]:
                    for item in resultado_cc[0][0]:
                        if item1['codigo'] == item['codigo']:
                            centros_cc = CentroCostos.objects.filter(estado=True).order_by('id')
                            for cc in centros_cc:
                                if cc.id == item['cc_id']:
                                    item1['CC_' + cc.nombre] = item['valor']
                                    if 'CC_' + cc.nombre in query:
                                        print('')
                                    else:
                                        query.append('CC_' + cc.nombre)
                                    item1['CC'] = query
            if isinstance(resultado[0][0], str):
                return json.loads(resultado[0][0])
            return resultado[0][0]
        else:
            return []
        
    @staticmethod
    def imprimir_consulta_estado_resultados(model):
        data = InformeService.filtro_estado_resultados(model)
        empresa = EmpresaService.obtener_datos_empresa()

        nombre = "consultaestadoresultados"

        params = {
            'data': data,
            'empresa': empresa,
            'model': model
        }

        pdf = Render.render_pdfkit('pdf/contabilidad/consultaestadoresultados.html', params, nombre)
        return pdf
    
    @staticmethod
    def exportar_consulta_estado_resultados(request_data):
        model = []
        for item in request_data['data']:

            if request_data['model']['ccosto'] == True:
                obj = {
                    'codigo': item['codigo'],
                    'nombre': item['nombre'],
                    'total': item['total'],
                }
            elif request_data['model'].get('estado_resultado_anual', False) == True:
                obj = {
                    'codigo': item['codigo'],
                    'nombre': item['nombre'],
                }

                for mes in request_data['model'].get("meses", []):
                    mes_nombre = next((f['nombre'].lower() for f in lists.mes_letra if f['mes'] == mes), None)
                    if mes_nombre:
                        obj[mes_nombre] = item.get(mes_nombre, 0)

                obj['total'] = item['total']
            else:
                obj = {
                    'codigo': item['codigo'],
                    'nombre': item['nombre'],
                    'parcial': item['parcial'],
                    'total': item['total'],
                }

            if request_data['model']['ccosto'] == True:
                try:
                    for cc in item['CC']:
                        obj[cc] = item[cc]
                except:
                    pass

            model.append(obj)

        dataReturn = Render.export_excel(model, 'INFORME DE ESTADO DE RESULTADOS AÑO: {} - MES: {}'.format(request_data['model']['año'], request_data['model']['mesfin']))

        return dataReturn
    
    @staticmethod
    def filtro_comprobante_diario(model, tipo):
        tag = 0
        if model['todas'] == None:
            tag = model['tipo']
        
        sql = """
            select json_agg(json_build_object(
                'numero', numero,
                'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                'codigo', codigo,
                'nombre', nombre,
                'documento', documento,
                'nombrecompleto', nombrecompleto,
                'nombre', nombre,
                'detalle', detalle,
                'valor_db', valor_db,
                'valor_cr', valor_cr,
                'estado', estado,
                'encabezado', encabezado,
                'total', total,
                'tipodocumento', tipodocumento,
                'tipo',tipo,
                'id',id
            )) from getcomprobante (%s,%s,%s,%s,%s,%s,%s,%s);"""
        
        params = [
            model['tipodoc'],
            model['finicio'],
            model['ffin'],
            1 if model['estado']['abiertos'] == True else 0,
            1 if model['estado']['cerrados'] == True else 0,
            1 if model['estado']['anulados'] == True else 0,
            tag,
            tipo
        ]

        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)
        
        if resultado[0][0] != None:
            return resultado[0][0]
        else:
            return []

    @staticmethod
    def exportar_consulta_comprobrante_diario(request_data):
        model = []
        if request_data['tab'] == "detalle":
            ccosto = ''
            cod_concepto = ''
            for item in request_data['model']:
                mov = Mov.objects.filter(documento_id=item['id'], detalle=item['detalle']).first()
                if mov:
                    cod_concepto = mov.concepto.codigo if mov.concepto else ''
                    ccosto = mov.centro_costos.nombre if mov.centro_costos else ''
                model.append({
                    'numero': item['numero'],
                    'fecha': item['fecha'],
                    'codigo': item['codigo'],
                    'nombre': item['nombre'],
                    'codigo_concepto': cod_concepto,
                    'centro_costo': ccosto,
                    'documento': item['documento'],
                    'nombre': item['nombrecompleto'],
                    'concepto': item['nombre'],
                    'detalle': item['detalle'],
                    'debito': item['valor_db'],
                    'credito': item['valor_cr'],
                })
            dataReturn = Render.export_excel(model, (
                'CONSULTA DE COMPROBANTE DIARIO - DETALLADA - DESDE {} - HASTA {}').format(request_data['finicio'],
                                                                                           request_data['ffin']))
        else:
            totaldb = 0
            totalcr = 0
            grantotal = 0

            for item in request_data['model']:
                totaldb = totaldb + int(item['valor_db'])
                totalcr = totalcr + int(item['valor_cr'])
                grantotal = grantotal + int(item['total'])

                model.append({
                    'codigo': item['codigol'],
                    'nombre': item['nombrel'],
                    'debito': item['valor_db'],
                    'credito': item['valor_cr'],
                    'total': item['total'],
                })

            model.append({
                'codigo': None,
                'nombre': 'Totales:',
                'debito': totaldb,
                'credito': totalcr,
                'total': grantotal,
            })
            dataReturn = Render.export_excel(model, 'CONSULTA DE COMPROBANTE DIARIO - TOTALES')
        return dataReturn
    
    @staticmethod
    def imprimir_consulta_comprobrante_diario(request_data):
        data = InformeService.filtro_comprobante_diario(request_data['model'], request_data['model']['imprimir'])
        empresa = EmpresaService.obtener_datos_empresa()

        nombre = "consultacomprobantediario"

        totales = {
            'db': 0,
            'cr': 0,
            'total': 0,
        }

        totalesdoc = []
        for item in data:
            item['valor_db'] = 0 if item['valor_db'] == None else item['valor_db']
            item['valor_cr'] = 0 if item['valor_cr'] == None else item['valor_cr']

            totales['db'] = totales['db'] + item['valor_db']
            totales['cr'] = totales['cr'] + item['valor_cr']

            if request_data['model']['imprimir'] == 2:
                item['total'] = 0 if item['total'] == None else item['total']
                totales['total'] = totales['total'] + item['total']

        # pdb.set_trace()
        totalesdoc = {
            'recibos_caja': request_data['abiertos']['recibos_caja'] + request_data['anulados']['recibos_caja'] + request_data['cerrados']['recibos_caja'],
            'egresos': request_data['abiertos']['egresos'] + request_data['anulados']['egresos'] + request_data['cerrados']['egresos'],
            'notas': request_data['abiertos']['notas'] + request_data['anulados']['notas'] + request_data['cerrados']['notas'],
            'facturas': request_data['abiertos']['facturas'] + request_data['anulados']['facturas'] +  request_data['cerrados']['facturas'],
        }
        params = {
            'data': data,
            'empresa': empresa,
            'abiertos': request_data['abiertos'],
            'anulados': request_data['anulados'],
            'cerrados': request_data['cerrados'],
            'model': request_data['model'],
            'totalesdoc': totalesdoc,
            'totales': totales,
        }
        pdf = Render.render_pdfkit('pdf/contabilidad/consultacomprobantediario.html', params, nombre)
        return pdf


class InformeFormatter:

    @staticmethod
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
    
    def _get_nombre_informe(request_data):
        nombreinforme = ''
        if request_data['tipo'] == 8:
            mes_ini = Mes.objects.get(id=request_data['mes_ini'])
            mes_fin = Mes.objects.get(id=request_data['mes_fin'])
            nombreinforme = 'CONSULTA DE BALANCE DE PRUEBA' + ' AÑO: ' + str(
            request_data['anio']) + ' - ' + 'MES: ' + str(mes_ini.nombre) + ' HASTA ' + str(mes_fin.nombre)

        return nombreinforme