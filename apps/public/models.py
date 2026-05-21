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

    class Meta:
        ordering = ['orden']

        permissions = (
            # Menu Gestion de archivos
            ("view_menu_gestion_archivo", "pm/gestion_archivo/"),
            # Direcctorio de personas
            ("view_menu_gestion_archivo_directorio_personas", "pm/gestion_archivo/directorio_personas/"),
            # Acciones Direcctorio de personas
            ("view_menu_gestion_archivo_directorio_acciones_personas_crear", "pm/gestion_archivo/directorio_personas/acciones/crear"),
            ("view_menu_gestion_archivo_directorio_acciones_personas_editar", "pm/gestion_archivo/directorio_personas/acciones/editar"),
            ("view_menu_gestion_archivo_directorio_acciones_personas_bitacora", "pm/gestion_archivo/directorio_personas/acciones/bitacora"),
            ("view_menu_gestion_archivo_directorio_acciones_personas_cambio_estado", "pm/gestion_archivo/directorio_personas/acciones/cambio_estado"),
            
            # Adminsitracion de inmuebles
            ("view_menu_gestion_archivo_administracion_inmuebles", "pm/gestion_archivo/administracion_inmuebles/"),
            # Acciones Adminsitracion de inmuebles
            ("view_menu_gestion_archivo_administracion_acciones_inmuebles_editar", "pm/gestion_archivo/administracion_inmuebles/acciones/editar"),
            ("view_menu_gestion_archivo_administracion_acciones_inmuebles_bitacora", "pm/gestion_archivo/administracion_inmuebles/acciones/bitacora"),
            
            
            # Menu Facturacion
            ("view_menu_facturacion", "pm/comercial/procesos"),
            # Descuentos en contratos
            ("view_menu_facturacion_descuentos_en_contratos", "pm/comercial/procesos/descuentos_en_contratos"),
            # Acciones Descuentos en contratos
            # - - - - -
            # Novedades
            ("view_menu_facturacion_novedades", "pm/comercial/procesos/novedades"),
            # Acciones Novedades
            ("view_menu_facturacion_novedades_acciones_generar_novedad", "pm/comercial/procesos/novedades/acciones/generar_novedad"),
            # Cupones
            ("view_menu_facturacion_cupones", "pm/factucacion/cupones"),
            # Acciones generar cupones
            ("view_menu_facturacion_cupones_acciones_buscar_copones", "pm/factucacion/cupones/acciones/buscar_copones"),
            ("view_menu_facturacion_cupones_acciones_generar_cupones", "pm/factucacion/cupones/acciones/generar_cupones"),
            ("view_menu_facturacion_cupones_acciones_anular_cupones", "pm/factucacion/cupones/acciones/anular_cupones"),
            ("view_menu_facturacion_cupones_acciones_imprimir_cupones", "pm/factucacion/cupones/acciones/imprimir_cupones"),
            ("view_menu_facturacion_cupones_acciones_parametros", "pm/factucacion/cupones/acciones/parametros"),
            ("view_menu_facturacion_cupones_acciones_enviar_correo", "pm/factucacion/cupones/acciones/enviar_correo"),
            ("view_menu_facturacion_cupones_acciones_general_plano", "pm/factucacion/cupones/acciones/general_plano"),
            ("view_menu_facturacion_cupones_acciones_enviar_whatsapp", "pm/factucacion/cupones/acciones/enviar_whatsapp"),
            ("view_menu_facturacion_cupones_acciones_enviar_zona_cliente", "pm/factucacion/cupones/acciones/enviar_zona_cliente"),
            ("view_menu_arriendos_cupones_generar_cupones_acciones_reactivar_cupon", "pm/arriendos/cupones/generar cupones/acciones/parametros"),

            # Facturacion
            ("view_menu_facturacion_facturacion", "pm/facturacion"),
            # Auditoria de facturacion
            ("view_menu_facturacion_facturacion_auditoria", "pm/facturacion/auditoria"),
            # Acciones auditoria
            ("view_menu_facturacion_facturacion_auditoria_acciones_buscar_facturas", "pm/facturacion/auditoria/acciones/buscar_facturas"),
            ("view_menu_facturacion_facturacion_auditoria_acciones_generar_auditoria", "pm/facturacion/auditoria/acciones/generar_auditoria"),
            ("view_menu_facturacion_facturacion_auditoria_acciones_parametros", "pm/facturacion/auditoria/acciones/parametros"),
            # Facturacion mensual
            ("view_menu_facturacion_facturacion_mensual", "pm/facturacion/mensual"),
            # Acciones facturarion mensual
            ("view_menu_facturacion_facturacion_mensual_acciones_buscar_facturas", "pm/facturacion/mensual/acciones/buscar_facturas"),
            ("view_menu_facturacion_facturacion_mensual_acciones_generar_facturas", "pm/facturacion/mensual/acciones/generar_facturas"),
            ("view_menu_facturacion_facturacion_mensual_acciones_parametros", "pm/facturacion/mensual/acciones/parametros"),
            # Facturacion individual
            ("view_menu_facturacion_facturacion_individual", "pm/facturacion/individual"),
            # Acciones facturarion individual
            ("view_menu_facturacion_facturacion_individual_acciones_facturacion_individual", "pm/facturacion/individual/acciones/facturacion_individual"),
            ("view_menu_facturacion_facturacion_individual_acciones_adicion", "pm/facturacion/individual/acciones/adicion"),
            ("view_menu_facturacion_facturacion_individual_acciones_cupon_parcial", "pm/facturacion/individual/acciones/cupon_parcial"),
            # Transmision de facturas
            ("view_menu_facturacion_transmision_de_facturas", "pm/facturacion/transmision_de_facturas"),
            # Acciones Transmision de facturas
            ("view_menu_facturacion_transmision_de_facturas_acciones_buscar", "pm/facturacion/transmision_de_facturas/acciones/buscar"),
            ("view_menu_facturacion_transmision_de_facturas_acciones_transmitir", "pm/facturacion/transmision_de_facturas/acciones/transmitir"),

            # Menu Pagos y recaudos
            ("view_menu_pagos_y_recaudos", "pm/pagos_y_recaudos"),
            # Recaudos
            ("view_menu_pagos_y_recaudos_recaudos", "pm/pagos_y_recaudos/recaudos"),
            # Recaudos - Recaudos
            ("view_menu_pagos_y_recaudos_recaudos_recaudos", "pm/pagos_y_recaudos/recaudos/recaudos"),
            # Acciones Recaudos - Recaudos
            ("view_menu_pagos_y_recaudos_recaudos_recaudos_acciones_contabilizar", "pm/pagos_y_recaudos/recaudos/recaudos/acciones/contabilizar"),
            ("view_menu_pagos_y_recaudos_recaudos_recaudos_acciones_eliminiar_recaudos", "pm/pagos_y_recaudos/recaudos/recaudos/acciones/eliminiar_recaudos"),
            # Estado de cuentas
            ("view_menu_pagos_y_recaudos_recaudos_estado_de_cuentas", "pm/pagos_y_recaudos/recaudos/recaudos_estado_de_cuentas"),
            # Acciones Estado de cuentas
            # - - - - -
            # Pago a propietarios
            ("view_menu_pagos_y_recaudos_recaudos_pagos_propietarios", "pm/pagos_y_recaudos/pagos/pago_a_propietarios"),
            # Acciones pago a propietarios
            ("view_menu_pagos_y_recaudos_recaudos_pagos_propietarios_acciones_buscar_pagos", "pm/pagos_y_recaudos/pagos/pago_a_propietarios/acciones/buscar_pagos"),
            ("view_menu_pagos_y_recaudos_recaudos_pagos_propietarios_acciones_pagar", "pm/pagos_y_recaudos/pagos/pago_a_propietarios/acciones/pagar"),
            ("view_menu_pagos_y_recaudos_recaudos_pagos_propietarios_acciones_bitacora_whtatsapp", "pm/pagos_y_recaudos/pagos/pago_a_propietarios/acciones/bitacora_whtatsapp"),
            ("view_menu_pagos_y_recaudos_recaudos_pagos_propietarios_acciones_enviar_whtatsapp", "pm/pagos_y_recaudos/pagos/pago_a_propietarios/acciones/enviar_whtatsapp"),
            ("view_menu_pagos_y_recaudos_recaudos_pagos_propietarios_acciones_enviar_zona_clientes", "pm/pagos_y_recaudos/pagos/pago_a_propietarios/acciones/enviar_zona_clientes"),
            ("view_menu_pagos_y_recaudos_recaudos_pagos_propietarios_acciones_enviar_correos", "pm/pagos_y_recaudos/pagos/pago_a_propietarios/acciones/enviar_correos"),
            ("view_menu_pagos_y_recaudos_recaudos_pagos_propietarios_acciones_traslado_saldos_negativos", "pm/pagos_y_recaudos/pagos/pago_a_propietarios/acciones/traslado_saldos_negativos"),
            ("view_menu_arriendos_pagos_propietarios_acciones_suspender_pago_prop", "pm/arriendos/pagos/pago a propietarios/acciones/suspender_pago_prop"),
            # Pago administraciones
            ("view_menu_pagos_y_recaudos_recaudos_pagos_administracion", "pm/pagos_y_recaudos/pagos/pago_administraciones"),
            # Acciones pago administraciones
            ("view_menu_pagos_y_recaudos_recaudos_pagos_administracion_acciones_buscar_pagos", "pm/pagos_y_recaudos/pagos/pago_administraciones/acciones/buscar pagos"),
            ("view_menu_pagos_y_recaudos_recaudos_pagos_administracion_acciones_pagar", "pm/pagos_y_recaudos/pagos/pago_administraciones/acciones/pagar"),
            ("view_menu_pagos_y_recaudos_recaudos_pagos_administracion_acciones_enviar_correos", "pm/pagos_y_recaudos/pagos/pago_administraciones/acciones/enviar_correos"),
            # Pago a proveedores
            ("view_menu_pagos_y_recaudos_recaudos_pagos_proveedores", "pm/pagos_y_recaudos/pagos/pago_proveedores"),
            # Acciones Pago a proveedores
            # - - - - -

            # Menus contabilidad
            ("view_menu_gestion_contable", "pm/gestion_contable"),
            # Directorio contable
            ("view_menu_gestion_contable_directorio_contable", "pm/gestion_contable/directorio_contable"),
            # Plan unico de cuentas
            ("view_menu_gestion_contable_directorio_contable_plan_unico_de_cuentas", "pm/gestion_contable/directorio_contable/plan_unico_de_cuentas"),
            # Acciones Plan unico de cuentas
            ("view_menu_gestion_contable_directorio_contable_plan_unico_de_cuentas_acciones_crear_cuenta", "pm/gestion_contable/directorio_contable/plan_unico_de_cuentasacciones/crear_cuenta"),
            ("view_menu_gestion_contable_directorio_contable_plan_unico_de_cuentas_acciones_editar_cuenta", "pm/gestion_contable/directorio_contable/plan_unico_de_cuentasacciones/editar_cuenta"),
            ("view_menu_gestion_contable_directorio_contable_plan_unico_de_cuentas_acciones_bitacora", "pm/gestion_contable/directorio_contable/plan_unico_de_cuentasacciones/bitacora"),
            ("view_menu_gestion_contable_directorio_contable_plan_unico_de_cuentas_acciones_imprimir_puc", "pm/gestion_contable/directorio_contable/plan_unico_de_cuentasacciones/imprimir_puc"),
            # Conceptos
            ("view_menu_gestion_contable_directorio_contable_conceptos", "pm/gestion_contable/directorio_contable/conceptos"),
            # Acciones conceptos
            ("view_menu_gestion_contable_directorio_contable_conceptos_acciones_crear_concepto", "pm/gestion_contable/directorio_contable/conceptos/acciones/crear_concepto"),
            ("view_menu_gestion_contable_directorio_contable_conceptos_acciones_editar_concepto", "pm/gestion_contable/directorio_contable/conceptos/acciones/editar_concepto"),
            ("view_menu_gestion_contable_directorio_contable_conceptos_acciones_bitacora", "pm/gestion_contable/directorio_contable/conceptos/acciones/bitacora"),
            ("view_menu_gestion_contable_directorio_contable_conceptos_acciones_imprimir_concepto", "pm/gestion_contable/directorio_contable/conceptos/acciones/imprimir_conceptos"),
            # Tipo de documentos
            ("view_menu_gestion_contable_directorio_contable_tipo_documentos", "pm/gestion_contable/directorio_contable/tipo_de_documentos"),
            # Acciones Tipo de documentos
            ("view_menu_gestion_contable_directorio_contable_tipo_documentos_acciones_crear_tipo_documento", "pm/gestion_contable/directorio_contable/tipo_de_documentos/acciones/crear_tipo_de_documento"),
            ("view_menu_gestion_contable_directorio_contable_tipo_documentos_acciones_editar_tipo_documento", "pm/gestion_contable/directorio_contable/tipo_de_documentos/acciones/editar_tipo_de_documento"),
            ("view_menu_gestion_contable_directorio_contable_tipo_documentos_acciones_bitacora", "pm/gestion_contable/directorio_contable/tipo_de_documentos/acciones/bitacora"),
            ("view_menu_gestion_contable_directorio_contable_tipo_documentos_acciones_imprimir_tipo_documento", "pm/gestion_contable/directorio_contable/tipo_de_documentos/acciones/imprimir_tipo_de_documento"),
            # Centro de costos
            ("view_menu_gestion_contable_directorio_contable_centro_costos", "pm/gestion_contable/directorio_contable/centro_de_costos"),
            # Acciones Centro de costos
            ("view_menu_gestion_contable_directorio_contable_centro_costos_acciones_crear_centro_costos", "pm/gestion_contable/directorio_contable/centro_de_costos/acciones/crear_centro_de_costos"),
            ("view_menu_gestion_contable_directorio_contable_centro_costos_acciones_editar_centro_costos", "pm/gestion_contable/directorio_contable/centro_de_costos/acciones/editar_centro_de_costos"),
            ("view_menu_gestion_contable_directorio_contable_centro_costos_acciones_bitacora", "pm/gestion_contable/directorio_contable/centro_de_costos/acciones/bitacora"),
            ("view_menu_gestion_contable_directorio_contable_centro_costos_acciones_imprimir_centro_costos", "pm/gestion_contable/directorio_contable/centro_de_costos/acciones/imprimir_centro_de_costos"),
            # Bancos
            ("view_menu_gestion_contable_directorio_contable_bancos", "pm/gestion_contable/directorio_contable/bancos"),
            # Acciones bancos
            ("view_menu_gestion_contable_directorio_contable_bancos_acciones_crear_bancos", "pm/gestion_contable/directorio_contable/bancos/acciones/crear_bancos"),
            ("view_menu_gestion_contable_directorio_contable_bancos_acciones_editar_bancos", "pm/gestion_contable/directorio_contable/bancos/acciones/editar_bancos"),
            ("view_menu_gestion_contable_directorio_contable_bancos_acciones_bitacora", "pm/gestion_contable/directorio_contable/bancos/acciones/bitacora"),
            ("view_menu_gestion_contable_directorio_contable_bancos_acciones_imprimir_bancos", "pm/gestion_contable/directorio_contable/bancos/acciones/imprimir_bancos"),
            # Cuentas bancarias
            ("view_menu_gestion_contable_directorio_contable_bancarias", "pm/gestion_contable/directorio_contable/cuentas_bancarias"),
            # Acciones Cuentas bancarias
            ("view_menu_gestion_contable_directorio_contable_bancarias_acciones_crear_cuentas_bancarias", "pm/gestion_contable/directorio_contable/cuentas_bancarias/acciones/crear_cuentas_bancarias"),
            ("view_menu_gestion_contable_directorio_contable_bancarias_acciones_editar_cuentas_bancarias", "pm/gestion_contable/directorio_contable/cuentas_bancarias/acciones/editar_cuentas_bancarias"),
            ("view_menu_gestion_contable_directorio_contable_bancarias_acciones_bitacora", "pm/gestion_contable/directorio_contable/cuentas_bancarias/acciones/bitacora"),
            ("view_menu_gestion_contable_directorio_contable_bancarias_acciones_imprimir_cuentas_bancarias", "pm/gestion_contable/directorio_contable/cuentas_bancarias/acciones/imprimir_cuentas_bancarias"),
            # Gastos Administrativos
            ("view_menu_gestion_contable_gastos_administrativos", "pm/gestion_contable/gastos_administrativos"),
            # Generacion de documentos
            ("view_menu_gestion_contable_gastos_administrativos_documentos", "pm/gestion_contable/gastos_administrativos/documentos"),
            # Acciones documentos
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_crear_documento", "pm/gestion_contable/gastos_administrativos/documentos/acciones/crear_documento"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_buscar_documentos", "pm/gestion_contable/gastos_administrativos/documentos/acciones/buscar_documentos"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_imprimir_listado_documentos", "pm/gestion_contable/gastos_administrativos/documentos/acciones/imprimir_listado_de_documentos"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_ver_documento", "pm/gestion_contable/gastos_administrativos/documentos/acciones/ver_documento"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_adjuntar_archivos", "pm/gestion_contable/gastos_administrativos/documentos/acciones/adjuntar_archivos"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_editar_documento", "pm/gestion_contable/gastos_administrativos/documentos/acciones/editar_documento"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_reabrir_documento", "pm/gestion_contable/gastos_administrativos/documentos/acciones/reabrir_documento"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_cerrar_documento", "pm/gestion_contable/gastos_administrativos/documentos/acciones/cerrar_documento"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_anular_documento", "pm/gestion_contable/gastos_administrativos/documentos/acciones/anular_documento"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_nota_credito", "pm/gestion_contable/gastos_administrativos/documentos/acciones/generar_nota_credito"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_anular_nota_credito", "pm/gestion_contable/gastos_administrativos/documentos/acciones/anular_generar_nota_credito"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_copiar_documento", "pm/gestion_contable/gastos_administrativos/documentos/acciones/copiar_documento"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_imprimir_documento", "pm/gestion_contable/gastos_administrativos/documentos/acciones/imprimir_documento"),
            ("view_menu_gestion_contable_gastos_administrativos_documentos_acciones_nota_debito", "pm/gestion_contable/gastos_administrativos/documentos/acciones/generar_nota_debito"),
            # Consultas
            ("view_menu_gestion_contable_consultas", "pm/gestion_contable/consultas"),
            # Consulta de auxiliares
            ("view_menu_gestion_contable_consultas_consulta_de_auxiliares", "pm/gestion_contable/consultas/consulta_de_auxiliares"),
            # Acciones Consulta de auxiliares
            ("view_menu_gestion_contable_consultas_consulta_de_auxiliares_acciones_buscar", "pm/gestion_contable/consultas/consulta_de_auxiliares/acciones/buscar"),
            ("view_menu_gestion_contable_consultas_consulta_de_auxiliares_acciones_imprimir", "pm/gestion_contable/consultas/consulta_de_auxiliares/acciones/imprimir"),
            # Auxiliar de bancos
            ("view_menu_gestion_contable_consultas_auxiliar_bancos", "pm/gestion_contable/consultas/auxiliar_bancos"),
            # Acciones Auxiliar de bancos
            ("view_menu_gestion_contable_consultas_auxiliar_bancos_acciones_buscar", "pm/gestion_contable/consultas/auxiliar_bancos/acciones/buscar"),
            ("view_menu_gestion_contable_consultas_auxiliar_bancos_acciones_imprimir", "pm/gestion_contable/consultas/auxiliar_bancos/acciones/imprimir"),
            # Certificados
            ("view_menu_gestion_contable_consultas_certificados", "pm/gestion_contable/consultas/certificados"),
            # Acciones Certificados
            ("view_menu_gestion_contable_consultas_certificados_enviar_correo", "pm/gestion_contable/consultas/certificados/enviar_a_correo"),
            ("view_menu_gestion_contable_consultas_certificados_imprimir", "pm/gestion_contable/consultas/certificados/imprimir"),
            ("view_menu_gestion_contable_consultas_certificados_exportar", "pm/gestion_contable/consultas/certificados/exportar"),
            # Informes
            ("view_menu_gestion_contable_informes", "pm/gestion_contable/informes"),
            # Informe diario de caja
            ("view_menu_gestion_contable_informes_informe_diario_de_caja", "pm/gestion_contable/informes/informe_diario_de_caja"),
            # Acciones Informe diario de caja
            ("view_menu_gestion_contable_informes_informe_diario_de_caja_acciones_inicializar_caja", "pm/gestion_contable/informes/informe_diario_de_caja/acciones/inicializar_caja"),
            ("view_menu_gestion_contable_informes_informe_diario_de_caja_acciones_cerrar_caja", "pm/gestion_contable/informes/informe_diario_de_caja/acciones/cerrar_caja"),
            ("view_menu_gestion_contable_informes_informe_diario_de_caja_acciones_agregar_consignacion", "pm/gestion_contable/informes/informe_diario_de_caja/acciones/agregar_consignacion"),
            ("view_menu_gestion_contable_informes_informe_diario_de_caja_acciones_editar_consecutivos", "pm/gestion_contable/informes/informe_diario_de_caja/acciones/editar_consecutivos"),
            ("view_menu_gestion_contable_informes_informe_diario_de_caja_acciones_imprimir", "pm/gestion_contable/informes/informe_diario_de_caja/acciones/imprimir"),
            # Balance general
            ("view_menu_gestion_contable_informes_balence_general", "pm/gestion_contable/informes/balance_general"),
            # Acciones balence general
            ("view_menu_gestion_contable_informes_balence_general_acciones_buscar", "pm/gestion_contable/informes/balance_general/acciones/buscar"),
            ("view_menu_gestion_contable_informes_balence_general_acciones_imprimir", "pm/gestion_contable/informes/balance_general/acciones/imprimir"),
            # Balance de prueba
            ("view_menu_gestion_contable_informes_balence_de_prueba", "pm/gestion_contable/informes/balance_de_prueba"),
            # Acciones Balance de prueba
            ("view_menu_gestion_contable_informes_balence_de_prueba_acciones_buscar", "pm/gestion_contable/informes/balance_de_prueba/acciones/buscar"),
            ("view_menu_gestion_contable_informes_balence_de_prueba_acciones_imprimir", "pm/gestion_contable/informes/balance_de_prueba/acciones/imprimir"),
            # Estado de resultados
            ("view_menu_gestion_contable_informes_estado_de_resultados", "pm/gestion_contable/informes/estado_de_resultados"),
            # Acciones Estado de resultados
            ("view_menu_gestion_contable_informes_estado_de_resultados_acciones_buscar", "pm/gestion_contable/informes/estado_de_resultados/acciones/buscar"),
            ("view_menu_gestion_contable_informes_estado_de_resultados_acciones_imprimir", "pm/gestion_contable/informes/estado_de_resultados/acciones/imprimir"),
            # Comprobante diario
            ("view_menu_gestion_contable_informes_comprobante_diario", "pm/gestion_contable/informes/comprobante_diario"),
            # Acciones Comprobante diario
            ("view_menu_gestion_contable_informes_comprobante_diario_acciones_buscar", "pm/gestion_contable/informes/comprobante_diario/acciones/buscar"),
            ("view_menu_gestion_contable_informes_comprobante_diario_acciones_imprimir", "pm/gestion_contable/informes/comprobante_diario/acciones/imprimir"),
            # Informes compararivos
            ("view_menu_gestion_contable_informes_informes_comparativos", "pm/gestion_contable/informes/informes_comparativos"),
            # Acciones Informes compararivos
            ("view_menu_gestion_contable_informes_informes_comparativos_acciones_buscar", "pm/gestion_contable/informes/informes_comparativos/acciones/buscar"),
            ("view_menu_gestion_contable_informes_informes_comparativos_acciones_imprimir", "pm/gestion_contable/informes/informes_comparativos/acciones/imprimir"),
            # Informe de cartera
            ("view_menu_gestion_contable_informes_informe_de_cartera", "pm/gestion_contable/informes/informe_de_cartera"),
            # Acciones Informe de cartera
            ("view_menu_contabilidad_consultas_informe_de_cartera_acciones_buscar", "pm/gestion_contable/informes/informe_de_cartera/acciones/buscar"),
            ("view_menu_contabilidad_consultas_informe_de_cartera_acciones_imprimir", "pm/gestion_contable/informes/informe_de_cartera/acciones/imprimir"),
            # Procesos
            ("view_menu_contabilidad_procesos", "pm/gestion_contable/procesos"),
            # Auditorias
            ("view_menu_contabilidad_consultas_auditorias", "pm/gestion_contable/auditorias"),
            # Acciones Auditorias
            ("view_menu_contabilidad_consultas_auditorias_acciones_buscar", "pm/gestion_contable/auditorias/acciones/buscar"),
            ("view_menu_contabilidad_consultas_auditorias_acciones_imprimir", "pm/gestion_contable/auditorias/acciones/imprimir"),
            # Cierres
            ("view_menu_contabilidad_consultas_cierres", "pm/gestion_contable/cierres"),
            # Acciones Cierres
            ("view_menu_contabilidad_consultas_cierres_acciones_cerrar_mes", "pm/gestion_contable/cierres/acciones/cerrar_mes"),
            ("view_menu_contabilidad_consultas_cierres_acciones_reabrir_mes", "pm/gestion_contable/cierres/acciones/reabrir_mes"),
            ("view_menu_contabilidad_consultas_cierres_acciones_cerrar_anio", "pm/gestion_contable/cierres/acciones/cerrar_anio"),
            # Reconsturccion de movimientos
            ("view_menu_contabilidad_consultas_reconstruccion_de_movimientos", "pm/gestion_contable/reconstruccion_de_movimientos"),
            # Acciones Reconsturccion de movimientos
            ("view_menu_contabilidad_consultas_reconstruccion_de_movimientos_acciones_reconstruir", "pm/gestion_contable/reconstruccion_de_movimientos/acciones/reconstruir"),
            # Cambio de fecha
            ("view_menu_contabilidad_procesos_cambio_fecha", "pm/gestion_contable/procesos/cambio_fechas"),
            # Acciones cambio de fecha
            ("view_menu_contabilidad_procesos_cambio_fecha_acciones_cambio_fecha", "pm/gestion_contable/procesos/cambio_fechas/acciones/reconstruir"),
            # cierres especiales
            ("view_menu_contabilidad_procesos_cerres_especiales", "pm/contabilidad/procesos/cierres especiales"),
            ("view_menu_contabilidad_procesos_cerres_especiales_acciones_crear", "pm/contabilidad/procesos/cierres especiales/acciones/crear"),
            # Conciliacion bancaria
            ("view_menu_contabilidad_procesos_conciliacion_bancaria", "pm/contabilidad/procesos/conciliacion bancaria"),
            # Acciones
            ("view_menu_contabilidad_procesos_conciliacion_bancaria_acciones_conciliar", "pm/contabilidad/procesos/conciliacion bancaria/acciones/conciliar"),
            ("view_menu_contabilidad_procesos_conciliacion_bancaria_acciones_cerrar_conciliacion", "pm/contabilidad/procesos/conciliacion bancaria/acciones/cerrar conciliacion"),
            ("view_menu_contabilidad_procesos_conciliacion_bancaria_acciones_cambiar_valor_extracto", "pm/contabilidad/procesos/conciliacion bancaria/acciones/cambiar valor extracto"),
            # Fin Conciliacion bancaria

            # Menus parametrizacion
            ("view_menu_parametrizacion", "pm/parametrizacion"),
            # Parametros generales
            ("view_menu_parametrizacion_generales", "pm/parametrizacion/generales"),
            # Acciones Parametros generales
            ("view_menu_parametrizacion_generales_acciones_guardar", "pm/parametrizacion/generales/acciones/guardar"),
            # Administrativos
            ("view_menu_parametrizacion_administrativos", "pm/parametrizacion/administrativos"),
            # Cobros adicionales
            ("view_menu_parametrizacion_administrativos_cobros_adicionales", "pm/parametrizacion/administrativos/cobros_adicionales"),
            # Acciones Cobros adicionales
            ("view_menu_parametrizacion_administrativos_cobros_adicionales_acciones_crear_cobro_adicional", "pm/parametrizacion/administrativos/cobros_adicionales/acciones/crear_cobro_adicional"),
            ("view_menu_parametrizacion_administrativos_cobros_adicionales_acciones_editar_cobro_adicional", "pm/parametrizacion/administrativos/cobros_adicionales/acciones/editar_cobro_adicional"),
            ("view_menu_parametrizacion_administrativos_cobros_adicionales_acciones_bitacora", "pm/parametrizacion/administrativos/cobros_adicionales/acciones/bitacora"),
            ("view_menu_parametrizacion_administrativos_cobros_adicionales_acciones_imprimir_cobro_adicional", "pm/parametrizacion/administrativos/cobros_adicionales/acciones/imprimir_cobro_adicional"),
            # Novedades
            ("view_menu_parametrizacion_administrativos_novedades", "pm/parametrizacion/administrativos/novedades"),
            # Acciones Novedades
            ("view_menu_parametrizacion_administrativos_novedades_acciones_crear_novedad", "pm/parametrizacion/administrativos/novedades/acciones/crear_novedad"),
            ("view_menu_parametrizacion_administrativos_novedades_acciones_editar_novedad", "pm/parametrizacion/administrativos/novedades/acciones/editar_novedad"),
            # Contrato conceptos
            ("view_menu_parametrizacion_administrativos_contrato_conceptos", "pm/parametrizacion/administrativos/contrato_conceptos"),
            # Acciones conceptos
            ("view_menu_parametrizacion_administrativos_contrato_conceptos_acciones_crear_concepto", "pm/parametrizacion/administrativos/contrato_conceptos/acciones/crear_concepto"),
            ("view_menu_parametrizacion_administrativos_contrato_conceptos_acciones_editar_concepto", "pm/parametrizacion/administrativos/contrato_conceptos/acciones/editar_concepto"),
            ("view_menu_parametrizacion_administrativos_contrato_conceptos_acciones_bitacora", "pm/parametrizacion/administrativos/contrato_conceptos/acciones/bitacora"),
            ("view_menu_parametrizacion_administrativos_contrato_conceptos_acciones_imprimir_concepto", "pm/parametrizacion/administrativos/contrato_conceptos/acciones/imprimir_concepto"),
            # Beneficiarios
            ("view_menu_parametrizacion_administrativos_beneficiarios", "pm/parametrizacion/arriendos/beneficiarios"),
            # Acciones Beneficiarios
            ("view_menu_parametrizacion_administrativos_beneficiarios_acciones_crear_beneficiario", "pm/parametrizacion/administrativos/beneficiarios/acciones/crear_beneficiario"),
            ("view_menu_parametrizacion_administrativos_beneficiarios_acciones_editar_beneficiario", "pm/parametrizacion/administrativos/beneficiarios/acciones/editar_beneficiario"),
            ("view_menu_parametrizacion_administrativos_beneficiarios_acciones_bitacora", "pm/parametrizacion/administrativos/beneficiarios/acciones/bitacora"),
            ("view_menu_parametrizacion_administrativos_beneficiarios_acciones_imprimir_beneficiario", "pm/parametrizacion/administrativos/beneficiarios/acciones/imprimir_beneficiario"),
            # Departamentos
            ("view_menu_parametrizacion_administrativos_departamentos", "pm/parametrizacion/administrativos/departamento"),
            # Acciones Departamentos
            ("view_menu_parametrizacion_administrativos_departamentos_crear", "pm/parametrizacion/administrativos/departamento/acciones/crear"),
            ("view_menu_parametrizacion_administrativos_departamentos_editar", "pm/parametrizacion/administrativos/departamento/acciones/editar"),
            ("view_menu_parametrizacion_administrativos_departamentos_bitacora", "pm/parametrizacion/administrativos/departamento/acciones/bitacora"),
            ("view_menu_parametrizacion_administrativos_departamentos_imprimir", "pm/parametrizacion/administrativos/departamento/acciones/imprimir"),
            # Acceso (Usuarios)
            ("view_menu_parametrizacion_acceso", "pm/parametrizacion/acceso"),
            # Acciones usuarios
            ("view_menu_parametrizacion_acceso_acciones_crear_usuario", "pm/parametrizacion/acceso/acciones/crear_usuario"),
            ("view_menu_parametrizacion_acceso_acciones_editar_usuario", "pm/parametrizacion/acceso/acciones/editar_usuario"),
            ("view_menu_parametrizacion_acceso_acciones_asginar_grupo", "pm/parametrizacion/acceso/acciones/asignar_grupo"),
            ("view_menu_parametrizacion_acceso_acciones_asignar_permisos", "pm/parametrizacion/acceso/acciones/asignar_permisos"),
           
            # Procesos generales 
            # Casos
            ("view_ver_casos", "pm/generales/casos/acciones/ver casos"),
            ("view_crear_casos", "pm/generales/casos/acciones/crear casos"),
            ("view_crear_seguimientos_casos", "pm/generales/casos/acciones/crear seguimientos a casos"),
            ("view_finalizar_casos", "pm/generales/casos/acciones/finalizar casos"),
            ("view_todas_las_notificaciones", "pm/generales/casos/acciones/ver todas las notificaciones"),
            ("view_editar_contrato_mandato", "pm/generales/impresion/contrado_mandato/editar"),
            ("view_imprimir_contrato_mandato", "pm/generales/impresion/contrado_mandato/imprimir"),
            ("view_editar_contrato_arriendo", "pm/generales/impresion/contrado_arriendo/editar"),
            ("view_seleccionar_plantilla_contrato_arriendo", "pm/generales/impresion/contrado_arriendo/seleccionar_plantilla"),
            ("view_imprimir_contrato_arriendo", "pm/generales/impresion/contrado_arriendo/imprimir"),
            
            
            # Generador de consultas - Desarrollo
            ("view_menu_parametrizacion_generador_consulta", "pm/parametrizacion/generador de consultas"),     
            # Menu de generador de consultas
            ("view_menu_generador_consultas", "pm/generador de consultas/"),

            # Menu de cargos fijos
            ("view_menu_contabilidad_cargos_fijos", "pm/contabilidad/cargos_fijos/"),
            ("view_menu_contabilidad_acciones_cargos_fijos_generar", "pm/contabilidad/cargos_fijos/acciones/generar"),
            ("view_menu_comercial_directorio_personas_acciones_cargos_fijos", "pm/comrcial/dir_personas/acciones/cargos_fijos"),


            # Menu tablero inteligente
            ("view_menu_tablero_inteligente", "pm/tablero inteligente"),

            ("view_menu_arriendos_prestamos", "pm/arriendos/prestamos/"),
            ("view_menu_gestion_administrativa_prestamos_editar", "pm/gestion_administrativa/prestamos"),

            # Menu Pago Proveedores
            ("view_menu_pago_proveedores", "pm/pago proveedores/"),
            # Acciones Pago Proveedores
            ("view_menu_pago_proveedores_acciones_pagar_proveedores", "pm/pago proveedores/acciones/pagar proveedores"),

            # Menu de nomina
            ("view_menu_nomina", "pm/nomina"),
            # Novedades
            ("view_menu_nomina_novedades", "pm/nomina/novedades"),
            # Acciones
            ("view_menu_nomina_novedades_acciones_crear", "pm/nomina/novedades/acciones/crear"),
            ("view_menu_nomina_novedades_acciones_editar", "pm/nomina/novedades/acciones/editar"),
            ("view_menu_nomina_novedades_acciones_exportar", "pm/nomina/novedades/acciones/exportar"),
            ("view_menu_nomina_novedades_acciones_imprimir", "pm/nomina/novedades/acciones/imprimir"),
            ("view_menu_nomina_novedades_acciones_bitacora", "pm/nomina/novedades/acciones/bitacora"),
            # Fin Novedades
            # Contratos
            ("view_menu_nomina_contratos", "pm/nomina/contratos"),
            # Acciones
            ("view_menu_nomina_contratos_acciones_crear", "pm/nomina/contratos/acciones/crear"),
            ("view_menu_nomina_contratos_acciones_editar", "pm/nomina/contratos/acciones/editar"),
            ("view_menu_nomina_contratos_acciones_ver", "pm/nomina/contratos/acciones/ver"),
            ("view_menu_nomina_contratos_acciones_novedades", "pm/nomina/contratos/acciones/novedades"),
            ("view_menu_nomina_contratos_acciones_exportar", "pm/nomina/contratos/acciones/exportar"),
            ("view_menu_nomina_contratos_acciones_imprimir", "pm/nomina/contratos/acciones/imprimir"),
            ("view_menu_nomina_contratos_acciones_bitacora", "pm/nomina/contratos/acciones/bitacora"),
            # Fin Contratos
            # Liquidacion
            ("view_menu_nomina_liquidacion", "pm/nomina/liquidacion"),
            # Acciones
            ("view_menu_nomina_liquidacion_acciones_novedades", "pm/nomina/liquidacion/acciones/novedades"),
            ("view_menu_nomina_liquidacion_acciones_liquidar", "pm/nomina/liquidacion/acciones/liquidar"),
            ("view_menu_nomina_liquidacion_acciones_imprimir", "pm/nomina/liquidacion/acciones/imprimir"),
            ("view_menu_nomina_liquidacion_acciones_imprimir_desprendible", "pm/nomina/liquidacion/acciones/imprimir_desprendible"),
            ("view_menu_nomina_liquidacion_acciones_enviar_desprendible", "pm/nomina/liquidacion/acciones/enviar_desprendible"),
            # Fin Liquidacion
            # Transmision
            ("view_menu_nomina_transmision", "pm/nomina/transmision"),
            # Acciones
            ("view_menu_nomina_transmision_acciones_transmitir", "pm/nomina/transmision/acciones/transmitir"),
            # Fin Transmision
            # Pago empleados
            ("view_menu_nomina_pago_empleado", "pm/nomina/pago_empleados"),
            # Acciones
            ("view_menu_nomina_pago_empleados_acciones_pagar_empleados", "pm/nomina/pago_empleados/acciones/pagar_empleados"),
            ("view_menu_nomina_pago_empleados_acciones_exportar", "pm/nomina/pago_empleados/acciones/exportar"),
            ("view_menu_nomina_pago_empleados_acciones_imprimir", "pm/nomina/pago_empleados/acciones/imprimir"),
            # Fin Pago empleados
            # Fin Menu de nomina
            
            # Menu de parametrizacion de nomina
            ("view_menu_parametrizacion_nomina", "pm/nomina/parametrizacion/nomina"),
            # Centros de costos
            ("view_menu_parametrizacion_nomina_contro_costros", "pm/nomina/parametrizacion/nomina/centro_costros"),
            # Acciones
            ("view_menu_parametrizacion_nomina_contro_costros_acciones_crear", "pm/nomina/parametrizacion/nomina/centro_costros/acciones/crear"),
            ("view_menu_parametrizacion_nomina_contro_costros_acciones_editar", "pm/nomina/parametrizacion/nomina/centro_costros/acciones/editar"),
            ("view_menu_parametrizacion_nomina_contro_costros_acciones_imprimir", "pm/nomina/parametrizacion/nomina/centro_costros/acciones/imprimir"),
            ("view_menu_parametrizacion_nomina_contro_costros_acciones_bitacora", "pm/nomina/parametrizacion/nomina/centro_costros/acciones/bitacora"),
            # Fin Centros de costos
            # Cargos
            ("view_menu_parametrizacion_nomina_cargos", "pm/nomina/parametrizacion/nomina/cargos"),
            # Acciones
            ("view_menu_parametrizacion_nomina_cargos_acciones_crear", "pm/nomina/parametrizacion/nomina/cargos/acciones/crear"),
            ("view_menu_parametrizacion_nomina_cargos_acciones_editar", "pm/nomina/parametrizacion/nomina/cargos/acciones/editar"),
            ("view_menu_parametrizacion_nomina_cargos_acciones_imprimir", "pm/nomina/parametrizacion/nomina/cargos/acciones/imprimir"),
            ("view_menu_parametrizacion_nomina_cargos_acciones_bitacora", "pm/nomina/parametrizacion/nomina/cargos/acciones/bitacora"),
            # Fin Cargos
            # Entidades
            ("view_menu_parametrizacion_nomina_entidades", "pm/nomina/parametrizacion/nomina/entidades"),
            # Acciones
            ("view_menu_parametrizacion_nomina_entidades_acciones_crear", "pm/nomina/parametrizacion/nomina/entidades/acciones/crear"),
            ("view_menu_parametrizacion_nomina_entidades_acciones_editar", "pm/nomina/parametrizacion/nomina/entidades/acciones/editar"),
            ("view_menu_parametrizacion_nomina_entidades_acciones_imprimir", "pm/nomina/parametrizacion/nomina/entidades/acciones/imprimir"),
            ("view_menu_parametrizacion_nomina_entidades_acciones_exportar", "pm/nomina/parametrizacion/nomina/entidades/acciones/exportar"),
            ("view_menu_parametrizacion_nomina_entidades_acciones_bitacora", "pm/nomina/parametrizacion/nomina/entidades/acciones/bitacora"),
            # Fin Entidades
            # Parametrización
            ("view_menu_parametrizacion_nomina_parametrizacion", "pm/nomina/parametrizacion/nomina/parametrizacion"),
            # Acciones
            ("view_menu_parametrizacion_nomina_parametrizacion_acciones_guardar", "pm/nomina/parametrizacion/nomina/parametrizacion/acciones/guardar"),
            # Fin Parametrización

            # Permiso de ingreso sin restricciones
            ("view_ingreso_sin_restriccion_horario", "pm/generales/ingreso sin restriccion de horario"),
            # Fin Menu de parametrizacion de nomina
        
        )

    def __str__(self):
        try:
            return self.titulo
        except:
            return ""

class PermisosMenuAcciones(models.Model):
    permiso_menu = models.CharField(max_length=255, help_text="Permiso menu", blank=True, null=True)
    permiso_accion = models.CharField(max_length=255, help_text="Permiso accion", blank=True, null=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name="menu_permiso_menu", blank=True, null=True)
    accion = models.CharField(max_length=255, help_text="Nombre de la accion", blank=True, null=True)
    grupo = models.ForeignKey(Group, on_delete=models.CASCADE, related_name="menu_permiso_grupo", blank=True, null=True)

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