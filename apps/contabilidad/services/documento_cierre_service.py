from django.db import transaction
import json
from apps.common_db.db import execute_procedure
from decimal import Decimal
from django.db.models import Sum
import datetime
from apps.contabilidad.models.documento import Documentos, Mov, PagoDocumento, FactElectronicaDocumento, DocumentosBita, Estado
import pdb
class DocumentoCierreService:

    @staticmethod
    def validar_cierre(doc_id):
        """
        Valida que el documento esté en condiciones de cerrarse.
        Lanza Exception con el mensaje correspondiente si falla alguna validación.
        """
        movimientos = Mov.objects.filter(documento_id=doc_id).select_related('mayor')

        if not movimientos.exists():
            raise Exception('No existen movimientos en el documento')

        if movimientos.filter(valor_db=0, valor_cr=0).exists():
            raise Exception('Hay movimientos sin valores')

        totales = movimientos.aggregate(
            total_db=Sum('valor_db'),
            total_cr=Sum('valor_cr')
        )
        diferencia = (totales['total_db'] or 0) - (totales['total_cr'] or 0)
        if abs(diferencia) > 0.01:
            raise Exception('El movimiento está descuadrado')

        inconsistentes = movimientos.filter(
            mayor__isnull=True
        ) | movimientos.filter(persona__isnull=True) | movimientos.filter(concepto__isnull=True)

        if inconsistentes.exists():
            raise Exception('El movimiento contiene cuentas, personas o conceptos inconsistentes')

        for mov in movimientos:
            mayor = mov.mayor

            if mayor.tipo == 'GENERAL':   # ⚠️ ajusta al valor real de tu TextChoices
                raise Exception(f'La cuenta {mayor.codigo} no es auxiliar')

            if mayor.nittercero and not mov.nittercero_id:
                raise Exception(f'La cuenta {mayor.codigo} exige un NIT de tercero')

            # if mayor.ccosto and not mov.centro_costos_id:
            #     raise Exception(f'La cuenta {mayor.codigo} exige centro de costo')

            # if mayor.base and not mov.base:
            #     raise Exception(f'La cuenta {mayor.codigo} exige una base')

    @staticmethod
    def cerrar(doc_id, usuario_id):
        doc = Documentos.objects.get(pk=doc_id)

        if doc.estado not in (Estado.ABIERTO, Estado.REABIERTO):
            raise Exception('Solo se pueden cerrar documentos abiertos o reabiertos')

        DocumentoCierreService.validar_cierre(doc_id)   # 

        doc.estado = Estado.CERRADO
        doc.save(update_fields=['estado'])

        DocumentosBita.objects.create(
            documentos_id=doc_id,
            usuario_id=usuario_id,
            fecha=datetime.datetime.now(),
            evento=f'DOCUMENTO CERRADO No. {doc.numero}',
            estado_id=doc.estado,
        )
        return doc
    
    @staticmethod
    def reabrir(doc_id, usuario_id):
        doc = Documentos.objects.get(pk=doc_id)

        if doc.estado not in (Estado.CERRADO, Estado.ANULADO):
            raise Exception('Solo se pueden reabrir documentos cerrados o anulados')

        doc.estado = Estado.REABIERTO
        doc.save(update_fields=['estado'])

        DocumentosBita.objects.create(
            documentos_id=doc_id,
            usuario_id=usuario_id,
            fecha=datetime.datetime.now(),
            evento=f'DOCUMENTO REABIERTO No. {doc.numero}',
            estado_id=doc.estado,
        )
        return doc

    @staticmethod
    def anular(doc_id, usuario_id, observacion=None):
        doc = Documentos.objects.get(pk=doc_id)

        if doc.estado == Estado.ANULADO:
            raise Exception('El documento ya está anulado')

        doc.estado = Estado.ANULADO
        doc.save(update_fields=['estado'])

        evento = f'DOCUMENTO ANULADO No. {doc.numero}'
        if observacion:
            evento += f' - Motivo: {observacion}'

        DocumentosBita.objects.create(
            documentos_id=doc_id,
            usuario_id=usuario_id,
            fecha=datetime.datetime.now(),
            evento=evento,
            estado_id=doc.estado,
        )
        return doc