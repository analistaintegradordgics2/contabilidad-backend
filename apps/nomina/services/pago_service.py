import os
import json
import errno
from django.conf import settings
from django.db import transaction
from django.http import HttpResponse
import pdb

from apps.common_db.db import execute_procedure
from apps.nomina.models.novedades import NovedadesCentroCosto
from apps.nomina.models.parametrizacion import NominaParametros
from apps.parametros.models.parametrizacion import Mes
from apps.parametros.services.empresa_service import EmpresaService
from apps.contabilidad.services.documento_cierre_service import DocumentoCierreService
from apps.utils.funciones import Funciones
from apps.utils.render import Render
from apps.utils.util import NumeroA


class PagoService:

    @staticmethod
    def consultar_empleados_a_pagar(periodo_id, mes_id, anio_id, centro_costos_id=None):
        """
        Consulta los empleados pendientes de pago mediante procedimiento almacenado.
        """
        sql = "select * from get_pago_empleados(%s, %s, %s, %s);"
        params = [periodo_id, mes_id, anio_id, centro_costos_id]

        resultado = execute_procedure(sql, params)

        if resultado and len(resultado) > 0 and resultado[0][0] is not None:
            return resultado[0][0]

        return []

    @staticmethod
    def validar_parametrizacion(data):
        """
        Valida que existan los parámetros requeridos antes de realizar el pago:
        - Parámetro de sueldo configurado.
        - Centros de costo con cta crédito configurada para la novedad de sueldo.
        - Módulo de nómina (grupo 9) totalmente parametrizado.
        """
        params_sueldo = NominaParametros.objects.filter(parametro="sueldo").first()
        if not params_sueldo or params_sueldo.valor is None:
            return {
                "valido": False,
                "status": 400,
                "data": None,
                "msg": "Por favor primero parametrice el sueldo antes de realizar el pago.",
                "error": "",
            }

        for liqui in data:
            novedad_cc = NovedadesCentroCosto.objects.filter(
                centro_costos_id=liqui.get("centro_costos_id"),
                novedades_id=params_sueldo.valor
            ).first()

            if novedad_cc is not None:
                if novedad_cc.mayor_cta_credito_id is None:
                    return {
                        "valido": False,
                        "status": 400,
                        "data": None,
                        "msg": "Por favor primero parametrice la cta crédito del centro de costo en sueldo antes de realizar el pago.",
                        "error": "",
                    }
            else:
                return {
                    "valido": False,
                    "status": 400,
                    "data": None,
                    "msg": "Por favor primero parametrice el centro de costo en la novedad de sueldo antes de realizar el pago.",
                    "error": "",
                }

        params_pago_nomina = NominaParametros.objects.filter(valor=None, grupo=9)
        if params_pago_nomina.exists():
            return {
                "valido": False,
                "status": 400,
                "data": None,
                "msg": "Por favor primero parametrice el módulo de nómina antes de realizar el pago.",
                "error": "",
            }

        return {"valido": True}

    @staticmethod
    @transaction.atomic
    def pagar(filtros, data, user=None):
        """
        Valida y ejecuta el procedimiento almacenado para realizar el pago a empleados
        y cierra los documentos generados en Python.
        """
        validacion = PagoService.validar_parametrizacion(data)
        if not validacion.get("valido"):
            return {
                "status": validacion.get("status", 400),
                "data": validacion.get("data"),
                "msg": validacion.get("msg"),
                "error": validacion.get("error", ""),
            }

        user_id = user.id if user and hasattr(user, 'id') else (filtros.get("usuario") or 1)
        filtros["usuario"] = user_id

        sql = "select * from pago_empleados(%s, %s);"
        params = [json.dumps(filtros), json.dumps(data)]

        resultado = execute_procedure(sql, params)

        docs_generados = []
        if resultado and len(resultado) > 0 and resultado[0][0] is not None:
            docs_generados = resultado[0][0]

        # Cerrar los documentos contables generados mediante DocumentoCierreService
        for doc in docs_generados:
            doc_id = doc.get("documento_id")
            if doc_id:
                try:
                    DocumentoCierreService.cerrar(doc_id, user_id)
                except Exception as e:
                    pass

        return {
            "status": 200,
            "data": docs_generados
        }

    @staticmethod
    def generar_archivo(filtros, data):
        """
        Genera archivo según la forma de pago:
        - 2: Cheques (Excel)
        - 3: Transferencia bancaria (archivo plano txt o csv)
        """
        forma_pago = filtros.get("forma_pago")

        if forma_pago == 4:
            # Cheque - Generar archivo excel de cheques
            numero = NumeroA()
            array = []
            # pdb.set_trace()
            num_cheque = int(filtros.get("num_cheque", 1)) - 1

            for item in data:
                num_cheque += 1
                array.append({
                    "empleado": item["persona"]["nombre"],
                    "documento": item["persona"]["documento"],
                    "total": item["neto"],
                    "numero_cheque": num_cheque,
                    "fecha": filtros.get("fecha_doc"),
                    "valor_letra": numero.numero_a_moneda(int(item["neto"])),
                    "cuenta": item["forma_pago"]["num_cuenta"],
                    "banco": item["forma_pago"]["banco"]["nombre"],
                    "tipo_cuenta": item["forma_pago"]["tipo_cuenta"]["nombre"]
                })

            return Render.export_excel(array, "CHEQUES PAGO EMPLEADOS")

        elif forma_pago == 5:
            # Transferencia - Generar archivo plano de transferencias
            nomina_path = os.path.join(settings.MEDIA_ROOT, "nomina")
            os.makedirs(nomina_path, exist_ok=True)

            mes_pago = Mes.objects.get(pk=filtros["mes_pago"]).numero
            archivo_path = os.path.join(nomina_path, "plano_pago_empleados.txt")

            model = {
                "archivo": archivo_path,
                "data": data,
                "cta_banco": filtros.get("ctabanco"),
                "mes_pago": int(mes_pago),
                "tipopago": 4
            }

            result = Funciones.generar_plano_banco(model)

            if result.get("tipo_archivo") == "txt":
                return HttpResponse(open(model['archivo'], "r"), content_type='text/plain')
            elif result.get("tipo_archivo") == "csv":
                return result["archivo"]

        return HttpResponse("Forma de pago no soportada", status=400)

    @staticmethod
    def exportar(request_data):
        """
        Exporta a Excel los pagos por pagar o pagados, incluyendo detalles si tipo == 2.
        """
        data = request_data
        model = []
        tab = data.get("tab")
        tipo = data.get("tipo")

        if tab == 1:
            nombre_archivo = "PAGO EMPLEADO POR PAGAR"
        else:
            nombre_archivo = "PAGO EMPLEADO PAGADOS"

        for item in data.get("data", []):
            if tab == 1:
                model.append({
                    "identificacion": item["persona"]["documento"],
                    "nombre": item["persona"]["nombre"],
                    "total_devengado": item["total_devengado"],
                    "total_deducido": item["total_deducido"],
                    "neto": item["neto"],
                })
            else:
                model.append({
                    "identificacion": item["persona"]["documento"],
                    "nombre": item["persona"]["nombre"],
                    "total_devengado": item["total_devengado"],
                    "total_deducido": item["total_deducido"],
                    "neto_pagado": item["neto"],
                    "documento": item["documento"]["numero"],
                    "fecha_pago": item["fecha_pago"],
                    "usuario_pago": item["usuario_pago"]["nombre"],
                })

            if tipo == 2:
                result = [f for f in item.get("detalle_liquidacion", []) if f.get("tipo_novedad", {}).get("id") == 3]
                for det in result:
                    model.append({
                        "identificacion": det["descripcion"],
                        "nombre": det["cantidad"],
                        "total_devengado": det["tipo_valor_novedad"]["nombre"],
                        "total_deducido": det["valor"],
                        "neto": None,
                    })
                model.append({
                    "identificacion": None,
                    "nombre": None,
                    "total_devengado": "TOTAL DEVENGADO",
                    "total_deducido": item["total_devengado"],
                    "neto": None,
                })

                result = [f for f in item.get("detalle_liquidacion", []) if f.get("tipo_novedad", {}).get("id") in [1, 2]]
                for det in result:
                    model.append({
                        "identificacion": det["descripcion"],
                        "nombre": det["cantidad"],
                        "total_devengado": det["tipo_valor_novedad"]["nombre"],
                        "total_deducido": det["valor"],
                        "neto": None,
                    })
                model.append({
                    "identificacion": None,
                    "nombre": None,
                    "total_devengado": "TOTAL DEDUCIDO",
                    "total_deducido": item["total_deducido"],
                    "neto": None,
                })

        return Render.export_excel(model, nombre_archivo)

    @staticmethod
    def imprimir(request_data):
        """
        Genera el reporte PDF de pagos de empleados.
        """
        data = request_data
        empresa = EmpresaService.obtener_datos_empresa()

        params = {
            "empresa": empresa,
            "tab": data.get("tab"),
            "tipo": data.get("tipo"),
            "data": data.get("data")
        }

        return Render.render_pdfkit('pdf/nomina/pagos_empleados.html', params, "PAGO EMPLEADOS")
