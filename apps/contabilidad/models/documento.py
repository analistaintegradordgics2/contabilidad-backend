from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel
from apps.contabilidad.models.cuenta import *
from apps.contabilidad.models.parametros import *
from apps.contabilidad.models.tipodocumento import *
from apps.contabilidad.models.concepto import *
from apps.contabilidad.models.pago import *
from apps.personas.models.persona import *

class Estado(models.IntegerChoices):
    ABIERTO    = 1, 'Abierto'
    CERRADO    = 2, 'Cerrado'
    ANULADO    = 3, 'Anulado'
    REABIERTO  = 4, 'Reabierto'

class Documentos(BaseModel):
    history = HistoricalRecords()
    # archivos = GenericRelation(Archivo)
    numero             = models.CharField(max_length=15, blank=True, null=True)
    fecha              = models.DateField(blank=True, null=True)
    fecha_vencimiento  = models.DateField(blank=True, null=True)
    referencia         = models.CharField(max_length=40, blank=True, null=True,default='')
    detalle            = models.CharField(max_length=254, blank=True, null=True)
    estado             = models.IntegerField(choices=Estado.choices, default=Estado.ABIERTO)
    total              = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    concepto           = models.ForeignKey(Concepto, on_delete=models.CASCADE)
    tipo_documento     = models.ForeignKey(TiposDocumentos, on_delete=models.CASCADE)
    prtefte            = models.DecimalField(max_digits=9, decimal_places=4, blank=True, null=True)
    prteica            = models.DecimalField(max_digits=9, decimal_places=4, blank=True, null=True)
    prteiva            = models.DecimalField(max_digits=9, decimal_places=4, blank=True, null=True)
    rtefte             = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    rteica             = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    rteiva             = models.DecimalField(max_digits=9, decimal_places=2, blank=True, null=True)
    subtotal           = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    pdescuento         = models.FloatField(blank=True, null=True)
    descuento          = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    piva               = models.FloatField(blank=True, null=True)
    iva                = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    gtotal             = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    personas           = models.ForeignKey(Persona,on_delete=models.CASCADE, related_name="documento_personas")
    nombre             = models.CharField(max_length=200, blank=True, null=True)
    direccion          = models.CharField(max_length=200, blank=True, null=True)
    telefono           = models.CharField(max_length=70, blank=True, null=True)
    movil              = models.CharField(max_length=70, blank=True, null=True)
    ciudad             = models.CharField(max_length=80, blank=True, null=True)    
    fpago              = models.IntegerField(blank=True, null=True)
    # conf_usuarios      = models.ForeignKey(User, on_delete=models.CASCADE)
    conf_sucursales_id = models.CharField(max_length=4, blank=True, null=True)    
    origen             = models.CharField(max_length=50, blank=True, null=True)
    anio               = models.IntegerField(blank=True, null=True)
    mes                = models.IntegerField(blank=True, null=True)
    mandato = models.BooleanField(default=False, blank=True, null=True, help_text="Identificar la factura es de tipo mandato")
    nota_parcial       = models.BooleanField(default=False, blank=True, null=True)
    automatico = models.BooleanField(default=False, blank=True, null=True, help_text="Campo para saber si el documento es automatico")
    nota_saldos_iniciales = models.BooleanField(default=False, blank=True, null=True)
    fecha_anterior = models.DateField(blank=True, null=True)
    

    class Meta:
        db_table = 'cont_documentos' 


class FactElectronicaDocumento(BaseModel):

    documento = models.OneToOneField(
        Documentos,
        related_name='facturacion_electronica',
        on_delete=models.CASCADE
    )
    numero_generado    = models.CharField(max_length=30, blank=True, null=True)
    estado = models.ForeignKey(
        EstadoFactElectro,
        on_delete=models.SET_NULL,
        null=True
    )
    operacion          = models.CharField(max_length=50, blank=True, null=True)


    observacion = models.TextField(
        blank=True,
        null=True
    )

    fecha_envio = models.DateTimeField(
        null=True,
        blank=True
    )
    webservice = models.TextField(blank=True, null=True, help_text="Se usa para guardar request y response del proveedor de facturación electrónica")

class PagoDocumento(BaseModel):

    documento = models.ForeignKey(
        Documentos,
        related_name='pagos',
        on_delete=models.CASCADE
    )

    forma_pago = models.ForeignKey(
        FormaPago,
        on_delete=models.PROTECT
    )

    medio_pago = models.ForeignKey(
        MedioPagoElectro,
        on_delete=models.PROTECT
    )

class PagoEfectivo(BaseModel):
    pago  = models.OneToOneField(PagoDocumento, on_delete=models.CASCADE, related_name='detalle_efectivo')
    valor = models.DecimalField(max_digits=18, decimal_places=2)


