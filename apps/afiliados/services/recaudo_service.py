"""
Servicio para manejar operaciones de recaudo (cobro de pagos).
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

import requests
import math
from dateutil import parser as dateutil_parser

from django.db import transaction
from django.db.models import QuerySet

from apps.afiliados.models.afiliado import Afiliado
from apps.afiliados.models.cupon import Cupon, DetalleCupones
from apps.afiliados.serializers.afiliado import AfiliadoResumenSerializer
from apps.contabilidad.models.concepto import Concepto
from apps.contabilidad.models.pago import CuentaBancaria
from apps.contabilidad.services.documento_service import DocumentoService
from apps.parametros.models.parametrizacion import Parametros


class RecaudoService:
    """
    Clase servicio para manejar operaciones de cobro de pagos.
    
    Este servicio se encarga de:
    - Listar pagos desde API externa
    - Gestión de parámetros de configuración de recaudo
    - Contabilización de pagos y generación de documentos
    - Sincronización de pagos con sistemas externos
    """
    
    # URLs de la API
    API_SINCRONIZACION_URL = "https://pagodgi.webdgi.site/api/restful/sincronizacion/"
    
    # Nombres de parámetros para configuración de recaudo
    PARAMETROS_RECAUDO = {
        'conc_sancion': 'conc_sancion',
        'recaudo_cta_mora': 'recaudo_cta_mora',
        'recaudo_tipo_documento': 'recaudo_tipo_documento',
        'recaudo_concepto': 'recaudo_concepto',
        'recaudo_ctabanco': 'recaudo_ctabanco',
        'recaudo_forma_documento': 'recaudo_forma_documento',
    }
    
    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        """
        Obtener y listar pagos desde API externa con información de afiliado.
        
        Returns:
            Lista de diccionarios de pagos con datos de afiliado incluidos.
            
        Raises:
            Exception: Si falla la petición a la API.
        """
        response = requests.get(RecaudoService.API_SINCRONIZACION_URL)
        
        if response.status_code != 200:
            raise Exception(f"Error obteniendo pagos: {response.json()}")
        
        return RecaudoService._enriquecer_pagos_con_afiliado(response.json())
    
    @staticmethod
    def _enriquecer_pagos_con_afiliado(pagos: List[Dict]) -> List[Dict[str, Any]]:
        """
        Enriquecer datos de pago con información de afiliado.
        
        Args:
            pagos: Lista de diccionarios de pagos desde la API.
            
        Returns:
            Lista de pagos con datos de afiliado agregados.
        """
        result = []
        for item in pagos:
            afiliado = Afiliado.objects.filter(cupon__numero=item['ref_1']).first()
            serializer = AfiliadoResumenSerializer(afiliado).data
            item['afiliado'] = serializer
            result.append(item)
        return result
    
    @staticmethod
    def listar_parametros() -> List[Dict[str, Any]]:
        """
        Listar parámetros de recaudo con valores parseados.
        
        Returns:
            Lista de diccionarios de parámetros con valores parseados.
        """
        parametros = Parametros.objects.filter(tipo_tab="3").order_by('orden')
        return [
            {
                'id': x.id,
                'parametro': x.parametro,
                'valor': RecaudoService._parsear_valor(x.tipo, x.valor)
            }
            for x in parametros
        ]
    
    @staticmethod
    def _parsear_valor(tipo: str, valor: str) -> Any:
        """
        Parsear valor de parámetro según su tipo.
        
        Args:
            tipo: Tipo de parámetro (boolean, numeric, o string).
            valor: Valor del parámetro como string.
            
        Returns:
            Valor parseado en el tipo apropiado.
        """
        if not valor:
            return None
            
        if tipo == 'boolean':
            return valor.lower() == 'true'
        elif tipo == 'numeric':
            return int(valor)
        return valor
    
    @staticmethod
    def contabilizar(data: List[Dict[str, Any]], user) -> Any:
        """
        Procesar pagos y crear documentos contables.
        
        Args:
            data: Lista de datos de pagos a procesar.
            user: Usuario que realiza la operación.
            
        Returns:
            Resultado del(los) documento(s) creado(s).
            
        Raises:
            Exception: Si faltan parámetros de configuración.
        """
        # Mapear campos del API a los internos
        for item in data:
            item['numero_cupon'] = item['ref_1']
            item['fecha_pago'] = item['fecha_transaccion']

        # Obtener todos los parámetros requeridos
        config = RecaudoService._obtener_configuracion_recaudo()
        
        # Construir payloads para cada cupón
        payloads = RecaudoService._construir_todos_los_payloads(
            data,
            config
        )
        
        # Crear documentos según configuración
        forma_documento = int(config['recaudo_forma_documento'])
        
        if forma_documento == 1:
            return RecaudoService._crear_documento_consolidado(
                payloads,
                config,
                data,
                user
            )
        else:
            return RecaudoService._crear_documentos_individuales(
                payloads,
                data,
                user
            )
    
    @staticmethod
    def _obtener_configuracion_recaudo() -> Dict[str, Any]:
        """
        Obtener todos los parámetros de configuración de recaudo.
        
        Returns:
            Diccionario con todos los valores de configuración.
            
        Raises:
            Exception: Si falta algún parámetro requerido.
        """
        config = {}
        parametros_faltantes = []
        
        for nombre_parametro in RecaudoService.PARAMETROS_RECAUDO.values():
            parametro = Parametros.objects.filter(parametro=nombre_parametro, valor__isnull=False).exclude(valor='').first()
            if parametro:
                config[nombre_parametro] = parametro.valor
            else:
                parametros_faltantes.append(nombre_parametro)
        
        if parametros_faltantes:
            raise Exception(f"Revisar parametrización de recaudos: faltan {parametros_faltantes}")
        
        return config
    
    @staticmethod
    def _construir_todos_los_payloads(
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Construir payloads contables para todos los cupones.
        
        Args:
            data: Lista de datos de pagos.
            config: Diccionario de configuración de recaudo.
            
        Returns:
            Lista de diccionarios de payloads.
        """
        ctabanco = CuentaBancaria.objects.get(pk=config['recaudo_ctabanco'])
        conc_sancion = Concepto.objects.filter(pk=config['conc_sancion']).first()
        obj_recaudo_concepto = Concepto.objects.get(pk=config['recaudo_concepto'])
        
        return [
            RecaudoService._construir_payload_cupon(
                item,
                conc_sancion=conc_sancion,
                recaudo_cta_mora=config['recaudo_cta_mora'],
                recaudo_tipo_documento=config['recaudo_tipo_documento'],
                ctabanco=ctabanco,
                recaudo_concepto=obj_recaudo_concepto
            )
            for item in data
        ]
    
    @staticmethod
    def _construir_payload_cupon(
        data: Dict[str, Any],
        conc_sancion: Optional[Concepto],
        recaudo_cta_mora: str,
        recaudo_tipo_documento: str,
        ctabanco: CuentaBancaria,
        recaudo_concepto: Concepto
    ) -> Dict[str, Any]:
        """
        Construir payload contable para un cupón individual.
        
        Args:
            data: Datos de pago para el cupón.
            conc_sancion: Concepto de sanción (opcional).
            recaudo_cta_mora: Parámetro de cuenta mora.
            recaudo_tipo_documento: Parámetro de tipo documento.
            ctabanco: Instancia de cuenta bancaria.
            recaudo_concepto: Instancia de concepto de recaudo.
            
        Returns:
            Diccionario de payload para creación de documento.
            
        Raises:
            Exception: Si el cupón no se encuentra.
        """
        numero_cupon = data.get('numero_cupon')
        fecha_pago = data.get('fecha_pago')
        valor_pagado = data.get('valor_pagado')
        
        cupon = Cupon.objects.filter(numero=numero_cupon).first()
        if not cupon:
            raise Exception(f"Cupón {numero_cupon} no encontrado")
        
        fecha_recaudo = dateutil_parser.parse(fecha_pago).date().isoformat()
        detalles = DetalleCupones.objects.filter(cupon_id=cupon.id)
        
        # Calcular total y detalles de sanción
        total, detalles_sancion = RecaudoService._calcular_total_cupon(
            cupon,
            fecha_recaudo,
            conc_sancion,
            recaudo_cta_mora
        )
        
        # Construir movimientos desde detalles
        movimientos = RecaudoService._construir_movimientos(
            detalles,
            cupon,
            detalles_sancion
        )
        
        return {
            'fecha': fecha_recaudo,
            'tipo_documento': int(recaudo_tipo_documento),
            'concepto': recaudo_concepto.id,
            'total': float(total),
            'detalle': recaudo_concepto.detalle,
            'personas': cupon.afiliado.persona.id,
            'movimientos': movimientos,
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
    
    @staticmethod
    def _calcular_total_cupon(
        cupon: Cupon,
        fecha_recaudo: str,
        conc_sancion: Optional[Concepto],
        recaudo_cta_mora: str
    ) -> tuple:
        """
        Calcular el monto total y detalles de sanción para un cupón.
        
        Args:
            cupon: Instancia de Cupón.
            fecha_recaudo: Fecha de pago en formato ISO.
            conc_sancion: Concepto de sanción (opcional).
            recaudo_cta_mora: Parámetro de cuenta mora.
            
        Returns:
            Tupla de (total, lista_detalles_sancion).
        """
        total = 0
        detalles_sancion = []
        
        fecha1_str = datetime.strftime(cupon.fecha1, "%Y-%m-%d")
        fecha2_str = datetime.strftime(cupon.fecha2, "%Y-%m-%d") if cupon.fecha2 else None
        
        if fecha_recaudo <= fecha1_str:
            total = cupon.gran_total
        elif fecha2_str and fecha_recaudo > fecha1_str and fecha_recaudo <= fecha2_str:
            total = cupon.valor2
            valor_diferencia = math.floor(float(cupon.valor2 - cupon.valor1))
            
            if conc_sancion:
                detalles_sancion.append({
                    'detalle': conc_sancion.detalle,
                    'concepto': conc_sancion.id,
                    'valor_cr': float(valor_diferencia),
                    'valor_db': 0,
                    'mayor': recaudo_cta_mora,
                    'persona_id': cupon.afiliado.persona.id,
                })
        
        return total, detalles_sancion
    
    @staticmethod
    def _construir_movimientos(
        detalles: QuerySet,
        cupon: Cupon,
        detalles_sancion: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Construir entradas de movimiento desde detalles de cupón.
        
        Args:
            detalles: QuerySet de DetalleCupones.
            cupon: Instancia de Cupón.
            detalles_sancion: Lista de diccionarios de detalle de sanción.
            
        Returns:
            Lista de diccionarios de movimientos.
        """
        movimientos = []
        
        for det in detalles:
            valor = det.valor if det.valor else 0
            valor = valor + (valor * (det.piva / 100)) if det.piva > 0 else valor
            
            movimientos.append({
                'concepto': det.concepto_id,
                'mayor': det.concepto_causacion.mayor_id,
                'persona_id': cupon.afiliado.persona.id,
                'detalle': det.detalle,
                'valor_db': 0,
                'valor_cr': float(valor),
            })
        
        movimientos.extend(detalles_sancion)
        return movimientos
    
    @staticmethod
    def _crear_documento_consolidado(
        payloads: List[Dict[str, Any]],
        config: Dict[str, Any],
        data: List[Dict[str, Any]],
        user
    ) -> Any:
        """
        Crear un documento consolidado para todos los cupones.
        
        Args:
            payloads: Lista de payloads de cupones.
            config: Configuración de recaudo.
            data: Datos de pagos originales.
            user: Usuario que realiza la operación.
            
        Returns:
            Resultado del documento creado.
        """
        obj_recaudo_concepto = Concepto.objects.get(pk=config['recaudo_concepto'])
        ctabanco = CuentaBancaria.objects.get(pk=config['recaudo_ctabanco'])
        
        documento_payload = RecaudoService._consolidar_payloads(
            payloads,
            recaudo_concepto=obj_recaudo_concepto,
            recaudo_tipo_documento=config['recaudo_tipo_documento'],
            ctabanco=ctabanco
        )
        
        result = DocumentoService.crear(documento_payload, user.id)
        RecaudoService.sincronizar_pagos(data)
        
        return result
    
    @staticmethod
    def _crear_documentos_individuales(
        payloads: List[Dict[str, Any]],
        data: List[Dict[str, Any]],
        user
    ) -> List[Any]:
        """
        Crear documentos individuales para cada cupón.
        
        Args:
            payloads: Lista de payloads de cupones.
            data: Datos de pagos originales.
            user: Usuario que realiza la operación.
            
        Returns:
            Lista de resultados de documentos creados.
        """
        result = [DocumentoService.crear(p, user.id) for p in payloads]
        RecaudoService.sincronizar_pagos(data)
        return result
    
    @staticmethod
    def _consolidar_payloads(
        payloads: List[Dict[str, Any]],
        recaudo_concepto: Concepto,
        recaudo_tipo_documento: str,
        ctabanco: CuentaBancaria
    ) -> Dict[str, Any]:
        """
        Consolidar múltiples payloads de cupones en un solo payload de documento.
        
        Args:
            payloads: Lista de payloads de cupones.
            recaudo_concepto: Instancia de concepto de recaudo.
            recaudo_tipo_documento: Parámetro de tipo documento.
            ctabanco: Instancia de cuenta bancaria.
            
        Returns:
            Diccionario de payload consolidado.
            
        Raises:
            Exception: Si no hay payloads.
        """
        if not payloads:
            raise Exception("No hay cupones para contabilizar")
        
        base = payloads[0]
        total = math.floor(sum(Decimal(str(p['total'])) for p in payloads))
        valor_pagado_total = sum(Decimal(str(p['pagos']['consig']['valor'])) for p in payloads)
        
        movimiento_debito = RecaudoService._crear_movimiento_debito(
            total=float(total),
            mayor=ctabanco.mayor_id,
            concepto=recaudo_concepto.id,
            detalle=recaudo_concepto.detalle
        )
        
        movimientos = [movimiento_debito]
        for p in payloads:
            movimientos.extend(p['movimientos'])
        
        return {
            'fecha': base['fecha'],
            'tipo_documento': int(recaudo_tipo_documento),
            'concepto': recaudo_concepto.id,
            'total': float(total),
            'detalle': recaudo_concepto.detalle,
            'personas': base['personas'],
            'movimientos': movimientos,
            'pagos': {
                'consig': {
                    **base['pagos']['consig'],
                    'valor': float(valor_pagado_total),
                }
            }
        }
    
    @staticmethod
    def _crear_movimiento_debito(
        total: float,
        mayor: int,
        concepto: int,
        persona_id: Optional[int] = None,
        detalle: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Crear entrada de movimiento débito.
        
        Args:
            total: Monto total.
            mayor: ID de cuenta mayor.
            concepto: ID de concepto.
            persona_id: ID de persona (opcional).
            detalle: Texto de detalle (opcional).
            
        Returns:
            Diccionario de movimiento.
        """
        return {
            'concepto': concepto,
            'mayor': mayor,
            'persona_id': persona_id,
            'detalle': detalle,
            'valor_db': float(total),
            'valor_cr': 0,
        }
    
    @staticmethod
    def sincronizar_pagos(data: List[Dict[str, Any]]) -> None:
        """
        Sincronizar pagos con API externa.
        
        Args:
            data: Lista de datos de pagos a sincronizar.
            
        Raises:
            Exception: Si falla la sincronización.
        """
        payload = [
            {
                'pago_id': x['pago_id'],
                'sincronizado': True,
            }
            for x in data
        ]
        
        response = requests.post(RecaudoService.API_SINCRONIZACION_URL, json=payload)
        
        if response.status_code != 200:
            raise Exception(f"Error sincronizando pagos: {response.json()}")