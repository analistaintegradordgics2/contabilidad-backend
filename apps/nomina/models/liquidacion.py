from django.db import models

from apps.utils.models import BaseModel

from apps.nomina.models.parametrizacion import Periodo
from apps.parametros.models.parametrizacion import Mes, Anio
from apps.nomina.models.contratos import ContratoNomina
from apps.accounts.models import Usuario
from apps.contabilidad.models.documento import Documentos
from apps.nomina.models.novedades import Novedad

class LiquidacionNomina(BaseModel):
    periodo = models.ForeignKey(Periodo, related_name='liquidacion_nomina_periodo', on_delete=models.CASCADE)
    mes = models.ForeignKey(Mes, related_name='liquidacion_nomina_mes', on_delete=models.CASCADE)
    anio = models.ForeignKey(Anio, related_name='liquidacion_nomina_anio', on_delete=models.CASCADE)
    contrato = models.ForeignKey(ContratoNomina, related_name='liquidacion_nomina_contrato', on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, null=True)
    dias_laborados = models.IntegerField(blank=True, null=True)
    sueldo_trabajado = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    auxilio_transporte = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    otros_devengados = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    salud = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    pension = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    otros_deducidos = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    fecha_inicial = models.DateField()
    fecha_final = models.DateField()
    contabilizado = models.BooleanField(default=False)
    pago = models.BooleanField(default=False)
    fecha_pago = models.DateTimeField(blank=True, null=True)
    usuario_pago = models.ForeignKey(Usuario, blank=True, null=True, related_name='liquidacion_user_pago', on_delete=models.CASCADE)
    estado = models.BooleanField(default=True)
    documento = models.ForeignKey(Documentos, blank=True, null=True, related_name='liquidacion_documento', on_delete=models.CASCADE)
    class Meta:
        db_table = 'nomina_liquidaciones'

class DetalleLiquidacionNomina(BaseModel):
    liquidacion = models.ForeignKey(LiquidacionNomina, related_name='detalle_liquidacion_nomina_liquidacion', on_delete=models.CASCADE)
    novedad = models.ForeignKey(Novedad, related_name='detalle_liquidacion_nomina_novedad', on_delete=models.CASCADE)
    descripcion = models.TextField(blank=True, null=True)
    cantidad = models.IntegerField(blank=True, null=True)
    valor_empleado = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    valor_patrono = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    fecha_inicial = models.DateTimeField()
    fecha_final = models.DateTimeField()
    
    class Meta:
        db_table = 'nomina_detalle_liquidaciones'