class PagoCheque(BaseModel):
    pago         = models.OneToOneField(PagoDocumento, on_delete=models.CASCADE, related_name='detalle_cheque')
    banco        = models.ForeignKey(Banco, on_delete=models.PROTECT)
    numero       = models.CharField(max_length=50)
    fecha        = models.DateField()
    valor        = models.DecimalField(max_digits=18, decimal_places=2)


class PagoConsignacion(BaseModel):
    pago            = models.OneToOneField(PagoDocumento, on_delete=models.CASCADE, related_name='detalle_consignacion')
    banco           = models.ForeignKey(Banco, on_delete=models.PROTECT)
    cuenta_bancaria = models.ForeignKey(CuentaBancaria, on_delete=models.PROTECT)
    numero          = models.CharField(max_length=100)
    fecha           = models.DateField()
    valor           = models.DecimalField(max_digits=18, decimal_places=2)


class PagoTarjeta(BaseModel):
    pago            = models.OneToOneField(PagoDocumento, on_delete=models.CASCADE, related_name='detalle_tarjeta')
    banco           = models.ForeignKey(Banco, on_delete=models.PROTECT)
    cuenta_bancaria = models.ForeignKey(CuentaBancaria, on_delete=models.PROTECT, null=True, blank=True)
    numero_tarjeta  = models.CharField(max_length=45)
    valor           = models.DecimalField(max_digits=18, decimal_places=2)   

class PagoTransferencia(BaseModel):
    pago            = models.OneToOneField(PagoDocumento, on_delete=models.CASCADE, related_name='detalle_transferencia')
    valor           = models.DecimalField(max_digits=18, decimal_places=2)   
    cuenta_origen   = models.ForeignKey(CuentaBancaria, on_delete=models.PROTECT, null=True, blank=True)
    banco_destino   = models.ForeignKey(Banco, on_delete=models.PROTECT)
    cuenta_destino  = models.CharField(max_length=100)
    numero_cheque   = models.CharField(max_length=45)
class Mov(models.Model):
    documento           = models.ForeignKey(Documentos,on_delete=models.CASCADE, related_name="mov_documentos")
    mayor               = models.ForeignKey(Mayor, on_delete=models.CASCADE, related_name="mov_mayor")
    valor_db            = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True, editable=True)
    valor_cr            = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    persona             = models.ForeignKey(Persona, on_delete=models.CASCADE)
    detalle             = models.TextField(blank=True, null=True)
    centro_costos       = models.ForeignKey(CentroCostos,on_delete=models.CASCADE, blank=True, null=True)
    base                = models.FloatField(blank=True, null=True)
    sistema             = models.IntegerField(blank=True, null=True)
    docref              = models.CharField(max_length=30, blank=True, null=True)
    nittercero          = models.ForeignKey(Persona,on_delete=models.CASCADE, db_column='nittercero',related_name="nittercero", blank=True, null=True)
    flujocaja           = models.IntegerField(blank=True, null=True)
    concepto            = models.ForeignKey(Concepto, on_delete=models.CASCADE, blank=True, null=True)
    conciliado          = models.BooleanField(default=False, help_text="Check para saber si este movimiento ya se concilio", blank=True, null=True)
    fecha_conciliacion  = models.DateTimeField(blank=True, null=True)
    mes_anio_conciliado = models.TextField(blank=True, null=True)
    user_conciliacion   = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True, null=True, related_name="mov_conciliacion_user")
    dcierre             = models.IntegerField(blank=True, null=True)
    

class DocumentosBita(models.Model):
    documentos = models.ForeignKey(Documentos, on_delete=models.CASCADE)
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    fecha = models.DateTimeField(blank=True, null=True)
    evento = models.CharField(max_length=254, blank=True, null=True)
    estado = models.ForeignKey(EstadoDocumento, on_delete=models.CASCADE)

    class Meta:
        #managed = False
        db_table = 'cont_documentos_bita'

class DetalleFacturas(models.Model):
    documentos      = models.ForeignKey(Documentos,on_delete=models.CASCADE)
    cantidad        = models.CharField(max_length=45, blank=True, null=True)
    detalle         = models.CharField(max_length=300, blank=True, null=True)
    valor           = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    piva            = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    pdescuento      = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    concepto        = models.ForeignKey(Concepto, on_delete=models.CASCADE, blank=True, null=True)
    mandantes       = models.TextField(blank=True, null=True)
    orden           = models.IntegerField(blank=True, null=True)
    prtefuente      = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    prteica         = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)
    prteiva         = models.DecimalField(max_digits=18, decimal_places=4, blank=True, null=True)


