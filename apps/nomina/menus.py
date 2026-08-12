
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]


MENUS = [
    {
        "codigo": "nomina",
        "titulo": "Nomina",
        "icono": "afiliados.png",
        "permiso": "view_menu_nomina",
        "ruta": "nomina_novedades",
        "orden": "6",

        "children": [

            {
                "codigo": "nomina_novedades",
                "titulo": "Novedades",
                "permiso": "view_menu_nomina_novedades",
                "ruta": "nomina_novedades",
                "orden": "1"

            },
            {
                "codigo": "nomina_contratos",
                "titulo": "Contratos",
                "permiso": "view_menu_nomina_contratos",
                "ruta": "nomina_contratos",
                "orden": "2"
            },
            {
                "codigo": "nomina_liquidacion",
                "titulo": "Liquidación",
                "permiso": "view_menu_nomina_liquidacion",
                "ruta": "nomina_liquidacion",
                "orden": "3"
            },
            {
                "codigo": "nomina_transmision",
                "titulo": "Transmisiones",
                "permiso": "view_menu_nomina_transmision",
                "ruta": "nomina_transmision",
                "orden": "4"
            },
            {
                "codigo": "nomina_pago_empleados",
                "titulo": "Pago Empleados",
                "permiso": "view_menu_nomina_pago_empleados",
                "ruta": "nomina_pago_empleados",
                "orden": "5"
            },

        ]
    },
    

]


