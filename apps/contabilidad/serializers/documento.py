from rest_framework import serializers
from apps.contabilidad.models.documento import Documentos, Mov, PagoDocumento, FactElectronicaDocumento, DocumentosBita
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

class DocumentosBitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentosBita
        fields = '__all__'


class MovSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Mov
        fields = (
            'id', 'mayor', 'persona', 'concepto',
            'detalle', 'valor_db', 'valor_cr',
            'docref', 'base', 'centro_costos', 'nittercero',
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

    class Meta:
        model = Documentos

        fields = (
            'id',
            'numero',
            'fecha',
            'fecha_vencimiento',
            'tipo_documento',
            'concepto',
            'detalle',
            'personas',
            'estado',
            'subtotal',
            'descuento',
            'iva',
            'total',
            'gtotal',
            'movimientos',
            'pagos'
        )

    def get_pagos(self, documento):

        pagos = {
            'efectivo': {},
            'consig': {},
            'tarjeta': {},
            'cheques': [],
        }
        
        for pago in documento.pagos.all():

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

        return pagos