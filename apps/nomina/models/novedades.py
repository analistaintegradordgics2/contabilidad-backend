from django.db import models
from simple_history.models import HistoricalRecords

from apps.utils.models import BaseModel

from apps.contabilidad.models.concepto import Concepto
from apps.contabilidad.models.parametros import CentroCostos
from apps.contabilidad.models.cuenta import Mayor

class TipoNovedad(models.Model):
    nombre = models.CharField(max_length=150)
    estado = models.BooleanField(default=True)

class TipoValorNovedad(models.Model):
    nombre = models.CharField(max_length=150)
    valor = models.IntegerField(blank=True, null=True)
    estado = models.BooleanField(default=True)

class GrupoNomina(models.Model):
    nombre = models.CharField(max_length=150)
    estado = models.BooleanField(default=True)

class SubGrupoNomina(models.Model):
    nombre = models.CharField(max_length=150)
    codigo = models.IntegerField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    grupo_nomina = models.ForeignKey(GrupoNomina, related_name='sub_grupo_nomina_grupo_nomina', on_delete=models.CASCADE)

class Novedad(BaseModel):
    history = HistoricalRecords()
    nombre = models.CharField(max_length=150)
    tipo_novedad = models.ForeignKey(TipoNovedad, related_name='novedades_tipo_novedad', on_delete=models.CASCADE)
    grupo_nomina = models.ForeignKey(GrupoNomina, related_name='novedades_grupo_nomina', on_delete=models.CASCADE)
    sub_grupo_nomina = models.ForeignKey(SubGrupoNomina, related_name='novedades_sub_grupo_nomina', on_delete=models.CASCADE, blank=True, null=True)
    entidad = models.ForeignKey('nomina.Entidad', related_name='novedades_entidades', on_delete=models.CASCADE, blank=True, null=True)
    tipo_valor_novedad = models.ForeignKey(TipoValorNovedad, related_name='novedades_tipo_valor_novedad', on_delete=models.CASCADE)
    valor = models.IntegerField(blank=True, null=True)
    estado = models.BooleanField(default=True)
    concepto = models.ForeignKey(Concepto, blank=True, null=True, related_name='novedades_concepto', on_delete=models.CASCADE)
    automatica = models.BooleanField(default=False)
    periodo_automatico = models.ForeignKey('nomina.Periodo', blank=True, null=True, related_name='novedades_periodo_automatico', on_delete=models.CASCADE)

    class Meta:
        db_table = 'nomina_novedades'

class NovedadesCentroCosto(BaseModel):
    history = HistoricalRecords()
    novedades = models.ForeignKey(Novedad, related_name='novedades_centro_costos_novedades', on_delete=models.CASCADE)
    centro_costos = models.ForeignKey(CentroCostos, related_name='novedades_centro_costos_centro_costos', on_delete=models.CASCADE, blank=True, null=True)
    entidades_centro_costos = models.ForeignKey('nomina.EntidadCentroCosto', related_name='novedades_centro_costos_entidades_centro_costos', on_delete=models.CASCADE, blank=True, null=True)
    mayor_cta_debito = models.ForeignKey(Mayor, related_name='novedades_centro_costos_mayor_debito', on_delete=models.CASCADE, blank=True, null=True)
    mayor_cta_credito = models.ForeignKey(Mayor, related_name='novedades_centro_costos_mayor_credito', on_delete=models.CASCADE, blank=True, null=True)
    eliminado = models.BooleanField(default=False)