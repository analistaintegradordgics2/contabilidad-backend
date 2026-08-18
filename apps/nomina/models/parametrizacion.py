from django.db import models
from simple_history.models import HistoricalRecords

from apps.utils.models import BaseModel

class Periodo(models.Model):
    nombre = models.CharField(max_length=100)
    dias = models.IntegerField(blank=True, null=True)
    cod_dian = models.CharField(max_length=3, blank=True, null=True)
    estado = models.BooleanField(default=True)

class BaseLiquidacionEmpleado(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)
    tipo = models.IntegerField()

class BaseLiquidacionNovedad(BaseModel):
    history = HistoricalRecords()
    base_liquidacion = models.ForeignKey(BaseLiquidacionEmpleado, related_name='base_liquidacion_novedades_base_liquidacion', on_delete=models.CASCADE)
    novedades = models.ForeignKey('nomina.Novedad', related_name='base_liquidacion_novedades_novedades', on_delete=models.CASCADE)
    eliminado = models.BooleanField(default=False)

class TipoContrato(models.Model):
    nombre = models.CharField(max_length=100)
    cod_dian = models.CharField(max_length=3, blank=True, null=True)
    estado = models.BooleanField(default=True)

class TipoTrabajador(models.Model):
    nombre = models.CharField(max_length=100)
    cod_dian = models.CharField(max_length=3, blank=True, null=True)
    estado = models.BooleanField(default=True)

class NivelRiesgo(models.Model):
    nombre = models.CharField(max_length=100)
    valor = models.DecimalField(max_digits=12, decimal_places=3, default=0.00)
    estado = models.BooleanField(default=True)

class NominaParametros(models.Model):
    parametro = models.CharField(max_length=255, blank=True, null=True)
    valor = models.TextField(blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=100, blank=True, null=True)
    grupo = models.CharField(max_length=30, blank=True, null=True, help_text="Agrupar los parametros")
    orden = models.IntegerField(blank=True, null=True, help_text="Orden a mostrar")
    comentario = models.TextField(blank=True, null=True, help_text="Comentario para indicar algo del parametro")

    class Meta:
        db_table = 'nomina_parametros'