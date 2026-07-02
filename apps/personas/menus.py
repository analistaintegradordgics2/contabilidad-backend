
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]


MENUS = [
    {
        "codigo": "directorio_personas",
        "titulo": "Directorio de Personas",
        "icono": "gestionarchivos.png",
        "permiso": "view_menu_directorio_personas",
        "ruta": "PersonaListar",
        "orden": "2",

        "children": [

            {
                "codigo": "directorio_personas",
                "titulo": "Directorio de Personas",
                "permiso": "view_menu_directorio_personas",
                "ruta": "PersonaListar",
                "orden": "1"

            },


        ]
    },
    

]


