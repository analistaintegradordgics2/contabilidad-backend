from django.db import transaction
from decimal import Decimal
from apps.contabilidad.models.documento import Documentos, Mov, PagoDocumento, FactElectronicaDocumento

class DocumentoService:

    @staticmethod
    @transaction.atomic
    def crear(data, user):

        movimientos_data = data.pop('movimientos', [])
        pagos_data = data.pop('pagos', [])
        fact_data = data.pop('facturacion', None)

        # =========================
        # VALIDACIÓN CONTABLE
        # =========================
        total_db = Decimal(0)
        total_cr = Decimal(0)

        for mov in movimientos_data:
            total_db += Decimal(mov.get('valor_db') or 0)
            total_cr += Decimal(mov.get('valor_cr') or 0)

        if total_db != total_cr:
            raise Exception("El documento no cuadra (Débito != Crédito)")

        # =========================
        # CREAR DOCUMENTO
        # =========================
        documento = Documentos.objects.create(**data)

        # =========================
        # MOVIMIENTOS
        # =========================
        movs = []
        for mov in movimientos_data:
            mov['documento'] = documento
            movs.append(Mov(**mov))

        Mov.objects.bulk_create(movs)

        # =========================
        # PAGOS
        # =========================
        for pago in pagos_data:
            PagoDocumento.objects.create(documento=documento, **pago)

        # =========================
        # FACT ELECTRÓNICA
        # =========================
        if fact_data:
            FactElectronicaDocumento.objects.create(
                documento=documento,
                **fact_data
            )

        return documento