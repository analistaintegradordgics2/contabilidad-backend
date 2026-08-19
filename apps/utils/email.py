# Django
from django.conf import settings
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template import TemplateDoesNotExist
from django.template.exceptions import TemplateSyntaxError
from django.template.loader import render_to_string
from django.db import connection as db_connection

from apps.parametros.models.parametrizacion import Parametros
from apps.parametros.models.email_logs import (
    CategoriaError,
    EmailLog,
    EmailLogAdjunto,
    EstadoEnvio,
    TipoRemitente,
    TIPO_REMITENTE_MAP,
)
from cryptography.fernet import Fernet

# Standard library
import os, traceback, logging, pdb
import threading
import time
import atexit
import smtplib
from functools import lru_cache
from typing import Optional
import time


# ---------------------------------------------------------------------------
# Pool global de conexiones SMTP reutilizables
# ---------------------------------------------------------------------------

_SMTP_LOCAL = threading.local()
_SMTP_LOCK = threading.Lock()

# ---------------------------------------------------------------------------
# Rate limiter SMTP
# ---------------------------------------------------------------------------

class _SmtpRateLimiter:

    MIN_INTERVALO: float = 0.3

    def __init__(self):
        self._lock = threading.Lock()
        self._ultimo_envio = {}

    def esperar(self, correo_remitente):

        while True:

            with self._lock:

                ahora = time.monotonic()
                ultimo = self._ultimo_envio.get(correo_remitente, 0)

                espera = self.MIN_INTERVALO - (ahora - ultimo)

                if espera <= 0:
                    self._ultimo_envio[correo_remitente] = ahora
                    return

            time.sleep(min(espera, 0.1))


_smtp_rate_limiter = _SmtpRateLimiter()

# ---------------------------------------------------------------------------
# Caché de parámetros
# ---------------------------------------------------------------------------
# lru_cache guarda el resultado de la primera llamada y lo reutiliza en las
# llamadas posteriores dentro del mismo proceso. Esto evita que, al hacer un
# bucle de envíos, cada iteración lance N queries a la base de datos para
# cargar la misma configuración.
#
# INVALIDACIÓN: si necesitas refrescar los parámetros sin reiniciar el servidor,
# llama a `_get_smtp_config.cache_clear()` o `_get_sender_config.cache_clear()`.
# ---------------------------------------------------------------------------

@lru_cache(maxsize=1)
def _get_smtp_config():
    """Retorna host y puerto SMTP desde Parametros (cacheado)."""
    host = Parametros.objects.filter(parametro="smtp_correo_generales").values_list("valor", flat=True).first()
    port = Parametros.objects.filter(parametro="puerto_smtp_correo_generales").values_list("valor", flat=True).first()

    host = (host or "smtp.gmail.com").lower()

    try:
        port = int(port) if port else 587
    except (ValueError, TypeError):
        port = 587

    return host, port


@lru_cache(maxsize=None)
def _get_sender_config(parametro: str):
    """
    Retorna (email, password_descifrada) para un parámetro de correo dado.
    Ejemplo de valores para `parametro`:
        'correo_generales', 'correo_para_propietarios', 'correo_para_arrendatarios', ...
    """
    obj = Parametros.objects.filter(parametro=parametro).first()
    if not obj or not obj.valor or not obj.valor2:
        return None, None

    password = Fernet(obj.key.encode("utf-8")).decrypt(obj.valor2.encode("utf-8")).decode()
    return obj.valor, password


@lru_cache(maxsize=1)
def _get_tracking_config():
    """
    Retorna el diccionario de configuración de tracking (cacheado).
    Estructura: {"tracking": bool, "email": str|None, "password": str|None, "status": int}
    """
    result = {"status": 200, "tracking": False, "email": None, "password": None}

    param = Parametros.objects.filter(parametro="enviar_email_tracking").first()
    if not param or not param.valor or param.valor.lower() != "true":
        return result

    email_obj    = Parametros.objects.filter(parametro="email_tracking").first()
    password_obj = Parametros.objects.filter(parametro="password_email_tracking").first()

    if email_obj and email_obj.valor and password_obj and password_obj.valor:
        result.update({"tracking": True, "email": email_obj.valor, "password": password_obj.valor})
    else:
        result["status"] = 500

    return result


