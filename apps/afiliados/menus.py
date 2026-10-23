
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]

AFILIADOS_ACCIONES = [
    {"codigo": "editar", "nombre": "Parametrizar / Editar"},
    {"codigo": "cambio_estado", "nombre": "Cambio de Estado"},
    {"codigo": "bitacora", "nombre": "Bitácora"},
]

FACTURACION_ACCIONES = [
    {"codigo": "crear", "nombre": "Generar Facturas"},
]

CUPONES_ACCIONES = [
    {"codigo": "crear", "nombre": "Generar Cupones"},
    {"codigo": "wompi", "nombre": "Wompi"},
    {"codigo": "parametros", "nombre": "Parámetros"},
    {"codigo": "imprimir", "nombre": "Imprimir"},
    {"codigo": "anular", "nombre": "Anular"},
]

RECAUDOS_ACCIONES = [
    {"codigo": "wompi", "nombre": "Wompi"},
    {"codigo": "contabilizar", "nombre": "Contabilizar"},
    {"codigo": "parametros", "nombre": "Parámetros"},
    {"codigo": "editar_detalle", "nombre": "Editar Detalle"},
]

GRUPO = "Afiliados"

MENUS = [
    {
        "codigo": "afiliados",
        "titulo": "Afiliados",
        "grupo": "Afiliados",
        "icono": "pagosrecaudos.png",
        "permiso": "view_menu_afiliados",
        "ruta": "afiliados",
        "orden": "3",

        "children": [

            {
                "codigo": "sub_afiliados",
                "titulo": "Afiliados",
                "permiso": "view_menu_afiliados",
                "ruta": "afiliados",
                "orden": "1",
                "acciones": AFILIADOS_ACCIONES,
            },
            {
                "codigo": "facturacion_afiliados",
                "titulo": "Facturación",
                "permiso": "view_menu_afiliados_facturacion_afiliados",
                "ruta": "causacion",
                "orden": "2",
                "acciones": FACTURACION_ACCIONES,
            },
            {
                "codigo": "cupones",
                "titulo": "Cupones",
                "permiso": "view_menu_afiliados_cupones",
                "ruta": "cupones",
                "orden": "3",
                "acciones": CUPONES_ACCIONES,
            },
            {
                "codigo": "recaudos",
                "titulo": "Recaudos",
                "permiso": "view_menu_afiliados_recaudos",
                "ruta": "recaudos",
                "orden": "4",
                "acciones": RECAUDOS_ACCIONES,
            },

        ]
    },
]

