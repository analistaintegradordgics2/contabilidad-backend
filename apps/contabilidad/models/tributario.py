from django.db import models
from apps.utils.models import BaseModel
from apps.contabilidad.models.cuenta import Mayor


class VariableContable(BaseModel):
    """
    Catálogo de variables contables para cálculos dinámicos en plantillas y motor tributario.
    """
    codigo = models.CharField(max_length=50, unique=True)
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(null=True, blank=True)
    es_sistema = models.BooleanField(default=True)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'cont_variable_contable'
        ordering = ['nombre']

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class ReglaTributaria(BaseModel):
    """
    Parametrización de impuestos y retenciones administrada por el Contador.
    Desacoplada de las cuentas de las plantillas contables.
    """
    VARIABLE_CHOICES = [
        ('IMPUESTO_IVA', 'IVA Calculado'),
        ('RETEFUENTE', 'Retención en la Fuente'),
        ('RETEICA', 'Retención de ICA'),
        ('RETEIVA', 'Retención de IVA'),
    ]

    nombre = models.CharField(max_length=150)
    tipo_variable = models.CharField(max_length=50, choices=VARIABLE_CHOICES)
    tarifa_porcentaje = models.DecimalField(max_digits=7, decimal_places=4, default=0.0000)
    base_minima = models.DecimalField(max_digits=18, decimal_places=2, default=0.00)
    cuenta_contable = models.ForeignKey(Mayor, on_delete=models.PROTECT, null=True, blank=True, related_name="reglas_tributarias")
    vigencia_anio = models.IntegerField(default=2026)
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'cont_regla_tributaria'
        ordering = ['tipo_variable', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.tarifa_porcentaje}%)"


class ConceptoReglaTributaria(BaseModel):
    """
    Relación de reglas tributarias asociadas a cada concepto contable.
    """
    concepto = models.ForeignKey('contabilidad.Concepto', on_delete=models.CASCADE, related_name="reglas_tributarias")
    regla_tributaria = models.ForeignKey(ReglaTributaria, on_delete=models.CASCADE, related_name="conceptos_asociados")
    activa = models.BooleanField(default=True)

    class Meta:
        db_table = 'cont_concepto_regla_tributaria'
        unique_together = ['concepto', 'regla_tributaria']

    def __str__(self):
        return f"{self.concepto} - {self.regla_tributaria}"
