from django.db import models

from apps.utils.models import BaseModel
from apps.personas.models.clasificacion import *
from apps.personas.models.contacto import *
from apps.personas.models.persona import *
from apps.personas.models.tributario import *
from apps.parametros.models.ubicacion import Ciudad
from simple_history.models import HistoricalRecords
from django.contrib.contenttypes.fields import GenericRelation
from apps.public.models import Archivo
from django.conf import settings

class Persona(BaseModel):
    archivos = GenericRelation(Archivo)
    history = HistoricalRecords()
    tipo_persona_save = None

    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='user_persona')
    documento = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nit_tributario = models.CharField(max_length=20, unique=True, null=True, blank=True)
    tipo_documento = models.ForeignKey(TipoDocumento, on_delete=models.SET_NULL, null=True, blank=True)
    genero = models.ForeignKey(Genero, on_delete=models.SET_NULL, null=True, blank=True, related_name='personas_genero')
    estado_civil = models.ForeignKey(EstadoCivil, on_delete=models.SET_NULL, null=True, blank=True,  related_name='personas_estado_civil')
    p_nombre = models.CharField(max_length=250, blank=True, null=True)
    s_nombre = models.CharField(max_length=250, blank=True, null=True)
    p_apellido = models.CharField(max_length=250, blank=True, null=True)
    s_apellido = models.CharField(max_length=250, blank=True, null=True)
    n_completo = models.CharField(max_length=250)
    email = models.EmailField()
    fecha_nacimiento = models.DateField(null=True, blank=True)
    ciudad_expedicion = models.ForeignKey(Ciudad,on_delete=models.CASCADE, related_name='persona_ciudad_expedicion', blank=True, null=True)
    fecha_expedicion = models.DateField( help_text='Fecha de Expedición', blank=True, null=True)
    profesion = models.CharField(max_length=255, help_text="Profesión", blank=True, null=True)
    estado =  models.ForeignKey(EstadoPersona,related_name='estado_persona', on_delete=models.CASCADE,blank=True,null=True)
    observacion = models.CharField(max_length=255, help_text="Observación de la Persona", blank=True, null=True)

    documento_representante_legal = models.CharField(max_length=20, blank=True, null=True)
    ciudad_representante_legal = models.ForeignKey(Ciudad,on_delete=models.CASCADE,related_name='datos_representante_legal_ciudad',blank=True, null=True)
    nombre_representante_legal = models.CharField(max_length=255, blank=True, null=True)
    profesion_representante_legal = models.CharField(max_length=250, help_text="Dirección", blank=True, null=True)

    tipo_persona = models.ManyToManyField(TipoPersona, through='PersonaTipoPersona', through_fields=('persona', 'tipo_persona'))

    def save_tipo_persona(self, tipo_persona):
        tipo_persona_query = TipoPersona.objects.get(pk=tipo_persona)
        self.tipo_persona_save = self.tipo_persona.add(tipo_persona_query)

    
    def save(self, *args, **kwargs):
        
        #Asignar el documento en nit_tributario
        if self.nit_tributario in [None, '']:
            self.nit_tributario = self.documento
        # Convertir a mayusculas
        self.p_nombre = self.p_nombre.strip().upper() if not self.p_nombre in [None, ''] else ''
        self.s_nombre = self.s_nombre.strip().upper() if not self.s_nombre in [None, ''] else ''
        self.p_apellido = self.p_apellido.strip().upper() if not self.p_apellido in [None, ''] else ''
        self.s_apellido = self.s_apellido.strip().upper() if not self.s_apellido in [None, ''] else ''
        
        self.n_completo = self.n_completo.strip().upper() if not self.n_completo in [None,''] else self.n_completo

        if self.n_completo in [None, ''] :
            nombres = self.p_nombre
            apellidos = self.p_apellido

            if not self.s_nombre in [None, ''] :
                nombres = "{} {}".format(nombres, self.s_nombre)

            if not self.s_apellido in [None, ''] :
                apellidos = "{} {}".format(apellidos, self.s_apellido)
            
            self.n_completo = "{} {}".format(apellidos, nombres)

        super().save(*args, **kwargs)

    class Meta:
        """Meta class."""
        ordering = ['-created', '-modified']