# ---------------------------------------------------------------------------
# Mapa de tipos de envío
# ---------------------------------------------------------------------------
# Relaciona cada tipo (int) con el nombre del parámetro en la tabla Parametros.
# Agregar un nuevo tipo solo requiere una línea aquí.
# ---------------------------------------------------------------------------

_TIPO_PARAMETRO = {}


# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------

def _build_connection(host, port, username, password, use_tls=True):
    """
    Retorna una conexión SMTP reutilizable POR HILO.

    Cada hilo mantiene su propia conexión SMTP.
    Esto evita problemas de concurrencia/thread-safety.
    """

    key = f"{host}:{port}:{username}:{use_tls}"

    # Crear almacenamiento por hilo si no existe
    if not hasattr(_SMTP_LOCAL, "connections"):
        _SMTP_LOCAL.connections = {}

    connections = _SMTP_LOCAL.connections

    conn = connections.get(key)

    if conn:

        try:
            conn.connection.noop()
            return conn

        except Exception:

            try:
                conn.close()
            except Exception:
                pass

            connections.pop(key, None)

    # Crear nueva conexión
    conn = get_connection(
        host=host,
        port=port,
        username=username,
        password=password,
        use_tls=use_tls
    )

    ultimo_error = None

    for intento in range(2):

        try:

            conn.open()

            connections[key] = conn

            return conn

        except Exception as exc:

            ultimo_error = exc

            try:
                conn.close()
            except Exception:
                pass

            time.sleep(1)

    raise ultimo_error


def _resolve_credentials(base_email, base_password, tracking):
    """
    Decide qué credenciales usar para la conexión SMTP según la configuración
    de tracking. Si el tracking está activo, usa sus credenciales; de lo
    contrario usa las credenciales base del remitente.
    """
    if tracking["tracking"]:
        return tracking["email"], tracking["password"]
    return base_email, base_password


def _build_msg_from_general(host, port, content, subject, recipients, tracking):
    """Construye el mensaje usando el correo general configurado."""
    sender_email, sender_password = _get_sender_config("correo_generales")

    if sender_email:
        conn_email, conn_password = _resolve_credentials(sender_email, sender_password, tracking)
        conn = _build_connection(host, port, conn_email, conn_password)
        return EmailMultiAlternatives(subject, content, sender_email, recipients, connection=conn), sender_email

    raise ValueError(f"No se encontraron credenciales para (correo_generales).")


def _build_msg_from_tipo(tipo, host, port, content, subject, recipients, tracking):
    """
    Construye el mensaje para los tipos 3-8 usando el parámetro correspondiente.

    El tipo 8 (reparaciones) tiene un comportamiento especial heredado del código
    original: si su correo no está configurado en Parametros (valor o valor2 vacíos),
    en lugar de fallar cae silenciosamente al correo general. Para señalar ese caso,
    retorna None y el llamador (`_build_message`) se encarga de hacer el fallback.

    Los tipos 3-7 se asume que siempre tienen credenciales; si no las tienen se lanza
    un ValueError para que el error sea visible.
    """
    parametro = _TIPO_PARAMETRO[tipo]
    sender_email, sender_password = _get_sender_config(parametro)

    if not sender_email:
        if tipo == 8:
            # Sin credenciales configuradas → el llamador usará el correo general
            return None
        raise ValueError(f"No se encontraron credenciales para el tipo {tipo} ({parametro}).")

    conn_email, conn_password = _resolve_credentials(sender_email, sender_password, tracking)
    conn = _build_connection(host, port, conn_email, conn_password)
    return EmailMultiAlternatives(subject, content, sender_email, recipients, connection=conn), sender_email


