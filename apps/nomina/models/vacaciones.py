from django.db import models
from apps.utils.models import BaseModel

from apps.nomina.models.contratos import ContratoNomina, ContratoNominaNovedades

class Vacaciones(BaseModel):
    contrato = models.ForeignKey(ContratoNomina, related_name='vacaciones_contrato', on_delete=models.CASCADE)
    contrato_novedades = models.ForeignKey(ContratoNominaNovedades, related_name='vacaciones_contrato_novedades', on_delete=models.CASCADE)
    dias = models.IntegerField()
    sueldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    valor_dia = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    salud_valor_porcentaje = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    salud_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    pension_valor_porcentaje = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    pension_total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    
    class Meta:
        db_table = 'nomina_vacaciones'