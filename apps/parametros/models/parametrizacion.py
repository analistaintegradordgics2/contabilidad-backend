from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel
from django.contrib.auth.models import Group

# Create your models here.
class Parametros(BaseModel):
    history = HistoricalRecords()
    parametro = models.CharField(max_length=255, blank=True, null=True)
    valor = models.TextField(blank=True, null=True)
    label = models.CharField(max_length=255, blank=True, null=True)
    tipo = models.CharField(max_length=100, blank=True, null=True)
    url = models.CharField(max_length=250, blank=True, null=True)
    decimales = models.CharField(max_length=2, blank=True, null=True)
    option_label = models.CharField(max_length=50, blank=True, null=True)
    rules = models.CharField(max_length=250, blank=True, null=True)
    activo = models.BooleanField(default=True, blank=True, null=True)
    valor2 = models.TextField(blank=True, null=True, help_text="Se usa guardar un segundo valor como ejemplo contraseñas")
    tipo_tab = models.CharField(max_length=30, blank=True, null=True,
        help_text="Identificar el tab al que pertecenece el parametro, 1=Empresa, 2=Codigos contables, 3=Tasas y porcentajes, 4=Conceptos, 5=Correos"
    )
    orden = models.IntegerField(blank=True, null=True, help_text="Orden a mostrar")
    key = models.TextField(blank=True, null=True, help_text="Este campo de usa para des encriptar las contraseñas")
    cupon = models.BooleanField(default=False, blank=True, null=True,help_text="Identificar si son parametros de cupones")
    comentario = models.TextField(blank=True, null=True, help_text="Comentario para indicar algo del parametro")
    imagen_membrete = models.TextField(blank=True, null=True, help_text="Se para guardar la imagen del membrete de cartas en base64")
    requerido = models.BooleanField(default=True, blank=True, null=True)

class Procesos(models.Model):
    nombre = models.CharField(max_length=50, blank=True, null=True)
    codigo = models.CharField(max_length=4, blank=True, null=True)


class ParametroProceso(models.Model):
    parametros = models.ForeignKey(Parametros,related_name="parametros_procesos", on_delete=models.CASCADE)
    proceso = models.ForeignKey(Procesos,related_name="procesos_parametros", on_delete=models.CASCADE)

class Mes(models.Model):
    nombre = models.CharField(
        max_length=20,
        help_text="mes",
        blank=True, null=True
    )
    numero = models.CharField(
        max_length=2,
        help_text="numer mes",
        blank=True, null=True
    )

class Anio(models.Model):
    nombre = models.IntegerField(blank=True, null=True)
    cierre = models.IntegerField(blank=True, null=True)
    salario_minimo = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    aux_transporte = models.DecimalField(max_digits=12, decimal_places=2, default=0.0)
    actualizado = models.BooleanField(default=False)

# Nelson Lugo - 20/01/2024 Se crea este modelo con el fin de guardar datos adicionales segun el mes y el año
class MesAnio(models.Model):
    mes = models.ForeignKey(Mes, related_name="mes_anio_mes", on_delete=models.CASCADE)
    anio = models.ForeignKey(Anio, related_name="mes_anio_anio", on_delete=models.CASCADE)
    parametro = models.TextField()
    valor = models.TextField(blank=True, null=True)
    valor2 = models.TextField(blank=True, null=True)
    tipo = models.TextField(blank=True, null=True)

class ParametrosWhatsapp(models.Model):
    parametro = models.CharField(max_length=100, blank=True, null=True)
    valor = models.TextField(blank=True, null=True)
    external_id = models.TextField(blank=True, null=True)
    modificar_archivo = models.BooleanField(default=False)


class GeneradorConsultas(BaseModel):
    history = HistoricalRecords()
    nombre = models.TextField(blank=True, null=True)
    valor = models.TextField(blank=True, null=True)
    script_sql = models.TextField(blank=True, null=True, help_text="Se guarda el sql como tal")
    modulo = models.ForeignKey(Group, related_name="generador_consultas_grupos", on_delete=models.CASCADE, blank=True, null=True)
    tipo = models.TextField(blank=True, null=True, help_text="Saber si es una parametrizacion o una consulta de cliente",)
    observacion = models.TextField(blank=True, null=True, help_text="Texto de ayuda para saber que hace la consulta")
    consulta_base = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='self_generador_consulta',
        on_delete=models.SET_NULL,
        help_text="Consulta base que se uso para crear la consulta dle cliente"
    )
    estado = models.BooleanField(default=True)
    tipo_excel = models.TextField(blank=True, null=True, help_text="Saber si es por hojas el excel")

class TipoContrato(models.Model):
    nombre = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

class Aplicativo(models.Model):
    nombre = models.CharField(max_length=50)
    activo = models.BooleanField(default=True)