# ---------------------------------------------------------------------------
# Funciones públicas
# ---------------------------------------------------------------------------

def get_correos_personas(correos):
    """
    Recibe una lista de correos y retorna todos los correos asociados a esas
    personas en personas_persona, incluyendo sus correos adicionales.
    """
    if not isinstance(correos, list):
        raise ValueError("El argumento 'correos' debe ser una lista de correos electrónicos.")

    all_correos = []
    correos_limpios = [
        c.strip().lower().replace("\r", "").replace("\n", "")
        for c in correos if c not in (None, "")
    ]

    if not correos_limpios:
        return all_correos

    # Una sola query con IN en lugar de un loop de queries individuales
    placeholders = ", ".join(["%s"] * len(correos_limpios))
    sql = f"""
        SELECT COALESCE(json_agg(json_build_object(
            'id',                 tp.id,
            'email',              lower(trim(tp.email))
        )), '[]'::json)
        FROM (
            SELECT tp.id, tp.email
            FROM personas_persona tp
            WHERE lower(trim(tp.email)) IN ({placeholders})
        ) tp;
    """

    with db_connection.cursor() as cursor:
        cursor.execute(sql, correos_limpios)
        resultado = cursor.fetchone()

    encontrados_set = set()
    personas = resultado[0] if resultado and resultado[0] else []

    for item in personas:
        email = item.get("email", "")
        if email and email not in all_correos:
            all_correos.append(email)
            encontrados_set.add(email)

        adicionales = item.get("emails_adicionales", "") or ""
        for correo_adicional in adicionales.split(";"):
            correo_adicional = correo_adicional.strip()
            if correo_adicional and correo_adicional not in all_correos:
                all_correos.append(correo_adicional)

    # Correos que no están en la BD se agregan tal cual
    for correo in correos_limpios:
        if correo not in encontrados_set and correo not in all_correos:
            all_correos.append(correo)

    return all_correos


def get_correo_tracking():
    """
    Retorna la configuración de tracking. Delega al caché interno.
    Mantenida por compatibilidad; el caché evita queries repetidas.
    """
    return _get_tracking_config()


def sendCorreoGenerales(my_host, my_port, content, subject, to):
    """
    Construye y retorna un mensaje de correo usando el remitente general.
    Firma idéntica a la versión original.
    """
    all_correos = get_correos_personas(to) if not _is_already_resolved(to) else to
    tracking    = _get_tracking_config()
    msg, _      = _build_msg_from_general(my_host, my_port, content, subject, all_correos, tracking)
    return msg


