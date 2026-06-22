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
            item = ConsultaAuxiliarFormatter.procesar_detalles(item)
        
        empresa = EmpresaService.obtener_datos_empresa()

        nombre = "consultasaux"
        params = {
            'data': data,
            'empresa': empresa,
            'model': model,
            'sumas': sumas,
            'filtros': filtro
        }

        if request_data["tipo_impresion"] == 2:
            # Extracto
            total_debito = 0
            total_credito = 0
            total_comision = 0
            total_iva = 0
            total_otros = 0
            total_pagos = 0

            concepto_comision = int(Parametros.objects.filter(parametro='concepto_comision').first().valor)
            concepto_iva = int(Parametros.objects.filter(parametro='concepto_iva').first().valor)
            concepto_pago_propietario = int(Parametros.objects.filter(parametro='concepto_pago_propietario').first().valor)

            data_extracto = []
            for i, item in enumerate(data):
                # pdb.set_trace()
                if (i + 1) < len(data):
                    if item["concepto"] == concepto_comision:
                        total_comision = total_comision + item["valor_db"]
                    elif item["concepto"] == concepto_iva:
                        total_iva = total_iva + item["valor_db"]
                    elif item["concepto"] == concepto_pago_propietario:
                        total_pagos = total_pagos + (item["valor_db"] if item["valor_db"] != None else 0)

                    # Nelson lugo 03/09/2024 - Se agrega esta validacion para que solo tenga en cuenta los movimientos mas no los saldos
                    if item["id"] != None:
                        total_debito = total_debito + item["valor_db"]
                        total_credito = total_credito + item["valor_cr"]
                        total_otros = total_otros + item["valor_db"]

                    data_extracto.append({
                        "detalle": item["detalle"],
                        "valor_db": item["valor_db"],
                        "valor_cr": item["valor_cr"],
                        "concepto_id": int(item["concepto"]) if item["concepto"] != None else "",
                        "fecha_documento": item["fecha"] if item["fecha"] != None else "",
                        "numero_documento": item["numero"] if item["numero"] != None else "",
                        "tipo_documento": item["tipo"] if item["tipo"] != None else "",
                        "color": item["color"],
                    })
            
            # Nelson Lugo 03/09/2024 - Se le suma al valor total debito y credito el saldo inicial
            if len(data) > 0 :
                total_debito += data[0]["valor_db"]
                total_credito += data[0]["valor_cr"]
            # pdb.set_trace()
            total_debito = round(total_debito, 1)
            total_credito = round(total_credito, 1)
            total_comision = round(total_comision, 1)
            total_iva = round(total_iva, 1)
            total_otros = round(total_otros, 1)
            total_pagos = round(total_pagos, 1)
            total_cancelar = round(total_credito - total_debito, 1)

            resumen = {
                "total_debito": total_debito,
                "total_credito": total_credito,
                "total_comision": total_comision,
                "total_iva": total_iva,
                "total_otros": total_otros,
                "total_pagos": total_pagos,
                "total_cancelar": total_cancelar
            }

            obj_persona = Persona.objects.get(pk=request_data["model"]["persona"])

            numero = NumeroA()
            mespago = numero.mes_letra("0{}".format(request_data['model']['mesini']) if request_data['model']['mesini'] < 10 else str(request_data['model']['mesini']))
            mespago = "{} {}".format(mespago, datetime.date.today().strftime("%Y"))

            cta_prop = Parametros.objects.filter(parametro='cta_prop_id').first().valor
            cta_arr = Parametros.objects.filter(parametro='cta_arr_id').first().valor
            tipo_estado_cuenta = "ESTADO DE CUENTA"
            prop_arren = "n"
            modelIn = model
            if modelIn["codigo"] == int(cta_prop) :
                tipo_estado_cuenta = "ESTADO DE CUENTA DE PROPIETARIO"
                prop_arren = "p"
            
            if modelIn["codigo"] == int(cta_arr) :
                tipo_estado_cuenta = "ESTADO DE CUENTA DE ARRENDATARIO"
                prop_arren = "a"
            
            numero = NumeroA()
            mes_inicio = numero.mes_letra(f"0{modelIn['mesini']}" if modelIn["mesini"] < 10 else modelIn["mesini"])
            mes_fin = numero.mes_letra(f"0{modelIn['mesfin']}" if modelIn["mesini"] < 10 else modelIn["mesini"])

            persona = PersonaFormatter._get_data_persona_pago(obj_persona)

            params = {
                "empresa": empresa,
                "persona": persona,
                "data": data_extracto,
                "mespago": "",
                "observacion": "",
                "resumen": resumen,
                "tipo": "P",
                "extracto_total": False,
                "inmuebles": [],
                "encabezado": {
                    "tipo": "auxiliar",
                    "titulo": tipo_estado_cuenta,
                    "tipo_estado_cuenta": prop_arren,
                    "mes_inicio": mes_inicio,
                    "mes_fin": mes_fin,
                    "anio": modelIn["año"],
                }
            }
            pdf = Render.render('pdf/contrato/extractos.html', {"datos": [params]}, "Extracto propietarios")

            if request_data["enviar_correo"] == True:

                ruta_tmp = os.path.join(settings.MEDIA_ROOT, "tmp")
                if os.path.exists(ruta_tmp):
                    shutil.rmtree(ruta_tmp)
                
                os.makedirs(ruta_tmp, exist_ok=True)

                today = datetime.date.today()
                tt = today.timetuple()
                monthText = lists.months[tt.tm_mon]
                dayWeekText = lists.weeks[tt.tm_wday]
                self_ciudad_empresa = get_ciudad_inmo()
                datos_email = {
                    'fecha': '{}, {} {} de {} {}'.format(self_ciudad_empresa, dayWeekText, tt.tm_mday, monthText, tt.tm_year),
                    'persona': obj_persona.n_completo,
                    'mespago': "",
                    'tipo': "p",
                    'empresa': empresa
                }

                subject = '{} {}'.format(tipo_estado_cuenta, obj_persona.n_completo)
                template = settings.MEDIA_ROOT + '/../apps/templates/pdf/pagos/plantilla_email_extractos.html'

                archivo = settings.MEDIA_ROOT + "/tmp/{}_extracto.pdf".format(obj_persona.documento)
                pdfs = []

                with open(archivo, "wb") as file:  # Abrimos el archivo en modo escritura
                    file.write(pdf.content)
                    file.close()

                pdfs.append(archivo)
                emails = request_data["email"].split(';')

                #@TODO
                # # LeidyB - Se envia como parametro tipo = 3 para correo de propietarios
                # try:
                #     send_email_client(template, datos_email, subject, emails, pdfs, {"tipo": 3})
                # except:
                #     pass

            return pdf

        pdf = Render.render_pdfkit('pdf/contabilidad/consultasaux.html', params, nombre)
        return pdf
            
class ConsultaAuxiliarFormatter:

    def procesar_detalles(item):
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
            if len(item['detalle']) > 100:
                item['detalle'] = item['detalle'][:100] + "..."
