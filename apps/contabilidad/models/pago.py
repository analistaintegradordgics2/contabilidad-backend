
from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel
from apps.contabilidad.models.cuenta import *

class FormaPagoElectro(models.Model):
    nombre  = models.CharField(max_length=255, blank=True, null=True)
    codigo  = models.CharField(max_length=5, blank=True, null=True)
    

class MedioPagoElectro(models.Model):
    nombre  = models.CharField(max_length=255, blank=True, null=True)
    codigo  = models.CharField(max_length=5, blank=True, null=True)

class Banco(BaseModel):
    history = HistoricalRecords()
    nombre = models.CharField(
        max_length=255,
        help_text="Nombre del banco",
        blank=True, null=True
    )
    codigo = models.IntegerField(
        help_text="Código del banco",
        blank=True, null=True
    )
    estado = models.BooleanField(
        help_text="Estado del banco",
        default=True
    )
    codigo_ach = models.CharField(
        max_length=50,
        help_text="Código ACH",
        blank=True, null=True
    )
    cupon_tercero = models.BooleanField(default=False, blank=True, null=True)

    class Meta:
        db_table = 'conf_bancos'
        ordering = ['id']


class FormaPago(models.Model):
    nombre = models.CharField(
        max_length=255,
        blank=True, null=True
    )
  

class TipoCuenta(models.Model):
    nombre = models.CharField(
        max_length=255,
        help_text="tipo de cuenta",
        blank=True, null=True
    )


class CuentaBancaria(BaseModel):
    history = HistoricalRecords()
    numero_cuenta   = models.CharField(max_length=50)
    banco           = models.ForeignKey(Banco, on_delete=models.CASCADE, blank=True, null=True)
    mayor           = models.ForeignKey(Mayor,on_delete=models.CASCADE, blank=True, null=True)
    nombre          = models.CharField(max_length=200, blank=True, null=True)
    tipo_cuenta     = models.ForeignKey(TipoCuenta, on_delete=models.CASCADE, blank=True, null=True)
    activo          = models.BooleanField(default=True)


    

