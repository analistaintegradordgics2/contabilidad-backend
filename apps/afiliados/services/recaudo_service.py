from apps.afiliados.models.afiliado import Afiliado
from apps.afiliados.serializers.afiliado import AfiliadoResumenSerializer
from apps.parametros.models.parametrizacion import Parametros
from apps.afiliados.models.cupon import Cupon, DetalleCupones
from apps.contabilidad.models.concepto import Concepto
from apps.contabilidad.models.pago import CuentaBancaria
from apps.contabilidad.services.documento_service import DocumentoService

from dateutil import parser as dateutil_parser
from datetime import datetime

import pdb, requests, math

class RecaudoService:
    
    @staticmethod
    def listar():
        url = "https://pagodgi.webdgi.site/api/restful/sincronizacion/"
        response = requests.get(url)

        if response.status_code != 200:
            return response.json()
        
        result = []
        for item in response.json():
            afiliado = Afiliado.objects.filter(cupon__numero=item['ref_1']).first()
            serializer = AfiliadoResumenSerializer(afiliado).data
            item['afiliado'] = serializer

            result.append(item)
    
        return result
    
    @staticmethod
    def listar_parametros():
        return list(map(lambda x: {
            'id': x.id,
            'parametro': x.parametro,
            'valor': RecaudoService.parser_valor(x.tipo, x.valor)
        }, Parametros.objects.filter(tipo_tab="3").order_by('orden')))
    
    @staticmethod
    def parser_valor(tipo, valor):
        if not valor:
            return None
        
        if tipo == 'boolean':
            return valor.lower() == 'true'
        elif tipo == 'numeric':
            return int(valor)
        return valor
    
    @staticmethod
    def contabilizar(data, user):
        param_conc_sancion = Parametros.objects.filter(parametro='conc_sancion').first().valor
        recaudo_cta_mora = Parametros.objects.filter(parametro='recaudo_cta_mora').first().valor
        recaudo_tipo_documento = Parametros.objects.filter(parametro='recaudo_tipo_documento').first().valor
        recaudo_concepto = Parametros.objects.filter(parametro='recaudo_concepto').first().valor
        recaudo_ctabanco = Parametros.objects.filter(parametro='recaudo_ctabanco').first().valor
        recaudo_forma_documento = Parametros.objects.filter(parametro='recaudo_forma_documento').first().valor

        if not param_conc_sancion or not recaudo_cta_mora or not recaudo_tipo_documento or not recaudo_concepto or not recaudo_ctabanco or not recaudo_forma_documento:
            raise Exception("Revisar parametrización de recaudos")

        ctabanco = CuentaBancaria.objects.get(pk=recaudo_ctabanco)
        conc_sancion = Concepto.objects.filter(pk=param_conc_sancion).first()

        obj_recaudo_concepto = Concepto.objects.get(pk=recaudo_concepto)

        # Armamos el payload de cada cupón, sin crear todavía el documento
        payloads = []
        for item in data:
            payload = RecaudoService.armar_contabilizacion(
                item,
                conc_sancion=conc_sancion,
                recaudo_cta_mora=recaudo_cta_mora,
                recaudo_tipo_documento=recaudo_tipo_documento,
                ctabanco=ctabanco,
                recaudo_concepto=obj_recaudo_concepto
            )
            payloads.append(payload)

        recaudo_forma_documento = int(recaudo_forma_documento)

        if recaudo_forma_documento == 1:
            # Un documento para todo: totalizamos y concatenamos movimientos
            documento_payload = RecaudoService._consolidar_payloads(
                payloads,
                recaudo_concepto=obj_recaudo_concepto,
                recaudo_tipo_documento=recaudo_tipo_documento,
                ctabanco=ctabanco
            )
            result = DocumentoService.crear(documento_payload, user.id)

            # sincronizar pagos en wl webservice
            RecaudoService.sincronizar_pagos(data)

            return result
        else:
            # Un documento por cada cupón, sin totalizar nada
            result = [DocumentoService.crear(p, user.id) for p in payloads]

            # sincronizar pagos en wl webservice
            RecaudoService.sincronizar_pagos(data)

            return result

    @staticmethod
    def _consolidar_payloads(payloads, recaudo_concepto, recaudo_tipo_documento, ctabanco):
        if not payloads:
            raise Exception("No hay cupones para contabilizar")

        base = payloads[0]

        total = math.floor(sum(float(p['total']) for p in payloads))
        valor_pagado_total = sum(float(p['pagos']['consig']['valor']) for p in payloads)

        # Movimiento al débito con el total de TODOS los cupones, de primero en la lista
        movimiento_debito = RecaudoService._movimiento_debito(
            total=total,
            mayor=ctabanco.mayor_id,
            concepto=recaudo_concepto.id if recaudo_concepto else None,
            persona_id=None,
            detalle=recaudo_concepto.detalle
        )

        movimientos = [movimiento_debito]
        for p in payloads:
            movimientos.extend(p['movimientos'])

        return {
            'fecha': base['fecha'],
            'tipo_documento': int(recaudo_tipo_documento),
            'concepto': int(recaudo_concepto.id),
            'total': total,
            'detalle': recaudo_concepto.detalle,
            'personas': base['personas'],
            'movimientos': movimientos,
            'pagos': {
                'consig': {
                    **base['pagos']['consig'],
                    'valor': valor_pagado_total,
                }
            }
        }

    @staticmethod
    def armar_contabilizacion(data, conc_sancion, recaudo_cta_mora, recaudo_tipo_documento, ctabanco, recaudo_concepto):
        numero_cupon = data.get('numero_cupon', None)
        fecha_pago = data.get('fecha_pago', None)
        valor_pagado = data.get('valor_pagado', None)

        cupon = Cupon.objects.filter(numero=numero_cupon).first()
        if not cupon:
            raise Exception("Cupon no encontrado")

        detalles_sancion = []
        fecha_recaudo = dateutil_parser.parse(fecha_pago).date().isoformat()
        detalles = DetalleCupones.objects.filter(cupon_id=cupon.id)

        total = 0

        if fecha_recaudo <= datetime.strftime(cupon.fecha1, "%Y-%m-%d"):
            total = cupon.gran_total
        elif fecha_recaudo > datetime.strftime(cupon.fecha1, "%Y-%m-%d") and fecha_recaudo <= datetime.strftime(cupon.fecha2, "%Y-%m-%d"):
            total = cupon.valor2
            valor_diferencia = math.floor(float(cupon.valor2 - cupon.valor1))

            obj = {
                'detalle': conc_sancion.detalle if conc_sancion else None,
                'concepto': conc_sancion.id if conc_sancion else None,
                'valor_cr': valor_diferencia,
                'valor_db': 0,
                'mayor': recaudo_cta_mora,
                'persona_id': cupon.afiliado.persona.id,
            }
            detalles_sancion.append(obj)

        detalle_cupones_list = []
        for det in detalles:
            valor = det.valor if det.valor else 0
            valor = valor + (valor * (det.piva / 100)) if det.piva > 0 else valor
            detalle_cupones_list.append({
                'concepto': det.concepto_id,
                'mayor': det.concepto_causacion.mayor_id,
                'persona_id': cupon.afiliado.persona.id,
                'detalle': det.detalle,
                'valor_db': 0,
                'valor_cr': float(valor),
            })

        for i in detalles_sancion:
            detalle_cupones_list.append(i)

        payload = {
            'fecha': fecha_recaudo,
            'tipo_documento': int(recaudo_tipo_documento),
            'concepto': recaudo_concepto.id if recaudo_concepto else None,
            'total': float(total),
            'detalle': recaudo_concepto.detalle if recaudo_concepto else None,
            'personas': cupon.afiliado.persona.id,
            'movimientos': detalle_cupones_list,
            'pagos': {
                'consig': {
                    'medio_pago': None,
                    'banco': ctabanco.banco.id,
                    'fecha': fecha_recaudo,
                    'cuenta_bancaria': ctabanco.id,
                    'valor': float(valor_pagado),
                    'numero': ctabanco.numero_cuenta
                }
            },
        }

        return payload
    
    @staticmethod
    def _movimiento_debito(total, mayor, concepto, persona_id=None, detalle=None):
        return {
            'concepto': concepto,
            'mayor': mayor,
            'persona_id': persona_id,
            'detalle': detalle,
            'valor_db': float(total),
            'valor_cr': 0,
        }

    @staticmethod
    def sincronizar_pagos(data):
        data = list(map(lambda x: {
            'pago_id': x['pago_id'],
            'sincronizado': True,
        }, data))
        url = "https://pagodgi.webdgi.site/api/restful/sincronizacion/"
        response = requests.post(url, json=data)
        if response.status_code != 200:
            raise Exception(response.json())