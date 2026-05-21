from django.db import models

# Create your models here.
from apps.utils.models import BaseModel

class TipoDocumento(BaseModel):
    nombre  = models.CharField(max_length=255, help_text="Nombre", )
    codigo  = models.CharField(max_length=3, help_text="codigo", )
    prefijo = models.CharField(max_length=3, help_text="prefijo", blank=True, null=True)

    def __str__(self):
        """Return post title."""
        return '{}'.format(self.nombre, )

    class Meta:
        """Meta class."""
        ordering = ['-id']

class TipoPersona(BaseModel):
    nombre = models.CharField(max_length=255, help_text="Nombre")
    orden  =  models.CharField(max_length=10)    
    color  = models.CharField(
        max_length=255,
        help_text="Color",
        blank=True,
        null=True,
    )

    class Meta:
        """Meta class."""
        ordering = ['-created', '-modified']

class Genero(BaseModel):
    nombre = models.CharField(max_length=50, help_text="Nombre", )

    def __str__(self):
        """Return post title."""
        return '{}'.format(self.nombre, )

    class Meta:
        """Meta class."""
        ordering = ['-created', '-modified']


class EstadoCivil(BaseModel):
    nombre = models.CharField(max_length=50, help_text="Nombre", )

    def __str__(self):
        """Return post title."""
        return '{}'.format(self.nombre, )

    class Meta:
        """Meta class."""
        ordering = ['-created', '-modified']

class EstadoPersona(models.Model):
    nombre = models.CharField(max_length=50, blank=True, null=True)
    
