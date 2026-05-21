from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel

class Mayor(BaseModel):
    history     = HistoricalRecords()
    codigo        = models.CharField(max_length=45, blank=True, null=True)
    nombre        = models.CharField(max_length=250, blank=True, null=True)  
    tipo          = models.CharField(max_length=50, blank=True, null=True)
    estado        = models.BooleanField(default=True)
    maneja_nits   = models.BooleanField(default=False, blank=True, null=True)
    maneja_base   = models.BooleanField(default=False, blank=True, null=True)
    maneja_ccosto = models.BooleanField(default=False, blank=True, null=True)
    cuenta_cxc    = models.BooleanField(default=False, blank=True, null=True)
    cuenta_cxp    = models.BooleanField(default=False, blank=True, null=True)
    flujocaja     = models.BooleanField(default=False, blank=True, null=True)
    naturaleza = models.CharField(
        max_length=1,
        choices=(
            ('D', 'Débito'),
            ('C', 'Crédito')
        )
    )
    nittercero    = models.BooleanField(default=False, blank=True, null=True)

    def __str__(self):
        try:
            return self.nombre
        except:
            return ''




