import datetime
import json

from requests import Session
from zeep import Client
from zeep.transports import Transport
from lxml import etree

from apps.contabilidad.models.documento import Documentos, FactElectronicaDocumento, DetalleFacturas
from apps.parametros.models.parametrizacion import Parametros

from apps.utils.funciones import Funciones


class FacturacionElectronicaError(Exception):
    """Excepción de negocio para errores controlados durante la transmisión electrónica (Felix)."""

    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class _FacturaTransmisionContext:
    """
    Contenedor del estado mutable que se va construyendo mientras se arma
    el payload de una factura individual. Evita pasar 10 variables sueltas
    entre los métodos privados del service.
    """

    def __init__(self, obj_factura):
        self.obj_factura = obj_factura
        self.persona = obj_factura.personas
        self.documento_referenciado = Documentos.objects.filter(numero=obj_factura.referencia).first()

        self.tipo_documento_trans = 2
        self.tipo_operacion = None
        self.codigo_tipo_documento = self.persona.tipo_documento.codigo
        self.campos_soporte = ''
        self.campos_nota = ''
        self.nota = ''
        self.funcion = 'enviarFacturaElectronica'
        self.xml_service = 'FacturaElectronicaWS'
        self.xml_port = 'FacturaElectronicaWSPort'
        self.xml_formato = (
            '<x:Envelope xmlns:x="http://schemas.xmlsoap.org/soap/envelope/" '
            'xmlns:ws="http://ws.informatix.co/">'
            '<x:Header>{}</x:Header><x:Body>{}</x:Body></x:Envelope>'
        )
        self.url = None


