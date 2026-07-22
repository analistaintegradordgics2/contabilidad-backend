"""
Service for handling recaudo (payment collection) operations.
"""

from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime

import requests, pdb, math
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
    Service class for handling payment collection operations.
    
    This service handles:
    - Listing payments from external API
    - Parameter management for recaudo configuration
    - Payment accounting and document generation
    - Payment synchronization with external systems
    """
    
    # API endpoints
    API_SINCRONIZACION_URL = "https://pagodgi.webdgi.site/api/restful/sincronizacion/"
    
    # Parameter names for recaudo configuration
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
        Fetch and list payments from external API with afiliado information.
        
        Returns:
            List of payment dictionaries with afiliado data included.
            
        Raises:
            Exception: If API request fails.
        """
        response = requests.get(RecaudoService.API_SINCRONIZACION_URL)
        
        if response.status_code != 200:
            raise Exception(f"Error fetching payments: {response.json()}")
        
        return RecaudoService._enrich_payments_with_afiliado(response.json())
    
    @staticmethod
    def _enrich_payments_with_afiliado(payments: List[Dict]) -> List[Dict[str, Any]]:
        """
        Enrich payment data with afiliado information.
        
        Args:
            payments: List of payment dictionaries from API.
            
        Returns:
            List of payments with afiliado data added.
        """
        result = []
        for item in payments:
            afiliado = Afiliado.objects.filter(cupon__numero=item['ref_1']).first()
            serializer = AfiliadoResumenSerializer(afiliado).data
            item['afiliado'] = serializer
            result.append(item)
        return result
    
    @staticmethod
    def listar_parametros() -> List[Dict[str, Any]]:
        """
        List recaudo parameters with parsed values.
        
        Returns:
            List of parameter dictionaries with parsed values.
        """
        parametros = Parametros.objects.filter(tipo_tab="3").order_by('orden')
        return [
            {
                'id': x.id,
                'parametro': x.parametro,
                'valor': RecaudoService._parse_valor(x.tipo, x.valor)
            }
            for x in parametros
        ]
    
    @staticmethod
    def _parse_valor(tipo: str, valor: str) -> Any:
        """
        Parse parameter value based on its type.
        
        Args:
            tipo: Parameter type (boolean, numeric, or string).
            valor: Parameter value as string.
            
        Returns:
            Parsed value in the appropriate type.
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
        Process payments and create accounting documents.
        
        Args:
            data: List of payment data to process.
            user: User performing the operation.
            
        Returns:
            Created document(s) result.
            
        Raises:
            Exception: If configuration parameters are missing.
        """

        for item in data:
            item['numero_cupon'] = item['ref_1']
            item['fecha_pago'] = item['fecha_transaccion']

        # Get all required parameters
        config = RecaudoService._get_recaudo_config()
        
        # Build payloads for each cupon
        payloads = RecaudoService._build_all_payloads(
            data,
            config
        )
        
        # Create documents based on configuration
        forma_documento = int(config['recaudo_forma_documento'])
        
        if forma_documento == 1:
            return RecaudoService._create_consolidated_document(
                payloads,
                config,
                data,
                user
            )
        else:
            return RecaudoService._create_individual_documents(
                payloads,
                data,
                user
            )
    
    @staticmethod
    def _get_recaudo_config() -> Dict[str, Any]:
        """
        Fetch all required recaudo configuration parameters.
        
        Returns:
            Dictionary with all configuration values.
            
        Raises:
            Exception: If any required parameter is missing.
        """
        config = {}
        missing_params = []
        
        for param_name in RecaudoService.PARAMETROS_RECAUDO.values():
            param = Parametros.objects.filter(parametro=param_name, valor__isnull=False).exclude(valor='').first()
            if param:
                config[param_name] = param.valor
            else:
                missing_params.append(param_name)
        
        if missing_params:
            raise Exception(f"Revisar parametrización de recaudos: faltan {missing_params}")
        
        return config
    
    @staticmethod
    def _build_all_payloads(
        data: List[Dict[str, Any]],
        config: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Build accounting payloads for all cupones.
        
        Args:
            data: List of payment data.
            config: Recaudo configuration dictionary.
            
        Returns:
            List of payload dictionaries.
        """
        ctabanco = CuentaBancaria.objects.get(pk=config['recaudo_ctabanco'])
        conc_sancion = Concepto.objects.filter(pk=config['conc_sancion']).first()
        obj_recaudo_concepto = Concepto.objects.get(pk=config['recaudo_concepto'])
        
        return [
            RecaudoService._build_cupon_payload(
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
    def _build_cupon_payload(
        data: Dict[str, Any],
        conc_sancion: Optional[Concepto],
        recaudo_cta_mora: str,
        recaudo_tipo_documento: str,
        ctabanco: CuentaBancaria,
        recaudo_concepto: Concepto
    ) -> Dict[str, Any]:
        """
        Build accounting payload for a single cupon.
        
        Args:
            data: Payment data for the cupon.
            conc_sancion: Sancion concept (optional).
            recaudo_cta_mora: Cuenta mora parameter.
            recaudo_tipo_documento: Tipo documento parameter.
            ctabanco: Cuenta bancaria instance.
            recaudo_concepto: Recaudo concepto instance.
            
        Returns:
            Payload dictionary for document creation.
            
        Raises:
            Exception: If cupon is not found.
        """
        numero_cupon = data.get('numero_cupon')
        fecha_pago = data.get('fecha_pago')
        valor_pagado = data.get('valor_pagado')
        
        cupon = Cupon.objects.filter(numero=numero_cupon).first()
        if not cupon:
            raise Exception(f"Cupon {numero_cupon} no encontrado")
        
        fecha_recaudo = dateutil_parser.parse(fecha_pago).date().isoformat()
        detalles = DetalleCupones.objects.filter(cupon_id=cupon.id)
        
        # Calculate total and sancion details
        total, detalles_sancion = RecaudoService._calculate_cupon_total(
            cupon,
            fecha_recaudo,
            conc_sancion,
            recaudo_cta_mora
        )
        
        # Build movimientos from detalles
        movimientos = RecaudoService._build_movimientos(
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
    def _calculate_cupon_total(
        cupon: Cupon,
        fecha_recaudo: str,
        conc_sancion: Optional[Concepto],
        recaudo_cta_mora: str
    ) -> tuple:
        """
        Calculate the total amount and sancion details for a cupon.
        
        Args:
            cupon: Cupon instance.
            fecha_recaudo: Payment date in ISO format.
            conc_sancion: Sancion concept (optional).
            recaudo_cta_mora: Cuenta mora parameter.
            
        Returns:
            Tuple of (total, sancion_details_list).
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
    def _build_movimientos(
        detalles: QuerySet,
        cupon: Cupon,
        detalles_sancion: List[Dict]
    ) -> List[Dict[str, Any]]:
        """
        Build movimiento entries from cupon detalles.
        
        Args:
            detalles: QuerySet of DetalleCupones.
            cupon: Cupon instance.
            detalles_sancion: List of sancion detail dictionaries.
            
        Returns:
            List of movimiento dictionaries.
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
    def _create_consolidated_document(
        payloads: List[Dict[str, Any]],
        config: Dict[str, Any],
        data: List[Dict[str, Any]],
        user
    ) -> Any:
        """
        Create a single consolidated document for all cupones.
        
        Args:
            payloads: List of cupon payloads.
            config: Recaudo configuration.
            user: User performing the operation.
            
        Returns:
            Created document result.
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
    def _create_individual_documents(
        payloads: List[Dict[str, Any]],
        data: List[Dict[str, Any]],
        user
    ) -> List[Any]:
        """
        Create individual documents for each cupon.
        
        Args:
            payloads: List of cupon payloads.
            data: Original payment data.
            user: User performing the operation.
            
        Returns:
            List of created document results.
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
        Consolidate multiple cupon payloads into a single document payload.
        
        Args:
            payloads: List of cupon payloads.
            recaudo_concepto: Recaudo concepto instance.
            recaudo_tipo_documento: Tipo documento parameter.
            ctabanco: Cuenta bancaria instance.
            
        Returns:
            Consolidated payload dictionary.
            
        Raises:
            Exception: If no payloads provided.
        """
        if not payloads:
            raise Exception("No hay cupones para contabilizar")
        
        base = payloads[0]
        total =  math.floor(sum(Decimal(str(p['total'])) for p in payloads))
        valor_pagado_total = sum(Decimal(str(p['pagos']['consig']['valor'])) for p in payloads)
        
        movimiento_debito = RecaudoService._create_movimiento_debito(
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
    def _create_movimiento_debito(
        total: float,
        mayor: int,
        concepto: int,
        persona_id: Optional[int] = None,
        detalle: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a debit movement entry.
        
        Args:
            total: Total amount.
            mayor: Mayor account ID.
            concepto: Concept ID.
            persona_id: Optional persona ID.
            detalle: Optional detail text.
            
        Returns:
            Movimiento dictionary.
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
        Synchronize payments with external API.
        
        Args:
            data: List of payment data to synchronize.
            
        Raises:
            Exception: If synchronization fails.
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