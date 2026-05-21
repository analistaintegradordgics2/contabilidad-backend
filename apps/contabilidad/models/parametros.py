from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel
from apps.contabilidad.models.cuenta import *

class Fuentes(models.Model):
    nombre = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        try:
            return self.nombre
        except:
            return ''


class CentroCostos(BaseModel):
    history = HistoricalRecords()
    codigo          = models.CharField(max_length=5, blank=True, null=True)
    nombre          = models.CharField(max_length=45, blank=True, null=True)
    estado          = models.BooleanField(default=True)
    tipo            = models.CharField(max_length=1, blank=True, null=True)
    cod_sucursal    = models.CharField(max_length=10, blank=True, null=True)

class EstadoFactElectro(models.Model):
    codigo = models.IntegerField(blank=True, null=True)
    nombre = models.CharField(max_length=80)
    color = models.CharField(max_length=20,blank=True,null=True)

class EstadoDocumento(models.Model):
    estado = models.CharField(max_length=100)

    class Meta:
        db_table = 'contabilidad_estados'