class FacturacionTransmisionService:
    """
    Encapsula la transmisión de facturas electrónicas al proveedor tecnológico Felix (Informatix).
    """

    def __init__(self, usuario):
        self.usuario = usuario
        self._cargar_parametros()

    # ------------------------------------------------------------------ #
    # Carga y validación de parámetros
    # ------------------------------------------------------------------ #

    def _cargar_parametros(self):
        self.tipo_fac_arr_id = self._valor_parametro('tipo_fac_arr_id')
        self.nota_credito_id = self._valor_parametro('nota_credito_id')
        self.nota_debito_id = self._valor_parametro('nota_debito_id')
        self.nota_ajuste_id = self._valor_parametro('nota_ajuste_id')
        self.doc_soporte_id = self._valor_parametro('doc_soporte_id')
        self.regimen_simple = self._valor_parametro('regimen_simple')
        self.responsable_iva = self._valor_parametro('responsable_iva')

        fact_elec_produccion = Parametros.objects.filter(parametro='fact_elec_produccion').first()
        self.fact_elec_produccion = (
            fact_elec_produccion.valor
            if fact_elec_produccion is not None and fact_elec_produccion.valor is not None
            else "false"
        )

        username_param = Parametros.objects.filter(parametro='username_facturador').first()
        password_param = Parametros.objects.filter(parametro='password_facturador').first()

        if username_param is None or password_param is None:
            raise FacturacionElectronicaError(
                "Por favor revisar la parametrización de facturación electrónica (felix)"
            )

        self.username = username_param.valor
        self.password = password_param.valor

    @staticmethod
    def _valor_parametro(nombre):
        parametro = Parametros.objects.filter(parametro=nombre).first()
        return parametro.valor if parametro else None

    # ------------------------------------------------------------------ #
    # Acceso a contabilidad_factelectronicadocumento
    # (cont_estadofact_id y numero_generado ya no viven en Documentos)
    # ------------------------------------------------------------------ #

    @staticmethod
    def _obtener_fact_electronica(documento_id):
        """
        Devuelve la fila vigente de contabilidad_factelectronicadocumento para el documento,
        o None si el documento aún no ha entrado al proceso de facturación electrónica.
        """
        return (
            FactElectronicaDocumento.objects
            .filter(documento_id=documento_id)
            .order_by('-id')
            .first()
        )

    @staticmethod
    def _obtener_estado_fact_actual(documento_id):
        cfe = FacturacionTransmisionService._obtener_fact_electronica(documento_id)
        return cfe.estado_id if cfe is not None else 1  # 1 = Sin transmitir (default, ver nota más abajo)

    @staticmethod
    def _actualizar_estado_fact_electronica(documento_id, estado_id, numero_generado=None):
        """
        Crea o actualiza la fila de contabilidad_factelectronicadocumento para el documento,
        registrando el nuevo estado (y el numero_generado si se transmitió con éxito).
        """
        cfe = FacturacionTransmisionService._obtener_fact_electronica(documento_id)
        ahora = datetime.datetime.now()

        if cfe is not None:
            cfe.estado_id = estado_id
            cfe.modified = ahora
            if numero_generado is not None:
                cfe.numero_generado = numero_generado
            cfe.save()
        else:
            FactElectronicaDocumento.objects.create(
                documento_id=documento_id,
                estado_id=estado_id,
                numero_generado=numero_generado,
                created=ahora,
                modified=ahora,
            )

    # ------------------------------------------------------------------ #
    # Orquestación pública
    # ------------------------------------------------------------------ #

    def transmitir_facturas(self, facturas_ids):
        """
        Transmite cada factura en orden. Se detiene en la primera que falle,
        igual que el comportamiento original (lanza FacturacionElectronicaError).
        """
        for factura_id in facturas_ids:
            self.transmitir_factura(factura_id)

        return {"status": 200, "msg": "ok"}

    def transmitir_factura(self, factura_id):
        obj_factura = Documentos.objects.get(pk=factura_id)

        if self._obtener_estado_fact_actual(obj_factura.id) == 4:
            # Ya fue transmitida correctamente, no se reenvía.
            return

        ctx = _FacturaTransmisionContext(obj_factura)

        datos_existentes = json.loads(obj_factura.webservice) if obj_factura.webservice else []
        datos_webservice = []

        self._resolver_tipo_documento_y_endpoint(ctx)

        cliente_xml = self._construir_cliente_xml(ctx)
        producto_servicio_xml = self._construir_producto_servicio_xml(ctx)
        payload = self._construir_payload(ctx, cliente_xml, producto_servicio_xml)

        datos_webservice.append(self._log_request(ctx, payload))

        response = self._enviar_soap(ctx, payload)

        if response.status_code != 200:
            raise FacturacionElectronicaError("No hubo conexión con el proveedor tecnológico.")

        jresp = self.parsear_respuesta_xml_felix(response.content, ctx.funcion, obj_factura.numero)

        self._procesar_respuesta(ctx, jresp, response, datos_webservice, datos_existentes)

    # ------------------------------------------------------------------ #
    # Resolución de tipo de documento / endpoint / función SOAP
    # ------------------------------------------------------------------ #

    def _resolver_tipo_documento_y_endpoint(self, ctx):
        obj_factura = ctx.obj_factura
        documento = ctx.documento_referenciado
        tipo_doc_referenciado = (
            documento.tipo_documentos.tipo_documento_nota_credito_id if documento is not None else None
        )

        es_documento_soporte_o_ajuste = (
            obj_factura.tipo_documentos.es_nota is True and tipo_doc_referenciado == int(self.nota_ajuste_id)
        ) or (
            obj_factura.tipo_documentos_id == int(self.doc_soporte_id) and not obj_factura.tipo_documentos.es_nota
        )

        if es_documento_soporte_o_ajuste:
            ctx.funcion = "enviarDocumentoSoporte"
            ctx.xml_formato = (
                '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
                'xmlns:ws="http://ws.informatix.co/">'
                '<soapenv:Header>{}</soapenv:Header><soapenv:Body>{}</soapenv:Body></soapenv:Envelope>'
            )
            ctx.url = "https://www.pruebas.v2.ifelix.co/API-FELIX/DocumentoSoporteWS?wsdl"
            if self.fact_elec_produccion.lower() == "true":
                ctx.url = "https://www.ifelix.co/API-FELIX/DocumentoSoporteWS?wsdl"

            ctx.xml_service = 'DocumentoSoporteWS'
            ctx.xml_port = 'DocumentoSoporteWSPort'

            ctx.campos_soporte = '<numeroDocumento>{}</numeroDocumento><codigoTipoEnvio>{}</codigoTipoEnvio>'.format(
                obj_factura.numero, 1
            )

            if len(ctx.persona.documento.split('-')) == 1:
                documento_dv = Funciones.calcular_digito_verificacion(ctx.persona.documento)
                ctx.persona.documento += '-' + str(documento_dv)

            ctx.codigo_tipo_documento = 31  # NIT

            if not obj_factura.tipo_documentos.es_nota:
                ctx.tipo_documento_trans = 12  # Documento soporte
            else:
                ctx.tipo_documento_trans = 13  # Nota de ajuste
                ctx.campos_nota = "<codigoConcepto>{}</codigoConcepto><numeroReferenciaFactura>{}</numeroReferenciaFactura>".format(
                    2, obj_factura.referencia
                )

        elif obj_factura.tipo_documentos.es_nota is True:
            ctx.funcion = 'enviarNota'
            ctx.url = "https://www.pruebas.v2.ifelix.co/API-FELIX/FacturaElectronicaWS?wsdl"
            if self.fact_elec_produccion.lower() == "true":
                ctx.url = "https://www.ifelix.co/API-FELIX/FacturaElectronicaWS?wsdl"

            tipo_doc_credito = documento.tipo_documentos.tipo_documento_nota_credito_id if documento is not None else None
            tipo_doc_debito = documento.tipo_documentos.tipo_documento_nota_debito_id if documento is not None else None

            if tipo_doc_credito == obj_factura.tipo_documentos_id and tipo_doc_credito != int(self.nota_ajuste_id):
                ctx.tipo_documento_trans = 3
                codigo_concepto = 6 if obj_factura.nota_parcial else 2
                ctx.tipo_operacion = 20  # Nota Crédito que referencia una factura electrónica
            elif tipo_doc_debito == obj_factura.tipo_documentos_id and tipo_doc_debito != int(self.nota_ajuste_id):
                ctx.tipo_documento_trans = 4
                codigo_concepto = 3  # Cambio de valor
                ctx.tipo_operacion = 30  # Nota Débito que referencia una factura electrónica
            else:
                codigo_concepto = ''

            ctx.campos_nota = "<codigoConcepto>{}</codigoConcepto><numeroReferenciaFactura>{}</numeroReferenciaFactura>".format(
                codigo_concepto, obj_factura.referencia
            )
        else:
            ctx.url = "https://www.pruebas.v2.ifelix.co/API-FELIX/FacturaElectronicaWS?wsdl"
            if self.fact_elec_produccion.lower() == "true":
                ctx.url = "https://www.ifelix.co/API-FELIX/FacturaElectronicaWS?wsdl"

        if ctx.tipo_operacion is None:
            ctx.tipo_operacion = self._get_tipo_operacion(obj_factura.operacion)

    # ------------------------------------------------------------------ #
    # Construcción del XML de cliente/adquiriente
    # ------------------------------------------------------------------ #

    def _construir_cliente_xml(self, ctx):
        persona = ctx.persona
        obj_factura = ctx.obj_factura

        if persona.contribuyente_id != 1:
            nombres_persona = "{} {}".format(persona.p_nombre or '', persona.s_nombre or '')
        else:
            nombres_persona = persona.n_completo

        apellidos_persona = (
            "{} {}".format(persona.p_apellido or '', persona.s_apellido or '')
            if persona.contribuyente_id != 1 else ""
        )

        direccion = persona.direcciones_personas.filter(incluir_a_factura=True).exclude(eliminado=True).first()
        coddane = direccion.ciudad.coddane
        coddpto = coddane[0:2]
        codeciudad = coddane[2:]

        tipo_persona = 1 if persona.contribuyente and persona.contribuyente.id == 1 else 2
        tipo_regimen = (
            48 if obj_factura.personas.tipo_regimen_id in (self.regimen_simple, self.responsable_iva) else 49
        )

        return (
            '<adquirienteElectronico></adquirienteElectronico><apellidos>{}</apellidos><autoretenedor></autoretenedor>'
            '<barrioVereda></barrioVereda><barrioVeredaFiscal></barrioVeredaFiscal><codigoActividadEconomica></codigoActividadEconomica>'
            '<codigoMoneda>{}</codigoMoneda><codigoTipoDocumento>{}</codigoTipoDocumento><codigoTipoImpuesto>{}</codigoTipoImpuesto>'
            '<codigoTipoPersona>{}</codigoTipoPersona><codigoTipoRegimen>{}</codigoTipoRegimen><correoElectronico>{}</correoElectronico>'
            '<departamento>{}</departamento><departamentoFiscal></departamentoFiscal><direccion>{}</direccion>'
            '<direccionFiscal></direccionFiscal><documento>{}</documento><id></id><idEmpresa></idEmpresa>'
            '<idTipoDocumento>{}</idTipoDocumento><idTipoEmpresa></idTipoEmpresa><identificadorDuns></identificadorDuns>'
            '<identificadorPostal></identificadorPostal><logo></logo><municipio>{}</municipio><municipioFiscal></municipioFiscal>'
            '<nombreComercial></nombreComercial><nombreRegimen></nombreRegimen><nombreTipoDocumento>{}</nombreTipoDocumento>'
            '<nombreTipoPersona>{}</nombreTipoPersona><nombres>{}</nombres><pais>{}</pais><paisFiscal></paisFiscal>'
            '<responsable>{}</responsable><telefono>{}</telefono><responsabilidades></responsabilidades>'
        ).format(
            apellidos_persona,
            "COP",
            ctx.codigo_tipo_documento,
            "01" if persona.tipo_regimen is not None and persona.tipo_regimen.id == int(self.responsable_iva) else "",
            tipo_persona,
            tipo_regimen,
            persona.email,
            coddpto,
            direccion.descripcion,
            persona.nit_tributario if persona.nit_tributario is not None else persona.documento,
            ctx.codigo_tipo_documento,
            codeciudad,
            ctx.codigo_tipo_documento,
            tipo_persona,
            nombres_persona,
            "CO",
            persona.tipo_regimen is not None and persona.tipo_regimen.id == int(self.responsable_iva),
            obj_factura.movil,
        )

    # ------------------------------------------------------------------ #
    # Construcción del XML de producto/servicio (detalle de la factura)
    # ------------------------------------------------------------------ #

    def _construir_producto_servicio_xml(self, ctx):
        obj_factura = ctx.obj_factura
        producto_servicio = ""

        obj_det = DetalleFacturas.objects.filter(documentos_id=obj_factura.id)

        for det in obj_det:
            mandantes = []
            if det.mandantes is not None and self.nota_credito_id != obj_factura.tipo_documentos_id:
                mandantes = json.loads(det.mandantes)

            lista_tercero = self._construir_lista_tercero_xml(ctx, mandantes)
            lista_tarifa_impuesto = self._construir_lista_tarifa_impuesto_xml(ctx, det)

            producto_servicio += (
                '<productoServicio><cantidad>{}</cantidad><codigo>{}</codigo><fechaFin></fechaFin>'
                '<fechaInicio></fechaInicio><item></item><marca></marca><modelo></modelo><nombre>{}</nombre>'
                '<detalle>{}</detalle><precioReferencia></precioReferencia><regalo>{}</regalo><servicio></servicio>'
                '<servicioTercerizado></servicioTercerizado><tasaCargo></tasaCargo><tasaDescuentos></tasaDescuentos>'
                '<tasaImpuestos></tasaImpuestos>{}<unidadMedida>{}</unidadMedida><valorBase></valorBase>'
                '<valorCargo></valorCargo><valorDescuento></valorDescuento><valorImpuestos></valorImpuestos>'
                '<valorTotal>{}</valorTotal><valorUnitario>{}</valorUnitario>{}</productoServicio>'
            ).format(
                det.cantidad,
                det.concepto.codigo,
                det.concepto.detalle,
                det.detalle,
                False,
                lista_tercero,
                "94",
                round(float(det.valor) + (float(det.valor) * (float(det.piva) / 100))),
                float(det.valor),
                lista_tarifa_impuesto,
            )

        return producto_servicio

    def _construir_lista_tercero_xml(self, ctx, mandantes):
        obj_factura = ctx.obj_factura
        observacion_contrato = obj_factura.contrato.observacion_factura if obj_factura.contrato is not None else ''
        lista_tercero = ""

        for item in mandantes:
            prop = None
            if item.get("Identificacion") and obj_factura.inmueble:
                prop = obj_factura.inmueble.inmueble_propietario.filter(
                    activo=True, persona__documento=item['Identificacion'].split('-')[0]
                )

            porcentaje = 100
            if prop and prop.exists():
                prop = prop.first()
                if ctx.nota == "":
                    ctx.nota += "INGRESOS RECIBIDOS PARA TERCEROS:"
                ctx.nota += " Propietario {} - Documento: {} % Part {}".format(
                    item['Nombre'], prop.persona.documento, prop.participacion
                )
                porcentaje = prop.participacion

            lista_tercero += (
                '<listaTercero><codigoTipoDocumento>{}</codigoTipoDocumento><documento>{}</documento>'
                '<nombres>{}</nombres><valor>{}</valor><porcentaje>{}</porcentaje></listaTercero>'
            ).format(item['TipoIdentificacion'], item['Identificacion'], item['Nombre'], item['Valor'], porcentaje)

        ctx.nota += (' Observación del contrato: ' + observacion_contrato) if observacion_contrato else ''
        return lista_tercero

    def _construir_lista_tarifa_impuesto_xml(self, ctx, det):
        obj_factura = ctx.obj_factura
        lista = ""

        if float(det.piva) > 0:
            lista += self.build_trasmision_impuesto_xml("01", "Tarifa general", float(det.piva), "")

        if det.concepto.retencion is True:
            if obj_factura.prteiva > 0:
                prteiva = (float(det.prteiva) if det.prteiva > 0 else float(obj_factura.prteiva)) \
                    if det.prteiva is not None else float(obj_factura.prteiva)
                lista += self.build_trasmision_impuesto_xml("05", "Tarifa general", prteiva, "")

            if obj_factura.prteica > 0:
                prteica = (float(det.prteica) if det.prteica > 0 else float(obj_factura.prteica)) \
                    if det.prteica is not None else float(obj_factura.prteica)
                prteica *= 10
                lista += self.build_trasmision_impuesto_xml("07", f"Tarifa {obj_factura.ciudad}", prteica, "")

            if obj_factura.prtefte > 0:
                persona = obj_factura.personas
                if obj_factura.operacion == 'PROPIETARIO':
                    concepto = "Honorarios y comisiones personas naturales que suscriban contrato o cuya sumatoria de los pagos o abonos en cuenta superen las 3.300 UVT ($105.135.000)"
                elif persona.tipo_actividad_id == 1:
                    concepto = "Arrendamiento de bienes inmuebles (declarantes)"
                else:
                    concepto = "Arrendamiento de bienes inmuebles (no declarantes)"

                prtefte = (float(det.prtefuente) if det.prtefuente > 0 else float(obj_factura.prtefte)) \
                    if det.prtefuente is not None else float(obj_factura.prtefte)
                lista += self.build_trasmision_impuesto_xml("06", concepto, prtefte, "")

        return lista

    @staticmethod
    def build_trasmision_impuesto_xml(codigo_tipo_impuesto, concepto, valor_tarifa, valor_aplicado_producto):
        return (
            "<listaTarifaImpuestoPJ><codigoTipoImpuesto>{}</codigoTipoImpuesto><concepto>{}</concepto>"
            "<valorTarifa>{}</valorTarifa><valorAplicadoProducto>{}</valorAplicadoProducto></listaTarifaImpuestoPJ>"
        ).format(codigo_tipo_impuesto, concepto, valor_tarifa, valor_aplicado_producto)

    # ------------------------------------------------------------------ #
    # Construcción del payload SOAP completo
    # ------------------------------------------------------------------ #

    def _construir_payload(self, ctx, cliente_xml, producto_servicio_xml):
        obj_factura = ctx.obj_factura

        xml_header = (
            '<wsse:Security xmlns:wsse="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-secext-1.0.xsd" '
            'xmlns:wsu="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-wssecurity-utility-1.0.xsd">'
            '<wsse:UsernameToken><wsse:Username>{}</wsse:Username>'
            '<wsse:Password Type="http://docs.oasis-open.org/wss/2004/01/oasis-200401-wss-username-token-profile-1.0#PasswordText">{}</wsse:Password>'
            '</wsse:UsernameToken></wsse:Security>'
        ).format(self.username, self.password)

        xml_body = (
            '<ws:{}><arg0><cliente>{}</cliente><codigoCondicionEntrega></codigoCondicionEntrega>'
            '<codigoDocumentoReferencia></codigoDocumentoReferencia><codigoEstadoDocumentoDian></codigoEstadoDocumentoDian>'
            '<codigoFormaPago>{}</codigoFormaPago><codigoIntervalo></codigoIntervalo><codigoMedioPago>{}</codigoMedioPago>'
            '<codigoMoneda>{}</codigoMoneda><codigoTipoDocumentoContable>{}</codigoTipoDocumentoContable>'
            '<codigoTipoFactura>{}</codigoTipoFactura><codigoTipoOperacion>{}</codigoTipoOperacion>'
            '<documentoRecibidoDian></documentoRecibidoDian><errorDian></errorDian>'
            '<facturador><documento>{}</documento><username>{}</username></facturador>'
            '<fechaDocumentoDian></fechaDocumentoDian><fechaExpedicion>{}</fechaExpedicion><fechaTasaCambio></fechaTasaCambio>'
            '<fechaTranscripcion></fechaTranscripcion><fechaVencimiento>{}</fechaVencimiento>'
            '<fechaVencimientoPago>{}</fechaVencimientoPago><formaPago></formaPago><nota>{}</nota>'
            '<notaCondicionEntrega></notaCondicionEntrega><numeroFactura>{}</numeroFactura>'
            '<prefijoDocumento>{}</prefijoDocumento>{}<tasaCambio></tasaCambio><valorAntesImpuestos>{}</valorAntesImpuestos>'
            '<valorTotal>{}</valorTotal><valorVenta>{}</valorVenta>{}{}</arg0></ws:{}>'
        ).format(
            ctx.funcion,
            cliente_xml,
            obj_factura.forma_pago.codigo,
            obj_factura.medio_pago.codigo,
            "COP",
            ctx.tipo_documento_trans,
            ctx.tipo_documento_trans,
            ctx.tipo_operacion,
            self.username,
            self.username,
            datetime.datetime.combine(obj_factura.fecha, datetime.datetime.min.time()).strftime("%Y-%m-%dT%H:%M:%S"),
            datetime.datetime.combine(obj_factura.fechaven, datetime.datetime.min.time()).strftime("%Y-%m-%dT%H:%M:%S"),
            datetime.datetime.combine(obj_factura.fechaven, datetime.datetime.min.time()).strftime("%Y-%m-%dT%H:%M:%S"),
            ctx.nota,
            obj_factura.numero,
            obj_factura.tipo_documentos.prefijo,
            producto_servicio_xml,
            obj_factura.subtotal,
            obj_factura.gtotal,
            obj_factura.gtotal,
            ctx.campos_nota,
            ctx.campos_soporte,
            ctx.funcion,
        )

        return ctx.xml_formato.format(xml_header, xml_body)

    # ------------------------------------------------------------------ #
    # Envío SOAP
    # ------------------------------------------------------------------ #

    def _enviar_soap(self, ctx, payload):
        session = Session()
        session.verify = False

        transport = Transport(session=session)
        client = Client(wsdl=ctx.url, transport=transport)

        service = client.wsdl.services[ctx.xml_service]
        port = service.ports[ctx.xml_port]
        endpoint = port.binding_options['address']

        xml_element = etree.fromstring(payload.encode('utf-8'))
        return client.transport.post_xml(endpoint, xml_element, headers={})

    # ------------------------------------------------------------------ #
    # Procesamiento de la respuesta y persistencia
    # ------------------------------------------------------------------ #

    def _procesar_respuesta(self, ctx, jresp, response, datos_webservice, datos_existentes):
        obj_factura = ctx.obj_factura

        datos = {
            "fecha_hora": datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
            "documento_id": obj_factura.id,
            "numero_documento": obj_factura.numero,
            "usuario_id": self.usuario,
            "tipo": "response",
            "mensaje_dian": None,
            "data": response.content.decode("utf-8"),
        }

        if jresp["tipo"] != "exito":
            self._actualizar_estado_fact_electronica(obj_factura.id, estado_id=3)
            obj_factura.observacion_electronica = " | ".join(jresp["listaMensajes"]) if jresp["listaMensajes"] else ''
            datos["mensaje_dian"] = obj_factura.observacion_electronica
            datos_webservice.append(datos)
            datos_webservice.extend(datos_existentes)
            obj_factura.webservice = json.dumps(datos_webservice, indent=4, ensure_ascii=False)
            obj_factura.save()

            raise FacturacionElectronicaError("Por favor revisar la factura rechazada.")

        # Nota: en la rama Felix el 'numero_generado' original siempre se guardaba como None
        # tras un envío exitoso (así estaba en el código fuente). Se mantiene ese comportamiento.
        self._actualizar_estado_fact_electronica(obj_factura.id, estado_id=4, numero_generado=None)
        obj_factura.observacion_electronica = "Factura Transmitida Correctamente."
        datos["mensaje_dian"] = obj_factura.observacion_electronica
        datos_webservice.append(datos)
        datos_webservice.extend(datos_existentes)
        obj_factura.webservice = json.dumps(datos_webservice, indent=4, ensure_ascii=False)
        obj_factura.save()

    def _log_request(self, ctx, payload):
        return {
            "fecha_hora": datetime.datetime.now().strftime("%Y-%m-%d %I:%M:%S %p"),
            "documento_id": ctx.obj_factura.id,
            "numero_documento": ctx.obj_factura.numero,
            "usuario_id": self.usuario,
            "tipo": "request",
            "data": payload,
        }

    @staticmethod
    def parsear_respuesta_xml_felix(xml_bytes, funcion, num_factura):
        try:
            root = etree.fromstring(xml_bytes)
            ns = {
                "soap": "http://schemas.xmlsoap.org/soap/envelope/",
                "ns2": "http://ws.informatix.co/",
            }

            fault = root.xpath("//soap:Fault", namespaces=ns)
            if fault:
                return {
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "factura": num_factura,
                    "tipo": "soap_fault",
                    "enviado": False,
                    "numero": None,
                    "mensaje": None,
                    "listaMensajes": [],
                    "codigo": (root.xpath("//soap:Fault/faultcode/text()", namespaces=ns) or [None])[0],
                    "error": (root.xpath("//soap:Fault/faultstring/text()", namespaces=ns) or [None])[0],
                }

            lista_mensajes = root.xpath(f"//ns2:{funcion}Response/return/listaMensajes/text()", namespaces=ns)
            enviado = root.xpath(f"//ns2:{funcion}Response/return/enviado/text()", namespaces=ns)

            if lista_mensajes and enviado[0].lower() == "false":
                return {
                    "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "factura": num_factura,
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
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "factura": num_factura,
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
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "factura": num_factura,
                "tipo": "error_exception",
                "enviado": False,
                "numero": None,
                "mensaje": None,
                "listaMensajes": [],
                "codigo": None,
                "error": str(e),
            }

    # ------------------------------------------------------------------ #
    # TODO: mover implementación real desde el ViewSet original
    # ------------------------------------------------------------------ #

    def _get_tipo_operacion(self, operacion):
        raise NotImplementedError(
            "Mover aquí la implementación real de ViewSet.getTipoOperacion()"
        )

    def _get_ciudad_cod_dane(self, personas_id):
        raise NotImplementedError(
            "Mover aquí la implementación real de ViewSet.getCiudadCodDane() "
            "(nota: en la rama Felix no se usaba directamente, revisa si aún es necesaria)"
        )