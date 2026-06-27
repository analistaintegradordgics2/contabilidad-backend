from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel
from apps.parametros.models.parametrizacion import TipoContrato, Aplicativo
from apps.personas.models.persona import Persona

class Afiliado(BaseModel):
    history = HistoricalRecords()
    nombre = models.CharField(max_length=100)
    tipo_contrato = models.ForeignKey(TipoContrato, on_delete=models.CASCADE)
    aplicativo = models.ForeignKey(Aplicativo, on_delete=models.CASCADE)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    porc_reajuste = models.DecimalField(max_digits=18, decimal_places=2)
    porc_iva = models.DecimalField(max_digits=18, decimal_places=2)
    porc_rte_fte = models.DecimalField(max_digits=18, decimal_places=2)
    porc_rte_ica = models.DecimalField(max_digits=18, decimal_places=2)
    porc_rte_iva = models.DecimalField(max_digits=18, decimal_places=2)
    porc_bomberil = models.DecimalField(max_digits=18, decimal_places=2)
    porc_avisos = models.DecimalField(max_digits=18, decimal_places=2)
    fecha_reajuste = models.DateField()
    activo = models.BooleanField(default=True)
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='afiliado_persona')


    class Meta:
        db_table = 'afiliados_afiliado'