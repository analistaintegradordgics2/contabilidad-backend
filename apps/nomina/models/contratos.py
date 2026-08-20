from django.db import models
from simple_history.models import HistoricalRecords
from django.contrib.contenttypes.fields import GenericRelation

from apps.public.models import Archivo
from apps.personas.models.persona import Persona
from apps.contabilidad.models.parametros import CentroCostos
from apps.nomina.models.parametrizacion import TipoContrato, TipoTrabajador, NivelRiesgo, Periodo
from apps.nomina.models.novedades import NovedadesCentroCosto, Novedad
from apps.contabilidad.models.pago import Banco, TipoCuenta, FormaPagoElectro, MedioPagoElectro
from apps.nomina.models.entidades import Entidad

from apps.utils.models import BaseModel

class Cargo(BaseModel):
    history = HistoricalRecords()
    nombre = models.CharField(max_length=100, blank=True, null=True)
    estado = models.BooleanField(default=True)

class ContratoNomina(BaseModel):
    history = HistoricalRecords()
    archivos = GenericRelation(Archivo)
    persona = models.ForeignKey(Persona, related_name='contrato_nomina_persona', on_delete=models.CASCADE)
    fecha_ingreso = models.DateTimeField()
    cargo = models.ForeignKey(Cargo, related_name='contrato_nomina_cargo', on_delete=models.CASCADE)
    centro_costo = models.ForeignKey(CentroCostos, related_name='contrato_nomina_centro_costo', on_delete=models.CASCADE)
    jefe = models.CharField(max_length=100, blank=True, null=True)
    sueldo = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    tipo_contrato = models.ForeignKey(TipoContrato, related_name='contrato_nomina_tipo_contrato', on_delete=models.CASCADE)
    numero_meses = models.IntegerField(blank=True, null=True)
    fecha_vencimiento = models.DateTimeField(blank=True, null=True)
    tipo_trabajador = models.ForeignKey(TipoTrabajador, related_name='contrato_nomina_tipo_trabajador', on_delete=models.CASCADE)
    subtipo_trabajador = models.CharField(max_length=5)
    fecha_retiro = models.DateTimeField(blank=True, null=True)
    auxilio_transporte = models.BooleanField(default=False)
    alto_riesgo_pension = models.BooleanField(default=False)
    salario_integral = models.BooleanField(default=False)
    salario_promedio = models.BooleanField(default=False)
    salario_minimo = models.BooleanField(default=False)
    estado = models.BooleanField(default=True)
    medio_auxilio_transporte = models.BooleanField(default=False)
    contrato_medio_tiempo = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'nomina_contrato'

class DatosPago(BaseModel):
    history = HistoricalRecords()
    banco = models.ForeignKey(Banco, related_name='datos_pago_banco', on_delete=models.CASCADE)
    tipo_cuenta = models.ForeignKey(TipoCuenta, related_name='datos_pago_tipo_cuenta', on_delete=models.CASCADE)
    numero_cuenta = models.CharField(max_length=30)
    contrato = models.OneToOneField(ContratoNomina, related_name='datos_pago_contrato_nomina', on_delete=models.CASCADE)
    forma_pago = models.ForeignKey(FormaPagoElectro, related_name='datos_pago_forma_pago', on_delete=models.CASCADE)
    medio_pago = models.ForeignKey(MedioPagoElectro, related_name='datos_pago_medio_pago', on_delete=models.CASCADE)

class DatosAportes(BaseModel):
    history = HistoricalRecords()
    entidad_salud = models.ForeignKey(Entidad, related_name='datos_aportes_entidad_salud', on_delete=models.CASCADE)
    porcentaje_salud = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    entidad_pension = models.ForeignKey(Entidad, related_name='datos_aportes_entidad_pension', on_delete=models.CASCADE, blank=True, null=True)
    porcentaje_pension = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, blank=True, null=True)
    caja_compensacion = models.ForeignKey(Entidad, related_name='datos_aportes_caja_compensacion', on_delete=models.CASCADE, blank=True, null=True)
    arl = models.ForeignKey(Entidad, related_name='datos_aportes_entidad_arl', on_delete=models.CASCADE)
    porcentaje_arl = models.DecimalField(max_digits=12, decimal_places=3, default=0.0)
    nivel_riesgo = models.ForeignKey(NivelRiesgo, related_name='datos_aportes_nivel_riesgo', on_delete=models.CASCADE)
    contrato = models.OneToOneField(ContratoNomina, related_name='datos_aportes_contrato_nomina', on_delete=models.CASCADE)

class DatosEmergencia(BaseModel):
    history = HistoricalRecords()
    nombre = models.CharField(max_length=150)
    celular = models.CharField(max_length=20)
    parentesco = models.CharField(max_length=80, blank=True, null=True)
    contrato = models.ForeignKey(ContratoNomina, related_name='datos_emergencia_contrato_nomina', on_delete=models.CASCADE)
    eliminado = models.BooleanField(default=False)

class ComposicionFamiliar(BaseModel):
    history = HistoricalRecords()
    nombre = models.CharField(max_length=150)
    edad = models.IntegerField(blank=True, null=True)
    parentesco = models.CharField(max_length=80, blank=True, null=True)
    contrato = models.ForeignKey(ContratoNomina, related_name='composicion_familiar_contrato_nomina', on_delete=models.CASCADE)
    eliminado = models.BooleanField(default=False)

class ContratoNominaNovedades(BaseModel):
    history = HistoricalRecords()
    contrato = models.ForeignKey(ContratoNomina, related_name='contrato_nomina_novedades_contrato', on_delete=models.CASCADE)
    descripcion = models.TextField()
    centro_costos_novedades = models.ForeignKey(NovedadesCentroCosto, related_name='contrato_nomina_novedades_contrato', on_delete=models.CASCADE)
    fecha_inicial = models.DateTimeField()
    fecha_final = models.DateTimeField(blank=True, null=True)
    valor = models.IntegerField()
    eliminado = models.BooleanField(default=False)
    novedad = models.ForeignKey(Novedad, related_name='contrato_nomina_novedades_novedad', on_delete=models.CASCADE)
    porcentaje_liquidacion = models.DecimalField(max_digits=12, decimal_places=2, default=0.0, blank=True, null=True)
    vacaciones = models.BooleanField(default=False)
    periodo_ini_vacaciones = models.DateField(blank=True, null=True)
    periodo_fin_vacaciones = models.DateField(blank=True, null=True)
    fecha_reintegro = models.DateField(blank=True, null=True)
    vacaciones_liquidadas = models.BooleanField(default=True)

class ContratoNovedadesPeriodos(models.Model):
    valor = models.IntegerField()
    mes = models.CharField(max_length=2)
    anio = models.CharField(max_length=5)
    fecha_ini = models.DateField()
    fecha_fin = models.DateField()
    contrato_novedades = models.ForeignKey(ContratoNominaNovedades, related_name='novedad_periodos_contrato_novedades', on_delete=models.CASCADE)
    periodo = models.ForeignKey(Periodo, related_name='novedad_periodos_periodos', on_delete=models.CASCADE)
    contrato = models.ForeignKey(ContratoNomina, related_name='novedad_periodos_contrato', on_delete=models.CASCADE)
    vacaciones = models.BooleanField(default=False)