from django.db import transaction
import json
from apps.common_db.db import execute_procedure
from decimal import Decimal
from django.db.models import Sum
import datetime
from apps.contabilidad.models.documento import Documentos, Mov, PagoDocumento, FactElectronicaDocumento, DocumentosBita, Estado
from apps.contabilidad.models.tipodocumento import TiposDocumentos
import pdb
class DocumentoService:

    @staticmethod
    @transaction.atomic
    def crear(data, user_id):

        encabezado   = data
        movimientos  = data.get('movimientos', [])
        pagos        = data.get('pagos', [])

        encabezado['usuario'] = user_id

        resultado = DocumentoService.crear_documento(
            encabezado,
            movimientos,
            pagos
        )

        return resultado

    @staticmethod
    def crear_documento(encabezado, movimientos, pagos):

        sql = ""
        params = None

        fuente = TiposDocumentos.objects.filter(
            pk=encabezado['tipo_documento']
        ).values_list('fuentes_id', flat=True).first()

        try:
            enca = encabezado

            # Contabilización
            cont = movimientos
            # CAMPOS_CLAVE = ("mayor_id", "persona_id", "concepto_id")
            # if len(cont) == 1 and all(cont[0].get(c) is None for c in CAMPOS_CLAVE):
            #     cont = []
            mov_json = json.dumps([
                {
                    'mov_id':        m.get('id', 0) or 0,
                    'mayor_id':      m.get('mayor'),
                    'persona_id':    m.get('persona'),
                    'concepto_id':   m.get('concepto'),
                    'detalle':       m.get('detalle', ''),
                    'valor_db':      float(m.get('valor_db', 0)),
                    'valor_cr':      float(m.get('valor_cr', 0)),
                    'cc_id':         m.get('centro_costos'),
                    'base':          float(m.get('base', 0)),
                    'docref':        m.get('docref', ''),
                    'nittercero_id': m.get('nittercero'),
                }
                for m in movimientos
            ])
            contabilizacion = mov_json

            if fuente != 4:
                
                # ─── Serializar pagos ───
                pagos_list = []

                # EFECTIVO
                if len(pagos) > 0:
                    efectivo = pagos.get('efectivo', {})

                    if efectivo and efectivo.get('valor', 0):

                        pagos_list.append({
                            'tipo': 'efectivo',
                            'forma_pago_id': 1,
                            'medio_pago_id': efectivo.get('medio_pago'),
                            'valor': float(efectivo.get('valor', 0)),
                        })
                    # pdb.set_trace()
                    # CHEQUES
                    for cheque in pagos.get('cheques', []):

                        pagos_list.append({
                            'tipo': 'cheque',
                            'forma_pago_id': 4,
                            'medio_pago_id': cheque.get('medio_pago'),
                            'banco_id': cheque.get('banco'),
                            'numero': cheque.get('numero', ''),
                            'fecha': cheque.get('fecha'),
                            'valor': float(cheque.get('valor', 0)),
                        })

                    # CONSIGNACION
                    consig = pagos.get('consig', {})

                    if consig and consig.get('valor', 0):

                        pagos_list.append({
                            'tipo': 'consignacion',
                            'forma_pago_id': 2,
                            'medio_pago_id': consig.get('medio_pago'),
                            'banco_id': consig.get('banco'),
                            'cuenta_bancaria_id': consig.get('cuenta_bancaria'),
                            'numero': consig.get('numero', ''),
                            'fecha': consig.get('fecha'),
                            'valor': float(consig.get('valor', 0)),
                        })
                    
                    # TRANSFERENCIA
                    transferencia = pagos.get('transferencia', {})

                    if transferencia and transferencia.get('valor', 0):

                        pagos_list.append({
                            'tipo': 'transferencia',
                            'forma_pago_id': 5,
                            'cuenta_origen_id': transferencia.get('cuenta_origen'),
                            'banco_destino_id': transferencia.get('banco'),
                            'cuenta_destino': transferencia.get('cuenta_destino'),
                            'numero_cheque': transferencia.get('numero_cheque', ''),
                            'valor': float(transferencia.get('valor', 0)),
                        })

                    # TARJETA
                    tarjeta = pagos.get('tarjeta', {})

                    if tarjeta and tarjeta.get('valor', 0):

                        pagos_list.append({
                            'tipo': 'tarjeta',
                            'forma_pago_id': 3,
                            'medio_pago_id': tarjeta.get('medio_pago'),
                            'banco_id': tarjeta.get('banco'),
                            'cuenta_bancaria_id': tarjeta.get('cuenta_bancaria'),
                            'numero_tarjeta': tarjeta.get('numero_tarjeta', ''),
                            'valor': float(tarjeta.get('valor', 0)),
                        })
                    # pdb.set_trace()

                pagos_json = json.dumps(pagos_list)

                
                sql = "select * from addingresos (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                params = (
                    encabezado.get('id') or 0,
                    encabezado.get('tipo_documento'),
                    encabezado.get('fecha'),
                    encabezado.get('concepto'),
                    encabezado.get('detalle', ''),
                    encabezado.get('referencia', ''),
                    encabezado.get('personas'),
                    float(encabezado.get('total', 0)),
                    1,
                    contabilizacion,
                    pagos_json,
                )

            else:
                factura_grid = json.dumps([
                    {
                        'concepto': item.get('concepto'),
                        'cantidad': str(item.get('cantidad', 1)),
                        'detalle':  item.get('detalle', ''),
                        'piva':     float(item.get('iva', 0)),
                        'valor':    float(item.get('valor', 0)),
                        'orden':    i + 1,
                        'prtefuente': 0,
                        'prteica':    0,
                        'prteiva':    0,
                    }
                    for i, item in enumerate(encabezado.get('items', []))
                ])

                sql = """
                    SELECT out_id, out_documento
                    FROM addfacturas(
                        %s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,
                        %s,%s
                    )
                """

                total_retenciones = (
                    float(encabezado.get('rtefte', 0)) +
                    float(encabezado.get('rteiva', 0)) +
                    float(encabezado.get('rteica', 0))
                )
                # pdb.set_trace()

                params = (
                    encabezado.get('id') or 0,
                    encabezado.get('tipo_documento'),
                    '2026-06-20',
                    '2026-06-20',
                    encabezado.get('personas'),
                    float(encabezado.get('subtotal',   0)),
                    float(encabezado.get('pdescuento', 0)),
                    float(encabezado.get('descuento',  0)),
                    float(encabezado.get('subtotal',   0)),  # in_total (sin iva)
                    float(encabezado.get('iva',        0)),
                    float(encabezado.get('subtotal',     0)),
                    float(encabezado.get('prtefte', 0)),
                    float(encabezado.get('prteiva', 0)),
                    float(encabezado.get('prteica', 0)),
                    float(encabezado.get('rtefte',  0)),
                    float(encabezado.get('rteiva',  0)),
                    float(encabezado.get('rteica',  0)),
                    total_retenciones,
                    encabezado.get('detalle', ''),
                    encabezado.get('usuario', 1),
                    encabezado.get('fpago',1),
                    encabezado.get('medio_pago',1),
                    mov_json,
                    factura_grid,
                    bool(encabezado.get('nota_parcial', False)),
                )
                # pdb.set_trace()
            resultado = execute_procedure(sql, params)

        except Exception:
            return {"status": 404, "data": None}

        # doc = Documentos.objects.get(pk=resultado[0][0])
        # DocumentoService._post_procesar_documento(doc, resultado[0][0], enca, data)
        # pdb.set_trace()

        return {"status": 200, "data": resultado}


    def _post_procesar_documento(self, doc, doc_id, enca, data):
        for campo in ('nota_parcial', 'nofactura_proveedor'):
            valor = enca.get(campo)
            if valor is not None:
                setattr(doc, campo, valor)
                doc.save()

        if enca.get('automatico') is True:
            doc.automatico = True
            doc.save()

        if data.get('copiado') is True:
            DocumentosBita.objects.create(
                documentos_id=doc_id,
                estado_id=2,
                evento="DOCUMENTO COPIADO",
                usuario_id=enca['usuario'],
                fecha=datetime.datetime.now(),
            )

    
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

            if mayor.ccosto and not mov.centro_costos_id:
                raise Exception(f'La cuenta {mayor.codigo} exige centro de costo')

            if mayor.base and not mov.base:
                raise Exception(f'La cuenta {mayor.codigo} exige una base')

    @staticmethod
    def cerrar(doc_id, usuario_id):
        doc = Documentos.objects.get(pk=doc_id)

        if doc.estado not in (Estado.ABIERTO, Estado.REABIERTO):
            raise Exception('Solo se pueden cerrar documentos abiertos o reabiertos')

        DocumentoService.validar_cierre(doc_id)   # ✅ nuevo

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