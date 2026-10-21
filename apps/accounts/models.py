from django.db import models

from django.contrib.auth.models import AbstractUser
from django.db import models

from django.conf import settings

class Usuario(AbstractUser):
    pass

class RegistroIngreso(models.Model):
    """Auditoría de inicios de sesión exitosos en la plataforma."""

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='registros_ingreso',
    )
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    direccion_ip = models.GenericIPAddressField(null=True, blank=True)
    agente_usuario = models.TextField(blank=True, default='')

    class Meta:
        db_table = '_auth_registros_ingreso'
        ordering = ['-fecha_ingreso']
        verbose_name = 'registro de ingreso'
        verbose_name_plural = 'registros de ingreso'

    def __str__(self):
        return '{} - {}'.format(self.usuario, self.fecha_ingreso)