def send_email_client(template, body, subject, to, files, senddif=None, attachments_memory=None):
    """
    Envía un correo electrónico según la configuración de `senddif` y registra
    el resultado en EmailLog.

    senddif=None   → correo general configurado en Parametros
    """
    files              = files or []
    attachments_memory = attachments_memory or []
    tipo_senddif       = senddif.get("tipo") if senddif else None
    tipo_remitente     = TIPO_REMITENTE_MAP.get(tipo_senddif, TipoRemitente.DESCONOCIDO)

    host, port = _get_smtp_config()
    tracking   = _get_tracking_config()

    # -- Validación de tracking -------------------------------------------------
    if tracking["tracking"] and tracking["status"] == 500:
        _crear_log_fallido(
            asunto          = subject,
            destinatarios   = to,
            tipo_remitente  = tipo_remitente,
            correo_remitente= "",
            smtp_host       = host,
            smtp_port       = port,
            usando_tracking = True,
            template        = template,
            files           = files,
            attachments_memory = attachments_memory,
            categoria       = CategoriaError.TRACKING,
            mensaje         = "Configuración de tracking inválida (status 500). Envío cancelado.",
        )
        return False

    # -- Resolver destinatarios -------------------------------------------------
    try:
        all_correos = get_correos_personas(to)
    except Exception as exc:
        tb = traceback.format_exc()
        _crear_log_fallido(
            asunto          = subject,
            destinatarios   = to,
            tipo_remitente  = tipo_remitente,
            correo_remitente= "",
            smtp_host       = host,
            smtp_port       = port,
            usando_tracking = tracking["tracking"],
            template        = template,
            files           = files,
            attachments_memory = attachments_memory,
            categoria       = CategoriaError.DESTINATARIO,
            mensaje         = str(exc),
            tb              = tb,
        )
        return False

    # -- Renderizar plantilla ---------------------------------------------------
    try:
        content = render_to_string(template, body)
    except (TemplateDoesNotExist, TemplateSyntaxError) as exc:
        tb = traceback.format_exc()
        _crear_log_fallido(
            asunto          = subject,
            destinatarios   = all_correos,
            tipo_remitente  = tipo_remitente,
            correo_remitente= "",
            smtp_host       = host,
            smtp_port       = port,
            usando_tracking = tracking["tracking"],
            template        = template,
            files           = files,
            attachments_memory = attachments_memory,
            categoria       = CategoriaError.PLANTILLA,
            mensaje         = f"{type(exc).__name__}: {exc}",
            tb              = tb,
        )
        return False
    except Exception as exc:
        tb = traceback.format_exc()
        _crear_log_fallido(
            asunto          = subject,
            destinatarios   = all_correos,
            tipo_remitente  = tipo_remitente,
            correo_remitente= "",
            smtp_host       = host,
            smtp_port       = port,
            usando_tracking = tracking["tracking"],
            template        = template,
            files           = files,
            attachments_memory = attachments_memory,
            categoria       = CategoriaError.PLANTILLA,
            mensaje         = f"Error inesperado en plantilla: {exc}",
            tb              = tb,
        )
        return False

    # -- Construir mensaje y detectar correo remitente --------------------------
    correo_remitente = ""
    try:
        msg, correo_remitente = _build_message(senddif, host, port, content, subject, all_correos, tracking)
    except Exception as exc:
        # Parámetro de configuración faltante en BD
        tb = traceback.format_exc()
        _crear_log_fallido(
            asunto          = subject,
            destinatarios   = all_correos,
            tipo_remitente  = tipo_remitente,
            correo_remitente= correo_remitente,
            smtp_host       = host,
            smtp_port       = port,
            usando_tracking = tracking["tracking"],
            template        = template,
            files           = files,
            attachments_memory = attachments_memory,
            categoria       = CategoriaError.CONFIGURACION,
            mensaje         = str(exc),
            tb              = tb,
        )
        return False

    # -- Crear registro pendiente (antes de intentar el envío) ------------------
    log_entry = _crear_log_pendiente(
        asunto           = subject,
        destinatarios    = all_correos,
        tipo_remitente   = tipo_remitente,
        correo_remitente = correo_remitente,
        smtp_host        = host,
        smtp_port        = port,
        usando_tracking  = tracking["tracking"],
        template         = template,
        files            = files,
        attachments_memory = attachments_memory,
    )

    # -- Adjuntar alternativa HTML ----------------------------------------------
    msg.attach_alternative(content, "text/html")
    msg.content_subtype = "html"

    # -- Adjuntar archivos desde disco -----------------------------------------
    adjunto_error = _attach_files_logged(msg, files, log_entry)
    if adjunto_error:
        log_entry.marcar_fallido(
            categoria  = CategoriaError.ADJUNTO,
            mensaje    = adjunto_error,
        )
        return False

    # -- Adjuntar archivos desde memoria ----------------------------------------
    adjunto_mem_error = _attach_memory_logged(msg, attachments_memory, log_entry)
    if adjunto_mem_error:
        log_entry.marcar_fallido(
            categoria  = CategoriaError.ADJUNTO,
            mensaje    = adjunto_mem_error,
        )
        return False

    # -- Enviar ----------------------------------------------------------------
    try:

        # Esperar según rate limiter
        _smtp_rate_limiter.esperar(correo_remitente)

        # Intentar envío
        msg.send()
        log_entry.marcar_exitoso()
        return True

    except smtplib.SMTPServerDisconnected:

        try:

            # Reabrir conexión SMTP automáticamente
            if msg.connection:
                msg.connection.close()
                msg.connection.open()

            # Reintento
            _smtp_rate_limiter.esperar(correo_remitente)

            msg.send()

            log_entry.marcar_exitoso()
            return True

        except Exception as exc:

            tb  = traceback.format_exc()
            cat = _categorizar_error_smtp(exc)

            log_entry.marcar_fallido(
                categoria  = cat,
                mensaje    = str(exc),
                traceback  = tb,
            )

            return False

    except Exception as exc:
        tb  = traceback.format_exc()
        cat = _categorizar_error_smtp(exc)
        log_entry.marcar_fallido(
            categoria  = cat,
            mensaje    = str(exc),
            traceback  = tb,
        )
        return False


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------

