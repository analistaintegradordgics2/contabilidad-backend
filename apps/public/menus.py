
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]


MENUS = [
    {
        "codigo": "tablerointeligente",
        "titulo": "Tablero Inteligente",
        "icono": "tablero.png",
        "permiso": "view_menu_tablero_inteligente",
        "orden": "1",

        "children": [

            {
                "codigo": "tablero_inteligente",
                "titulo": "Tablero Inteligente",
                "permiso": "view_menu_tablero_inteligente",
                "orden": "1",
            },

        ]
    },
    {
        "codigo": "parametrizacion",
        "titulo": "Parametrización",
        "icono": "parametrizacion.png",
        "permiso": "view_menu_parametrizacion",
        "orden": "5",

        "children": [
            {
                "codigo": "parametros_generales",
                "titulo": "Generales",
                "permiso": "view_menu_parametrizacion_generales",
                "ruta": "parametrizacion",
                "orden": "1",
            },
            {
                "codigo": "parametros_administrativos",
                "titulo": "Administrativos",
                "permiso": "view_menu_parametrizacion_administrativos",
                "ruta": "parametrizacion",
                "orden": "2",

                "children": [

                    {
                        "codigo": "parametros_administrativos_conceptos_causacion",
                        "titulo": "Conceptos Causacion",
                        "permiso": "view_menu_parametrizacion_administrativos_conceptos_causacion",
                        "ruta": "conceptos_causacion",
                        "orden": "1",
                        "acciones": CRUD
                    }

                ]
            },

        ]
    },

]


