from django.db import transaction
import json
import logging
from apps.common_db.db import execute_procedure

logger = logging.getLogger(__name__)
from decimal import Decimal
from django.db.models import Sum, Count
import datetime
from apps.contabilidad.models.documento import Documentos, Mov, PagoDocumento, FactElectronicaDocumento, DocumentosBita, Estado
from apps.contabilidad.models.pago import FormaPago
from apps.contabilidad.models.tipodocumento import TiposDocumentos
from apps.utils.querySQL import querySQL
from apps.afiliados.models.causacion import AfiliadoConceptoCausacion
import pdb
from apps.utils.render import Render
from apps.parametros.services.empresa_service import EmpresaService
from apps.contabilidad.models.cuenta import Mayor
from apps.contabilidad.models.concepto import Concepto
from apps.contabilidad.models.parametros import CentroCostos
from apps.personas.models.persona import Persona
from apps.contabilidad.services.documento_cierre_service import DocumentoCierreService
from typing import Dict, Any

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
                }
                for m in movimientos
            ])
            contabilizacion = mov_json

            if fuente != 4:
                
                # ─── Lookup ids de formas de pago por código semántico ───
                fp_ids = {fp.codigo: fp.id for fp in FormaPago.objects.all()}

                # ─── Serializar pagos ───
                pagos_list = []

                if isinstance(pagos, dict) and len(pagos) > 0:
                    tipo_pago = pagos.get('tipo_pago')
                    efectivo = pagos.get('efectivo', {})
                    val_efectivo = float((efectivo or {}).get('valor', 0)) if isinstance(efectivo, dict) else 0

                    # 1. TRANSFERENCIA
                    transferencia = pagos.get('transferencia', {})
                    if isinstance(transferencia, dict):
                        val_transf = float(transferencia.get('valor', 0)) or (val_efectivo if tipo_pago == 3 else 0)
                        if val_transf > 0:
                            pagos_list.append({
                                'tipo': 'transferencia',
                                'forma_pago_id': fp_ids.get('TRANSFERENCIA'),
                                'cuenta_origen_id': transferencia.get('cuenta_origen'),
                                'banco_destino_id': transferencia.get('banco') or transferencia.get('banco_destino'),
                                'cuenta_destino': transferencia.get('cuenta_destino', ''),
                                'referencia': transferencia.get('referencia') or transferencia.get('numero_cheque') or '',
                                'valor': val_transf,
                            })

                    # 2. CHEQUES
                    cheques_list = pagos.get('cheques', [])
                    if isinstance(cheques_list, list) and len(cheques_list) > 0:
                        for cheque in cheques_list:
                            if isinstance(cheque, dict) and float(cheque.get('valor', 0)) > 0:
                                pagos_list.append({
                                    'tipo': 'cheque',
                                    'forma_pago_id': fp_ids.get('CHEQUE'),
                                    'medio_pago_id': cheque.get('medio_pago'),
                                    'banco_id': cheque.get('banco'),
                                    'numero': cheque.get('numero', ''),
                                    'fecha': cheque.get('fecha'),
                                    'valor': float(cheque.get('valor', 0)),
                                })
                    elif tipo_pago == 2:
                        cheque_obj = pagos.get('cheque', {})
                        val_cheque = float((cheque_obj or {}).get('valor', 0)) or val_efectivo
                        if val_cheque > 0:
                            pagos_list.append({
                                'tipo': 'cheque',
                                'forma_pago_id': fp_ids.get('CHEQUE'),
                                'medio_pago_id': cheque_obj.get('medio_pago') if isinstance(cheque_obj, dict) else None,
                                'banco_id': cheque_obj.get('banco') if isinstance(cheque_obj, dict) else None,
                                'numero': cheque_obj.get('numero', '') if isinstance(cheque_obj, dict) else '',
                                'fecha': cheque_obj.get('fecha') if isinstance(cheque_obj, dict) else None,
                                'valor': val_cheque,
                            })

                    # 3. CONSIGNACION
                    consig = pagos.get('consig', {})
                    if isinstance(consig, dict) and float(consig.get('valor', 0)) > 0:
                        pagos_list.append({
                            'tipo': 'consignacion',
                            'forma_pago_id': fp_ids.get('CONSIGNACION'),
                            'medio_pago_id': consig.get('medio_pago'),
                            'banco_id': consig.get('banco'),
                            'cuenta_bancaria_id': consig.get('cuenta_bancaria'),
                            'numero': consig.get('numero', ''),
                            'fecha': consig.get('fecha'),
                            'valor': float(consig.get('valor', 0)),
                        })

                    # 4. TARJETA
                    tarjeta = pagos.get('tarjeta', {})
                    if isinstance(tarjeta, dict) and float(tarjeta.get('valor', 0)) > 0:
                        pagos_list.append({
                            'tipo': 'tarjeta',
                            'forma_pago_id': fp_ids.get('TARJETA'),
                            'medio_pago_id': tarjeta.get('medio_pago'),
                            'banco_id': tarjeta.get('banco'),
                            'cuenta_bancaria_id': tarjeta.get('cuenta_bancaria'),
                            'numero_tarjeta': tarjeta.get('numero_tarjeta', ''),
                            'valor': float(tarjeta.get('valor', 0)),
                        })

                    # 5. EFECTIVO (asume total del documento si no se han agregado otros pagos)
                    total_doc = float(encabezado.get('total', 0) or encabezado.get('gtotal', 0))
                    if val_efectivo <= 0 and len(pagos_list) == 0 and total_doc > 0 and tipo_pago not in [4, 5]:
                        val_efectivo = total_doc

                    if val_efectivo > 0 and tipo_pago not in [4, 5] and len(pagos_list) == 0:
                        pagos_list.append({
                            'tipo': 'efectivo',
                            'forma_pago_id': fp_ids.get('EFECTIVO'),
                            'medio_pago_id': efectivo.get('medio_pago') if isinstance(efectivo, dict) else None,
                            'valor': val_efectivo,
                        })

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
                        %s,%s,%s,%s,%s,%s,
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

                params = (
                    encabezado.get('id') or 0,
                    encabezado.get('tipo_documento'),
                    encabezado.get('fecha'),
                    encabezado.get('fecha_vencimiento'),
                    encabezado.get('personas'),
                    encabezado.get('referencia', ''),
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
            resultado = execute_procedure(sql, params)
            if fuente == 4 and resultado and resultado[0][0]:
                doc_id = resultado[0][0]
                pagos_data = encabezado.get('pagos', [])
                if isinstance(pagos_data, list):
                    for p in pagos_data:
                        if isinstance(p, dict):
                            pago_existente = PagoDocumento.objects.filter(documento_id=doc_id).first()
                            pago = pago_existente or PagoDocumento(documento_id=doc_id)
                            pago.forma_pago_id = encabezado.get('fpago', 3)
                            pago.forma_pago_electro_id = p.get('forma_pago_electro', None)
                            pago.medio_pago_id = p.get('medio_pago', None)
                            pago.save()

        except Exception as e:
            logger.error(f"Error en crear_documento: {str(e)}", exc_info=True)
            return {"status": 404, "data": None, "error": str(e)}

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
    def validar_resolucion(afiliados_id:list):
        # Extraer solo los tipos de factura de los conceptos causacion de los afiliados enviados
        afiliados_conceptos = AfiliadoConceptoCausacion.objects.filter(afiliado_id__in=set(afiliados_id)).values('concepto__tipo_factura').annotate(count=Count('concepto__tipo_factura')).values('concepto__tipo_factura', 'count')

        result = []

        for conc in afiliados_conceptos:
            tipo_fact_id = conc['concepto__tipo_factura']
            count = conc['count']
            validate = querySQL.validar_rango_resolucion(tipo_fact_id, count)

            result.append(validate)

        return result
    
    @staticmethod
    def exportar_excel(data, user):
        data["tipoconsulta"] = 1
        # pdb.set_trace()
        result = querySQL.consulta_de_documentos(data)

        data = []
        for item in result :
            model = {}
            for key, value in item.items() :
                if key != "mov" and key != "enca" :
                    model[key] = value

            data.append(model)

        data.append({
            'tipo': "Total de registros: {}".format(len(data))
        })
        # pdb.set_trace()
        data.append({
            'tipo': "Exportado por: {} {}".format(user.first_name, user.last_name)
        })

        return Render.export_excel(data, 'Documentos contables')
        
        return excel_file
    
    @staticmethod
    def imprimir_documento(filtros:dict):
        result = querySQL.consulta_de_documentos(filtros)
        empresa = EmpresaService.obtener_datos_empresa()

        nombre = "documento"
        params = {
            'data': result,
            'empresa': empresa,
        }
        options = {
            'page-size': 'A4',
            'encoding': 'UTF-8',
            'print-media-type': '',
            'margin-top': '10mm',  
            'margin-bottom': '10mm' 
        }
        return Render.render_pdfkit('pdf/contabilidad/documento.html', params, nombre, options)
    
    @staticmethod
    def exportar_movimiento(request_data):
        data = []
        for item in request_data :
            codigo = ""
            nit = ""
            concepto = ""
            centro_costo = ""

            if item["mayor"] != None :
                cta = Mayor.objects.get(pk=item["mayor"])
                codigo = "{} - {}".format(cta.codigo, cta.nombre)
            
            if item["persona"] != None :
                pers = Persona.objects.get(pk=item["persona"])
                nit = "{} - {}".format(pers.documento, pers.n_completo)
            
            if item["concepto"] != None :
                conc = Concepto.objects.get(pk=item["concepto"])
                concepto = "{} - {}".format(conc.codigo, conc.nombre)
            
            if item["centro_costos"] != None :
                cc = CentroCostos.objects.get(pk=item["centro_costos"])
                centro_costo = "{} - {}".format(cc.codigo, cc.nombre)

            data.append({
                "codigo": codigo,
                "nit": nit,
                "concepto": concepto,
                "detalle": item["detalle"] if item["detalle"] != None else "",
                "debito": item["valor_db"],
                "credito": item["valor_cr"],
                "docref": item["docref"],
                "base": item["base"],
                "centro_costo": centro_costo,
            })
        
        return Render.export_excel(data, "exportar_movimiento", False, True)

    @staticmethod
    def crear_y_cerrar_documento(payload: Dict[str, Any], user_id: int) -> Any:
        """
        Crear y cerrar documento contable.
        
        Args:
            payload: Diccionario de payload de documento.
            user_id: ID de usuario.
            
        Returns:
            Documento creado.
        """
        result = DocumentoService.crear(payload, user_id)

        if result['status'] != 200:
            raise Exception(f"Error creando documento")

        try:
            DocumentoCierreService.cerrar(result['data'][0][1], user_id)
        except Exception as e:
            raise Exception(f"Error cerrando documento: {result['data'][0][2]} - {str(e)}")
    
        return result