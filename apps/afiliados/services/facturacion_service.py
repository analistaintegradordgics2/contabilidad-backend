# apps/afiliados/services/facturacion_service.py

from apps.afiliados.models import AfiliadoConceptoCausacion
from apps.contabilidad.services.documento_service import DocumentoService
from apps.common_db.db import execute_procedure


class AfiliadoFacturacionService:

    @staticmethod
    def validar_resoluciones(afiliados_ids):
        """
        Verifica que todos los tipos de factura involucrados
        tengan resolución activa y con numeración disponible.

        """
        tipos_factura_ids = list(
            AfiliadoConceptoCausacion.objects
            .filter(
                afiliado_id__in=afiliados_ids,
                concepto__activo=True,
            )
            .values_list('concepto__tipo_factura_id', flat=True)
            .distinct()
        )

        errores = []
        for tipo_id in tipos_factura_ids:
            ok, mensaje = DocumentoService.validar_resolucion(tipo_id)
            if not ok:
                errores.append({
                    'tipo_factura_id': tipo_id,
                    'msg':             mensaje,
                })

        return errores

    @staticmethod
    def facturar_afiliado(afiliado_id, mes, anio, usuario_id):
   
        sql    = "SELECT * FROM facturar_afiliados(%s, %s, %s, %s)"
        params = [afiliado_id, mes, anio, usuario_id]
        return execute_procedure(sql=sql, params=params)

