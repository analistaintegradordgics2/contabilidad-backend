from django.db import models
from simple_history.models import HistoricalRecords

from apps.utils.models import BaseModel

from apps.personas.models.persona import Persona
from apps.contabilidad.models.parametros import CentroCostos
from apps.contabilidad.models.cuenta import Mayor

class TipoEntidad(models.Model):
    nombre = models.CharField(max_length=100, blank=True, null=True)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'nomina_tipoentidades'
        
class Entidad(BaseModel):
    history = HistoricalRecords()
    personas = models.ForeignKey(Persona, related_name='entidad_persona', on_delete=models.CASCADE, blank=True, null=True)
    tipo_entidad = models.ForeignKey(TipoEntidad, related_name='entidad_tipo_entidades', on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)

    class Meta:
        db_table = 'nomina_entidades'

class EntidadCentroCosto(BaseModel):
    history = HistoricalRecords()
    entidad = models.ForeignKey(Entidad, related_name='entidad_centro_costos_entidad', on_delete=models.CASCADE)
    centro_costos = models.ForeignKey(CentroCostos, related_name='entidad_centro_costos_centro_costos', on_delete=models.CASCADE)
    mayor_cta_debito = models.ForeignKey(Mayor, related_name='entidad_centro_costos_mayor_debito', on_delete=models.CASCADE)
    mayor_cta_credito = models.ForeignKey(Mayor, related_name='entidad_centro_costos_mayor_credito', on_delete=models.CASCADE)
    eliminado = models.BooleanField(default=False)

    class Meta:
        db_table = 'nomina_entidadescentrocostos'