def _is_already_resolved(to):
    """
    Detecta si `to` ya es una lista de correos resueltos (evita doble lookup).
    Heurística simple: si todos los elementos tienen '@' se asume resueltos.
    """
    return isinstance(to, list) and all("@" in c for c in to)


def _build_message(senddif, host, port, content, subject, recipients, tracking):
    """Despacha la construcción del mensaje según el tipo de senddif."""
    if senddif is None:
        msg, sender = _build_msg_from_general(host, port, content, subject, recipients, tracking)
        return msg, sender

    tipo = senddif.get("tipo")

    if tipo == 2:
        # Credenciales directas en senddif (correspondencia)
        sender_email = senddif["model"]["correo"]
        sender_password = senddif["model"]["password"]
        conn_email, conn_password = _resolve_credentials(sender_email, sender_password, tracking)
        conn = _build_connection(host, port, conn_email, conn_password)
        return EmailMultiAlternatives(subject, content, sender_email, recipients, connection=conn), sender_email

    if tipo in _TIPO_PARAMETRO:
        msg, sender = _build_msg_from_tipo(tipo, host, port, content, subject, recipients, tracking)
        if msg is not None:
            return msg, sender
        # Tipo 8 sin credenciales → fallback a general
        return _build_msg_from_general(host, port, content, subject, recipients, tracking)

    raise ValueError(f"Tipo de envío desconocido: {tipo}")


def _attach_files(msg, files):
    """Adjunta archivos desde el sistema de archivos (original, sin logging)."""
    for file in files:
        if os.path.exists(file):
            msg.attach_file(file)


def _attach_files_logged(msg, files, log_entry) -> Optional[str]:
    """
    Adjunta archivos desde disco y registra cada adjunto en EmailLogAdjunto.
    Retorna un mensaje de error si algún archivo no existe, None si todo OK.
    """
    missing = []
    for file in files:
        existe = os.path.exists(file)
        EmailLogAdjunto.objects.create(
            email_log     = log_entry,
            nombre        = os.path.basename(file),
            ruta          = file,
            desde_memoria = False,
            existe        = existe,
        )
        if existe:
            try:
                msg.attach_file(file)
            except Exception as exc:
                return f"Error adjuntando el archivo '{file}': {exc}"
        else:
            missing.append(file)

    if missing:
        return f"Archivos no encontrados: {', '.join(missing)}"
    return None


