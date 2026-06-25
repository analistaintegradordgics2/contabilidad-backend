from apps.afiliados.models.afiliado import Afiliado
from apps.afiliados.models.causacion import AfiliadoConceptoCausacion
from django.db import transaction
import pdb

class AfiliadoService:
    def __init__(self, usuario=None):
        self._usuario = usuario
    
    def create_afiliado(self, data:dict) -> Afiliado:
        conceptos_data = data.pop('conceptos_causacion', [])
        data['uc'] = self._usuario

        persona_id = data.get('persona')
        if persona_id and Afiliado.objects.filter(persona_id=persona_id).exists():
            raise Exception('Ya existe un afiliado para la persona')

        with transaction.atomic():
            afiliado = Afiliado(**data)
            afiliado.save()

            for conc in conceptos_data:
                AfiliadoConceptoCausacion.objects.create(
                    afiliado=afiliado,
                    concepto_id=conc['concepto'],
                    valor=conc['valor'],
                    detalle=conc['detalle'],
                    uc=self._usuario
                )

            return afiliado
    
    def update_afiliado(self, id:int, data:dict) -> Afiliado:
        conceptos_data = data.pop('conceptos_causacion', [])
        data['um'] = self._usuario
        afiliado = Afiliado.objects.get(pk=id)

        with transaction.atomic():
            for campo, valor in data.items():
                if campo == 'id':
                    continue
                setattr(afiliado, campo, valor)
            
            afiliado.save(update_fields=data.keys())

            ids_conceptos_enviados = []

            for conc in conceptos_data:
                id_conc_causacion = conc.get('id') 
                
                if id_conc_causacion:
                    # Viene con ID -> Se actualiza el registro existente
                    AfiliadoConceptoCausacion.objects.filter(
                        pk=id_conc_causacion, 
                        afiliado=afiliado
                    ).update(
                        concepto_id=conc['concepto'],
                        valor=conc['valor'],
                        detalle=conc['detalle'],
                        um=self._usuario
                    )
                    ids_conceptos_enviados.append(id_conc_causacion)
                
                else:
                    # No viene ID -> Es uno nuevo, se crea
                    nuevo_concepto = AfiliadoConceptoCausacion.objects.create(
                        afiliado=afiliado,
                        concepto_id=conc['concepto'],
                        valor=conc['valor'],
                        detalle=conc['detalle'],
                        uc=self._usuario # Guardamos quién creó esta fila
                    )
                    ids_conceptos_enviados.append(nuevo_concepto.id)

            # Borramos cualquier concepto en la BD que NO haya sido enviado en este JSON
            AfiliadoConceptoCausacion.objects.filter(afiliado=afiliado).exclude(id__in=ids_conceptos_enviados).delete()
        return afiliado