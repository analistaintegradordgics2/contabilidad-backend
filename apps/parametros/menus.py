
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]

ACCIONES_GENERALES = [
    {"codigo": "guardar", "nombre": "Guardar"},
]

ACCIONES_ACCESO = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
]

ACCIONES_CENTRO_COSTOS = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
    {"codigo": "imprimir", "nombre": "Imprimir"},
]

ACCIONES_ENTIDADES = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
    {"codigo": "imprimir", "nombre": "Imprimir"},
    {"codigo": "exportar", "nombre": "Exportar"},
]

ACCIONES_CARGOS = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
    {"codigo": "imprimir", "nombre": "Imprimir"},
]

ACCIONES_NOMINA_PARAMETRIZACION = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "guardar", "nombre": "Guardar"},
]

GRUPO = "Parametrización"

MENUS = [
    {
        "grupo": "Parametrización",
        "codigo": "parametrizacion",
        "titulo": "Parametrización",
        "icono": "parametrizacion.png",
        "permiso": "view_menu_parametrizacion",
        "orden": "6",
        "ruta": "parametrizacion",

        "children": [
            {
                "codigo": "parametros_generales",
                "titulo": "Generales",
                "permiso": "view_menu_parametrizacion_generales",
                "ruta": "parametrizacion",
                "orden": "1",
                "acciones": ACCIONES_GENERALES,
            },
            {
                "codigo": "parametros_administrativos",
                "titulo": "Administrativos",
                "permiso": "view_menu_parametrizacion_administrativos",
                "orden": "2",

                "children": [

                    {
                        "codigo": "parametros_administrativos_conceptos_causacion",
                        "titulo": "Conceptos Causación",
                        "permiso": "view_menu_parametrizacion_administrativos_conceptos_causacion",
                        "ruta": "conceptos_causacion",
                        "orden": "1",
                        "acciones": CRUD
                    }

                ]
            },
            {
                "codigo": "parametros_acceso",
                "titulo": "Acceso",
                "permiso": "view_menu_parametrizacion_acceso",
                "ruta": "usuarios",
                "orden": "3",
                "acciones": ACCIONES_ACCESO,
            },
            {
                "codigo": "parametros_nomina",
                "titulo": "Nómina",
                "permiso": "view_menu_parametrizacion_nomina",
                "orden": "4",

                "children": [

                    {
                        "codigo": "parametros_nomina_centro_costos",
                        "titulo": "Centros de Costos",
                        "permiso": "view_menu_parametrizacion_nomina_centro_costos",
                        "ruta": "centros_costos",
                        "orden": "1",
                        "acciones": ACCIONES_CENTRO_COSTOS
                    },
                    {
                        "codigo": "parametros_nomina_entidades",
                        "titulo": "Entidades",
                        "permiso": "view_menu_parametrizacion_nomina_entidades",
                        "ruta": "entidades",
                        "orden": "2",
                        "acciones": ACCIONES_ENTIDADES
                    },
                    {
                        "codigo": "parametros_nomina_cargos",
                        "titulo": "Cargos",
                        "permiso": "view_menu_parametrizacion_nomina_cargos",
                        "ruta": "cargos",
                        "orden": "3",
                        "acciones": ACCIONES_CARGOS
                    },
                    {
                        "codigo": "parametros_nomina_parametrizacion",
                        "titulo": "Parametrización",
                        "permiso": "view_menu_parametrizacion_nomina_parametrizacion",
                        "ruta": "parametrizacion_nomina",
                        "orden": "4",
                        "acciones": ACCIONES_NOMINA_PARAMETRIZACION
                    },

                ]
            },

        ]
    },

]
