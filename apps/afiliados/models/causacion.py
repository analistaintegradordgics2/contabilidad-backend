from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel
from apps.contabilidad.models.tipodocumento import TiposDocumentos
from apps.contabilidad.models.concepto import Concepto
from apps.contabilidad.models.cuenta import Mayor
from apps.afiliados.models.afiliado import Afiliado

class ConceptoCausacion(BaseModel):
    history = HistoricalRecords()
    nombre = models.CharField(max_length=100)
    tipo_factura = models.ForeignKey(TiposDocumentos, on_delete=models.CASCADE)
    concepto = models.ForeignKey(Concepto, on_delete=models.CASCADE)
    mayor = models.ForeignKey(Mayor, on_delete=models.CASCADE)
    iva = models.BooleanField(default=False)
    cta_iva = models.ForeignKey(Mayor, on_delete=models.CASCADE, related_name='cuenta_iva_concepto', blank=True, null=True)
    iva_incluido = models.BooleanField(default=False)
    agrupar = models.BooleanField(default=False)
    activo = models.BooleanField(default=True)
    es_retencion = models.BooleanField(default=False)

    class Meta:
        db_table = 'afiliados_concepto_causacion'

class AfiliadoConceptoCausacion(BaseModel):
    history = HistoricalRecords()
    afiliado = models.ForeignKey(Afiliado, on_delete=models.CASCADE, related_name='afiliado_concepto_causacion')
    concepto = models.ForeignKey(ConceptoCausacion, on_delete=models.CASCADE, related_name='concepto_concepto_causacion')
    valor = models.DecimalField(max_digits=18, decimal_places=2)
    detalle = models.TextField(blank=True, null=True)
    porcentaje = models.DecimalField(max_digits=18, decimal_places=2, blank=True, null=True)

    class Meta:
        db_table = 'afiliados_afiliado_concepto_causacion'