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
from apps.contabilidad.services.documento_cierre_service import DocumentoCierreService
from apps.parametros.models.parametrizacion import Parametros


class RecaudoService:
    """
    Clase servicio para manejar operaciones de cobro de pagos.

    Este servicio se encarga de:
    - Listar pagos desde API externa
    - Gestión de parámetros de configuración de recaudo
    - Contabilización de pagos y generación de documentos
    - Sincronización de pagos con sistemas externos

    Los parámetros de configuración de recaudo (PARAMETROS_RECAUDO) se cargan
    una única vez al instanciar la clase y quedan disponibles como atributos
    privados de instancia (self._conc_sancion, self._recaudo_cta_mora, etc.),
    en lugar de pasarse como argumentos entre métodos.
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

    def __init__(self):
        self._cargar_configuracion_recaudo()

    def _cargar_configuracion_recaudo(self) -> None:
        """
        Obtener los parámetros de recaudo y dejarlos listos como atributos
        privados de instancia para ser usados por el resto de los métodos.

        Raises:
            Exception: Si falta algún parámetro requerido.
        """
        config = self._obtener_configuracion_recaudo()

        self._conc_sancion = Concepto.objects.filter(pk=config['conc_sancion']).first()
        self._recaudo_cta_mora = config['recaudo_cta_mora']
        self._recaudo_tipo_documento = config['recaudo_tipo_documento']
        self._recaudo_concepto = Concepto.objects.get(pk=config['recaudo_concepto'])
        self._recaudo_ctabanco = CuentaBancaria.objects.get(pk=config['recaudo_ctabanco'])
        self._recaudo_forma_documento = int(config['recaudo_forma_documento'])

    @staticmethod
    def listar() -> List[Dict[str, Any]]:
        """
        Obtener y listar pagos desde API externa con información de afiliado.

        Returns:
            Lista de diccionarios de pagos con datos de afiliado incluidos.
        """
        try:
            response = requests.get(RecaudoService.API_SINCRONIZACION_URL, timeout=5)

            if response.status_code != 200:
                return []

            return RecaudoService._enriquecer_pagos_con_afiliado(response.json())
        except Exception:
            return []

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

    def contabilizar(self, data: List[Dict[str, Any]], user) -> Any:
        """
        Procesar pagos y crear documentos contables.

        Args:
            data: Lista de datos de pagos a procesar.
            user: Usuario que realiza la operación.

        Returns:
            Resultado del(los) documento(s) creado(s).
        """
        # Mapear campos del API a los internos
        for item in data:
            item['numero_cupon'] = item['ref_1']
            item['fecha_pago'] = item['fecha_transaccion']

        # Construir payloads para cada cupón
        payloads = self._construir_todos_los_payloads(data)

        # Crear documentos según configuración
        if self._recaudo_forma_documento == 1:
            return self._crear_documento_consolidado(payloads, data, user)
        else:
            return self._crear_documentos_individuales(payloads, data, user)

    @staticmethod
    def _obtener_configuracion_recaudo() -> Dict[str, Any]:
        """
        Obtener todos los parámetros de configuración de recaudo.

        Returns:
            Diccionario con todos los valores de configuración (crudos, sin parsear).

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

    def _construir_todos_los_payloads(
        self,
        data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Construir payloads contables para todos los cupones.

        Args:
            data: Lista de datos de pagos.

        Returns:
            Lista de diccionarios de payloads.
        """
        return [self._construir_payload_cupon(item) for item in data]

    def _construir_payload_cupon(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Construir payload contable para un cupón individual.

        Args:
            data: Datos de pago para el cupón.

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
        total, detalles_sancion = self._calcular_total_cupon(cupon, fecha_recaudo)

        # Construir movimientos desde detalles
        movimientos = RecaudoService._construir_movimientos(
            detalles,
            cupon,
            detalles_sancion
        )

        return {
            'fecha': fecha_recaudo,
            'tipo_documento': int(self._recaudo_tipo_documento),
            'concepto': self._recaudo_concepto.id,
            'total': float(total),
            'detalle': self._recaudo_concepto.detalle,
            'personas': cupon.afiliado.persona.id,
            'movimientos': movimientos,
            'pagos': {
                'consig': {
                    'medio_pago': None,
                    'banco': self._recaudo_ctabanco.banco.id,
                    'fecha': fecha_recaudo,
                    'cuenta_bancaria': self._recaudo_ctabanco.id,
                    'valor': float(valor_pagado),
                    'numero': self._recaudo_ctabanco.numero_cuenta
                }
            },
        }

    def _calcular_total_cupon(
        self,
        cupon: Cupon,
        fecha_recaudo: str
    ) -> tuple:
        """
        Calcular el monto total y detalles de sanción para un cupón.

        Args:
            cupon: Instancia de Cupón.
            fecha_recaudo: Fecha de pago en formato ISO.

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

            if self._conc_sancion:
                detalles_sancion.append({
                    'detalle': self._conc_sancion.detalle,
                    'concepto': self._conc_sancion.id,
                    'valor_cr': float(valor_diferencia),
                    'valor_db': 0,
                    'mayor': self._recaudo_cta_mora,
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

    def _crear_documento_consolidado(
        self,
        payloads: List[Dict[str, Any]],
        data: List[Dict[str, Any]],
        user
    ) -> Any:
        """
        Crear un documento consolidado para todos los cupones.

        Args:
            payloads: Lista de payloads de cupones.
            data: Datos de pagos originales.
            user: Usuario que realiza la operación.

        Returns:
            Resultado del documento creado.
        """
        documento_payload = self._consolidar_payloads(payloads)

        result = DocumentoService.crear_y_cerrar_documento(documento_payload, user.id)
        self.sincronizar_pagos(data)

        return result

    def _crear_documentos_individuales(
        self,
        payloads: List[Dict[str, Any]],
        data: List[Dict[str, Any]],
        user
    ) -> List[Any]:
        """
        Crear documentos individuales para cada cupón.

        A cada payload se le antepone su propio movimiento débito, calculado
        sobre su propio total, antes de crear el documento correspondiente.

        Args:
            payloads: Lista de payloads de cupones.
            data: Datos de pagos originales.
            user: Usuario que realiza la operación.

        Returns:
            Lista de resultados de documentos creados.
        """
        for payload in payloads:
            movimiento_debito = self._crear_movimiento_debito(
                total=math.floor(payload['total']),
                mayor=self._recaudo_ctabanco.mayor_id,
                concepto=self._recaudo_concepto.id,
                detalle=self._recaudo_concepto.detalle
            )
            payload['movimientos'] = [movimiento_debito, *payload['movimientos']]

        result = [DocumentoService.crear_y_cerrar_documento(p, user.id) for p in payloads]
        self.sincronizar_pagos(data)
        return result

    def _consolidar_payloads(
        self,
        payloads: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Consolidar múltiples payloads de cupones en un solo payload de documento.

        Args:
            payloads: Lista de payloads de cupones.

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

        movimiento_debito = self._crear_movimiento_debito(
            total=float(total),
            mayor=self._recaudo_ctabanco.mayor_id,
            concepto=self._recaudo_concepto.id,
            detalle=self._recaudo_concepto.detalle
        )

        movimientos = [movimiento_debito]
        for p in payloads:
            movimientos.extend(p['movimientos'])

        return {
            'fecha': base['fecha'],
            'tipo_documento': int(self._recaudo_tipo_documento),
            'concepto': self._recaudo_concepto.id,
            'total': float(total),
            'detalle': self._recaudo_concepto.detalle,
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