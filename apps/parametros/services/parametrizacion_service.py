import pdb

from apps.parametros.models.parametrizacion import Parametros
from cryptography.fernet import Fernet
from imap_tools import MailBox

class ParametrizacionService:

    @staticmethod
    def GuardarParametros(data=[], user=None):
        correos_invalidos = []
        for item in data :
            parametro = Parametros.objects.get(pk=item['id'])
            parametro.uc_id = user
            parametro.um_id = user
            tipo_tab = item.get('tipo_tab', None)
            if tipo_tab == "5" :
                if item["parametro"] == "smtp_correo_generales" :
                    parametro.valor = item['valor']
                elif item["parametro"] == "puerto_smtp_correo_generales" :
                    parametro.valor = item['valor']
                elif item["parametro"] == "imap_pop_correo_generales" :
                    parametro.valor = item['valor']
                elif item["parametro"] == "puerto_imap_pop_correo_generales" :
                    parametro.valor = item['valor']
                else :
                    # Se encripta las contraseñas para los correos
                    imap_pop = Parametros.objects.filter(parametro="imap_pop_correo_generales").first().valor
                    puerto = Parametros.objects.filter(parametro="puerto_imap_pop_correo_generales").first().valor
                    # pdb.set_trace()
                    try :
                        if not item['valor'] in [None, ""] and not item['valor2'] in [None, ""] :
                            with MailBox(imap_pop if imap_pop != None else "imap.gmail.com", int(puerto) if puerto != None else 587).login(item['valor'], item['valor2']) as mailbox :
                                key = Fernet.generate_key()
                                crypt = Fernet(key).encrypt(item['valor2'].encode())
                                parametro.valor = item['valor']
                                parametro.valor2 = crypt.decode('utf-8')
                                parametro.key = key.decode('utf-8')
                    except:
                        parametro.valor = item['valor']
                        correos_invalidos.append(item['valor'])
            elif item['parametro'] == 'persona_id_empresa' :
                parametro.valor = item['valor']
                persona = Parametros.objects.filter(parametro="persona_inmobiliaria_id").first()
                if persona :
                    persona.valor = item['valor']
                    persona.save()
            else :
                parametro.valor = item['valor']
            
            parametro.valor2 = item.get('valor2', parametro.valor2)
            parametro.save()