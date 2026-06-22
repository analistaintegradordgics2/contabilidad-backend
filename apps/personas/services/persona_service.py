from ..models.persona import Persona


class PersonaFormatter:

    @staticmethod
    def _get_data_persona_pago(obj_persona:Persona):
        direccion = obj_persona.direcciones_personas.first()
        telefono = obj_persona.telefonos_personas.filter(eliminado=False).first()

        persona = {
            "id": obj_persona.id,
            "nombre": obj_persona.n_completo,
            "documento": obj_persona.documento,
            "email": obj_persona.email,
            "ciudad": direccion.ciudad.nombre if direccion and direccion.ciudad_id else None,
            "telefono": telefono.valor if telefono != None else None,
            "datos_pago": {
                "forma_pago": obj_persona.forma_pago.nombre if obj_persona.forma_pago_id != None else "NO REGISTRA",
                "num_cuenta": obj_persona.fp_numero if obj_persona.fp_numero != None and obj_persona.fp_numero.strip() != '' else "NO REGISTRA",
                "banco": obj_persona.fp_banco.nombre if obj_persona.fp_banco_id != None else "NO REGISTRA",
                "tipo_cuenta": obj_persona.fp_tipo_cuenta if obj_persona.fp_tipo_cuenta != None and obj_persona.fp_tipo_cuenta != '0' else "NO REGISTRA",
                "titular": obj_persona.n_completo
            }
        }
    
        return persona