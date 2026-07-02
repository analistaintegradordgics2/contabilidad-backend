
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]


MENUS = [
    {
        "codigo": "afiliados",
        "titulo": "Afiliados",
        "icono": "afiliados.png",
        "permiso": "view_menu_afiliados",
        "orden": "3",

        "children": [

            {
                "codigo": "sub_afiliados",
                "titulo": "Afiliados",
                "permiso": "view_menu_afiliados",
                "ruta": "afiliados",
                "orden": "1"

            },
            {
                "codigo": "facturacion_afiliados",
                "titulo": "Facturación",
                "permiso": "view_menu_afiliados_facturacion_afiliados",
                "ruta": "causacion",
                "orden": "2"
            },

        ]
    },
    

]


