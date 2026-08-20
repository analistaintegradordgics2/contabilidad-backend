from django.db import models
from apps.utils.models import BaseModel

from apps.nomina.models.contratos import ContratoNomina
from apps.parametros.models.parametrizacion import Mes, Anio
from apps.contabilidad.models.parametros import EstadoFactElectro
from apps.nomina.models.novedades import Novedad
from apps.nomina.models.liquidacion import LiquidacionNomina

class NominaElectronica(BaseModel):

    contrato = models.ForeignKey(ContratoNomina, related_name='nomina_electronica_contrato', on_delete=models.CASCADE)
    fecha_ini_liquidacion = models.DateField()
    fecha_fin_liquidacion = models.DateField()
    mes = models.ForeignKey(Mes, related_name='nomina_electronica_mes', on_delete=models.CASCADE)
    anio = models.ForeignKey(Anio, related_name='nomina_electronica_anio', on_delete=models.CASCADE)
    dias_laborados = models.IntegerField()
    tipo_nomina = models.IntegerField()
    numero = models.CharField(max_length=50, blank=True, null=True)
    prefijo = models.CharField(max_length=50, blank=True, null=True)
    estado = models.ForeignKey(EstadoFactElectro, on_delete=models.CASCADE,blank=True, null=True)
    respuesta = models.TextField(blank=True, null=True)
    data_funcionalidad = models.TextField(blank=True, null=True)

class NominaElectronicaValores(models.Model):

    nomina_electronica = models.OneToOneField(NominaElectronica, related_name='nomina_electronica_valores', on_delete=models.CASCADE)
    sueldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    sueldo_trabajado = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    auxilio_transporte = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    viaticos_salarriales = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    viaticos_nosalariales = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    otros_devengados = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total_devengados = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    salud = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    pension = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    fondo = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    arl = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    otros_deducidos = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total_deducido = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)

class DetalleNominaElectronica(models.Model):

    nomina_electronica = models.ForeignKey(NominaElectronica, related_name='detalle_nomina_electronica', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    valor = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    novedad = models.ForeignKey(Novedad, related_name='novedades_detalle_nomina_electronica', on_delete=models.CASCADE, blank=True, null=True)
    descripcion = models.TextField(blank=True, null=True)
    patrono = models.BooleanField(default=False)
    provisional = models.BooleanField(default=False, blank=True, null=True)
    fecha_ini = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)

class NominaElectronicaLiquidaciones(models.Model):

    nomina_electronica = models.ForeignKey(NominaElectronica, related_name='nomina_electronica_nomina_electronica', on_delete=models.CASCADE)
    liquidacion = models.ForeignKey(LiquidacionNomina, related_name='liquidacion_nomina_electronica', on_delete=models.CASCADE)