from django.db import models

# Create your models here.
from apps.utils.models import BaseModel


class RegimenTributario(BaseModel):
    nombre = models.CharField(max_length=255, help_text="Nombre", )
    tributario = models.ForeignKey('self', null=True, related_name='self_tributario', on_delete=models.CASCADE)
    codigo = models.CharField(max_length=3, help_text="codigo", blank=True, null=True)

    def __str__(self):
        """Return post title."""
        return '{}:{}'.format(self.nombre, self.tributario)

    class Meta:
        """Meta class."""
        ordering = ['-created', '-modified']


class Contribuyente(BaseModel):
    nombre = models.CharField(max_length=255, help_text="Nombre", )

    def __str__(self):
        """Return post title."""
        return '{}'.format(self.nombre, )

    class Meta:
        """Meta class."""
        ordering = ['-id']

class Tributario(BaseModel):
    nombre = models.CharField(max_length=255, help_text="Nombre", )

    def __str__(self):
        """Return post title."""
        return '{}'.format(self.nombre, )

    class Meta:
        """Meta class."""
        ordering = ['-id']

