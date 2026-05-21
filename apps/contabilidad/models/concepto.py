from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel

class Concepto(BaseModel):
    history = HistoricalRecords()
    codigo = models.IntegerField(blank=True, null=True, help_text='Maximo de numero para codigo de 999')
    nombre = models.CharField(max_length=50, blank=True, null=True)
    detalle = models.CharField(max_length=100, blank=True, null=True)
    empresas_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        try:
            return self.nombre
        except:
            return ''

    class Meta:
        db_table = 'contabilidad_conceptos'

