# apps/contabilidad/services/tipodocumento_service.py

from apps.contabilidad.models.tipodocumento import TiposDocumentos, ResolucionFacturacion, FacturacionElectronica
from apps.contabilidad.serializers.tipodocumento import TiposDocumentosSerializer


class TipoDocumentoService:

    @staticmethod
    def crear_o_actualizar(data, tipo_id=None):

        datos_fe = {
            'usuario':  data.pop('fact_elec_user', None),
            'password': data.pop('fact_elec_pass', None),
            'url':      data.pop('fact_elec_url',  None),
        }

        datos_resolucion = {
            'numero_resolucion': data.pop('numero_resolucion',      None),
            'rango_inicial':     data.pop('numeracion_inicial',     None),
            'rango_final':       data.pop('numeracion_final',       None),
            'fecha_inicio':      data.pop('fecha_ini_resolucion',   None),
            'fecha_fin':         data.pop('fecha_fin_resolucion',   None),
            'observacion':       data.pop('observacion_resolucion', None),
        }

        if tipo_id:
            instancia  = TiposDocumentos.objects.get(pk=tipo_id)
            serializer = TiposDocumentosSerializer(instancia, data=data)
        else:
            serializer = TiposDocumentosSerializer(data=data)

        serializer.is_valid(raise_exception=True)
        tipo_doc =  serializer.save()

        es_factura     = tipo_doc.fuentes_id == 4
        tiene_datos_fe = any(v for v in datos_fe.values() if v)

        if es_factura and tiene_datos_fe:
            TipoDocumentoService._guardar_configuracion_fe(tipo_doc, datos_fe)

        if es_factura:
            TipoDocumentoService._guardar_resolucion(
                tipo_doc, datos_resolucion, tipo_id
            )

        return tipo_doc

    @staticmethod
    def puede_eliminar(tipo_id):
        """Valida que no tenga documentos asociados antes de eliminar"""
        from apps.contabilidad.models.documento import Documentos
        tiene_documentos = Documentos.objects.filter(
            tipo_documento_id=tipo_id
        ).exists()

        if tiene_documentos:
            return False, 'No se puede eliminar, tiene documentos asociados'

        return True, None
    
    @staticmethod
    def _guardar_configuracion_fe(tipo_doc, datos_fe):
        if tipo_doc.configuracion_fe:
            # ─── Actualizar existente ───
            fe          = tipo_doc.configuracion_fe
            fe.usuario  = datos_fe.get('usuario') or fe.usuario
            fe.password = datos_fe.get('password') or fe.password
            fe.url      = datos_fe.get('url') or fe.url
            fe.save(update_fields=['usuario', 'password', 'url'])
        else:
            # ─── Crear nueva y relacionar ───
            fe = FacturacionElectronica.objects.create(
                nombre   = tipo_doc.nombre,
                usuario  = datos_fe.get('usuario'),
                password = datos_fe.get('password'),
                url      = datos_fe.get('url'),
                estado   = True
            )
            tipo_doc.configuracion_fe = fe
            tipo_doc.save(update_fields=['configuracion_fe'])
    
    # Resolucion
    @staticmethod
    def _guardar_resolucion(tipo_doc, datos, tipo_id):
        rango_inicial = datos.get('rango_inicial')
        rango_final   = datos.get('rango_final')

        # Sin datos mínimos no guardamos
        if not rango_inicial or not rango_final:
            return

        # Validar fechas
        fecha_inicio = datos.get('fecha_inicio')
        fecha_fin    = datos.get('fecha_fin')

        if fecha_inicio and fecha_fin and fecha_inicio >= fecha_fin:
            raise ValueError('Fecha fin debe ser mayor a fecha inicio')

        if tipo_id:
            # ─── Edición — actualizar resolución activa ───
            resolucion = ResolucionFacturacion.objects.filter(
                tipo_documento=tipo_doc,
                activa=True
            ).first()

            if resolucion:
                resolucion.numero_resolucion = datos.get('numero_resolucion') or resolucion.numero_resolucion
                resolucion.rango_inicial     = int(rango_inicial)
                resolucion.rango_final       = int(rango_final)
                resolucion.fecha_inicio      = fecha_inicio or resolucion.fecha_inicio
                resolucion.fecha_fin         = fecha_fin    or resolucion.fecha_fin
                resolucion.observacion       = datos.get('observacion') or resolucion.observacion
                resolucion.save()
            else:
                TipoDocumentoService._crear_resolucion(tipo_doc, datos)
        else:
            # ─── Creación ───
            TipoDocumentoService._crear_resolucion(tipo_doc, datos)

    @staticmethod
    def _crear_resolucion(tipo_doc, datos):
        ResolucionFacturacion.objects.create(
            tipo_documento     = tipo_doc,
            numero_resolucion  = datos.get('numero_resolucion', ''),
            rango_inicial      = int(datos.get('rango_inicial', 0)),
            rango_final        = int(datos.get('rango_final',   0)),
            fecha_inicio       = datos.get('fecha_inicio'),
            fecha_fin          = datos.get('fecha_fin'),
            observacion        = datos.get('observacion'),
            consecutivo_actual = 0,
            activa             = True
        )
