from django.db import models
from simple_history.models import HistoricalRecords

from apps.utils.models import BaseModel

class Cargo(BaseModel):
    history = HistoricalRecords()
    nombre = models.CharField(max_length=100, blank=True, null=True)
    estado = models.BooleanField(default=True)