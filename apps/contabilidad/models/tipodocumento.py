from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel
from apps.contabilidad.models.parametros import *
from apps.contabilidad.models.pago import *

class FacturacionElectronica(BaseModel):

    nombre = models.CharField(max_length=150)

    proveedor = models.CharField(
        max_length=50,
        choices=(
            ('FELIX', 'Felix'),
            ('BPM', 'Bpm')
        )
    )

    ambiente = models.CharField(
        max_length=20,
        choices=(
            ('PRUEBA', 'Pruebas'),
            ('PRODUCCION', 'Producción')
        ),
        default='PRUEBA'
    )

    url = models.TextField()

    usuario = models.TextField()

    password = models.TextField()

    token = models.TextField(
        blank=True,
        null=True
    )

    estado = models.BooleanField(default=True)

class TiposDocumentos(BaseModel):
    history = HistoricalRecords()
    fuentes             = models.ForeignKey(Fuentes, blank=True, null=True, on_delete=models.CASCADE)
    nombre              = models.CharField(max_length=255, blank=True, null=True)
    tipo                = models.CharField(max_length=10, blank=True, null=True)
    numero              = models.IntegerField(blank=True, null=True)
    ndigitos            = models.IntegerField(blank=True, null=True)
    prefijo             = models.CharField(max_length=5, blank=True, null=True)
    numeracionxmes      = models.BooleanField(default=False, blank=True, null=True)
    empresas_id         = models.IntegerField(blank=True, null=True)
    dias_vencimiento    = models.IntegerField(blank=True, null=True)
    estado              = models.BooleanField(default=True)
    sucursales_id       = models.IntegerField(blank=True, null=True)
    tipo_electronica    = models.IntegerField(blank=True, null=True)
    es_nota             = models.BooleanField(default=False)
    forma_pago          = models.ForeignKey(FormaPagoElectro, blank=True, null=True, on_delete=models.CASCADE)
    medio_pago          = models.ForeignKey(MedioPagoElectro, blank=True, null=True, on_delete=models.CASCADE)
    es_nota_credito     = models.BooleanField(default=False)
    mandato             = models.BooleanField(default=False, help_text="Identificar la factura es de tipo mandato")
    configuracion_fe = models.ForeignKey(
        FacturacionElectronica,
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )
    tipo_documento_nota_debito = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='documento_nota_debito',
        on_delete=models.SET_NULL
    )
    tipo_documento_nota_credito = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='documento_nota_credito',
        on_delete=models.SET_NULL
    )
    proveedor = models.BooleanField(default=False, blank=True, null=True, help_text="Identificar la factura es de tipo proveedor")

    def __str__(self):
        try:
            return self.nombre
        except:
            return ''

    class Meta:
        db_table = 'contabilidad_tipos_documentos' 

class NumeracionMesAnio(models.Model):
    tipo_documento = models.ForeignKey(TiposDocumentos, on_delete=models.CASCADE, related_name="numeracionmesanio_tipo_documento")
    anio = models.ForeignKey('parametros.Anio', on_delete=models.CASCADE, related_name="numeracionmesanio_anio")
    numerom01 = models.IntegerField(default=1)
    numerom02 = models.IntegerField(default=1)
    numerom03 = models.IntegerField(default=1)
    numerom04 = models.IntegerField(default=1)
    numerom05 = models.IntegerField(default=1)
    numerom06 = models.IntegerField(default=1)
    numerom07 = models.IntegerField(default=1)
    numerom08 = models.IntegerField(default=1)
    numerom09 = models.IntegerField(default=1)
    numerom10 = models.IntegerField(default=1)
    numerom11 = models.IntegerField(default=1)
    numerom12 = models.IntegerField(default=1)

    class Meta:
        db_table = 'contabilidad_numeracion_mes_anio'

class ResolucionFacturacion(BaseModel):

    tipo_documento = models.ForeignKey(
        TiposDocumentos,
        on_delete=models.CASCADE,
        related_name='resoluciones'
    )
    numero_resolucion = models.CharField(max_length=100)
    rango_inicial = models.IntegerField()
    rango_final = models.IntegerField()
    consecutivo_actual = models.IntegerField(default=0)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activa = models.BooleanField(default=True)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.numero_resolucion

    class Meta:
        db_table = 'contabilidad_resolucion_facturacion'



