
CRUD = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "eliminar", "nombre": "Eliminar"},
]

DOCUMENTO = [
    {"codigo": "ver", "nombre": "Ver"},
    {"codigo": "crear", "nombre": "Crear"},
    {"codigo": "editar", "nombre": "Editar"},
    {"codigo": "cerrar", "nombre": "Cerrar"},
    {"codigo": "reabrir", "nombre": "Reabrir"},
    {"codigo": "anular", "nombre": "Anular"},
    {"codigo": "copiar", "nombre": "Copiar"},
    {"codigo": "imprimir", "nombre": "Imprimir"},
    {"codigo": "exportar", "nombre": "Exportar"},
]

FACTURA = [
    *DOCUMENTO,
    {"codigo": "nota_credito", "nombre": "Generar Nota Crédito"},
    {"codigo": "nota_debito", "nombre": "Generar Nota Débito"},
]

CONSULTA = [
    {"codigo": "ver", "nombre": "Consultar"},
    {"codigo": "imprimir", "nombre": "Imprimir"},
    {"codigo": "exportar", "nombre": "Exportar"},
]


MENUS = [{
    "codigo": "contabilidad",
    "titulo": "Gestión Contable",
    "icono": "gestioncontable.png",
    "permiso": "view_menu_gestion_contable",
    "orden": "4",

    "children": [

        {
            "codigo": "gastos_administrativos",
            "titulo": "Gastos Administrativos",
            "permiso": "view_menu_gestion_contable_gastos_administrativos",
            "orden": "1",

            "children": [

                {
                    "codigo": "documentos",
                    "titulo": "Generación de Documentos",
                    "permiso": "view_menu_gestion_contable_gastos_administrativos_documentos",
                    "ruta": "documentos",
                    "orden": "1",
                    "acciones": FACTURA
                }

            ]
        },

        {
            "codigo": "directorio_contable",
            "titulo": "Directorio Contable",
            "permiso": "view_menu_gestion_contable_directorio_contable",
            "orden": "2",

            "children": [

                {
                    "codigo": "plandecuentas",
                    "titulo": "Plan Único de Cuentas",
                    "permiso": "view_menu_gestion_contable_directorio_contable_plan_cuentas",
                    "ruta": "plandecuentas",
                    "orden": "1",
                    "acciones": CRUD
                },
                {
                    "codigo": "tipodedocumentos",
                    "titulo": "Tipo de Documentos",
                    "permiso": "view_menu_gestion_contable_directorio_contable_tipo_documentos",
                    "ruta": "tipodedocumentos",
                    "orden": "2",
                    "acciones": CRUD
                },

                {
                    "codigo": "conceptos",
                    "titulo": "Conceptos",
                    "permiso": "view_menu_gestion_contable_directorio_contable_conceptos",
                    "ruta": "conceptos",
                    "orden": "3",
                    "acciones": CRUD
                },


            ]
        },

        {
            "codigo": "consultas",
            "titulo": "Consultas",
            "permiso": "view_menu_gestion_contable_consultas",
            "orden": "3",

            "children": [
                {
                    "codigo": "auxiliares",
                    "titulo": "Consulta de Auxiliares",
                    "permiso": "view_menu_gestion_contable_consultas_auxiliares",
                    "ruta": "auxcodigonit",
                    "orden": "1",
                    "acciones": CONSULTA
                },
                {
                    "codigo": "auxbancos",
                    "titulo": "Auxiliar de Bancos",
                    "permiso": "view_menu_gestion_contable_consultas_auxiliar_bancos",
                    "ruta": "auxbancos",
                    "orden": "2",
                    "acciones": CONSULTA
                }

            ]
        },

        {
            "codigo": "informes_gestion_contable",
            "titulo": "Informes",
            "permiso": "view_menu_gestion_contable_informes",
            "orden": "4",

            "children": [
                {
                    "codigo": "balancegeneral",
                    "titulo": "Balance General",
                    "permiso": "view_menu_gestion_contable_informes_balance_general",
                    "ruta": "balancegeneral",
                    "orden": "1",
                    "acciones": CONSULTA
                },
                {
                    "codigo": "balanceprueba",
                    "titulo": "Balance de Prueba",
                    "permiso": "view_menu_gestion_contable_informes_balance_prueba",
                    "ruta": "balanceprueba",
                    "orden": "2",
                    "acciones": CONSULTA
                },
                {
                    "codigo": "comprobantediario",
                    "titulo": "Comprobante Diario",
                    "permiso": "view_menu_gestion_contable_informes_comprobante_diario",
                    "ruta": "comprobantediario",
                    "orden": "3",
                    "acciones": CONSULTA
                },
                {
                    "codigo": "estadoresultados",
                    "titulo": "Estado Resultados",
                    "permiso": "view_menu_gestion_contable_informes_estado_resultados",
                    "ruta": "estadoresultados",
                    "orden": "4",
                    "acciones": CONSULTA
                },

            ]
        }

    ]
}]


