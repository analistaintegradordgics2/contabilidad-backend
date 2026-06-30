from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from apps.utils.models import BaseModel
import os
import base64
from django.contrib.auth.models import Permission, Group
import pdb


def image_as_base64(image_file, format='png'):
    """
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """
    if not os.path.isfile(image_file):
        return None
    encoded_string = ''
    with open(image_file, 'rb') as img_f:
        encoded_string = str(base64.b64encode(img_f.read()),'utf-8')
    return 'data:image/%s;base64,%s' % (format.lower(), encoded_string)

def get_upload_path(instance, filename):
    return os.path.join(
      "{}".format(instance.content_type.app_label), "carpeta_{}".format(instance.object_id), filename)


class Archivo(BaseModel):
    name = models.TextField(help_text="Nombre Archivos")
    src = models.FileField(upload_to=get_upload_path, max_length=None)
    # Below the mandatory fields for generic relation
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()
    tipo = models.CharField(
        max_length=255,
        help_text="Tipo",
        blank=True,
        null=True,
    )
    orden = models.IntegerField(
        blank=True,
        null=True,
        help_text="Ordenar los archivos",
    )
    url_s3 = models.TextField(null=True, blank=True, help_text="URL de S3 DigitalOceans")

    def img_base64(self):  
        try:
            # pdb.set_trace()
            imagen = self.src.path
            extension = os.path.splitext(imagen)[1].replace(".","")
            imagen  = image_as_base64(imagen,extension)
            return imagen
        except:
            return None

class Menu(models.Model):
    OPCIONES_ICONOS = [
        ('fact_check', 'DIRECTORIO'),
    ]

    titulo      =  models.CharField(max_length=80, help_text="Titulo del menu")
    icono       =  models.CharField(max_length=30, default=None, null=True, blank=True, help_text="Icono del menu",choices= OPCIONES_ICONOS)
    colorico    =  models.CharField(max_length=30, default=None, null=True, blank=True, help_text="color del icono del menu")
    ruta        =  models.CharField(max_length=80, default=None, null=True, blank=True, help_text="ruta del menu")
    orden       =  models.CharField(max_length=10, null=True, blank=True, help_text="orden del menu")
    menu_padre  =  models.ForeignKey('Menu', on_delete=models.CASCADE, blank=True, null=True, default=None, help_text="Menu padre")
    permiso     =  models.CharField(max_length=255, default=None, null=True, blank=True, help_text="permiso")
    codigo      =  models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['orden']

        
    def __str__(self):
        try:
            return self.titulo
        except:
            return ""

class PermisosMenuAcciones(models.Model):
    # permiso_menu = models.CharField(max_length=255, help_text="Permiso menu", blank=True, null=True)
    # permiso_accion = models.CharField(max_length=255, help_text="Permiso accion", blank=True, null=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="menu_permiso_menu", blank=True, null=True)
    accion = models.CharField(max_length=255, help_text="Nombre de la accion", blank=True, null=True)
    permiso  = models.ForeignKey(Permission, on_delete=models.CASCADE, related_name="menu_acciones_permiso", blank=True, null=True)
    # grupo = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="menu_permiso_grupo", blank=True, null=True)

    class Meta:
        """Meta class."""
        db_table = 'public_permisos_menu_acciones'

class DiasFestivos(models.Model):
    mes = models.CharField(max_length=2, help_text="Número de mes", blank=True, null=True)
    dia = models.CharField(max_length=2, help_text="Número de día", blank=True, null=True)
    anio = models.CharField(max_length=4, help_text="Número de año", blank=True, null=True)
    fecha = models.DateField(help_text='Fecha completa', blank=True, null=True)

    class Meta:
        """Meta class."""
        db_table = 'conf_dias_festivos'

class ProveedoresTecnologicos(models.Model):
    nombre = models.CharField(max_length=100)
    estado = models.BooleanField(default=True)

    class Meta:
        """Meta class."""
        db_table = 'conf_proveedores_tecnologicos'

class ControlErrores(BaseModel):
    nombre_apps = models.TextField(help_text='Nombre de la aplicación')
    nombre_viewset = models.TextField(help_text='Nombre del ViewSet')
    nombre_funcion = models.TextField(help_text='Nombre de la funcion')
    descripcion_error = models.TextField(help_text='Error retornado por la excepción')
    script_sql = models.TextField(help_text='Script sql ejecutado',  blank=True, null=True)
    
    class Meta:
        """Meta class."""
        db_table = 'public_control_errores'
    
class ProcedimientoSync(models.Model):
    nombre = models.CharField(max_length=50, help_text='Nombre del procedimiento')
    hash = models.CharField(max_length=64, help_text='Hash del procedimiento (para validar si es el mismo o si se cambió)')
    fecha_sync = models.DateTimeField()
    
    class Meta:
        """Meta class."""
        db_table = 'procedimientos_sync'