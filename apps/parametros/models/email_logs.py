from django.db import models
from django.utils import timezone

"""
Modelo de bitácora para el seguimiento de correos electrónicos enviados.
"""

# ---------------------------------------------------------------------------
# Constantes / choices
# ---------------------------------------------------------------------------

class EstadoEnvio(models.TextChoices):
    EXITOSO  = "exitoso",  "Exitoso"
    FALLIDO  = "fallido",  "Fallido"
    PENDIENTE = "pendiente", "Pendiente"


class CategoriaError(models.TextChoices):
    """
    Categorías de error para facilitar el filtrado y las alertas.

    DESTINATARIO  → el problema está en la dirección de correo del receptor (formato inválido, dominio inexistente, buzón lleno, rebote)
    REMITENTE     → credenciales incorrectas, cuenta suspendida, límite de envíos
    SMTP          → fallo de conexión, timeout, TLS, puerto bloqueado
    ADJUNTO       → archivo no encontrado, tamaño excedido, tipo MIME inválido
    PLANTILLA     → error al renderizar el template Django (TemplateDoesNotExist, TemplateSyntaxError, variable faltante, etc.)
    CONFIGURACION → parámetros SMTP/remitente ausentes o mal configurados en BD
    TRACKING      → configuración de tracking inválida (status 500)
    DESCONOCIDO   → cualquier otra excepción no categorizada
    """
    DESTINATARIO  = "destinatario",  "Dirección del destinatario"
    REMITENTE     = "remitente",     "Credenciales / cuenta remitente"
    SMTP          = "smtp",          "Conexión SMTP"
    ADJUNTO       = "adjunto",       "Adjunto inválido o no encontrado"
    PLANTILLA     = "plantilla",     "Error en la plantilla de correo"
    CONFIGURACION = "configuracion", "Configuración faltante o incorrecta"
    TRACKING      = "tracking",      "Configuración de tracking inválida"
    DESCONOCIDO   = "desconocido",   "Error desconocido"


class TipoRemitente(models.TextChoices):
    GENERAL        = "general",        "Correo general"
    PROPIETARIOS   = "propietarios",   "Correo propietarios"
    ARRENDATARIOS  = "arrendatarios",  "Correo arrendatarios"
    COMERCIAL      = "comercial",      "Correo comercial"
    ADMINISTRACION = "administracion", "Correo administración"
    CARTERA        = "cartera",        "Correo cartera"
    REPARACIONES   = "reparaciones",   "Correo reparaciones"
    CORRESPONDENCIA = "correspondencia", "Correspondencia (tipo 2)"
    DESCONOCIDO    = "desconocido",    "Desconocido"


# Mapa senddif.tipo → TipoRemitente (para el helper en email.py)
TIPO_REMITENTE_MAP = {
    None: TipoRemitente.GENERAL,
    2:    TipoRemitente.CORRESPONDENCIA,
    3:    TipoRemitente.PROPIETARIOS,
    4:    TipoRemitente.ARRENDATARIOS,
    5:    TipoRemitente.COMERCIAL,
    6:    TipoRemitente.ADMINISTRACION,
    7:    TipoRemitente.CARTERA,
    8:    TipoRemitente.REPARACIONES,
}


# ---------------------------------------------------------------------------
# Modelo principal
# ---------------------------------------------------------------------------

