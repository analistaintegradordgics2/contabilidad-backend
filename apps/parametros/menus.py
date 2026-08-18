
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]


MENUS = [
    {
        "codigo": "parametrizacion",
        "titulo": "Parametrización",
        "icono": "parametrizacion.png",
        "permiso": "view_menu_parametrizacion",
        "orden": "5",
        "ruta": "parametrizacion",

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
            {
                "codigo": "parametros_acceso",
                "titulo": "Acceso",
                "permiso": "view_menu_parametrizacion_acceso",
                "ruta": "usuarios",
                "orden": "3",
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
                        "acciones": CRUD
                    },
                    {
                        "codigo": "parametros_nomina_entidades",
                        "titulo": "Entidades",
                        "permiso": "view_menu_parametrizacion_nomina_entidades",
                        "ruta": "entidades",
                        "orden": "2",
                        "acciones": CRUD
                    },
                    {
                        "codigo": "parametros_nomina_cargos",
                        "titulo": "Cargos",
                        "permiso": "view_menu_parametrizacion_nomina_cargos",
                        "ruta": "cargos",
                        "orden": "3",
                        "acciones": CRUD
                    },
                    {
                        "codigo": "parametros_nomina_parametrizacion",
                        "titulo": "Parametrización",
                        "permiso": "view_menu_parametrizacion_nomina_parametrizacion",
                        "ruta": "parametrizacion",
                        "orden": "4",
                        "acciones": CRUD
                    },

                ]
            },

        ]
    },

]


