from django.db import models
from apps.afiliados.models.afiliado import Afiliado
from apps.parametros.models.parametrizacion import Anio, Mes
from simple_history.models import HistoricalRecords
from apps.accounts.models import Usuario
from apps.contabilidad.models.concepto import Concepto
from apps.afiliados.models.causacion import ConceptoCausacion

class Cupon(models.Model): 
    history            = HistoricalRecords()
    fecha              = models.DateField(blank=True, null=True)
    numero             = models.CharField(max_length=40, blank=True, null=True,default='')
    afiliado           = models.ForeignKey(Afiliado, on_delete=models.CASCADE, blank=True, null=True)
    anio               = models.ForeignKey(Anio, on_delete=models.CASCADE, blank=True, null=True)
    mes                = models.ForeignKey(Mes, on_delete=models.CASCADE, blank=True, null=True)
    estado             = models.BooleanField(default=False)
    usuario            = models.ForeignKey(Usuario, on_delete=models.CASCADE)
    nombre             = models.CharField(max_length=200, blank=True, null=True)
    direccion          = models.CharField(max_length=200, blank=True, null=True)
    telefono           = models.CharField(max_length=70, blank=True, null=True)
    ciudad             = models.CharField(max_length=80, blank=True, null=True)
    subtotal           = models.FloatField(blank=True, null=True)
    descuento          = models.FloatField(blank=True, null=True)
    iva                = models.FloatField(blank=True, null=True)
    gran_total         = models.FloatField(blank=True, null=True)
    saldo              = models.FloatField(blank=True, null=True)
    fecha1             = models.DateField(blank=True, null=True)
    fecha2             = models.DateField(blank=True, null=True)
    fecha3             = models.DateField(blank=True, null=True)
    pfecha2            = models.CharField(max_length=6, blank=True, null=True,default='')
    pfecha3            = models.CharField(max_length=6, blank=True, null=True,default='')
    valor1             = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    valor2             = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    valor3             = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    unica_fecha        = models.BooleanField(help_text="Unica Fecha", default=False, blank=True, null=True)
    referencia         = models.CharField(max_length=40, blank=True, null=True,default='')

    retefuente         = models.FloatField(blank=True, null=True)
    reteiva            = models.FloatField(blank=True, null=True)
    reteica            = models.FloatField(blank=True, null=True)
    rete_avisos        = models.FloatField(blank=True, null=True)
    rete_bomberil      = models.FloatField(blank=True, null=True)
    
    tipo_cupon         = models.CharField(max_length=20, blank=True, null=True)
    eliminado          = models.BooleanField(help_text="Cupón eliminado", default=False, blank=True, null=True)
    url_s3             = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'afiliados_cupones' 


class DetalleCupones(models.Model):
    cupon           = models.ForeignKey(Cupon,on_delete=models.CASCADE,related_name='detalle_cupones')
    cantidad        = models.CharField(max_length=45, blank=True, null=True)
    # detalle         = models.CharField(max_length=45, blank=True, null=True)
    detalle         = models.TextField(blank=True, null=True)
    valor           = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    piva            = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    pdescuento      = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)
    concepto        = models.ForeignKey(Concepto, on_delete=models.CASCADE, blank=True, null=True)
    concepto_causacion        = models.ForeignKey(ConceptoCausacion, on_delete=models.CASCADE, blank=True, null=True)

    class Meta:
        db_table = 'afiliados_detalle_cupones'