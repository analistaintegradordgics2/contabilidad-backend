# apps/contabilidad/serializers/tipodocumento.py

from rest_framework import serializers
from apps.contabilidad.models.tipodocumento import (
    TiposDocumentos,
    FacturacionElectronica,
    ResolucionFacturacion,
    NumeracionMesAnio,
    Fuentes,
    FormaPagoElectro,
    MedioPagoElectro
)


# apps/contabilidad/serializers/tipodocumento.py — agregar

class FacturacionElectronicaSelectSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FacturacionElectronica
        fields = ('id', 'nombre', 'tipo_electronica', 'ambiente', 'estado')


class FuentesSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Fuentes
        fields = ('id', 'nombre')


class FormaPagoElectroSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FormaPagoElectro
        fields = ('id', 'nombre', 'codigo')


class MedioPagoElectroSerializer(serializers.ModelSerializer):
    class Meta:
        model  = MedioPagoElectro
        fields = ('id', 'nombre', 'codigo')

# ─────────────────────────────────────
# FACTURACIÓN ELECTRÓNICA
# ─────────────────────────────────────
class FacturacionElectronicaSerializer(serializers.ModelSerializer):
    class Meta:
        model  = FacturacionElectronica
        fields = ('id', 'nombre', 'proveedor', 'ambiente', 'url',
                  'usuario', 'estado')
        # ✅ password y token nunca se exponen en el serializer


# ─────────────────────────────────────
# RESOLUCIÓN
# ─────────────────────────────────────
class ResolucionFacturacionSerializer(serializers.ModelSerializer):

    vigente = serializers.SerializerMethodField()

    def get_vigente(self, obj):
        from django.utils import timezone
        hoy = timezone.now().date()
        return (
            obj.activa and
            obj.fecha_inicio <= hoy <= obj.fecha_fin and
            obj.consecutivo_actual <= obj.rango_final
        )

    class Meta:
        model  = ResolucionFacturacion
        fields = (
            'id', 'numero_resolucion', 'rango_inicial', 'rango_final',
            'consecutivo_actual', 'fecha_inicio', 'fecha_fin',
            'activa', 'observacion', 'vigente'
        )


# ─────────────────────────────────────
# TIPO DOCUMENTO — LIST (liviano)
# ─────────────────────────────────────
class TiposDocumentosListSerializer(serializers.ModelSerializer):
    """Para listados y selects — sin relaciones pesadas"""

    class Meta:
        model  = TiposDocumentos
        fields = (
            'id', 'tipo', 'nombre', 'fuentes',
            'numero', 'ndigitos', 'prefijo',
            'numeracionxmes', 'dias_vencimiento', 'estado',
            'es_nota', 'es_nota_credito', 'mandato', 'proveedor',
            'forma_pago', 'medio_pago',
            'configuracion_fe',
            'tipo_documento_nota_debito',
            'tipo_documento_nota_credito',
            'tipo_electronica',
        )


# ─────────────────────────────────────
# TIPO DOCUMENTO — DETAIL (completo)
# ─────────────────────────────────────
class TiposDocumentosSerializer(serializers.ModelSerializer):
    """Para crear, editar y ver detalle"""

    tipo_display      = serializers.CharField(source='get_tipo_display', read_only=True)
    configuracion_fe  = FacturacionElectronicaSerializer(read_only=True)
    configuracion_fe_id = serializers.IntegerField(
        write_only=True, allow_null=True, required=False
    )
    resoluciones      = ResolucionFacturacionSerializer(many=True, read_only=True)

    # Booleanos como grupo para el frontend
    atributos = serializers.SerializerMethodField()

    def get_atributos(self, obj):
        return {
            'numeracionxmes':  obj.numeracionxmes,
            'es_nota':         obj.es_nota,
            'es_nota_credito': obj.es_nota_credito,
            'mandato':         obj.mandato,
            'proveedor':       obj.proveedor,
        }

    class Meta:
        model  = TiposDocumentos
        fields = (
            'id', 'nombre', 'tipo', 'tipo_display',
            'fuentes', 'numero', 'ndigitos', 'prefijo',
            'numeracionxmes', 'dias_vencimiento', 'estado',
            'es_nota', 'es_nota_credito', 'mandato', 'proveedor',
            'forma_pago', 'medio_pago',
            'configuracion_fe', 'configuracion_fe_id',
            'tipo_documento_nota_debito',
            'tipo_documento_nota_credito',
            'resoluciones', 'atributos',
            'empresas_id', 'sucursales_id',
        )


# ─────────────────────────────────────
# HISTORIAL
# ─────────────────────────────────────
class TiposDocumentosHistorySerializer(serializers.ModelSerializer):

    history = serializers.SerializerMethodField()

    def get_history(self, obj):
        from apps.utils.history import getHistorymodel
        campos = [
            {'db': 'nombre',           'label': 'Nombre'},
            {'db': 'tipo',             'label': 'Tipo'},
            {'db': 'numero',           'label': 'Número'},
            {'db': 'ndigitos',         'label': 'N° dígitos'},
            {'db': 'prefijo',          'label': 'Prefijo'},
            {'db': 'numeracionxmes',   'label': 'Numeración x mes'},
            {'db': 'dias_vencimiento', 'label': 'Días vencimiento'},
            {'db': 'estado',           'label': 'Estado'},
            {'db': 'es_nota',          'label': 'Es nota'},
            {'db': 'es_nota_credito',  'label': 'Es nota crédito'},
            {'db': 'mandato',          'label': 'Mandato'},
            {'db': 'proveedor',        'label': 'Proveedor'},
            {'db': 'history_date',     'label': 'fecha_bitacora'},
            {'db': 'history_user_id',  'label': 'usuario_bitacora', 'nombre_relacion': 'username'},
        ]
        return getHistorymodel(obj, campos, 'Tipo de Documento')

    class Meta:
        model  = TiposDocumentos
        fields = ('id', 'history')


# ─────────────────────────────────────
# SELECT
# ─────────────────────────────────────
class TiposDocumentosSelectSerializer(serializers.ModelSerializer):

    label = serializers.SerializerMethodField()
    def get_label(self, obj):
        return f"{obj.prefijo or ''} - {obj.nombre}" if obj.prefijo else obj.nombre

    class Meta:
        model  = TiposDocumentos
        fields = ('id', 'nombre', 'tipo', 'prefijo', 'numero', 'label')