
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]

NOVEDADES_ACCIONES = [
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "imprimir", "nombre": "Imprimir"},
    {"codigo": "exportar", "nombre": "Exportar"},
    {"codigo": "bitacora", "nombre": "Bitácora"},
]

CONTRATOS_ACCIONES = [
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "novedades", "nombre": "Novedades"},
    {"codigo": "imprimir", "nombre": "Imprimir"},
    {"codigo": "exportar", "nombre": "Exportar"},
    {"codigo": "bitacora", "nombre": "Bitácora"},
]

LIQUIDACION_ACCIONES = [
    {"codigo": "liquidar", "nombre": "Liquidar"},
    {"codigo": "anular", "nombre": "Anular"},
    {"codigo": "imprimir", "nombre": "Imprimir Planilla"},
    {"codigo": "imprimir_desprendible", "nombre": "Imprimir Desprendibles"},
    {"codigo": "enviar_correo", "nombre": "Enviar Desprendibles por Correo"},
    {"codigo": "enviar_whatsapp", "nombre": "Enviar Desprendibles por WhatsApp"},
    {"codigo": "parametros", "nombre": "Parametrización WhatsApp"},
    {"codigo": "bitacora", "nombre": "Bitácora WhatsApp"},
    {"codigo": "editar", "nombre": "Editar Liquidación"},
    {"codigo": "novedades", "nombre": "Novedades"},
]

TRANSMISION_ACCIONES = [
    {"codigo": "transmitir", "nombre": "Transmitir Nómina"},
    {"codigo": "archivos", "nombre": "Descargar Archivos"},
]

PAGO_EMPLEADOS_ACCIONES = [
    {"codigo": "pagar", "nombre": "Pagar Empleados"},
    {"codigo": "imprimir", "nombre": "Imprimir"},
    {"codigo": "exportar", "nombre": "Exportar"},
]

GRUPO = "Nómina"

MENUS = [
    {
        "grupo": "Nómina",
        "codigo": "nomina",
        "titulo": "Nómina",
        "icono": "afiliados.png",
        "permiso": "view_menu_nomina",
        "ruta": "nomina_novedades",
        "orden": "5",

        "children": [

            {
                "codigo": "nomina_novedades",
                "titulo": "Novedades",
                "permiso": "view_menu_nomina_novedades",
                "ruta": "nomina_novedades",
                "orden": "1",
                "acciones": NOVEDADES_ACCIONES,
            },
            {
                "codigo": "nomina_contratos",
                "titulo": "Contratos",
                "permiso": "view_menu_nomina_contratos",
                "ruta": "nomina_contratos",
                "orden": "2",
                "acciones": CONTRATOS_ACCIONES,
            },
            {
                "codigo": "nomina_liquidacion",
                "titulo": "Liquidación",
                "permiso": "view_menu_nomina_liquidacion",
                "ruta": "nomina_liquidacion",
                "orden": "3",
                "acciones": LIQUIDACION_ACCIONES,
            },
            {
                "codigo": "nomina_transmision",
                "titulo": "Transmisión",
                "permiso": "view_menu_nomina_transmision",
                "ruta": "nomina_transmision",
                "orden": "4",
                "acciones": TRANSMISION_ACCIONES,
            },
            {
                "codigo": "nomina_pago_empleados",
                "titulo": "Pago A Empleados",
                "permiso": "view_menu_nomina_pago_empleados",
                "ruta": "nomina_pago_empleados",
                "orden": "5",
                "acciones": PAGO_EMPLEADOS_ACCIONES,
            },

        ]
    },
]
