from django.db import models
from apps.utils.models import BaseModel
from apps.contabilidad.models.cuenta import Mayor
from apps.contabilidad.models.concepto import Concepto
from apps.contabilidad.models.tipodocumento import TiposDocumentos
from apps.contabilidad.models.parametros import Fuentes
from apps.contabilidad.models.tributario import ReglaTributaria


class PlantillaDocumento(BaseModel):
    """
    Parametrización creada por el Contador para la generación de comprobantes automáticos.
    """
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    fuente = models.ForeignKey(Fuentes, on_delete=models.PROTECT, null=True, blank=True, related_name="plantillas")
    tipo_documento = models.ForeignKey(TiposDocumentos, on_delete=models.PROTECT, related_name="plantillas")
    concepto = models.ForeignKey(Concepto, on_delete=models.PROTECT, related_name="plantillas")
    activa = models.BooleanField(default=True)
    icono = models.CharField(max_length=50, blank=True, null=True, default='assignment')
    color = models.CharField(max_length=20, blank=True, null=True, default='primary')
    requiere_tercero = models.BooleanField(default=True)
    requiere_valor = models.BooleanField(default=True)
    contador_usos = models.IntegerField(default=0)
    ultima_fecha_uso = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'cont_plantilla_documento'
        ordering = ['nombre']

    def __str__(self):
        return self.nombre


class PlantillaMovimiento(BaseModel):
    """
    Líneas de asiento preconfiguradas asociadas a una plantilla.
    """
    TIPO_VALOR_CHOICES = [
        ('fijo', 'Valor fijo'),
        ('porcentaje', 'Porcentaje del valor principal'),
        ('formula', 'Fórmula'),
    ]

    NATURALEZA_CHOICES = [
        ('debito', 'Débito'),
        ('credito', 'Crédito'),
    ]

    ORIGEN_VALOR_CHOICES = [
        ('VALOR_TOTAL', 'Valor Total Principal'),
        ('SUBTOTAL', 'Subtotal / Base Gravable'),
        ('IMPUESTO_IVA', 'Variable: IVA Calculado'),
        ('RETEFUENTE', 'Variable: Retención en la Fuente'),
        ('RETEICA', 'Variable: Retención de ICA'),
        ('RETEIVA', 'Variable: Retención de IVA'),
        ('NETO_PAGAR', 'Variable: Neto a Pagar (Cierre)'),
        ('PORCENTAJE_DIRECTO', 'Porcentaje Directo (Manual)'),
        ('VALOR_FIJO', 'Valor Fijo (Manual)'),
    ]

    plantilla = models.ForeignKey(
        PlantillaDocumento,
        on_delete=models.CASCADE,
        related_name='movimientos'
    )
    mayor = models.ForeignKey(Mayor, on_delete=models.PROTECT, related_name="plantilla_movimientos")
    concepto = models.ForeignKey(Concepto, on_delete=models.PROTECT, related_name="plantilla_movimientos")
    naturaleza = models.CharField(max_length=10, choices=NATURALEZA_CHOICES)
    tipo_valor = models.CharField(max_length=20, choices=TIPO_VALOR_CHOICES, default='porcentaje')
    origen_valor = models.CharField(max_length=50, choices=ORIGEN_VALOR_CHOICES, default='PORCENTAJE_DIRECTO')
    regla_tributaria = models.ForeignKey(ReglaTributaria, on_delete=models.SET_NULL, null=True, blank=True, related_name="plantilla_movimientos")
    valor_fijo = models.DecimalField(max_digits=18, decimal_places=2, null=True, blank=True)
    porcentaje = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    base_minima = models.DecimalField(max_digits=18, decimal_places=2, default=0.00, null=True, blank=True)
    usa_tercero = models.BooleanField(default=True)
    detalle_default = models.CharField(max_length=255, blank=True, null=True)
    orden = models.IntegerField(default=0)

    class Meta:
        db_table = 'cont_plantilla_movimiento'
        ordering = ['orden']

    def __str__(self):
        return f"{self.plantilla.nombre} - {self.mayor.codigo} ({self.naturaleza})"