class PersonaTipoPersona(BaseModel):
    history = HistoricalRecords()
    
    tipo_persona = models.ForeignKey(TipoPersona, on_delete=models.CASCADE, related_name='personas_tipos_personas_tipo')
    persona = models.ForeignKey(Persona, on_delete=models.CASCADE, related_name='personas_tipos_personas_persona')

    class Meta:
        """Meta class."""
        db_table = 'personas_tipo_persona'

class PersonaTributario(BaseModel):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)
    contribuyente = models.ForeignKey(Contribuyente, related_name='contribuyente', on_delete=models.CASCADE, blank=True, null=True)
    tipo_regimen = models.ForeignKey(RegimenTributario, on_delete=models.SET_NULL, null=True, related_name='datos_tributarios_regimen')
    tipo_actividad = models.ForeignKey(Tributario, on_delete=models.SET_NULL, null=True, related_name='datos_tributarios_tributario')
    agente_retenedor = models.BooleanField(default=False, blank=True, null=True)
    gran_contribuyente = models.BooleanField(default=False, blank=True, null=True)
    autoretenedor = models.BooleanField(default=False, blank=True, null=True)
    autoretenedor_cree = models.BooleanField(default=False, blank=True, null=True)
    no_contribuyente = models.BooleanField(default=False, blank=True, null=True)
    reteica = models.BooleanField(default=False, blank=True, null=True)
    reteiva = models.BooleanField(default=False, blank=True, null=True)
    retefuente = models.BooleanField(default=False, blank=True, null=True)

class PersonaConyuge(BaseModel):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)

    nombre    = models.CharField(max_length=250, help_text="Nombre completo del conyuge", blank=True, null=True)
    documento = models.CharField(max_length=20, blank=True, null=True, unique=True)
    tipo_documento = models.ForeignKey(TipoDocumento, related_name='tipo_documento_conyuge', on_delete=models.CASCADE, blank=True, null=True)
    ciudad_expedicion = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name='datos_conyuge_ciudad_expedicion', blank=True, null=True)
    profesion = models.CharField(max_length=250, help_text="Profesión del conyuge", blank=True, null=True)
    empresa = models.CharField(max_length=250, help_text="Empresa donde labora el conyuge", blank=True, null=True)
    sueldo = models.IntegerField(help_text="Sueldo del conyuge", blank=True, null=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name='datos_conyuge_ciudad', blank=True, null=True)
    tipo_direccion= models.ForeignKey('personas.TipoContacto', on_delete=models.SET_NULL, blank=True, null=True)
    barrio= models.ForeignKey('parametros.Barrio', related_name='datos_conyuge_barrio', on_delete=models.SET_NULL, blank=True, null=True)
    direccion= models.CharField(max_length=250, help_text="Dirección", blank=True, null=True)

class PersonaLaboral(BaseModel):
    persona = models.OneToOneField(Persona, on_delete=models.CASCADE)

    empresa = models.CharField(max_length=255, blank=True, null=True, unique=True)
    ciudad = models.ForeignKey(Ciudad, on_delete=models.CASCADE, related_name='datos_independiente_ciudad', blank=True, null=True)
    tipo_direccion = models.ForeignKey('personas.TipoContacto', related_name='datos_independiente_barrio', on_delete=models.SET_NULL, blank=True, null=True)
    barrio = models.ForeignKey('parametros.Barrio', on_delete=models.SET_NULL, blank=True, null=True)
    direccion = models.CharField(max_length=250, help_text="Dirección de persona independiente", blank=True, null=True)
    descripcion = models.CharField(max_length=250, help_text="Descripción de persona independiente", blank=True, null=True)
    telefono = models.CharField(max_length=20, help_text="Teléfono de contacto de persona independiente", blank=True, null=True)
    patrimonio  = models.IntegerField(help_text="Patrimonio de persona independiente", blank=True, null=True)
    registro_mercantil = models.CharField(max_length=250, help_text="Registro mercantil de persona independiente", blank=True, null=True)
    licencia_funcionamiento = models.CharField(max_length=250, help_text="Licencia de funcionamiento de persona independiente", blank=True, null=True)
    ingreso_neto = models.IntegerField(help_text="Ingreso neto de persona independiente", blank=True, null=True)
