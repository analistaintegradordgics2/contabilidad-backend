
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]

GRUPO = "Directorio de personas"

MENUS = [
    {
        "codigo": "directorio_personas",
        "titulo": "Directorio de Personas",
        "grupo": "Directorio de personas",
        "icono": "gestionarchivos.png",
        "permiso": "view_menu_directorio_personas",
        "ruta": "PersonaListar",
        "orden": "2",

        "children": [

            {
                "codigo": "directoriopersonas",
                "titulo": "Directorio de Personas",
                "permiso": "view_menu_directorio_personas",
                "ruta": "PersonaListar",
                "orden": "1"

            },


        ]
    },
    

]
