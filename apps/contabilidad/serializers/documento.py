from rest_framework import serializers
from apps.contabilidad.models.documento import Documentos, Mov, DetalleFacturas, PagoDocumento, FactElectronicaDocumento, DocumentosBita
from apps.contabilidad.serializers.tipodocumento import TiposDocumentosListSerializer
import pdb

class MovSerializer(serializers.ModelSerializer):
    class Meta:
        model = Mov
        fields = '__all__'


class PagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PagoDocumento
        fields = '__all__'


class FactElectronicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FactElectronicaDocumento
        fields = '__all__'


class DocumentoSerializer(serializers.ModelSerializer):

    movimientos = MovSerializer(many=True, write_only=True)
    pagos = PagoSerializer(many=True, required=False)
    facturacion = FactElectronicaSerializer(required=False)

    class Meta:
        model = Documentos
        fields = '__all__'

    def create(self, validated_data):
        raise NotImplementedError("Usar DocumentoService")

class DocumentoBitacoraSerializer(serializers.ModelSerializer):

    usuario = serializers.CharField(
        source='usuario.username',
        read_only=True
    )

    estado = serializers.CharField(
        source='estado.nombre',
        read_only=True
    )

    class Meta:
        model = DocumentosBita

        fields = (
            'id',
            'fecha',
            'evento',
            'usuario',
            'estado'
        )

class MovSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Mov
        fields = (
            'id', 'mayor', 'persona', 'concepto',
            'detalle', 'valor_db', 'valor_cr',
            'docref', 'base', 'centro_costos', 'nittercero',
        )

class FacturaDetalleSerializer(serializers.ModelSerializer):

    class Meta:
        model = DetalleFacturas
        fields = (
            'id',
            'concepto',
            'cantidad',
            'detalle',
            'piva',
            'valor'
        )

class DocumentoCreateSerializer(serializers.ModelSerializer):
    movimientos = MovSerializer(
        many=True,
        source='mov_documentos',  # related_name del FK
        required=False
    )

    class Meta:
        model  = Documentos
        fields = (
            'id', 'numero', 'fecha',
            'tipo_documento', 'concepto', 'detalle',
            'personas', 'estado',
            'gtotal',
            'movimientos',
        )
class DocumentoDetailSerializer(serializers.ModelSerializer):

    movimientos = MovSerializer(
        source='mov_documentos',
        many=True,
        read_only=True
    )
    pagos = serializers.SerializerMethodField()
    items = FacturaDetalleSerializer(
        source='detalle_facturas',
        many=True,
        read_only=True
    )

    correo = serializers.SerializerMethodField()
    def get_correo(self, obj):
        correo = obj.personas.email if obj.personas_id != None else "" 
        return correo 
    
    tipo_documento_persona = serializers.SerializerMethodField()
    def get_tipo_documento_persona(self, obj):
        tipo_documento_persona = obj.personas.tipo_documento.nombre if obj.personas_id != None else "" 
        return tipo_documento_persona 
    
    obj_tipodocumento = serializers.SerializerMethodField()
    def get_obj_tipodocumento(self, obj):
        if obj.tipo_documento_id:
            return TiposDocumentosListSerializer(obj.tipo_documento).data
        return None 
    class Meta:
        model = Documentos

        fields = (
            'id',
            'numero',
            'referencia',
            'fecha',
            'fecha_vencimiento',
            'tipo_documento',
            'concepto',
            'detalle',
            'personas',
            'direccion',
            'correo',
            'telefono',
            'ciudad',
            'tipo_documento_persona',
            'estado',
            'subtotal',
            'descuento',
            'iva',
            'total',
            'gtotal',
            'movimientos',
            'pagos',
            'items',
            'obj_tipodocumento'
        )

    def get_pagos(self, documento):

        pagos = {
            'tipo_pago': None,
            'efectivo': {},
            'consig': {},
            'tarjeta': {},
            'cheques': [],
            'transferencia': {
                'cuenta_origen': None,
                'cuenta_destino': '',
                'banco_destino': None,
                'valor': 0
            },
        }
        
        for pago in documento.pagos.all():
            pagos['tipo_pago'] = pago.forma_pago_id
            
            base = {
                'id': pago.id,
                'forma_pago': pago.forma_pago_id,
                'medio_pago': pago.medio_pago_id,
            }

            try:
                d = pago.detalle_efectivo
                pagos['efectivo'] = {
                    **base,
                    'valor': float(d.valor)
                }
                continue
            except:
                pass

            try:
                d = pago.detalle_cheque
                pagos['cheques'].append({
                    **base,
                    'banco': d.banco_id,
                    'numero': d.numero,
                    'fecha': d.fecha,
                    'valor': float(d.valor)
                })
                continue
            except:
                pass

            try:
                d = pago.detalle_consignacion
                pagos['consig'] = {
                    **base,
                    'banco': d.banco_id,
                    'cuenta_bancaria': d.cuenta_bancaria_id,
                    'numero': d.numero,
                    'fecha': d.fecha,
                    'valor': float(d.valor)
                }
                continue
            except:
                pass

            try:
                d = pago.detalle_tarjeta
                pagos['tarjeta'] = {
                    **base,
                    'banco': d.banco_id,
                    'cuenta_bancaria': d.cuenta_bancaria_id,
                    'numero_tarjeta': d.numero_tarjeta,
                    'valor': float(d.valor)
                }
            except:
                pass

            try:
                d = pago.detalle_transferencia
                pagos['transferencia'] = {
                    **base,
                    'banco_destino': d.banco_destino_id,
                    'cuenta_destino': d.cuenta_destino,
                    'cuenta_origen': d.cuenta_origen_id,
                    'numero_cheque': d.numero_chque,
                    'valor': float(d.valor)
                }
            except:
                pass

        return pagos

class DocumentoListSerializer(serializers.ModelSerializer):

    persona_nombre = serializers.CharField(
        source='personas.n_completo',
        read_only=True
    )
    persona_documento = serializers.CharField(
        source='personas.documento',
        read_only=True
    )

    class Meta:
        model = Documentos

        fields = (
            'id',
            'numero',
            'fecha',
            'persona_nombre',
            'persona_documento',
            'detalle',
            'total',
            'estado'
        )