def _attach_memory_logged(msg, attachments_memory, log_entry) -> Optional[str]:
    """
    Adjunta archivos desde memoria y los registra en EmailLogAdjunto.
    Retorna mensaje de error si falla, None si todo OK.
    """
    for item in attachments_memory:
        EmailLogAdjunto.objects.create(
            email_log     = log_entry,
            nombre        = item.get("filename", "sin_nombre"),
            desde_memoria = True,
            mimetype      = item.get("mimetype", "application/octet-stream"),
            existe        = True,
        )
        try:
            msg.attach(
                item["filename"],
                item["content"],
                item.get("mimetype", "application/octet-stream"),
            )
        except Exception as exc:
            return f"Error adjuntando archivo en memoria '{item.get('filename')}': {exc}"
    return None


def _categorizar_error_smtp(exc: Exception) -> str:
    """
    Intenta inferir la categoría del error a partir del tipo de excepción
    y del mensaje de error. Retorna un valor de CategoriaError.
    """
    import smtplib
    msg = str(exc).lower()

    # Errores de autenticación / credenciales
    if isinstance(exc, smtplib.SMTPAuthenticationError):
        return CategoriaError.REMITENTE

    # Destinatario rechazado por el servidor
    if isinstance(exc, smtplib.SMTPRecipientsRefused):
        return CategoriaError.DESTINATARIO

    # Errores de conexión / TLS / timeout
    if isinstance(exc, (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, smtplib.SMTPHeloError, ConnectionRefusedError, TimeoutError)):
        return CategoriaError.SMTP

    # Heurísticas sobre el mensaje de texto
    if any(k in msg for k in ("invalid address", "bad destination", "user unknown", "mailbox not found", "no such user", "does not exist", "recipient", "550", "551", "552", "553", "554")):
        return CategoriaError.DESTINATARIO

    if any(k in msg for k in ("authentication", "credentials", "username", "password", "535", "534", "530")):
        return CategoriaError.REMITENTE

    if any(k in msg for k in ("connection", "timeout", "tls", "ssl", "eof", "refused", "network", "socket")):
        return CategoriaError.SMTP

    return CategoriaError.DESCONOCIDO


# ---------------------------------------------------------------------------
# Helpers para crear registros en EmailLog
# ---------------------------------------------------------------------------

def _build_log_kwargs(asunto, destinatarios, tipo_remitente, correo_remitente, smtp_host, smtp_port, usando_tracking, template, files, attachments_memory):
    """Construye el diccionario base de campos para EmailLog."""
    dest_list = destinatarios if isinstance(destinatarios, list) else list(destinatarios)
    return dict(
        asunto               = asunto[:500],
        destinatarios        = ", ".join(dest_list),
        total_destinatarios  = len(dest_list),
        tipo_remitente       = tipo_remitente,
        correo_remitente     = correo_remitente or "",
        smtp_host            = smtp_host or "",
        smtp_port            = smtp_port,
        usando_tracking      = usando_tracking,
        plantilla            = template or "",
        tiene_adjuntos       = bool(files or attachments_memory),
        total_adjuntos       = len(files or []) + len(attachments_memory or []),
    )


def _crear_log_pendiente(asunto, destinatarios, tipo_remitente, correo_remitente, smtp_host, smtp_port, usando_tracking, template, files, attachments_memory) -> EmailLog:
    kwargs = _build_log_kwargs(
        asunto, destinatarios, tipo_remitente, correo_remitente,
        smtp_host, smtp_port, usando_tracking, template, files, attachments_memory,
    )
    return EmailLog.objects.create(estado=EstadoEnvio.PENDIENTE, **kwargs)


def _crear_log_fallido(asunto, destinatarios, tipo_remitente, correo_remitente, smtp_host, smtp_port, usando_tracking, template, files, attachments_memory, categoria, mensaje, tb=""):
    kwargs = _build_log_kwargs(
        asunto, destinatarios, tipo_remitente, correo_remitente,
        smtp_host, smtp_port, usando_tracking, template, files, attachments_memory,
    )
    EmailLog.objects.create(
        estado          = EstadoEnvio.FALLIDO,
        categoria_error = categoria,
        mensaje_error   = mensaje[:4000],
        traceback_error = tb[:8000],
        **kwargs,
    )