from apps.afiliados.models.afiliado import Afiliado
from apps.afiliados.models.causacion import AfiliadoConceptoCausacion
from django.db import transaction
from apps.afiliados.models.causacion import FacturacionAfiliados
import pdb

class AfiliadoService:
    def __init__(self, usuario=None):
        self._usuario = usuario
    
    def create_afiliado(self, data:dict) -> Afiliado:
        conceptos_data = data.pop('conceptos_causacion', [])

        if not conceptos_data:
            raise ValueError('No se han proporcionado conceptos de causación')

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
                    uc=self._usuario,
                    facturar=conc.get('facturar', False)
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
                    # Viene con ID -> Se actualiza el registro existente llamando .save() para disparar señales de historial
                    obj = AfiliadoConceptoCausacion.objects.filter(
                        pk=id_conc_causacion, 
                        afiliado=afiliado
                    ).first()
                    if obj:
                        obj.concepto_id = conc['concepto']
                        obj.valor = conc['valor']
                        obj.detalle = conc['detalle']
                        obj.porcentaje = conc.get('porcentaje', None)
                        obj.um = self._usuario
                        obj.facturar = conc.get('facturar', False)
                        obj.save()
                        ids_conceptos_enviados.append(id_conc_causacion)
                
                else:
                    # No viene ID -> Es uno nuevo, se crea
                    nuevo_concepto = AfiliadoConceptoCausacion.objects.create(
                        afiliado=afiliado,
                        concepto_id=conc['concepto'],
                        valor=conc['valor'],
                        detalle=conc['detalle'],
                        porcentaje=conc.get('porcentaje', None),
                        uc=self._usuario, # Guardamos quién creó esta fila
                        facturar=conc.get('facturar', False)
                    )
                    ids_conceptos_enviados.append(nuevo_concepto.id)

            # Borramos cualquier concepto en la BD que NO haya sido enviado en este JSON usando .delete() individual para señales
            for conc_del in AfiliadoConceptoCausacion.objects.filter(afiliado=afiliado).exclude(id__in=ids_conceptos_enviados):
                conc_del.delete()

        return afiliado
    
    def afiliados_facturacion(self, params:dict, sin_facturar=False):
        mes = params.get('mes')
        anio = params.get('año')

        if sin_facturar:
            # Filtrar los afiliados que no se han facturado en el mes y anio indicados
            queryset = Afiliado.objects.filter(activo=True).exclude(afiliado_facturacion__mes=mes, afiliado_facturacion__anio=anio)
        else:
            # Filtrar los afiliados que se han facturado en el mes y anio indicados
            queryset = FacturacionAfiliados.objects.filter(mes=mes, anio=anio, afiliado__activo=True)

        return queryset