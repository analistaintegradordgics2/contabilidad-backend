from django.db import transaction
from apps.common_db.db import execute_procedure
from apps.parametros.services.empresa_service import EmpresaService
from apps.utils.render import Render
from apps.utils.util import NumeroA
from apps.parametros.models.parametrizacion import Mes

class InformeService:
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