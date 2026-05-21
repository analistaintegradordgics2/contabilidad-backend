from django.db import models
from simple_history.models import HistoricalRecords
from apps.utils.models import BaseModel

class TipoContacto(BaseModel):
    nombre = models.CharField(max_length=50, help_text="Nombre", )


class Telefono(BaseModel):
    history = HistoricalRecords()

    persona = models.ForeignKey(
        "personas.Persona", 
        on_delete=models.CASCADE,
        related_name='telefonos_personas'
    )
    tipo = models.ForeignKey(
        TipoContacto,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='telefono_tipo_contacto'
    )
    valor = models.CharField(max_length=255, help_text="Teléfono", )
    sms = models.BooleanField(blank=True, null=True)
    prefijo = models.CharField(max_length=10, blank=True, null=True, default="+57", help_text="Prefijo")
    eliminado = models.BooleanField(blank=True, null=True)
    usar_en_portales = models.BooleanField(default=False, blank=False, null=True)


class Direccion(BaseModel):
    history = HistoricalRecords()

    persona = models.ForeignKey(
        "personas.Persona",
        on_delete=models.CASCADE,
        related_name='direcciones_personas'
    )
    tipo = models.ForeignKey(
        TipoContacto,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    barrio = models.ForeignKey(
        'parametros.Barrio',
        related_name='direccion_barrio_personas',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    ciudad = models.ForeignKey(
        'parametros.Ciudad',
        related_name='direccion_ciudad_personas',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    descripcion = models.CharField(
        max_length=255, help_text="Descripción",
    )
    codigo_postal = models.CharField(
        max_length=10, help_text="Codigo postal", blank=True, null=True
    )
    incluir_a_factura = models.BooleanField(blank=True, null=True)
    eliminado = models.BooleanField(blank=True, null=True)
    usar_en_portales = models.BooleanField(default=False, blank=False, null=True)


class DatosContactoPersona(BaseModel):
    
    history = HistoricalRecords()
    # personas = models.ForeignKey(Persona,on_delete=models.CASCADE,related_name='info_contacto')
    documento = models.CharField(max_length=50,blank=True,null=True,  help_text="documento")
    n_completo = models.CharField(max_length=100,blank=True,null=True,  help_text="nombre")
    ciudad = models.ForeignKey('parametros.Ciudad',related_name='direccion_ciudad_info_contacto',on_delete=models.SET_NULL,blank=True,null=True)
    barrio = models.ForeignKey('parametros.Barrio',related_name='info_contacto_barrio', on_delete=models.SET_NULL,blank=True,null=True)
    descripcion = models.CharField(max_length=255,blank=True,null=True,  help_text="descripcion")
    email = models.CharField(max_length=255,blank=True,null=True,  help_text="email")
    telefono_fijo = models.CharField(max_length=255,blank=True,null=True,  help_text="telefono_fijo")
    telefono_movil = models.CharField(max_length=255,blank=True,null=True,  help_text="telefono_movil")
    observaciones = models.CharField(max_length=255,blank=True,null=True,  help_text="observaciones")

    class Meta:
        """Meta class."""
        db_table = 'personas_datos_contacto'

class DatosContactoPersonaPersonas(BaseModel):
    
    personas = models.ForeignKey("personas.Persona",on_delete=models.CASCADE,related_name='persona_contacto')
    contacto = models.ForeignKey(DatosContactoPersona,on_delete=models.CASCADE,related_name='info_contacto')

    class Meta:
        """Meta class."""
        db_table = 'personas_datos_contacto_personas'

