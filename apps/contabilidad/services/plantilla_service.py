from decimal import Decimal
import logging
from django.db import transaction
from django.utils import timezone
from apps.contabilidad.models.plantilla import PlantillaDocumento, PlantillaMovimiento
from apps.contabilidad.services.documento_service import DocumentoService
from apps.contabilidad.services.tax_engine_service import TaxEngineService

logger = logging.getLogger(__name__)


class PlantillaService:
    """
    Servicio de negocio para la parametrización y ejecución de plantillas de comprobantes automáticos.
    """

    @staticmethod
    def _calcular_valor(mov: PlantillaMovimiento, valor_base: Decimal) -> Decimal:
        """
        Calcula el valor numérico de un movimiento a partir de su origen_valor (Motor Tributario o Fórmula).
        """
        try:
            # Evaluación de retenciones automáticas por base mínima
            if mov.base_minima and mov.base_minima > Decimal('0.00'):
                if valor_base < mov.base_minima:
                    return Decimal('0.00')

            # Resolución por Motor Tributario Desacoplado
            if mov.origen_valor and mov.origen_valor not in ['PORCENTAJE_DIRECTO', 'VALOR_FIJO']:
                tarifa_porcentaje = None
                base_minima_regla = None
                if mov.regla_tributaria:
                    tarifa_porcentaje = mov.regla_tributaria.tarifa_porcentaje
                    base_minima_regla = mov.regla_tributaria.base_minima

                liq = TaxEngineService.calcular_liquidacion(
                    valor_total=valor_base,
                    base_minima_manual=base_minima_regla or mov.base_minima,
                    tarifa_manual=tarifa_porcentaje,
                )

                mapping = {
                    'VALOR_TOTAL': liq['valor_total'],
                    'SUBTOTAL': liq['subtotal'],
                    'IMPUESTO_IVA': liq['iva'],
                    'RETEFUENTE': liq['retefuente'],
                    'RETEICA': liq['reteica'],
                    'RETEIVA': liq['reteiva'],
                    'NETO_PAGAR': liq['neto_pagar'],
                }
                return mapping.get(mov.origen_valor, Decimal('0.00'))

            # Modo manual directo (Retrocompatibilidad)
            if mov.tipo_valor == 'fijo' or mov.origen_valor == 'VALOR_FIJO':
                return Decimal(str(mov.valor_fijo or 0)).quantize(Decimal('0.01'))
            else:
                porcentaje = Decimal(str(mov.porcentaje or 0))
                return ((valor_base * porcentaje) / Decimal('100')).quantize(Decimal('0.01'))
        except Exception as e:
            logger.error(f"Error calculando valor en movimiento plantilla: {str(e)}", exc_info=True)
        return Decimal('0.00')

    @staticmethod
    def _calcular_base_desde_total(plantilla: PlantillaDocumento, valor_total: Decimal) -> Decimal:
        """
        Deduce la base gravable descontando el IVA cuando el auxiliar ingresa el Total Factura.
        """
        try:
            tarifa_iva = Decimal('19.00')
            for mov in plantilla.movimientos.all():
                if mov.origen_valor == 'IMPUESTO_IVA':
                    if mov.regla_tributaria and mov.regla_tributaria.tarifa_porcentaje:
                        tarifa_iva = mov.regla_tributaria.tarifa_porcentaje
                    break

            factor = Decimal('1.00') + (Decimal(str(tarifa_iva)) / Decimal('100'))
            if factor > Decimal('0.00'):
                return (valor_total / factor).quantize(Decimal('0.01'))
        except Exception as e:
            logger.error(f"Error deduciendo base desde total: {str(e)}", exc_info=True)
        return valor_total

    @staticmethod
    def _calcular_valores_movimientos(movimientos_list, valor_base: Decimal) -> list:
        """
        Calcula el valor numérico de cada movimiento de la plantilla.
        Para líneas con origen_valor == 'NETO_PAGAR', calcula la contrapartida exacta para garantizar partida doble.
        """
        movs_activos = []
        for mov in movimientos_list:
            if mov.base_minima and mov.base_minima > Decimal('0.00') and valor_base < mov.base_minima:
                continue
            movs_activos.append(mov)

        valores_por_idx = {}
        total_db = Decimal('0.00')
        total_cr = Decimal('0.00')
        neto_indices = []

        # Paso 1: Calcular líneas base
        for idx, mov in enumerate(movs_activos):
            if mov.origen_valor == 'NETO_PAGAR':
                neto_indices.append(idx)
            else:
                val = PlantillaService._calcular_valor(mov, valor_base)
                valores_por_idx[idx] = val
                if mov.naturaleza == 'debito':
                    total_db += val
                else:
                    total_cr += val

        # Paso 2: Resolver contrapartidas de NETO_PAGAR como saldo de cuadre
        for idx in neto_indices:
            mov = movs_activos[idx]
            if mov.naturaleza == 'credito':
                diferencia = total_db - total_cr
            else:
                diferencia = total_cr - total_db

            if diferencia > Decimal('0.00'):
                val = diferencia.quantize(Decimal('0.01'))
            else:
                val = PlantillaService._calcular_valor(mov, valor_base)

            valores_por_idx[idx] = val
            if mov.naturaleza == 'debito':
                total_db += val
            else:
                total_cr += val

        return [(mov, valores_por_idx[idx]) for idx, mov in enumerate(movs_activos)]

    @staticmethod
    def preview(plantilla_id: int, valor: float, modo_valor: str = 'BASE') -> list:
        """
        Genera la simulación de débitos y créditos antes de realizar la contabilización.
        """
        try:
            plantilla = PlantillaDocumento.objects.prefetch_related(
                'movimientos__mayor',
                'movimientos__concepto',
                'movimientos__regla_tributaria'
            ).get(pk=plantilla_id, activa=True)

            try:
                valor_float = float(valor) if valor is not None else 0.0
            except (ValueError, TypeError):
                valor_float = 0.0

            raw_valor = Decimal(str(valor_float))
            if modo_valor == 'TOTAL':
                valor_base = PlantillaService._calcular_base_desde_total(plantilla, raw_valor)
            else:
                valor_base = raw_valor

            movimientos_calculados = PlantillaService._calcular_valores_movimientos(
                plantilla.movimientos.all(), valor_base
            )

            resultado = []
            for mov, valor_mov in movimientos_calculados:
                resultado.append({
                    'mayor_id': mov.mayor_id,
                    'mayor_codigo': mov.mayor.codigo if mov.mayor else '',
                    'mayor_nombre': mov.mayor.nombre if mov.mayor else '',
                    'concepto_id': mov.concepto_id,
                    'concepto_nombre': mov.concepto.nombre if mov.concepto else '',
                    'naturaleza': mov.naturaleza,
                    'origen_valor': mov.origen_valor,
                    'usa_tercero': mov.usa_tercero,
                    'base_calculada': float(valor_base),
                    'valor_db': float(valor_mov) if mov.naturaleza == 'debito' else 0.0,
                    'valor_cr': float(valor_mov) if mov.naturaleza == 'credito' else 0.0,
                    'detalle': mov.detalle_default or plantilla.nombre,
                })

            return resultado

        except PlantillaDocumento.DoesNotExist:
            logger.warning(f"Plantilla ID {plantilla_id} no encontrada o inactiva.")
            raise ValueError(f"La plantilla solicitada (ID: {plantilla_id}) no existe o se encuentra inactiva.")
        except Exception as e:
            logger.error(f"Error generando vista previa de plantilla {plantilla_id}: {str(e)}", exc_info=True)
            raise Exception("Ocurrió un error al calcular la vista previa del comprobante.")

    @staticmethod
    @transaction.atomic
    def ejecutar(plantilla_id: int, datos: dict, usuario_id: int) -> dict:
        """
        Ejecuta la contabilización automática a partir de la plantilla seleccionada por el auxiliar.
        """
        try:
            plantilla = PlantillaDocumento.objects.prefetch_related(
                'movimientos__mayor',
                'movimientos__concepto',
                'movimientos__regla_tributaria'
            ).get(pk=plantilla_id, activa=True)

            raw_valor = Decimal(str(datos.get('valor', 0)))
            modo_valor = datos.get('modo_valor', 'BASE')

            if modo_valor == 'TOTAL':
                valor_base = PlantillaService._calcular_base_desde_total(plantilla, raw_valor)
            else:
                valor_base = raw_valor

            persona_id = datos.get('persona')
            fecha = datos.get('fecha')
            referencia = datos.get('referencia', '')
            detalle_general = datos.get('detalle') or plantilla.nombre

            raw_cc = datos.get('centro_costos')
            centro_costos_id = None
            if raw_cc:
                if isinstance(raw_cc, dict):
                    centro_costos_id = raw_cc.get('id') or raw_cc.get('value')
                else:
                    try:
                        centro_costos_id = int(raw_cc)
                    except (ValueError, TypeError):
                        centro_costos_id = None

            if plantilla.requiere_tercero and not persona_id:
                raise ValueError("Debe seleccionar un tercero para ejecutar esta plantilla.")

            if plantilla.requiere_valor and valor_base <= 0:
                raise ValueError("Debe ingresar un valor mayor a cero para contabilizar.")

            movimientos_calculados = PlantillaService._calcular_valores_movimientos(
                plantilla.movimientos.all(), valor_base
            )

            movimientos_payload = []
            total_debito = Decimal('0.00')
            total_credito = Decimal('0.00')

            for mov, valor_mov in movimientos_calculados:
                valor_db = float(valor_mov) if mov.naturaleza == 'debito' else 0.0
                valor_cr = float(valor_mov) if mov.naturaleza == 'credito' else 0.0

                if mov.naturaleza == 'debito':
                    total_debito += valor_mov
                else:
                    total_credito += valor_mov

                movimientos_payload.append({
                    'id': 0,
                    'mayor': mov.mayor_id,
                    'persona': persona_id if mov.usa_tercero else None,
                    'concepto': mov.concepto_id,
                    'detalle': mov.detalle_default or detalle_general,
                    'valor_db': valor_db,
                    'valor_cr': valor_cr,
                    'base': float(valor_base) if mov.origen_valor in ['IMPUESTO_IVA', 'RETEFUENTE', 'RETEICA', 'RETEIVA'] else 0.0,
                    'docref': referencia,
                    'centro_costos': centro_costos_id,
                })

            encabezado_payload = {
                'id': 0,
                'tipo_documento': plantilla.tipo_documento_id,
                'concepto': plantilla.concepto_id,
                'detalle': detalle_general,
                'referencia': referencia,
                'personas': persona_id,
                'fecha': fecha,
                'total': float(valor_base),
                'usuario': usuario_id,
                'automatico': True,
                'movimientos': movimientos_payload,
                'pagos': [],
            }

            resultado = DocumentoService.crear(encabezado_payload, usuario_id)

            plantilla.contador_usos += 1
            plantilla.ultima_fecha_uso = timezone.now()
            plantilla.save(update_fields=['contador_usos', 'ultima_fecha_uso'])

            return resultado

        except PlantillaDocumento.DoesNotExist:
            logger.warning(f"Intento de ejecución en plantilla inactiva/inexistente ID {plantilla_id}")
            raise ValueError("La plantilla seleccionada no existe o se encuentra inactiva.")
        except ValueError as ve:
            logger.warning(f"Validación fallida en ejecución de plantilla {plantilla_id}: {str(ve)}")
            raise ve
        except Exception as e:
            logger.error(f"Error inesperado al ejecutar plantilla {plantilla_id}: {str(e)}", exc_info=True)
            raise Exception("No fue posible generar el documento contable a partir de la plantilla.")

    @staticmethod
    @transaction.atomic
    def guardar_plantilla(data: dict) -> PlantillaDocumento:
        """
        Crea o actualiza una plantilla y sus líneas asociadas (Rol Contador).
        """
        def _extract_id(val):
            if val is None:
                return None
            if isinstance(val, dict):
                return val.get('id') or val.get('value')
            try:
                return int(val)
            except (ValueError, TypeError):
                return val

        def _extract_str(val, default=''):
            if isinstance(val, dict):
                return str(val.get('value') or val.get('id') or default)
            return str(val or default)

        try:
            plantilla_id = data.get('id')
            movimientos_data = data.get('movimientos', [])

            fuente_id = _extract_id(data.get('fuente'))
            tipo_doc_id = _extract_id(data.get('tipo_documento'))
            conc_id = _extract_id(data.get('concepto'))

            if not tipo_doc_id:
                raise ValueError("El tipo de documento es obligatorio.")
            if not conc_id:
                raise ValueError("El concepto principal es obligatorio.")

            if plantilla_id:
                plantilla = PlantillaDocumento.objects.get(pk=plantilla_id)
                plantilla.nombre = data.get('nombre', plantilla.nombre)
                plantilla.descripcion = data.get('descripcion', plantilla.descripcion)
                plantilla.fuente_id = fuente_id
                plantilla.tipo_documento_id = tipo_doc_id
                plantilla.concepto_id = conc_id
                plantilla.activa = data.get('activa', plantilla.activa)
                plantilla.icono = data.get('icono', plantilla.icono)
                plantilla.color = data.get('color', plantilla.color)
                plantilla.requiere_tercero = data.get('requiere_tercero', plantilla.requiere_tercero)
                plantilla.requiere_valor = data.get('requiere_valor', plantilla.requiere_valor)
                plantilla.save()
            else:
                plantilla = PlantillaDocumento.objects.create(
                    nombre=data['nombre'],
                    descripcion=data.get('descripcion', ''),
                    fuente_id=fuente_id,
                    tipo_documento_id=tipo_doc_id,
                    concepto_id=conc_id,
                    activa=data.get('activa', True),
                    icono=data.get('icono', 'assignment'),
                    color=data.get('color', 'primary'),
                    requiere_tercero=data.get('requiere_tercero', True),
                    requiere_valor=data.get('requiere_valor', True),
                )

            # Reemplazar movimientos
            if 'movimientos' in data:
                PlantillaMovimiento.objects.filter(plantilla=plantilla).delete()
                for idx, mov in enumerate(movimientos_data):
                    m_mayor_id = _extract_id(mov.get('mayor'))
                    m_conc_id = _extract_id(mov.get('concepto')) or conc_id
                    m_regla_id = _extract_id(mov.get('regla_tributaria'))
                    m_nat = _extract_str(mov.get('naturaleza'), 'debito')
                    m_tipo_val = _extract_str(mov.get('tipo_valor'), 'porcentaje')
                    m_origen_val = _extract_str(mov.get('origen_valor'), 'PORCENTAJE_DIRECTO')

                    if not m_mayor_id:
                        raise ValueError(f"La línea {idx + 1} no tiene una cuenta mayor válida.")

                    PlantillaMovimiento.objects.create(
                        plantilla=plantilla,
                        mayor_id=m_mayor_id,
                        concepto_id=m_conc_id,
                        regla_tributaria_id=m_regla_id,
                        naturaleza=m_nat,
                        tipo_valor=m_tipo_val,
                        origen_valor=m_origen_val,
                        valor_fijo=mov.get('valor_fijo'),
                        porcentaje=mov.get('porcentaje'),
                        base_minima=mov.get('base_minima', 0),
                        usa_tercero=mov.get('usa_tercero', True),
                        detalle_default=mov.get('detalle_default', ''),
                        orden=idx + 1
                    )

            return plantilla

        except Exception as e:
            logger.error(f"Error al guardar plantilla contable: {str(e)}", exc_info=True)
            raise Exception(f"Error al procesar la plantilla: {str(e)}")

    @staticmethod
    @transaction.atomic
    def duplicar_plantilla(plantilla_id: int) -> PlantillaDocumento:
        """
        Duplica una plantilla existente y todas sus líneas de asiento asociadas.
        """
        try:
            original = PlantillaDocumento.objects.prefetch_related('movimientos').get(pk=plantilla_id)
            nueva = PlantillaDocumento.objects.create(
                nombre=f"{original.nombre} (Copia)",
                descripcion=original.descripcion,
                fuente_id=original.fuente_id,
                tipo_documento_id=original.tipo_documento_id,
                concepto_id=original.concepto_id,
                activa=True,
                icono=original.icono,
                color=original.color,
                requiere_tercero=original.requiere_tercero,
                requiere_valor=original.requiere_valor,
            )

            for mov in original.movimientos.all():
                PlantillaMovimiento.objects.create(
                    plantilla=nueva,
                    mayor_id=mov.mayor_id,
                    concepto_id=mov.concepto_id,
                    regla_tributaria_id=mov.regla_tributaria_id,
                    naturaleza=mov.naturaleza,
                    tipo_valor=mov.tipo_valor,
                    origen_valor=mov.origen_valor,
                    valor_fijo=mov.valor_fijo,
                    porcentaje=mov.porcentaje,
                    base_minima=mov.base_minima,
                    usa_tercero=mov.usa_tercero,
                    detalle_default=mov.detalle_default,
                    orden=mov.orden
                )
            return nueva
        except Exception as e:
            logger.error(f"Error al duplicar plantilla {plantilla_id}: {str(e)}", exc_info=True)
            raise Exception(f"No fue posible duplicar la plantilla: {str(e)}")
