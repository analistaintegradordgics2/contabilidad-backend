from django.db import models
# Create your models here.
from apps.utils.models import BaseModel


class Ciudad(models.Model):
    coddane = models.CharField(max_length=5)
    nombre = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        """Meta class."""
        db_table = 'parametros_ubicacion_ciudades'

class Zona(BaseModel):
    nombre = models.CharField(max_length=100)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        """Meta class."""
        db_table = 'parametros_ubicacion_zonas'


class Barrio(BaseModel):
    nombre = models.CharField(max_length=100)
    zonas = models.ForeignKey(Zona, on_delete=models.SET_NULL, blank=True, null=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.SET_NULL, blank=True, null=True)

    class Meta:
        """Meta class."""
        db_table = 'parametros_ubicacion_barrios'

class TipoVia(BaseModel):
    nombre = models.CharField(max_length=255, help_text="Nombre")

    def __str__(self):
        """Return post title."""
        return '{}'.format(self.nombre, )

    class Meta:
        """Meta class."""
        db_table = 'parametros_tipos_vias'
        ordering = ['-created', '-modified']


