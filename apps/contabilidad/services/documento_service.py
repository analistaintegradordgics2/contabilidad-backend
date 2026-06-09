from django.db import transaction
import json
from apps.common_db.db import execute_procedure
from decimal import Decimal
from apps.contabilidad.models.documento import Documentos, Mov, PagoDocumento, FactElectronicaDocumento
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
        try:
            enca = encabezado

            # Contabilización
            cont = movimientos
            CAMPOS_CLAVE = ("mayor_id", "persona_id", "concepto_id")
            if len(cont) == 1 and all(cont[0].get(c) is None for c in CAMPOS_CLAVE):
                cont = []
            contabilizacion = json.dumps(cont)

            if encabezado['tipo_documento'] != 4:
                
                cons = {}
                tarj = {}
                cheq = []
                
                sql = "select out_id, out_documento from addingresos (%s::integer,%s::integer,%s::date,%s::integer,%s::varchar,%s::varchar,%s::integer,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::integer,%s::varchar,%s::date,%s::integer,%s::integer,%s::varchar,%s::integer,%s::integer,%s::integer,%s::varchar,%s::varchar,%s::integer,%s::integer,%s::integer,%s::json,%s::json)"
                # pdb.set_trace()
                params = (
                    enca['id'], enca['tipo_documento'], enca['fecha'], enca['concepto'],
                    enca['detalle'], 1, enca['persona'],
                    0,
                    0,  0,
                    1, 1, 1,
                    1, enca['fecha'], 1, 1,1,1,
                    1, 1, 1,
                    1, 1, 1,
                    enca['usuario'], contabilizacion, cheq,
                )

            else:
                suma = data['factura']['sumatorias']
                porc = data['factura']['porcentajes']
                rete = data['factura']['retenciones']
                factura = json.dumps(data['factura']['grid'])
                contrato_id = None

                # Una sola query, solo el campo necesario
                doc_operacion = Documentos.objects.filter(id=enca['id']).values_list('operacion', flat=True).first()
                fact_mandato = doc_operacion or 'GENERAL'

                mandato = enca.get('mandato', False)
                if mandato:
                    temp_cont = json.loads(contabilizacion)
                    mov_inmu = next((f for f in temp_cont if f.get("inmu_id") is not None), None)
                    if mov_inmu:
                        contrato = Contrato.objects.filter(
                            inmueble_id=mov_inmu["inmu_id"], estado_id=11
                        ).first()
                        if contrato:
                            contrato_id = contrato.id
                            fact_mandato = "ARRENDATARIO"

                sql = "select out_id, out_documento from addfacturas (%s::integer,%s::integer,%s::date,%s::date,%s::integer,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::numeric,%s::varchar,%s::integer,%s::integer,%s::integer,%s::varchar,%s::varchar,%s::json,%s::json,%s::integer,%s::integer,%s::integer,%s::integer,%s::boolean,%s::boolean)"
                params = (
                    enca['id'], enca['tipo'], enca['fecha'], enca['fechaven'],
                    enca['persona'], suma['subtotal'], porc['descuento'], suma['descuento'],
                    suma['total'], suma['iva'], suma['grantotal'],
                    porc['retefuente'], porc['reteiva'], porc['reteica'],
                    rete['retefuente'], rete['reteiva'], rete['reteica'],
                    suma['retenciones'], enca['detalle'], enca['usuario'],
                    enca['referencia'], contrato_id, None, fact_mandato,
                    contabilizacion, factura, enca["f_pago"], enca["medio_pago"],
                    None, None, mandato, enca.get("nota_parcial", False),
                )
            # pdb.set_trace()
            resultado = execute_procedure(sql, params)

        except Exception:
            return {"status": 404, "data": None}

        doc = Documentos.objects.get(pk=resultado[0][0])
        # DocumentoService._post_procesar_documento(doc, resultado[0][0], enca, data)
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