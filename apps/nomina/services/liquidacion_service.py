import json, pdb
import os
import shutil
from datetime import datetime
from django.db import transaction
from django.conf import settings

from django.db.models import Q, Sum

from apps.nomina.models.parametrizacion import NominaParametros
from apps.nomina.models.liquidacion import LiquidacionNomina
from apps.parametros.models.parametrizacion import Anio, Mes, Parametros
from apps.utils.util import NumeroA
from apps.parametros.services.empresa_service import EmpresaService
from apps.utils.render import Render
from apps.common_db.db import execute_procedure
from apps.nomina.models.vacaciones import Vacaciones
from apps.nomina.serializers.vacaciones import VacacionesSerializer
from apps.nomina.models.contratos import ContratoNominaNovedades
from apps.contabilidad.services.documento_cierre_service import DocumentoCierreService
from apps.utils.funciones import Funciones
from apps.utils.email import send_email_client
from apps.contabilidad.models.documento import Mov, Documentos

class LiquidacionService:

    @staticmethod
    def validar_parametrizacion(anio:Anio):
        transmitir_provisiones = NominaParametros.objects.filter(parametro="transmitir_provisiones").first().valor
        # Esta validacion la solicito wendy, que antes de ingresar a la liquidacion de la nomina, la nomina debe estar totalmente parametrisada
        validate = True
        parametros_faltantes = []
        for item in NominaParametros.objects.exclude(grupo="9"):
            if item.tipo == "select" or item.tipo == "decimal" or item.tipo == "boolean" or item.tipo == "number":
                if item.grupo == "8" :
                    if not transmitir_provisiones or transmitir_provisiones.lower() == "false" :
                        if item.valor == None :
                            validate = False
                            parametros_faltantes.append(item.label)
                else :
                    if item.valor == None :
                        validate = False
                        parametros_faltantes.append(item.label)
            elif item.tipo == "select_array" :
                if item.parametro != "licencias_no_remuneradas" :
                    if item.valor == "[]" or item.valor == None :
                        validate = False
                        parametros_faltantes.append(item.label)
        
        if anio.salario_minimo == None or anio.salario_minimo == 0 :
            validate = False
            parametros_faltantes.append("salario minimo")
        
        if anio.aux_transporte == None or anio.aux_transporte == 0 :
            validate = False
            parametros_faltantes.append("auxilio de transporte")
        # Fin de validacion

        return validate, parametros_faltantes

    @staticmethod
    def nominas_por_liquidar(anio, mes, periodo, centro_costo) :
        sql = "select * from get_nominas_por_liquidar(%s, %s, %s, %s);"
        params = [anio.nombre, str(mes), periodo, centro_costo]

        result = execute_procedure(sql, params)

        if result[0][0] != None:
            return {
                "por_liquidar": result[0][0]["por_liquidar"], 
                "liquidadas": result[0][0]["liquidadas"]
            }

        return {"por_liquidar": [], "liquidadas": []}

    @staticmethod
    def vacaciones(contrato_novedad_id) :
        sql = "select * from get_liquidar_vacaciones(%s);"
        params = [contrato_novedad_id]

        resultado = execute_procedure(sql, params)

        if len(resultado) > 0 :
            numero = NumeroA()
            resultado = resultado[0][0]
            resultado["fecha_vacaciones"]["fecha_ini"] = numero.format_fecha(datetime.strptime(resultado["fecha_vacaciones"]["fecha_ini"] , "%Y-%m-%d"), 1)
            resultado["fecha_vacaciones"]["fecha_fin"] = numero.format_fecha(datetime.strptime(resultado["fecha_vacaciones"]["fecha_fin"] , "%Y-%m-%d"), 1)
            resultado["fecha_vacaciones"]["fecha_reintegro"] = numero.format_fecha(datetime.strptime(resultado["fecha_vacaciones"]["fecha_reintegro"] , "%Y-%m-%d"), 1)
        else :
            resultado = []
        return resultado

    @staticmethod
    def liquidar_vacaciones(request_data, user=None):

        
        data = request_data

        if data["vacaciones_liquidadas"] == False :
            vac = Vacaciones()
            vac.contrato_id = data["contrato"]
            vac.contrato_novedades_id = data["id"]
            vac.dias = data["dias"]
            vac.sueldo = data["sueldo"]
            vac.valor_dia = data["valor_dia"]
            vac.subtotal = data["subtotal"]
            vac.salud_valor_porcentaje = data["salud"]["valor_porcentaje"]
            vac.salud_total = data["salud"]["total"]
            vac.pension_valor_porcentaje = data["pension"]["valor_porcentaje"]
            vac.pension_total = data["pension"]["total"]
            vac.total = data["total"]
            vac.uc_id = user.id
            vac.save()

            nove = ContratoNominaNovedades.objects.get(pk=data["id"])
            nove.vacaciones_liquidadas = True
            nove.save()
        else :
            data = VacacionesSerializer(Vacaciones.objects.get(pk=data["vacaciones_id"])).data
            data = data["data"]

        empresa = EmpresaService.obtener_datos_empresa()
            
        params = {
            'empresa': empresa,
            'data': data
        }

        pdf = Render.render_pdfkit('pdf/nomina/vacaciones.html', params, "Liquidación de vacaciones")

        return pdf

    @staticmethod
    @transaction.atomic
    def liquidar(request_data, user=None):
        
        data = request_data

        anio = Anio.objects.get(pk=data["filtros"]["anio"]).nombre
        mes = Mes.objects.get(pk=data["filtros"]["mes"]).numero
        periodo = data["filtros"]["periodo"]
        descripcion = data["filtros"]["descripcion"]
        totales = data["totales"]
        totales["fecha_doc"] = data["fecha_doc"]
        fecha_inicial = data["filtros"]["fecha_inicial"]
        fecha_final = data["filtros"]["fecha_final"]
    
        sql = "select * from liquidar_nomina(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        params = [anio, mes, periodo, descripcion, json.dumps(totales), data["data"], fecha_inicial, fecha_final, user.id]

        resultado = execute_procedure(sql, params) 

        result = resultado[0][0]

        if result.get("out_id_doc_empleador"):
            DocumentoCierreService.cerrar(result.get("out_id_doc_empleador"), user.id)

        if result.get("out_id_doc_empleado"):
            DocumentoCierreService.cerrar(result.get("out_id_doc_empleado"), user.id)

        return result

    @staticmethod
    def acciones(request_data):
        data = request_data
        whatsapp = data.get("whatsapp", False)
        email = data.get("email", False)
        
        licencias_no_remuneradas_param = NominaParametros.objects.filter(parametro='licencias_no_remuneradas').first()
        if licencias_no_remuneradas_param:
            licencias_no_remuneradas = json.loads(licencias_no_remuneradas_param.valor)
        else:
            licencias_no_remuneradas = []
            
        novedad_sueldo_param = NominaParametros.objects.filter(parametro='sueldo').first()
        if novedad_sueldo_param:
            novedad_sueldo = int(novedad_sueldo_param.valor)
        else:
            novedad_sueldo = 0

        ruta_tmp = os.path.join(settings.MEDIA_ROOT, "tmp")
        if os.path.exists(ruta_tmp):
            shutil.rmtree(ruta_tmp)
        
        os.makedirs(ruta_tmp, exist_ok=True)

        empresa = EmpresaService.obtener_datos_empresa()

        if data["tipo"] in [1, 2, 3]: # 1 = desprendible, 2 = liquidaciones, 3 = ???
            if email == True:
                return LiquidacionService._enviar_desprendibles_email(data, empresa, licencias_no_remuneradas, novedad_sueldo, ruta_tmp)
            elif whatsapp == True:
                return LiquidacionService._enviar_desprendibles_whatsapp(data, empresa, licencias_no_remuneradas, novedad_sueldo, ruta_tmp)
            else:
                params = {
                    'empresa': empresa,
                    'liquidaciones': data["data"],
                    'periodo': data["periodo"],
                    'licencias_no_remuneradas': licencias_no_remuneradas,
                    'novedad_sueldo': novedad_sueldo
                }
                
                if data["tipo"] == 1:
                    nombre = "Desprendible"
                    return Render.render_pdfkit('pdf/nomina/desprendibles.html', params, nombre)
                else:
                    nombre = "Liquidaciones"
                    return Render.render_pdfkit('pdf/nomina/liquidaciones.html', params, nombre)

    @staticmethod
    def _enviar_desprendibles_email(data, empresa, licencias_no_remuneradas, novedad_sueldo, ruta_tmp):
        sin_correo = []
        numero = NumeroA()
        now = datetime.now()
        subject = "Desprendible de pago - {} de {} {}".format(now.day, numero.mes_letra(str(now.month)), now.year)

        for item in data["data"]:
            params = {
                'empresa': empresa,
                'liquidaciones': [item],
                'periodo': data["periodo"],
                'licencias_no_remuneradas': licencias_no_remuneradas,
                'novedad_sueldo': novedad_sueldo
            }
            pdf = Render.render_pdfkit('pdf/nomina/desprendibles.html', params, "Desprendible")
            archivo = os.path.join(settings.MEDIA_ROOT, "tmp", "Desprendible de pago - {}.pdf".format(item["nombre"].replace(" ", "_")))
            
            with open(archivo, "wb") as file:
                file.write(pdf.content) 
                file.close()

            pdfs = [archivo]

            datos_email = {
                "data": {
                    "nombre": item["nombre"],
                    "periodo": data["periodo"]
                }
            }

            template = os.path.join(settings.TEMPLATES_DIR, "pdf", "nomina", "plantilla_desprendible_pago.html")

            if item.get("correo") and item["correo"] != " ":
                asunto = subject + " - " + item["nombre"]
                result = False
                try:
                    result = send_email_client(template, datos_email, asunto, [item["correo"]], pdfs)
                except:
                    pass

                if result is False:
                    raise Exception("Error al enviar el correo. Por favor validar bitacora de correos.")
            else:
                sin_correo.append(item["nombre"])
        
        if len(sin_correo) == 0:
            resp = {
                "status": "success",
                "status_code": 200,
                "msg": "Desprendibles enviados correctamente."
            }
        else:
            resp = {
                "status": "success" if len(sin_correo) < len(data["data"]) else "warning",
                "status_code": 400,
                "msg": f"{'Desprendibles enviados correctamente.' if len(sin_correo) < len(data['data']) else 'Desprendibles no enviados.'}<br>Los siguientes empleados no tienen correo electrónico:<br>{', '.join(sin_correo)}"
            }
        
        return resp

    @staticmethod
    def _enviar_desprendibles_whatsapp(data, empresa, licencias_no_remuneradas, novedad_sueldo, ruta_tmp):
        
        novedad = False
        for item in data["data"]:
            liqui = LiquidacionNomina.objects.filter(id=item["id"]).first()
            mes = Mes.objects.get(pk=liqui.mes_id).nombre
            anio = liqui.fecha_inicial.year
            persona = {
                "id": liqui.contrato.persona_id,
                "nombre": item["nombre"],
                "documento": item["documento"],
            }
            params = {
                'empresa': empresa,
                'liquidaciones': [item],
                'periodo': data["periodo"],
                'licencias_no_remuneradas': licencias_no_remuneradas,
                'novedad_sueldo': novedad_sueldo
            }
            pdf = Render.render_pdfkit('pdf/nomina/desprendibles.html', params, "Desprendible")
            nombre_archivo = "Desprendible de pago - {}.pdf".format(item["nombre"].replace(" ", "_"))
            archivo = os.path.join(settings.MEDIA_ROOT, "tmp", nombre_archivo)
            
            with open(archivo, "wb") as file:
                file.write(pdf.content) 
                file.close()
            
            params["periodo"] = liqui.periodo.nombre
            params["mes_anio"] = f"{mes.lower().capitalize()} de {anio}"
            params["persona"] = persona

            result = Funciones.enviar_whatsapp(nombre_archivo, archivo, params, 4)
            if result["status"] == 400:
                result["status"] = "warning"
                return result
            elif result["status"] != 200:
                novedad = True
        
        return {
            "status": "success" if novedad == False else "warning",
            "msg": "Desprendibles enviados correctamente." if novedad == False else "Algunos mensajes no fueron enviados por inconsistencia, por favor revise la bitácora de WhatsApp."
        }

    @staticmethod
    @transaction.atomic
    def anular(request_data, user=None):
        data = request_data

        msgError = None
        docAnulados = []
        docAfectados = []

        for item in data :
            # Primero. Eliminar o anular documento de empleado
            movs = Mov.objects.filter(Q(persona_id=item["persona_id"]) | Q(docref__iexact=f"liq emple: [{item['liquidacion_id']}]"), documento_id=item["documento_id"])
            if len(movs) == len(Mov.objects.filter(documento_id=item["documento_id"])) :
                # Si la cantidad de movimientos a eliminar es igual a la cantidad de movimientos que tiene el documento, se anula el documento
                doc = DocumentoCierreService.anular(item["documento_id"], user.id, "Anulación de liquidación de nómina")
                docAnulados.append(doc.numero)
            else :
                movs.delete()
                if not item["documento_id"] in docAfectados :
                    docAfectados.append(item["documento_id"])
            
            # Segundo. Eliminar o anular documento de empleador
            movs = Mov.objects.filter(docref__iexact=f"liq patro: [{item['liquidacion_id']}]")
            if len(movs) > 0 :
                if len(movs) == len(Mov.objects.filter(documento_id=movs[0].documento_id)) :
                    # Si la cantidad de movimientos a eliminar es igual a la cantidad de movimientos que tiene el documento, se anula el documento
                    doc = DocumentoCierreService.anular(movs[0].documento_id, user.id, "Anulación de liquidación de nómina")
                    docAnulados.append(doc.numero)
                else :
                    if not movs[0].documento_id in docAfectados :
                        docAfectados.append(movs[0].documento_id)
                    
                    movs.delete()
            
            # Marcar liquidación como anulada
            LiquidacionNomina.objects.filter(id=item["liquidacion_id"]).update(
                estado=False,
                um_id=user.id,
                delete=datetime.now(),
            )
        
        # Nelson Lugo 10/04/2025 Bita #66366 - Cuando se eliminen registros de una nota, se debe ajustar el valor total de la nota que solo los resgistros que quedaron
        for item in docAfectados :
            doc = Documentos.objects.get(pk=item)
            doc.total = Mov.objects.filter(documento_id=item).aggregate(Sum("valor_db"))["valor_db__sum"]
            doc.save()
        
        msgAnulado = ", ".join(map(str, docAnulados)) if len(docAnulados) > 0 else None

        resp = {
            "status": 200,
            "msg": f"Liquidación anulada correctamente.{f' Documentos anulados:  {msgAnulado}' if msgAnulado != None else ''}",
        }

        if msgError != None :
            resp["status"] = 400

        return resp