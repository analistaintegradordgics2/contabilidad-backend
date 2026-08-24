import os
import re
import math
import unicodedata
from decimal import Decimal, ROUND_HALF_UP
import requests
from django.utils import timezone
from django.conf import settings

from apps.parametros.models.parametrizacion import Parametros, ParametrosWhatsapp
from apps.personas.models.persona import Persona, Telefono
from apps.contabilidad.models.pago import CuentaBancaria, Banco
from apps.utils.util import NumeroA
from apps.utils.render import Render

class Funciones:

    @staticmethod
    def calcular_digito_verificacion(val: str):
        """
        Calcula el dígito de verificación de un NIT en Colombia.
        
        :param val: NIT en forma de string (solo números).
        :return: Dígito de verificación o None.
        """
        vpri = [0, 3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
        z = len(val)
        x = 0
        for i in range(z):
            y = int(val[i])
            x += y * vpri[z - i]
        y = x % 11
        return 11 - y if y > 1 else y

    @staticmethod
    def resolver_fk(value, attr_name, instance):
        """
        Convierte un entero ID a instancia de modelo si el campo es ForeignKey.
        Django's ForeignKey espera una instancia, no un ID puro.
        
        :param value: Valor a verificar (puede ser int o instancia)
        :param attr_name: Nombre del atributo/campo en el modelo
        :param instance: Instancia del modelo donde está el campo
        :return: Instancia de modelo si value es int y es FK, sino el valor original
        """
        if isinstance(value, int):
            try:
                field = instance._meta.get_field(attr_name)
                if field.is_relation:
                    related_model = field.related_model
                    return related_model.objects.get(pk=value)
            except Exception:
                pass
        return value

    def enviar_whatsapp(nombre_archivo, ruta_archivo, model, tipo_envio, pdf_bytes=None) :

        token = ParametrosWhatsapp.objects.filter(parametro="token").first()
        cliente_id = ParametrosWhatsapp.objects.filter(parametro="cliente_id").first()
        msg_resultado = ""
        telefono = None
        parametro_plantilla = None
        persona_id = None
        tipo_proceso = None

        # Nelson Lugo 04/07/2025 - ¡¡¡¡¡¡ Por favor si se crea un nuevo tipo de envío, llenar la variable tipo_proceso con el nombre del nuevo proceso. !!!!!!
        if tipo_envio == 4 :
            msg_resultado = "Desprendible de pago periodo: {} <> Empleado: {}".format(model["periodo"], model["liquidaciones"][0]["nombre"])
            parametro_plantilla = ParametrosWhatsapp.objects.filter(parametro="desprendible").first()
            persona_id = model["persona"]["id"]
            tipo_proceso = "Desprendible de pago"

        url_bitacora = "https://whatsapp.webdgi.site/api/restful/whatsapp/add/"
        # url_bitacora = "http://localhost:8001/api/restful/whatsapp/add/"

        if token != None and cliente_id != None and parametro_plantilla != None :
            
            token = token.valor
            cliente_id = cliente_id.valor
            parametro_plantilla = parametro_plantilla.valor

            url = "https://graph.facebook.com/v13.0/{}/media".format(cliente_id)

            headers = {
                'Authorization': 'Bearer {}'.format(token)
            }

            payload = {
                'type': 'application/pdf',
                'messaging_product': 'whatsapp'
            }

            # Si vienen bytes los usamos directamente, si no abrimos el archivo
            if pdf_bytes is not None:
                archivo = (nombre_archivo, pdf_bytes, 'application/pdf')
            else:
                archivo = (nombre_archivo, open(ruta_archivo, 'rb'), 'application/pdf')
            
            files = [('file', archivo)]

            response = requests.request("POST", url, headers=headers, data=payload, files=files)

            if response.status_code == 200 :
                result = response.json()

                url = "https://graph.facebook.com/v13.0/{}/messages".format(cliente_id)

                for tele in Telefono.objects.filter(persona_id=persona_id, sms=True).exclude(eliminado=True) :
                    try :
                        telefono = int(tele.valor)
                    except :
                        telefono = tele.valor

                        headers = {
                            "Content-type": "application/json"
                        }

                        msg = "El número {} es inconsistente, no se envió el mensaje".format(telefono)

                        payload = {
                            "celular": tele.valor,
                            "tipo": 1,
                            "mensaje": msg,
                            "idwp": None,
                            "status": "",
                            "idtel": cliente_id,
                            "mensaje2": msg,
                            "nit": model["persona"]["documento"],
                            "nombre": model["persona"]["nombre"],
                            "tipo_proceso": tipo_proceso,
                        }

                        response = requests.request("POST", url_bitacora, headers=headers, json=payload)

                        return {
                            "status": -100,
                            "msg": "ok"
                        }

                    try :
                        prefijo = "57"
                        if tele.prefijo != None and tele.prefijo != "":
                            prefijo = tele.prefijo.replace("+", "")
                        
                        if prefijo == "57" :
                            # Nelson Lugo - 06/12/2024 Bita #61537 - Se valida si el prefijo es de colombia en el numero de telefono debe tener 10 digitos
                            if len(str(telefono)) == 10 :
                                telefono = "{}{}".format(prefijo, telefono)
                            elif len(str(telefono)) < 10 :
                                headers = {
                                    "Content-type": "application/json"
                                }

                                msg = "El número {} es inconsistente, no se envió el mensaje".format(telefono)

                                payload = {
                                    "celular": telefono,
                                    "tipo": 1,
                                    "mensaje": msg,
                                    "idwp": None,
                                    "status": "",
                                    "idtel": cliente_id,
                                    "mensaje2": msg,
                                    "nit": model["persona"]["documento"],
                                    "nombre": model["persona"]["nombre"],
                                    "tipo_proceso": tipo_proceso,
                                }
                                response = requests.request("POST", url_bitacora, headers=headers, json=payload)

                                return {
                                    "status": -100,
                                    "msg": "ok"
                                }
                        else :
                            telefono = "{}{}".format(prefijo, telefono)
                        
                        headers["Content-type"] = "application/json"

                        payload = {
                            "messaging_product": "whatsapp",
                            "to": telefono,
                            "type": "template",
                            "template": {
                                "name": parametro_plantilla,
                                "language": {
                                    "code": "en_US"
                                },
                                "components": [
                                    {
                                        "type": "header",
                                        "parameters": [
                                            {
                                                "type": "document",
                                                "document": {
                                                    "id": result["id"],
                                                    "filename": nombre_archivo
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        }

                        if tipo_envio == 4 :
                            payload["template"]["components"].append({
                                "type": "body",
                                "parameters": [
                                    {
                                        "type": "text",
                                        "text": model["persona"]["nombre"]
                                    },
                                    {
                                        "type": "text",
                                        "text": model["empresa"]["nombre"]
                                    },
                                    {
                                        "type": "text",
                                        "text": model["periodo"]
                                    },
                                    {
                                        "type": "text",
                                        "text": model["mes_anio"]
                                    },
                                ]
                            })
                        
                        response = requests.request("POST", url, headers=headers, json=payload)

                        if response.status_code == 200 :
                            result = response.json()

                            headers = {
                                "Content-type": "application/json"
                            }

                            payload = {
                                "celular": telefono,
                                "tipo": 1,
                                "mensaje": msg_resultado,
                                "idwp": result["messages"][0]["id"],
                                "status": "",
                                "idtel": cliente_id,
                                "mensaje2": msg_resultado,
                                "nit": model["persona"]["documento"],
                                "nombre": model["persona"]["nombre"],
                                "tipo_proceso": tipo_proceso,
                            }

                            response = requests.request("POST", url_bitacora, headers=headers, json=payload)

                            return {
                                "status": 200,
                                "msg": "ok"
                            }

                        else :
                            result = response.json()
                            headers = {
                                "Content-type": "application/json"
                            }

                            payload = {
                                "celular": telefono,
                                "tipo": 1,
                                "mensaje": result["error"]["message"],
                                "idwp": None,
                                "status": "",
                                "idtel": cliente_id,
                                "mensaje2": result["error"]["message"],
                                "nit": model["persona"]["documento"],
                                "nombre": model["persona"]["nombre"],
                                "tipo_proceso": tipo_proceso,
                            }

                            response = requests.request("POST", url_bitacora, headers=headers, json=payload)

                            return {
                                "status": -100,
                                "msg": "ok"
                            }
                    except Exception as inst: 
                        # pdb.set_trace()
                        headers = {
                            "Content-type": "application/json"
                        }

                        payload = {
                            "celular": telefono,
                            "tipo": 1,
                            "mensaje": str(inst),
                            "idwp": None,
                            "status": "",
                            "idtel": cliente_id,
                            "mensaje2": str(inst),
                            "nit": model["persona"]["documento"],
                            "nombre": model["persona"]["nombre"],
                            "tipo_proceso": tipo_proceso,
                        }

                        response = requests.request("POST", url_bitacora, headers=headers, json=payload)

                        return {
                            "status": -100,
                            "msg": "ok"
                        }
                return {
                    "status": -100,
                    "msg": "ok"
                }
            else :
                return {
                    "status": 400,
                    "msg": "Por favor revisar la parametrización, no se esta conectando a Facebook Meta."
                }
        else :
            
            return {
                "status": 400,
                "msg": "Por favor revisar la parametrización de whatsapp."
            }

    @staticmethod
    def generar_plano_banco(model):
        """
        Genera el archivo plano bancario exclusivamente para el pago de empleados (tipopago == 4).
        Soporta los formatos de:
        - Banco Caja Social (código 32)
        - Davivienda (código 51, formatos TXT y CSV)
        - Bancolombia (código 7, formato TXT nómina)
        - Banco AV Villas (código 52, formato TXT)
        - Otros Bancos (formato delimitado por punto y coma)
        """
        numero = NumeroA()

        mes_num = int(model.get('mes_pago', 1))
        mespago = f"{mes_num:02d}"

        # Obtener cuenta bancaria y banco emisor
        cta_banco = CuentaBancaria.objects.filter(pk=model.get('cta_banco')).first()
        banco = cta_banco.banco if cta_banco else None
        codigo_banco_emisor = banco.codigo if banco and banco.codigo else 0

        # Función auxiliar para normalizar y limpiar texto sin acentos
        def limpiar_texto(texto: str) -> str:
            if not texto:
                return ""
            texto = unicodedata.normalize("NFD", str(texto))
            texto = texto.encode("ascii", "ignore").decode("utf-8")
            texto = re.sub(r"[^A-Za-z0-9 ]", " ", texto)
            return re.sub(r"\s+", " ", texto).strip()

        result = {
            "tipo_archivo": "txt"
        }

        # Validar si Davivienda debe generarse como CSV o TXT
        davivienda_txt_param = Parametros.objects.filter(parametro='davivienda_txt').first()
        davivienda_es_txt = davivienda_txt_param.valor.lower() == 'true' if davivienda_txt_param and davivienda_txt_param.valor else False

        if codigo_banco_emisor == 51 and not davivienda_es_txt:
            result["tipo_archivo"] = "csv"

        now = timezone.now()
        fecha_actual = now.strftime("%Y%m%d")
        hora_actual = now.strftime("%H%M%S")

        # Parámetros generales de la empresa
        param_nit = Parametros.objects.filter(parametro='nit_empresa').first()
        nit_empresa = param_nit.valor.replace(".", "").replace("-", "").strip() if param_nit and param_nit.valor else ""

        # Mapeos de tipo de documento
        # DIAN / Estándar: 1=CC (Cédula), 2=TI, 4=CE, 5=CE, 6=NIT, 7=Pasaporte
        tipo_documentos_davivienda = {
            1: "01",  # CC
            2: "05",  # TI
            4: "02",  # CE
            5: "02",  # CE
            6: "03",  # NIT
            7: "04",  # Pasaporte
        }
        tipo_documentos_bancolombia = {
            1: "1",   # CC
            2: "2",   # TI
            4: "3",   # CE
            5: "3",   # CE
            6: "3",   # NIT
            7: "4",   # Pasaporte
        }
        tipo_documentos_avvillas = {
            1: "1",   # CC
            4: "2",   # CE
            5: "2",   # CE
            6: "3",   # NIT
            7: "10",  # Pasaporte
            2: "5",   # TI
        }

        data_csv = []
        transaccion_total = 0

        # Abrir archivo para escritura
        archivo_path = model.get('archivo')
        text = open(archivo_path, "w")

        # =========================================================================
        # ENCABEZADOS POR BANCO (Antes de iterar los registros de empleados)
        # =========================================================================
        if codigo_banco_emisor == 52:
            # AV Villas - Encabezado (Tipo 1)
            tipo_cuenta_origen = "1" if cta_banco and cta_banco.tipo_cuenta_id == 1 else "0"
            nro_cuenta_origen = str(cta_banco.numero_cuenta if cta_banco else "").ljust(17, ' ')[:17]
            param_nombre_empresa = Parametros.objects.filter(parametro='nombre_empresa').first()
            nombre_empresa = limpiar_texto(param_nombre_empresa.valor if param_nombre_empresa else "").ljust(16, ' ')[:16]

            sec_cliente = "000001"
            text.write("{}{}{}{}{}{}{}{}{}{}{}{}\n".format(
                "1",                                       # Tipo de Registro
                nro_cuenta_origen,                         # Número Producto Origen
                tipo_cuenta_origen,                        # Tipo de Producto Origen (1: Ahorros, 0: Corriente)
                "PP",                                      # Código de Producto
                fecha_actual,                              # Fecha Efectiva (YYYYMMDD)
                str(nit_empresa).rjust(15, '0')[:15],      # Número Identificación Origen
                "03",                                      # Tipo Identificación Origen (NIT)
                nombre_empresa,                            # Nombre Origen
                "0001",                                    # Código Plaza Origen
                "PPD",                                     # Tipo Pago
                sec_cliente,                               # Secuencia Cliente
                "4",                                       # Canal
            ))

        elif codigo_banco_emisor == 51 and davivienda_es_txt:
            # Davivienda TXT - Encabezado (RC)
            total_empleados = len(model.get('data', []))
            suma_total = sum(float(item.get("neto", 0)) for item in model.get('data', []))
            nro_cuenta_empresa = str(cta_banco.numero_cuenta if cta_banco else "0").rjust(16, '0')[:16]
            tipo_cuenta_dav = 'CA' if cta_banco and cta_banco.tipo_cuenta_id == 1 else 'CC'

            text.write("{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}\n".format(
                'RC',                                      # Indicador del registro RC
                str(nit_empresa).rjust(16, '0')[:16],      # Nit empresa
                'NOM ',                                    # Código del servicio
                'NOM ',                                    # Código del subservicio
                nro_cuenta_empresa,                        # Cuenta de la empresa
                tipo_cuenta_dav,                           # Tipo de cuenta (CA/CC)
                '000051',                                  # Código del banco Davivienda
                str(int(suma_total)).rjust(16, '0')[:16],  # Valor total registros
                '00',                                      # Decimales valor total
                str(total_empleados).rjust(6, '0')[:6],    # Total de registros
                fecha_actual,                              # Fecha de cargue (YYYYMMDD)
                hora_actual,                               # Hora de cargue (HHMMSS)
                '0'.rjust(4, '0'),
                '9999',
                '0'.rjust(8, '0'),
                '0'.rjust(6, '0'),
                '0'.rjust(2, '0'),
                '03',                                      # Tipo identificación (NIT)
                '0'.rjust(12, '0'),
                '0'.rjust(4, '0'),
                '0'.rjust(40, '0')
            ))

        elif codigo_banco_emisor == 7:
            # Bancolombia - Encabezado (Tipo 1)
            total_empleados = len(model.get('data', []))
            suma_total_centavos = sum((Decimal(str(it.get('neto', 0))) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP) for it in model.get('data', []))
            suma_total_str = f"{int(suma_total_centavos):017d}"
            nro_cuenta_debito = str(cta_banco.numero_cuenta if cta_banco else "0").rjust(11, '0')[:11]
            tipo_cuenta_debito = "S" if cta_banco and cta_banco.tipo_cuenta_id == 1 else "D"
            descripcion_pago = f"NOM {numero.mes_letra(mespago)}".ljust(10)[:10]

            text.write("1{}{}{}{}{}{}{}{}{}{}{}{}{}\n".format(
                str(nit_empresa).strip().rjust(15, '0')[:15],  # NIT
                "I",                                           # Aplicación Inmediata
                " " * 15,                                      # Filler 15
                "225",                                         # Clase transacción (225: Pago Nómina)
                descripcion_pago,                              # Descripción
                fecha_actual,                                  # Fecha creación
                "A1",                                          # Secuencia
                fecha_actual,                                  # Fecha aplicación
                str(total_empleados).rjust(6, '0')[:6],        # Número registros
                "0".rjust(17, '0'),                            # Sumatoria débitos
                suma_total_str,                                # Sumatoria créditos
                nro_cuenta_debito,                             # Cuenta a debitar
                tipo_cuenta_debito,                            # Tipo cuenta debitar (S: Ahorros, D: Corriente)
                " " * 149,                                     # Filler
            ))

        # =========================================================================
        # DETALLE DE EMPLEADOS
        # =========================================================================
        for i, item in enumerate(model.get('data', [])):
            persona_data = item.get("persona", {})
            forma_pago_data = item.get("forma_pago", {})
            banco_dest_data = forma_pago_data.get("banco", {}) or {}
            tipo_cta_data = forma_pago_data.get("tipo_cuenta", {}) or {}

            persona_id = persona_data.get("id")
            empleado = Persona.objects.filter(pk=persona_id).first() if persona_id else None

            p_nombre = empleado.p_nombre if empleado and empleado.p_nombre else ""
            p_apellido = empleado.p_apellido if empleado and empleado.p_apellido else ""
            s_nombre = empleado.s_nombre if empleado and empleado.s_nombre else ""
            s_apellido = empleado.s_apellido if empleado and empleado.s_apellido else ""
            n_completo = persona_data.get("nombre") or (empleado.n_completo if empleado else "")
            documento = str(persona_data.get("documento", "")).replace(".", "").replace("-", "").strip()

            tipo_documento_id = empleado.tipo_documento_id if empleado and empleado.tipo_documento_id else 1
            cuenta_destino = str(forma_pago_data.get("num_cuenta", "")).strip()

            tipo_cuenta_nombre = (tipo_cta_data.get("nombre") or "Ahorros").lower()
            tipo_cuenta = "A" if "ahorro" in tipo_cuenta_nombre else "C"

            total = item.get("neto", 0)
            transaccion_total += total

            # Obtener banco destino y código ACH
            conf_banco_dest = None
            banco_dest_id = banco_dest_data.get("id")
            if banco_dest_id:
                conf_banco_dest = Banco.objects.filter(pk=banco_dest_id).first()

            codigo_ach = conf_banco_dest.codigo_ach if conf_banco_dest and conf_banco_dest.codigo_ach else ""
            codigo_banco_dest = conf_banco_dest.codigo if conf_banco_dest and conf_banco_dest.codigo else 0

            detalle = f"PAGO DE EMPLEADOS MES DE {numero.mes_letra(mespago)}"

            # ---------------------------------------------------------------------
            # Estructura por Banco Destino / Formato
            # ---------------------------------------------------------------------
            if codigo_banco_emisor == 32:
                # Banco Caja Social
                tipo_cta_code = 32 if tipo_cuenta == "A" else 22
                if isinstance(total, float):
                    centavos_f, valor_f = math.modf(total)
                    centavos = f"{round(centavos_f, 2):.2f}"[2:4]
                    valor_int = math.trunc(valor_f)
                else:
                    centavos = "00"
                    valor_int = math.trunc(total)

                valor_str = str(valor_int).rjust(10, '0')
                text.write("6{}{}{}{}{}{}{}{}{}{}.\n".format(
                    tipo_cta_code,
                    valor_str,
                    centavos,
                    cuenta_destino.ljust(17, ' ')[:17],
                    str(codigo_ach).rjust(9, '0')[:9],
                    documento.ljust(15, ' ')[:15],
                    limpiar_texto(n_completo).ljust(22, ' ')[:22],
                    "V ".ljust(2, ' '),
                    "".ljust(13, ' '),
                    detalle.ljust(66, ' ')[:66]
                ))

            elif codigo_banco_emisor == 51:
                # Davivienda
                cod_doc_dav = tipo_documentos_davivienda.get(tipo_documento_id, "01")
                if davivienda_es_txt:
                    text.write("{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}\n".format(
                        'TR',
                        documento.rjust(16, '0')[:16],
                        '0'.rjust(16, '0'),
                        cuenta_destino.rjust(16, '0')[:16],
                        'CA' if tipo_cuenta == 'A' else 'CC',
                        str(codigo_banco_dest).rjust(6, '0')[:6],
                        str(int(total)).rjust(16, '0')[:16],
                        '00',
                        '0'.rjust(6, '0'),
                        cod_doc_dav,
                        '1',
                        '9999',
                        '0'.rjust(40, '0'),
                        '0'.rjust(18, '0'),
                        '0'.rjust(8, '0'),
                        '0'.rjust(4, '0'),
                        '0'.rjust(4, '0'),
                        '0'.rjust(7, '0')
                    ))
                else:
                    # Davivienda CSV
                    nombre_empleado = f"{p_nombre} {s_nombre}".strip() or n_completo
                    apellido_empleado = f"{p_apellido} {s_apellido}".strip()
                    data_csv.append({
                        "tipo_de_identificacion": cod_doc_dav,
                        "numero_identificacion": documento,
                        "nombre": limpiar_texto(nombre_empleado),
                        "apellido": limpiar_texto(apellido_empleado),
                        "codigo_banco": str(codigo_banco_dest).rjust(2, '0')[:3] if codigo_banco_dest else "",
                        "tipo_servicio": 'CA' if tipo_cuenta == 'A' else 'CC',
                        "numero_producto": cuenta_destino,
                        "valor": int(total),
                        "referencia": '',
                        "correo_electronico": '',
                        "detalle": detalle,
                    })

            elif codigo_banco_emisor == 7:
                # Bancolombia - Registro Detalle (Tipo 6)
                cod_doc_ban = tipo_documentos_bancolombia.get(tipo_documento_id, "1")
                tipo_transaccion = "37" if tipo_cuenta == "A" else "27"
                ach_4 = codigo_ach[:4] if codigo_ach else ""
                banco_destino_str = str(ach_4).rjust(9, '0')[:9]

                monto_centavos = (Decimal(str(total)) * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP)
                valor_str = f"{int(monto_centavos):017d}"
                referencia = f"NOM {numero.mes_letra(mespago)}".ljust(21, ' ')[:21]

                text.write("6{}{}{}{}{}{}{}{}{}{}{}{}{}{}{}\n".format(
                    documento.ljust(15, ' ')[:15],
                    limpiar_texto(n_completo).ljust(30, ' ')[:30],
                    banco_destino_str,
                    cuenta_destino.ljust(17, ' ')[:17],
                    "S",
                    tipo_transaccion,
                    valor_str,
                    fecha_actual,
                    referencia,
                    cod_doc_ban[:1],
                    "00000",
                    "".ljust(15, ' '),
                    "".ljust(80, ' '),
                    "".ljust(15, ' '),
                    " " * 27
                ))

            elif codigo_banco_emisor == 52:
                # AV Villas - Registro Detalle (Tipo 2)
                cod_doc_av = tipo_documentos_avvillas.get(tipo_documento_id, "1")
                tipo_trans_av = "32" if tipo_cuenta == "A" else "22"
                tipo_prod_av = "1" if tipo_cuenta == "A" else "0"

                text.write("{}{}{}{}{}{}{}{}{}{}{}{}{}\n".format(
                    "2",
                    tipo_trans_av,
                    str(codigo_banco_dest).rjust(4, '0')[:4],
                    '0811',
                    documento.rjust(15, ' ')[:15],
                    cod_doc_av.rjust(2, '0')[:2],
                    cuenta_destino.ljust(17, ' ')[:17],
                    tipo_prod_av,
                    limpiar_texto(n_completo).ljust(22, ' ')[:22],
                    "0",
                    str(int(total)).rjust(16, '0')[:16],
                    "001",
                    " " * 16
                ))

            else:
                # Genérico / Delimitado por punto y coma
                text.write("{};{};{};{};{};{}00;{};\n".format(
                    limpiar_texto(n_completo),
                    documento,
                    cuenta_destino,
                    codigo_ach,
                    tipo_cuenta,
                    int(total),
                    detalle
                ))

        # =========================================================================
        # REGISTRO DE CONTROL (Cierre por Banco)
        # =========================================================================
        if codigo_banco_emisor == 52:
            # AV Villas - Registro de Control (Tipo 4)
            total_empleados = len(model.get('data', []))
            text.write("{}{}{}{}\n".format(
                "4",
                str(total_empleados).rjust(8, '0')[:8],
                str(int(transaccion_total)).rjust(16, '0')[:16],
                "00"
            ))

        text.close()

        if result["tipo_archivo"] == "csv":
            result["archivo"] = Render.export_excel(data_csv, 'plano.csv', True, True, False)
        else:
            result["archivo"] = text

        result["status"] = 200
        return result