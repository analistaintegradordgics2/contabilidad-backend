import requests

from apps.parametros.models.parametrizacion import ParametrosWhatsapp
from apps.personas.models.persona import Telefono

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