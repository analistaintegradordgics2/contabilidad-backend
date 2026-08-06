from decimal import Decimal
import logging
from apps.contabilidad.models.tributario import ReglaTributaria

logger = logging.getLogger(__name__)


class TaxEngineService:
    """
    Motor Tributario Desacoplado: Consulta la parametrización de ReglaTributaria
    en la base de datos para calcular IVA, Retefuente, ReteICA y Neto.
    """

    @staticmethod
    def obtener_reglas_activas(anio: int = 2026) -> dict:
        """
        Obtiene un mapa de reglas activas parametrizadas por el contador.
        """
        reglas = ReglaTributaria.objects.filter(activa=True, vigencia_anio=anio)
        mapa = {}
        for r in reglas:
            mapa[r.tipo_variable] = r
        return mapa

    @staticmethod
    def calcular_liquidacion(
        valor_total: Decimal,
        base_minima_manual: Decimal = None,
        tarifa_manual: Decimal = None,
        anio: int = 2026
    ) -> dict:
        """
        Dada una suma total o valor base, consulta las reglas parametrizadas y liquida las variables tributarias.
        """
        try:
            valor_base = Decimal(str(valor_total or 0)).quantize(Decimal('0.01'))
            reglas = TaxEngineService.obtener_reglas_activas(anio)

            # Regla IVA
            regla_iva = reglas.get('IMPUESTO_IVA')
            tarifa_iva = tarifa_manual if tarifa_manual is not None else (regla_iva.tarifa_porcentaje if regla_iva else Decimal('19.00'))
            subtotal = valor_base
            iva = (subtotal * Decimal(str(tarifa_iva)) / Decimal('100')).quantize(Decimal('0.01'))

            # Regla Retefuente
            regla_rf = reglas.get('RETEFUENTE')
            tarifa_rf = tarifa_manual if tarifa_manual is not None else (regla_rf.tarifa_porcentaje if regla_rf else Decimal('2.50'))
            base_min_rf = base_minima_manual if base_minima_manual is not None else (regla_rf.base_minima if regla_rf else Decimal('0.00'))

            if base_min_rf > Decimal('0.00') and subtotal < base_min_rf:
                retefuente = Decimal('0.00')
            else:
                retefuente = (subtotal * Decimal(str(tarifa_rf)) / Decimal('100')).quantize(Decimal('0.01'))

            # Regla ReteICA y ReteIVA
            regla_ica = reglas.get('RETEICA')
            tarifa_ica = regla_ica.tarifa_porcentaje if regla_ica else Decimal('0.966')
            reteica = (subtotal * Decimal(str(tarifa_ica)) / Decimal('1000')).quantize(Decimal('0.01'))

            regla_riva = reglas.get('RETEIVA')
            tarifa_riva = regla_riva.tarifa_porcentaje if regla_riva else Decimal('15.00')
            reteiva = (iva * Decimal(str(tarifa_riva)) / Decimal('100')).quantize(Decimal('0.01'))

            # Neto a pagar
            neto_pagar = subtotal + iva - retefuente - reteica

            return {
                'valor_total': valor_base,
                'subtotal': subtotal,
                'iva': iva,
                'retefuente': retefuente,
                'reteica': reteica,
                'reteiva': reteiva,
                'neto_pagar': neto_pagar,
                'tarifas_aplicadas': {
                    'iva': float(tarifa_iva),
                    'retefuente': float(tarifa_rf),
                    'reteica': float(tarifa_ica),
                }
            }
        except Exception as e:
            logger.error(f"Error en TaxEngineService.calcular_liquidacion: {str(e)}", exc_info=True)
            return {
                'valor_total': Decimal('0.00'),
                'subtotal': Decimal('0.00'),
                'iva': Decimal('0.00'),
                'retefuente': Decimal('0.00'),
                'reteica': Decimal('0.00'),
                'reteiva': Decimal('0.00'),
                'neto_pagar': Decimal('0.00'),
                'tarifas_aplicadas': {}
            }