class EmailLog(models.Model):
    """
    Registro de cada intento de envío de correo electrónico.

    Un registro se crea ANTES de intentar el envío (estado=PENDIENTE) y se
    actualiza al terminar (EXITOSO o FALLIDO). Esto permite detectar envíos
    que quedaron colgados si el proceso muere en medio del intento.
    """

    # -- Identificación del envío ------------------------------------------
    fecha_intento   = models.DateTimeField(default=timezone.now, db_index=True, verbose_name="Fecha y hora del intento")
    fecha_resultado = models.DateTimeField(null=True, blank=True, verbose_name="Fecha y hora del resultado")

    # -- Remitente ----------------------------------------------------------
    tipo_remitente  = models.CharField(max_length=20, choices=TipoRemitente.choices, default=TipoRemitente.DESCONOCIDO, verbose_name="Tipo de remitente")
    correo_remitente = models.EmailField(blank=True, default="", verbose_name="Correo remitente usado")

    # -- Destinatarios ------------------------------------------------------
    # Se almacena como texto separado por comas para evitar una tabla extra en casos de uso simple.
    destinatarios   = models.TextField(verbose_name="Destinatarios (separados por coma)")
    total_destinatarios = models.PositiveSmallIntegerField(default=0, verbose_name="Cantidad de destinatarios")

    # -- Contenido ----------------------------------------------------------
    asunto          = models.TextField(verbose_name="Asunto")
    plantilla       = models.TextField(blank=True, default="", verbose_name="Plantilla usada")

    # -- Estado y error -----------------------------------------------------
    estado          = models.CharField(max_length=25, choices=EstadoEnvio.choices, default=EstadoEnvio.PENDIENTE, db_index=True, verbose_name="Estado del envío")
    categoria_error = models.CharField(max_length=25, choices=CategoriaError.choices, blank=True, default="", db_index=True, verbose_name="Categoría del error")
    mensaje_error   = models.TextField(blank=True, default="", verbose_name="Mensaje de error detallado")
    traceback_error = models.TextField(blank=True, default="", verbose_name="Traceback completo")

    # -- SMTP usado ---------------------------------------------------------
    smtp_host       = models.CharField(max_length=255, blank=True, default="", verbose_name="Host SMTP")
    smtp_port       = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name="Puerto SMTP")

    # -- Metadatos opcionales -----------------------------------------------
    usando_tracking = models.BooleanField(default=False, verbose_name="Usó cuenta de tracking")
    tiene_adjuntos  = models.BooleanField(default=False, verbose_name="Tenía adjuntos")
    total_adjuntos  = models.PositiveSmallIntegerField(default=0, verbose_name="Total de adjuntos")

    class Meta:
        db_table            = "email_log"
        verbose_name        = "Log de correo"
        verbose_name_plural = "Logs de correos"
        ordering            = ["-fecha_intento"]
        indexes             = [
            models.Index(fields=["estado", "fecha_intento"]),
            models.Index(fields=["categoria_error", "fecha_intento"]),
            models.Index(fields=["tipo_remitente", "fecha_intento"]),
        ]

    def __str__(self):
        return (
            f"[{self.fecha_intento:%Y-%m-%d %H:%M}] "
            f"{self.get_estado_display()} | "
            f"{self.asunto[:40]} → {self.destinatarios[:60]}"
        )

    # -- Helpers ------------------------------------------------------------

    def marcar_exitoso(self):
        self.estado          = EstadoEnvio.EXITOSO
        self.fecha_resultado = timezone.now()
        self.save(update_fields=["estado", "fecha_resultado"])

    def marcar_fallido(self, categoria: str, mensaje: str, traceback: str = ""):
        self.estado          = EstadoEnvio.FALLIDO
        self.categoria_error = categoria
        self.mensaje_error   = mensaje[:4000]   # evita truncar en BD pequeñas
        self.traceback_error = traceback[:8000]
        self.fecha_resultado = timezone.now()
        self.save(update_fields=[
            "estado", "categoria_error", "mensaje_error",
            "traceback_error", "fecha_resultado",
        ])


# ---------------------------------------------------------------------------
# Modelo auxiliar para adjuntos (opcional, pero recomendado)
# ---------------------------------------------------------------------------

class EmailLogAdjunto(models.Model):
    """
    Detalle de cada adjunto asociado a un envío.
    Permite registrar exactamente qué archivo falló.
    """
    email_log    = models.ForeignKey(EmailLog, on_delete=models.CASCADE, related_name="adjuntos", verbose_name="Log de correo")
    nombre       = models.CharField(max_length=512, verbose_name="Nombre del archivo")
    ruta         = models.CharField(max_length=1024, blank=True, default="", verbose_name="Ruta en disco (si aplica)")
    desde_memoria = models.BooleanField(default=False, verbose_name="Adjunto desde memoria (bytes)")
    mimetype     = models.CharField(max_length=128, blank=True, default="", verbose_name="MIME type")
    existe       = models.BooleanField(default=True, verbose_name="El archivo existía al momento del envío")

    class Meta:
        db_table            = "email_log_adjunto"
        verbose_name        = "Adjunto de log"
        verbose_name_plural = "Adjuntos de log"

    def __str__(self):
        return f"{self.nombre} ({'memoria' if self.desde_memoria else self.ruta})"