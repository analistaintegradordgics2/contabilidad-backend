import os, pdb
import json
import errno
from datetime import datetime

from django.conf import settings
from django.db import transaction

from lxml import etree
from requests import Session
from zeep import Client
from zeep.transports import Transport

from apps.nomina.models.parametrizacion import NominaParametros
from apps.parametros.models.parametrizacion import Parametros, Mes, Anio
from apps.parametros.models.ubicacion import Ciudad
from apps.nomina.models.novedades import SubGrupoNomina
from apps.nomina.models.transmision import NominaElectronica, NominaElectronicaLiquidaciones, DetalleNominaElectronica, NominaElectronicaValores

class NominaElectronicaParametrizacionError(Exception):
    """Se lanza cuando falta parametrización requerida para poder transmitir."""

    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)


class NominaElectronicaTransmisionError(Exception):
    """Errores de negocio durante la transmisión (equivalentes a los status 400 originales)."""

    def __init__(self, msg):
        self.msg = msg
        super().__init__(msg)


class TransmitirNominaService:
    """
    Encapsula la transmisión de nómina electrónica al proveedor tecnológico FELIX.

    Uso típico desde la vista:

        service = TransmitirNominaService(user=request.user)
        resultado = service.transmitir(filtros=validated_data["filtros"],
                                        data_list=validated_data["data"])
    """

    # Códigos de grupo_nomina usados para consultar SubGrupoNomina (Felix)
    GRUPO_CESANTIAS = 13
    GRUPO_HUELGAS = 15
    GRUPO_INCAPACIDADES = 16
    GRUPO_LICENCIAS = 17
    GRUPO_PRIMAS = 18
    GRUPO_VACACIONES = 19

    WSDL_PRUEBAS = "https://www.pruebas.v2.ifelix.co/API-FELIX/NominaElectronicaWS?wsdl"
    WSDL_PRODUCCION = "https://www.ifelix.co/API-FELIX/NominaElectronicaWS?wsdl"

    def __init__(self, user):
        self.user = user
        self._cargar_parametros()

    # ------------------------------------------------------------------
    # Parametrización / setup
    # ------------------------------------------------------------------
    def _cargar_parametros(self):
        self.nomi_elect_produccion = self._valor_parametro(
            NominaParametros, "nomi_elect_produccion", default="false"
        )

        proveedor = NominaParametros.objects.filter(parametro="nomi_elect_proveedor").first()
        if proveedor is None or proveedor.valor is None:
            raise NominaElectronicaParametrizacionError("Proveedor tecnológico no parametrizado.")

        if proveedor.valor.lower() != "felix":
            # BPM (y cualquier otro proveedor) ya no está soportado por este service.
            raise NominaElectronicaParametrizacionError(
                "Proveedor tecnológico no soportado. Solo se encuentra habilitada la "
                "transmisión con FELIX."
            )
        self.nomi_elect_proveedor = proveedor.valor

        prefijo = NominaParametros.objects.filter(parametro="nomi_elect_prefijo").first()
        if prefijo is None or prefijo.valor is None:
            raise NominaElectronicaParametrizacionError(
                "Prefijo para nómina electrónica no parametrizado."
            )
        self.nomi_elect_prefijo = prefijo.valor

        self.nomi_elect_consecutivo = NominaParametros.objects.filter(
            parametro="nomi_elect_consecutivo"
        ).first()
        if self.nomi_elect_consecutivo is None or self.nomi_elect_consecutivo.valor is None:
            raise NominaElectronicaParametrizacionError(
                "Consecutivo para nómina electrónica no parametrizado."
            )

        username = NominaParametros.objects.filter(parametro="nomi_elect_usuario").first()
        password = NominaParametros.objects.filter(parametro="nomi_elect_password").first()
        if not username or username.valor is None or not password or password.valor is None:
            raise NominaElectronicaParametrizacionError(
                "Por favor revisar la parametrización de nómina electrónica (felix)."
            )
        self.username = username.valor
        self.password = password.valor

        self.nit_empresa = self._valor_parametro(Parametros, "nit_empresa")

        funcionalidad_nomina = Parametros.objects.filter(parametro="funcionalidad_nomina").first()
        self.funcionalidad_nomina = (
            funcionalidad_nomina.valor.lower() == "true" if funcionalidad_nomina else False
        )

        self.url = self.WSDL_PRUEBAS
        if self.nomi_elect_produccion.lower() == "true":
            self.url = self.WSDL_PRODUCCION

        self._asegurar_carpeta_media()

    @staticmethod
    def _valor_parametro(modelo, nombre, default=None):
        parametro = modelo.objects.filter(parametro=nombre).first()
        if parametro is None or parametro.valor is None:
            return default
        return parametro.valor

    @staticmethod
    def _asegurar_carpeta_media():
        try:
            os.mkdir("{}/nomina".format(settings.MEDIA_ROOT))
        except OSError as e:
            if e.errno != errno.EEXIST:
                pass

    # ------------------------------------------------------------------
    # Logging a disco (mismo comportamiento que el código original)
    # ------------------------------------------------------------------
    @staticmethod
    def _log_webservice(contenido):
        archivo = os.path.join(settings.MEDIA_ROOT, "nomina", "webservicenomina.txt")
        with open(archivo, "a", encoding="utf8") as f:
            f.write(contenido)

    @staticmethod
    def _log_data(contenido_dict):
        archivo = os.path.join(settings.MEDIA_ROOT, "nomina", "data.txt")
        with open(archivo, "a") as f:
            f.write(json.dumps(contenido_dict, ensure_ascii=False))
            f.write("\n")

    # ------------------------------------------------------------------
    # Entry point
    # ------------------------------------------------------------------
    def transmitir(self, filtros, data):
        """
        Punto de entrada del service.
        """
        try:
            return self._procesar_registro(data, filtros)
        except NominaElectronicaTransmisionError as exc:
            return {"status": 400, "msg": exc.msg}
        # except Exception as exc:
        #     return {
        #         "status": 400,
        #         "msg": "Se presentó un error en el proceso, por favor comuníquese con soporte.",
        #         "error": str(exc),
        #         "server_error": True,
        #     }

    # ------------------------------------------------------------------
    # Procesamiento de un registro
    # ------------------------------------------------------------------
    @transaction.atomic
    def _procesar_registro(self, data, filtros):
        procesar = data
        nomina_electronica_id = data["nomina_electronica_id"]

        if self.funcionalidad_nomina:
            procesar = self.build_data_funcionalidad(
                data, nomina_electronica_id, self.nomi_elect_proveedor.lower()
            )

        data["procesar"] = json.dumps(procesar)
        result = self.GuardarNominaElectronica(data, self.user.id, filtros, data)

        if result["status"] != 200:
            return result

        if self.funcionalidad_nomina:
            data = json.loads(data["procesar"])

        nomina_elect = result["data"]
        if nomina_elect.numero is None:
            nomina_elect.numero = f"{self.nomi_elect_prefijo}{self.nomi_elect_consecutivo.valor}"
            self.nomi_elect_consecutivo.valor = int(self.nomi_elect_consecutivo.valor) + 1
            self.nomi_elect_consecutivo.save()

        xml_body = self._construir_xml_body(data, nomina_elect)
        payload = self._construir_envelope(xml_body)

        self._log_webservice(
            "\n<<-------------{}------------>>{}\n".format(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                json.dumps(xml_body, indent=4, ensure_ascii=False),
            )
        )

        return self._enviar_y_procesar_respuesta(payload, nomina_elect)

    # ------------------------------------------------------------------
    # Envío SOAP + interpretación de respuesta
    # ------------------------------------------------------------------
    def _enviar_y_procesar_respuesta(self, payload, nomina_elect):
        session = Session()
        session.verify = False
        transport = Transport(session=session)

        client = Client(wsdl=self.url, transport=transport)
        service = client.wsdl.services["NominaElectronicaWS"]
        port = service.ports["NominaElectronicaWSPort"]
        endpoint = port.binding_options["address"]

        xml_element = etree.fromstring(payload.encode("utf-8"))
        response = client.transport.post_xml(endpoint, xml_element, headers={})
        jresp = self.parsear_respuesta_xml_felix(response.content, "enviarNominaElectronica")

        self._log_data(jresp)

        if response.status_code != 200:
            return {"status": 400, "msg": "No hubo conexión con el proveedor tecnológico."}

        if jresp["tipo"] != "exito":
            nomina_elect.respuesta = (
                " | ".join(jresp["listaMensajes"]) if len(jresp["listaMensajes"]) > 0 else ""
            )
            nomina_elect.estado_id = 3  # Rechazada
            nomina_elect.save()
            return {
                "status": 400,
                "msg": "Nomina no tramitada, se presentaron errores que hay que validar.",
            }

        nomina_elect.estado_id = 4  # Transmitida
        nomina_elect.respuesta = "Nomina Transmitida Correctamente."
        nomina_elect.save()
        return {"status": 200, "msg": "Nómina Transmitida Correctamente."}

    # ------------------------------------------------------------------
    # Construcción del XML (idéntica a la lógica original)
    # ------------------------------------------------------------------
    def _construir_envelope(self, xml_body):
        xml_header = (
            '<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/'
            'oasis-200401-wss-wssecurity-secext-1.0.xsd" '
            'xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/'
            'oasis-200401-wss-wssecurity-utility-1.0.xsd">'
            "<wsse:UsernameToken><wsse:Username>{}</wsse:Username>"
            '<wsse:Password soapenv:actor="http://schemas.xmlsoap.org/soap/actor/next" '
            'soapenv:mustUnderstand="0">{}</wsse:Password></wsse:UsernameToken>'
            "</wsse:Security>"
        ).format(self.username, self.password)

        xml_formato = (
            '<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" '
            'xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
            'xmlns:ws="http://ws.informatix.co/">'
            "<x:Header>{}</x:Header><x:Body>{}</x:Body></x:Envelope>"
        )
        return xml_formato.format(xml_header, xml_body)

    def _construir_xml_body(self, data, nomina_elect):
        empleado = data["Empleado"]
        devengados = data["Devengados"]
        deducciones = data["Deducciones"]

        fecha_ingreso = datetime.strptime(empleado["FechaIngreso"], "%Y-%m-%d")
        fecha_hora_emision = data["FechaHoraGeneracion"].split(" ")

        facturador = "<facturador><documento>{}</documento><username>{}</username></facturador>".format(
            self.username, self.username
        )

        if "ConfiguracionNomina" not in data:
            ciudad_empresa = Parametros.objects.filter(parametro="ciudad_empresa").first().valor
            periodo_nom = NominaParametros.objects.filter(parametro="forma_liquidacion").first().valor
            ubicacion = Ciudad.objects.get(pk=ciudad_empresa)

            if not periodo_nom and not self.funcionalidad_nomina:
                raise NominaElectronicaTransmisionError(
                    "Periodo Nomina no parametrizado. Por favor parametrizar."
                )

            data["ConfiguracionNomina"] = {
                "Municipio": ubicacion.coddane,
                "Pais": "CO",
                "PeriodoNomina": (5 if periodo_nom.lower() == "mensual" else 4) if periodo_nom else 5,
            }

        municipio = data["ConfiguracionNomina"]["Municipio"]
        configuracion_nomina = (
            "<configuracionNomina><abrevPais></abrevPais><departamento>{}</departamento>"
            "<municipio>{}</municipio><pais>{}</pais><periodoNomina>{}</periodoNomina>"
            "</configuracionNomina>"
        ).format(
            municipio[:2] if municipio not in ["", None] else "",
            municipio[2:] if municipio not in ["", None] else "",
            data["ConfiguracionNomina"]["Pais"],
            data["ConfiguracionNomina"]["PeriodoNomina"],
        )

        lista_deducciones = self.build_deducciones("", deducciones, data["TotalDevengados"])
        lista_otras_deducciones = self._construir_otras_deducciones(deducciones)
        lista_cesantias = self._construir_cesantias(devengados)
        lista_formas_pago = (
            "<listaFormasPagoNomina><fechaCreacion></fechaCreacion><fechaFinVigencia>"
            "</fechaFinVigencia><fechaPago>{}</fechaPago><id></id><idNomina></idNomina>"
            "<userName></userName></listaFormasPagoNomina>"
        ).format(data["FechaPago"])
        lista_hora_extra = self._construir_horas_extra(devengados)
        lista_huelga = self._construir_huelgas(devengados)
        lista_incapacidad_licencia = self._construir_incapacidades_licencias(devengados)
        lista_otros_devengados = self._construir_otros_devengados(devengados)
        lista_primas = self._construir_primas(devengados)
        lista_vacaciones = self._construir_vacaciones(devengados)
        trabajador = self._construir_trabajador(empleado, fecha_ingreso)

        auxilio_transporte = devengados.get("Transporte", {}).get("Auxilio", 0)
        viaticos_no_salarial = (
            devengados["Transporte"]["ViaticosNoSalarial"]
            if "Transporte" in devengados and devengados["Transporte"]["ViaticosNoSalarial"] > 0
            else ""
        )
        viaticos_salarial = (
            devengados["Transporte"]["ViaticosSalarial"]
            if "Transporte" in devengados and devengados["Transporte"]["ViaticosSalarial"] > 0
            else ""
        )

        return (
            "<ws:enviarNominaElectronica><arg0><codigoFormaPago>{}</codigoFormaPago>"
            "<codigoMedioPago>{}</codigoMedioPago><codigoMoneda>{}</codigoMoneda>"
            "<codigoTipoDocumentoContable>{}</codigoTipoDocumentoContable>{}"
            "<numeroNomina>{}</numeroNomina><prefijoDocumento></prefijoDocumento>"
            "<auxilioTransporte>{}</auxilioTransporte><codigoNominaNovedad></codigoNominaNovedad>"
            "<codigoNominaReferencia></codigoNominaReferencia><codigoTipoNomina>{}</codigoTipoNomina>"
            "<codigoTipoNota></codigoTipoNota><comprobanteTotal>{}</comprobanteTotal>{}"
            "<deduccionTotal>{}</deduccionTotal><devengadoTotal>{}</devengadoTotal>"
            "<diasTrabajados>{}</diasTrabajados><fechaEmision>{}</fechaEmision>"
            "<fechaFinLiquidacion>{}</fechaFinLiquidacion><fechaFinPeriodo></fechaFinPeriodo>"
            "<fechaInicioLiquidacion>{}</fechaInicioLiquidacion><fechaInicioPeriodo></fechaInicioPeriodo>"
            "<horaEmision>{}</horaEmision>{}{}{}{}{}{}{}{}{}{}<notas>{}</notas><novedad></novedad>"
            "<sueldoBase>{}</sueldoBase><sueldoTrabajado>{}</sueldoTrabajado>{}<trm></trm>"
            "<viaticosNoSalarial>{}</viaticosNoSalarial><viaticosSalarial>{}</viaticosSalarial>"
            "<prefijoDocumento>{}</prefijoDocumento></arg0></ws:enviarNominaElectronica>"
        ).format(
            "1",
            empleado["TipoMedioPago"],
            "COP",
            data["TipoDocumento"],
            facturador,
            nomina_elect.numero,
            auxilio_transporte,
            data.get("TipoNomina", "102"),
            data["TotalDocumento"],
            configuracion_nomina,
            data["TotalDeducciones"],
            data["TotalDevengados"],
            devengados["Basico"]["DiasTrabajados"],
            fecha_hora_emision[0],
            data["FechaLiquidacionFin"],
            data["FechaLiquidacionInicio"],
            fecha_hora_emision[1],
            lista_cesantias,
            lista_deducciones,
            lista_formas_pago,
            lista_hora_extra,
            lista_huelga,
            lista_incapacidad_licencia,
            lista_otras_deducciones,
            lista_otros_devengados,
            lista_primas,
            lista_vacaciones,
            data["Notas"],
            empleado["Sueldo"],
            devengados["Basico"]["Salario"],
            trabajador,
            viaticos_no_salarial,
            viaticos_salarial,
            self.nomi_elect_prefijo,
        )

    # -- Bloques XML individuales -------------------------------------
    @staticmethod
    def build_deducciones(xml, deducciones, total_devengados):
        for key, value in deducciones.items():
            if len(value) > 0 and key != "OtrasDeducciones":
                if not isinstance(value, list):
                    xml += (
                        "<listaDeducciones><codigo>{}</codigo><nombre></nombre>"
                        "<nombreTabla></nombreTabla><porcentaje>{}</porcentaje>"
                        "<deduccion>{}</deduccion><id>{}</id><valorBase>{}</valorBase>"
                        "</listaDeducciones>"
                    ).format(
                        value["Codigo"],
                        value.get("Porcentaje", ""),
                        value["Valor"],
                        "",
                        value.get("ValorBase", total_devengados),
                    )
                else:
                    for item in value:
                        xml += TransmitirNominaService.build_deducciones(
                            "", {key: item}, total_devengados
                        )
        return xml

    @staticmethod
    def _construir_otras_deducciones(deducciones):
        lista_otras_deducciones = ""
        if "OtrasDeducciones" not in deducciones:
            return lista_otras_deducciones

        agrupados = {}
        for item in deducciones["OtrasDeducciones"]:
            tipo = item["TipoDeduccion"]
            if tipo not in agrupados:
                agrupados[tipo] = {
                    "Descripcion": item["Descripcion"],
                    "TipoDeduccion": tipo,
                    "Valor": 0,
                    "Porcentaje": item.get("Porcentaje", 0),
                }
            agrupados[tipo]["Valor"] += item["Valor"]

        for item in agrupados.values():
            porcentaje = (
                f"<porcentaje>{item['Porcentaje']}</porcentaje>"
                if item.get("Porcentaje", 0) > 0
                else ""
            )
            lista_otras_deducciones += (
                "<listaOtrasDeducciones><codigo>{}</codigo><nombre></nombre>"
                "<nombreTabla></nombreTabla>{}<descripcion>{}</descripcion><id>{}</id>"
                "<pago>{}</pago></listaOtrasDeducciones>"
            ).format(
                item["TipoDeduccion"],
                porcentaje,
                item.get("Descripcion", "") or "",
                "",
                item["Valor"],
            )
        return lista_otras_deducciones

    @staticmethod
    def _construir_cesantias(devengados):
        if "Cesantias" not in devengados or len(devengados["Cesantias"]) == 0:
            return ""
        sub_grupo = SubGrupoNomina.objects.filter(
            grupo_nomina_id=TransmitirNominaService.GRUPO_CESANTIAS
        ).first()
        return (
            "<listaCesantias><codigo>{}</codigo><nombre></nombre><nombreTabla></nombreTabla>"
            "<porcentaje>{}</porcentaje><id>{}</id><pago>{}</pago>"
            "<pagoIntereses>{}</pagoIntereses></listaCesantias>"
        ).format(
            str(sub_grupo.codigo),
            devengados["Cesantias"]["Porcentaje"],
            "",
            devengados["Cesantias"]["Valor"],
            devengados["Cesantias"]["ValorInteres"],
        )

    @staticmethod
    def _construir_horas_extra(devengados):
        lista = ""
        for item in devengados.get("HorasExtra", []):
            lista += (
                "<listaHoraExtra><codigo>{}</codigo><nombre></nombre><nombreTabla></nombreTabla>"
                "<porcentaje></porcentaje><cantidad>{}</cantidad><codigoRecargo>{}</codigoRecargo>"
                "<horaFin>{}</horaFin><horaInicio>{}</horaInicio><id>{}</id><pago>{}</pago>"
                "</listaHoraExtra>"
            ).format(
                item["TipoHoraExtra"],
                item["Cantidad"],
                item["TipoHoraExtra"],
                item["FechaHoraFin"],
                item["FechaHoraInicio"],
                "",
                item["Valor"],
            )
        return lista

    @staticmethod
    def _construir_huelgas(devengados):
        lista = ""
        if "HuelgasLegales" not in devengados:
            return lista
        sub_grupo = SubGrupoNomina.objects.filter(
            grupo_nomina_id=TransmitirNominaService.GRUPO_HUELGAS
        ).first()
        for item in devengados["HuelgasLegales"]:
            lista += (
                "<listaHuelga><codigo>{}</codigo><nombre></nombre><nombreTabla></nombreTabla>"
                "<porcentaje></porcentaje><cantidad>{}</cantidad><fechaFin>{}</fechaFin>"
                "<fechaInicio>{}</fechaInicio><id>{}</id></listaHuelga>"
            ).format(str(sub_grupo.codigo), item["Cantidad"], item["FechaFin"], item["FechaInicio"], "")
        return lista

    @staticmethod
    def _construir_incapacidades_licencias(devengados):
        lista = ""
        if "Incapacidades" in devengados:
            sub_grupo = SubGrupoNomina.objects.filter(
                grupo_nomina_id=TransmitirNominaService.GRUPO_INCAPACIDADES
            ).first()
            for item in devengados["Incapacidades"]:
                lista += (
                    "<listaIncapacidadLicencia><codigo>{}</codigo><nombre></nombre>"
                    "<nombreTabla></nombreTabla><porcentaje></porcentaje><cantidad>{}</cantidad>"
                    "<codigoTipoLicencia>{}</codigoTipoLicencia><fechaFin>{}</fechaFin>"
                    "<fechaInicio>{}</fechaInicio><id>{}</id><incapacidad>{}</incapacidad>"
                    "<pago>{}</pago></listaIncapacidadLicencia>"
                ).format(
                    str(sub_grupo.codigo),
                    item["Cantidad"],
                    item["TipoIncapacidad"],
                    item["FechaFin"],
                    item["FechaInicio"],
                    "",
                    True,
                    item["Valor"],
                )

        if "Licencias" in devengados:
            sub_grupo = SubGrupoNomina.objects.filter(
                grupo_nomina_id=TransmitirNominaService.GRUPO_LICENCIAS
            ).first()
            for item in devengados["Licencias"]:
                lista += (
                    "<listaIncapacidadLicencia><codigo>{}</codigo><nombre></nombre>"
                    "<nombreTabla></nombreTabla><porcentaje></porcentaje><cantidad>{}</cantidad>"
                    "<codigoTipoLicencia>{}</codigoTipoLicencia><fechaFin>{}</fechaFin>"
                    "<fechaInicio>{}</fechaInicio><id>{}</id><incapacidad></incapacidad>"
                    "<pago>{}</pago></listaIncapacidadLicencia>"
                ).format(
                    str(sub_grupo.codigo),
                    item["Cantidad"],
                    item["TipoLicencia"],
                    item["FechaFin"],
                    item["FechaInicio"],
                    "",
                    item["Valor"],
                )
        return lista

    @staticmethod
    def _construir_otros_devengados(devengados):
        lista = ""
        for item in devengados.get("OtrosDevengados", []):
            valor_salarial = f"<pago>{item['Valor']}</pago>" if item["Valor"] > 0 else ""
            valor_no_salarial = (
                f"<pagoNoSalarial>{item['ValorNoSalarial']}</pagoNoSalarial>"
                if item["ValorNoSalarial"] > 0
                else ""
            )
            lista += (
                "<listaOtrosDevengados><codigo>{}</codigo><nombre></nombre><nombreTabla></nombreTabla>"
                "<porcentaje></porcentaje><descripcion>{}</descripcion><id>{}</id>{}{}"
                "</listaOtrosDevengados>"
            ).format(
                item["TipoDevengado"],
                item.get("Descripcion", "") or "",
                "",
                valor_salarial,
                valor_no_salarial,
            )
        return lista

    @staticmethod
    def _construir_primas(devengados):
        if "Prima" not in devengados or len(devengados["Prima"]) == 0:
            return ""
        sub_grupo = SubGrupoNomina.objects.filter(
            grupo_nomina_id=TransmitirNominaService.GRUPO_PRIMAS
        ).first()
        valor_salarial = (
            f"<pago>{devengados['Prima']['ValorSalarial']}</pago>"
            if devengados["Prima"]["ValorSalarial"] > 0
            else ""
        )
        valor_no_salarial = (
            f"<pagoNoSalarial>{devengados['Prima']['ValorNoSalarial']}</pagoNoSalarial>"
            if devengados["Prima"]["ValorNoSalarial"] > 0
            else ""
        )
        return (
            "<listaPrimas><codigo>{}</codigo><nombre></nombre><nombreTabla></nombreTabla>"
            "<porcentaje></porcentaje><cantidad>{}</cantidad><id>{}</id>{}{}</listaPrimas>"
        ).format(str(sub_grupo.codigo), devengados["Prima"]["Cantidad"], "", valor_salarial, valor_no_salarial)

    @staticmethod
    def _construir_vacaciones(devengados):
        lista = ""
        if "Vacaciones" in devengados:
            sub_grupo = SubGrupoNomina.objects.filter(
                grupo_nomina_id=TransmitirNominaService.GRUPO_VACACIONES
            ).first()
            for item in devengados["Vacaciones"]:
                lista += (
                    "<listaVacaciones><codigo>{}</codigo><nombre></nombre><nombreTabla></nombreTabla>"
                    "<porcentaje></porcentaje><cantidad>{}</cantidad>"
                    "<codigoTipoVacaciones>{}</codigoTipoVacaciones><fechaFin>{}</fechaFin>"
                    "<fechaInicio>{}</fechaInicio><id>{}</id><pago>{}</pago></listaVacaciones>"
                ).format(
                    str(sub_grupo.codigo),
                    item["Cantidad"],
                    item["TipoVacacion"],
                    f"{item['FechaFin']}",
                    f"{item['FechaInicio']}",
                    "",
                    item["Valor"],
                )

        if "VacacionesCompensadas" in devengados:
            sub_grupo = SubGrupoNomina.objects.filter(
                grupo_nomina_id=TransmitirNominaService.GRUPO_VACACIONES
            ).first()
            for item in devengados["VacacionesCompensadas"]:
                lista += (
                    "<listaVacaciones><codigo>{}</codigo><nombre></nombre><nombreTabla></nombreTabla>"
                    "<porcentaje></porcentaje><cantidad>{}</cantidad>"
                    "<codigoTipoVacaciones>{}</codigoTipoVacaciones><fechaFin>{}</fechaFin>"
                    "<fechaInicio>{}</fechaInicio><id>{}</id><pago>{}</pago></listaVacaciones>"
                ).format(
                    str(sub_grupo.codigo),
                    item["Cantidad"],
                    item["TipoVacacion"],
                    f"{item['FechaFin']}",
                    f"{item['FechaInicio']}",
                    "",
                    item["Valor"],
                )
        return lista

    @staticmethod
    def _construir_trabajador(empleado, fecha_ingreso):
        ciudad = empleado.get("Ciudad")
        return (
            "<trabajador><abrevPais></abrevPais><altoRiesgoPension>{}</altoRiesgoPension>"
            "<codigoTipoDocumento>{}</codigoTipoDocumento><codigoTrabajador>{}</codigoTrabajador>"
            "<departamento>{}</departamento><direccion>{}</direccion><entidadBancaria>{}</entidadBancaria>"
            "<fechaFinContratoAnterior></fechaFinContratoAnterior><fechaIngreso>{}</fechaIngreso>"
            "<fechaInicioContrato>{}</fechaInicioContrato><fechaRetiro>{}</fechaRetiro><id>{}</id>"
            "<municipio>{}</municipio><numeroCuenta>{}</numeroCuenta><numeroDocumento>{}</numeroDocumento>"
            "<otrosNombres>{}</otrosNombres><pais>{}</pais><primerApellido>{}</primerApellido>"
            "<primerNombre>{}</primerNombre><salarioIntegral>{}</salarioIntegral>"
            "<segundoApellido>{}</segundoApellido><subtipoTrabajador>{}</subtipoTrabajador>"
            "<sueldo>{}</sueldo><sueldoAnterior></sueldoAnterior><tiempoLaborado>{}</tiempoLaborado>"
            "<tipoContrato>{}</tipoContrato><tipoCuenta>{}</tipoCuenta><tipoTrabajador>{}</tipoTrabajador>"
            "</trabajador>"
        ).format(
            empleado["ActividadAltoRiesgo"],
            empleado["TipoIdentificacion"],
            empleado["Codigo"],
            ciudad[:2] if ciudad not in ["", None] else "",
            empleado["Direccion"] if empleado["Direccion"] not in ["", None] else "",
            empleado["NombreBanco"],
            empleado["FechaIngreso"],
            empleado["FechaIngreso"],
            empleado["FechaRetiro"],
            "",
            ciudad[2:] if ciudad not in ["", None] else "",
            empleado["NumeroCuentaBancaria"],
            empleado["Identificacion"],
            empleado["SegundoNombre"],
            empleado.get("Pais", "CO"),
            empleado["PrimerApellido"],
            empleado["PrimerNombre"],
            empleado["SalarioIntegral"],
            empleado["SegundoApellido"],
            empleado["SubTipoTrabajador"],
            empleado["Sueldo"],
            empleado.get("TiempoLaborado", (datetime.now() - fecha_ingreso).days),
            empleado["TipoContrato"],
            empleado["TipoCuentaBancaria"],
            empleado["TipoTrabajador"],
        )

    # ------------------------------------------------------------------
    # Parseo de la respuesta SOAP
    # ------------------------------------------------------------------
    @staticmethod
    def parsear_respuesta_xml_felix(xml_bytes, funcion):
        try:
            root = etree.fromstring(xml_bytes)
            ns = {
                "soap": "http://schemas.xmlsoap.org/soap/envelope/",
                "ns2": "http://ws.informatix.co/",
            }

            fault = root.xpath("//soap:Fault", namespaces=ns)
            if fault:
                return {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tipo": "soap_fault",
                    "enviado": False,
                    "numero": None,
                    "mensaje": None,
                    "listaMensajes": [],
                    "codigo": (
                        root.xpath("//soap:Fault/faultcode/text()", namespaces=ns)[0]
                        if root.xpath("//soap:Fault/faultcode/text()", namespaces=ns)
                        else None
                    ),
                    "error": (
                        root.xpath("//soap:Fault/faultstring/text()", namespaces=ns)[0]
                        if root.xpath("//soap:Fault/faultstring/text()", namespaces=ns)
                        else None
                    ),
                }

            lista_mensajes = root.xpath(
                f"//ns2:{funcion}Response/return/listaMensajes/text()", namespaces=ns
            )
            enviado = root.xpath(f"//ns2:{funcion}Response/return/enviado/text()", namespaces=ns)

            if len(lista_mensajes) > 0 and enviado[0].lower() == "false":
                return {
                    "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "tipo": "error_validacion",
                    "enviado": enviado[0],
                    "numero": None,
                    "mensaje": None,
                    "listaMensajes": lista_mensajes,
                    "codigo": None,
                    "error": None,
                }

            mensaje = root.xpath(f"//ns2:{funcion}Response/return/mensaje/text()", namespaces=ns)
            numero = root.xpath(f"//ns2:{funcion}Response/return/numeroDocumento/text()", namespaces=ns)
            return {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tipo": "exito",
                "enviado": enviado[0],
                "numero": numero[0] if numero else None,
                "mensaje": mensaje[0] if mensaje else None,
                "listaMensajes": [],
                "codigo": None,
                "error": None,
            }
        except Exception as e:
            return {
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "tipo": "error_exception",
                "enviado": False,
                "numero": None,
                "mensaje": None,
                "listaMensajes": [],
                "codigo": None,
                "error": str(e),
            }

    def GuardarNominaElectronica(self, data, user_id, filtros, temp_data=None):
        nomina_electronica_id = None
        contrato_id = None
        arl = 0
        novedades = []
        liquidaciones = []
        nomi_elect_prefijo = self.nomi_elect_prefijo

        try:
            nomina_electronica_id = temp_data["nomina_electronica_id"]
            contrato_id = temp_data["id"]
            arl = temp_data.get("Arl", 0)
            novedades = temp_data.get("Novedades", [])
            liquidaciones = temp_data.get("liquidaciones", [])
        except (KeyError, TypeError):
            nomina_electronica_id = data["nomina_electronica_id"]
            contrato_id = data["id"]
            arl = 0
            novedades = []
            liquidaciones = []

            data = json.loads(data["procesar"])
            filtros["mes"] = (
                filtros["mes_numero"]
                if "mes_numero" in filtros
                else filtros["mes"]
            )

        try:
            # ==========================================================
            # CREAR / ACTUALIZAR NOMINA ELECTRONICA
            # ==========================================================

            if nomina_electronica_id is None:
                nomina_elect = NominaElectronica()
            else:
                nomina_elect = NominaElectronica.objects.get(
                    pk=nomina_electronica_id
                )

                # Eliminar información anterior
                DetalleNominaElectronica.objects.filter(
                    nomina_electronica_id=nomina_electronica_id
                ).delete()

                NominaElectronicaLiquidaciones.objects.filter(
                    nomina_electronica_id=nomina_electronica_id
                ).delete()

                NominaElectronicaValores.objects.filter(
                    nomina_electronica_id=nomina_electronica_id
                ).delete()

            # ==========================================================
            # DATOS GENERALES
            # ==========================================================

            mes = Mes.objects.filter(
                numero=filtros["mes"]
            ).first()

            anio = Anio.objects.filter(
                nombre=filtros["anio"]
            ).first()

            nomina_elect.contrato_id = contrato_id
            nomina_elect.fecha_ini_liquidacion = data["FechaLiquidacionInicio"]
            nomina_elect.fecha_fin_liquidacion = data["FechaLiquidacionFin"]
            nomina_elect.mes = mes
            nomina_elect.anio = anio
            nomina_elect.dias_laborados = data["Devengados"]["Basico"]["DiasTrabajados"]
            nomina_elect.tipo_nomina = data["TipoDocumento"]
            nomina_elect.prefijo = nomi_elect_prefijo

            # Si estos campos ya existen en tu lógica de numeración,
            # puedes asignarlos aquí.
            # nomina_elect.numero = ...

            nomina_elect.uc_id = user_id

            nomina_elect.save()

            # ==========================================================
            # VALORES NOMINA ELECTRONICA
            # ==========================================================

            valores = NominaElectronicaValores(
                nomina_electronica=nomina_elect,

                sueldo=data["Empleado"]["Sueldo"],

                sueldo_trabajado=0,
                auxilio_transporte=0,
                viaticos_salarriales=0,
                viaticos_nosalariales=0,
                otros_devengados=0,

                total_devengados=data["TotalDevengados"],

                salud=0,
                pension=0,
                fondo=0,
                arl=arl,
                otros_deducidos=0,

                total_deducido=data["TotalDeducciones"],
                total=data["TotalDocumento"],
            )

            # ==========================================================
            # DEVENGADOS / DEDUCCIONES
            # ==========================================================

            try:
                valores.sueldo_trabajado = (
                    data["Devengados"]["Basico"]["Salario"]
                )

                valores.auxilio_transporte = (
                    data["Devengados"]["Transporte"]["Auxilio"]
                )

                valores.viaticos_salarriales = (
                    data["Devengados"]["Transporte"]["ViaticosSalarial"]
                )

                valores.viaticos_nosalariales = (
                    data["Devengados"]["Transporte"]["ViaticosNoSalarial"]
                )

                valores.salud = (
                    data["Deducciones"]["Salud"]["Valor"]
                )

                valores.pension = (
                    data["Deducciones"]["FondoPension"]["Valor"]
                )

                valores.fondo = (
                    data["Deducciones"]["FondoSeguridad"]["Valor"]
                )

                valores.otros_devengados = sum(
                    item["Valor"]
                    for item in data["Devengados"]["OtrosDevengados"]
                )

                valores.otros_deducidos = sum(
                    item["Valor"]
                    for item in data["Deducciones"]["OtrasDeducciones"]
                )

            except (KeyError, TypeError, ValueError):
                pass

            valores.save()

            # ==========================================================
            # NOVEDADES
            # ==========================================================

            for item in novedades:
                detalle = DetalleNominaElectronica()

                detalle.nomina_electronica_id = nomina_elect.id
                detalle.cantidad = item["Cantidad"]
                detalle.valor = item["Valor"]
                detalle.novedad_id = item["Novedad"]
                detalle.descripcion = item["Descripcion"]
                detalle.patrono = item["Patrono"]

                try:
                    detalle.provisional = item["Provisional"]
                    detalle.fecha_ini = item["FechaInicio"]
                    detalle.fecha_fin = item["FechaFin"]
                except KeyError:
                    pass

                detalle.save()

            # ==========================================================
            # LIQUIDACIONES
            # ==========================================================

            for item in liquidaciones:
                n_elect_liqui = NominaElectronicaLiquidaciones()

                n_elect_liqui.nomina_electronica_id = nomina_elect.id
                n_elect_liqui.liquidacion_id = item

                n_elect_liqui.save()

            # ==========================================================
            # RESPUESTA
            # ==========================================================

            return {
                "status": 200,
                "data": nomina_elect,
                "msg": "Ok",
                "error": "",
            }

        except Exception as inst:
            return {
                "status": 400,
                "data": None,
                "msg": (
                    "Se presentó un error en el proceso, "
                    "por favor comuníquese con soporte."
                ),
                "error": str(inst),
            }
    
    # ------------------------------------------------------------------
    # Construcción del modelo intermedio a partir del contrato/liquidación
    # ------------------------------------------------------------------
    def build_data_funcionalidad(self, data, nomi_elec_id, proveedor="felix"):
        nomi_elec = NominaElectronica.objects.get(pk=nomi_elec_id)
 
        # NOTA: con BPM eliminado, `proveedor` siempre llega como "felix" desde
        # este service (ver self.nomi_elect_proveedor en _cargar_parametros),
        # por lo que TipoDocumento siempre será 11. Se deja el condicional por
        # si en el futuro se reactiva otro proveedor con codificación distinta.
        model = {
            "TipoDocumento": 1 if proveedor == "bpm" else 11,
            "TipoPeriodo": "5",  # Periodo mensual (Codigo DIAN)
            "FechaHoraGeneracion": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "FechaLiquidacionInicio": (
                nomi_elec.fecha_ini_liquidacion.strftime("%Y-%m-%d")
                if nomi_elec.fecha_ini_liquidacion is not None
                else ""
            ),
            "FechaLiquidacionFin": (
                nomi_elec.fecha_fin_liquidacion.strftime("%Y-%m-%d")
                if nomi_elec.fecha_fin_liquidacion is not None
                else ""
            ),
            "FechaPago": (
                nomi_elec.fecha_fin_liquidacion.strftime("%Y-%m-%d")
                if nomi_elec.fecha_fin_liquidacion is not None
                else ""
            ),
            "Notas": "",
            "TotalDevengados": int(float(nomi_elec.total_devengados)),
            "TotalDeducciones": int(float(nomi_elec.total_deducido)),
            "TotalDocumento": int(float(nomi_elec.total)),
            "Empleado": {
                "Codigo": "C{}".format(data["id"]),
                "TipoIdentificacion": data["persona"]["tipo_documento"],
                "Identificacion": data["persona"]["documento"],
                "PrimerNombre": data["persona"]["p_nombre"] or "",
                "SegundoNombre": data["persona"]["s_nombre"] or "",
                "PrimerApellido": data["persona"]["p_apellido"] or "",
                "SegundoApellido": data["persona"]["s_apellido"] or "",
                "TipoTrabajador": data["foraneas"]["tipo_trabajador"] or "",
                "SubTipoTrabajador": data["foraneas"]["subtipo_trabajador"] or "",
                "Ciudad": data["persona"]["ciudad"] or "",
                "TipoContrato": data["foraneas"]["tipo_contrato"] or "",
                "CorreoElectronico": data["persona"]["email"] or "",
                "Direccion": data["persona"]["direccion"] or "",
                "ActividadAltoRiesgo": data["alto_riesgo_pension"],
                "SalarioIntegral": data["salario_integral"],
                "Sueldo": int(float(data["sueldo"])),
                "FechaIngreso": data["fecha_ingreso"] or "",
                "FechaRetiro": data["fecha_retiro"] or "",
                "Area": data["foraneas"]["cargo"] or "",
                "Cargo": data["foraneas"]["cargo"] or "",
                "TipoMedioPago": data["foraneas"]["datos_pago"]["medio_pago"] or "",
                "TipoCuentaBancaria": (
                    str(data["foraneas"]["datos_pago"]["tipo_cuenta"])
                    if data["foraneas"]["datos_pago"]["tipo_cuenta"] is not None
                    else ""
                ),
                "NombreBanco": data["foraneas"]["datos_pago"]["banco"] or "",
                "NumeroCuentaBancaria": data["foraneas"]["datos_pago"]["numero_cuenta"] or "",
                "CodigoSucursal": data["foraneas"]["codigo_sucursal"] or "",
            },
            "Devengados": {},
            "Deducciones": {},
        }
 
        model["Devengados"] = self._mapear_seccion(data["devengados"])
        model["Deducciones"] = self._mapear_seccion(data["deducidos"])
        return model
 
    @staticmethod
    def _normalizar_campo(field):
        """Aplica la misma coerción de tipos que el código original a un
        campo dinámico proveniente del formulario (number/money/datetime-local)."""
        if field["value"] is not None:
            if field["type"] in ("number", "money"):
                field["value"] = int(field["value"])
            elif field["type"] == "datetime-local":
                field["value"] = "{}:00".format(field["value"].replace("T", " "))
        else:
            if field["type"] in ("number", "money"):
                field["value"] = 0
            else:
                field["value"] = ""
        return field["value"]
 
    @classmethod
    def _mapear_seccion(cls, items):
        """Reemplaza el bloque duplicado que originalmente se repetía para
        `devengados` y `deducidos` (y para `Devengados`/`Deducciones`)."""
        resultado = {}
        for entrada in items:
            key = entrada["select"]["key"]
            if entrada["select"]["type"] == "object":
                resultado[key] = {}
                for field in entrada["select"]["fields"]:
                    valor = cls._normalizar_campo(field)
                    resultado[key][field["key"]] = valor
            else:
                resultado[key] = []
                for item in entrada["select"]["data"]:
                    model_tmp = {}
                    for field in item:
                        valor = cls._normalizar_campo(field)
                        model_tmp[field["key"]] = valor
                    resultado[key].append(model_tmp)
        return resultado