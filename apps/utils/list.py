class lists:
    TIPO_TELEFONO = [
        (1, 'Personal')
    ]
    TIPOS_LLAMADAS = [
        (1, 'Entrante'),
        (2, 'Saliente'),
    ]
    ESTADOS_ACTIVIDADES = [
        (1, 'Activo'),
        (2, 'Cancelada'),
        (3, 'Finalizada'),
    ]
    months = (
        '',
        'Enero',
        'Febrero',
        'Marzo',
        'Abril',
        'Mayo',
        'Junio',
        'Julio',
        'Agosto',
        'Septiembre',
        'Octubre',
        'Noviembre',
        'Diciembre'
    )

    mes_letra = [
        {
            "mes": 1,
            "nombre": "Enero",
        },
        {
            "mes": 2,
            "nombre": "Febrero",
        },
        {
            "mes": 3,
            "nombre": "Marzo",
        },
        {
            "mes": 4,
            "nombre": "Abril",
        },
        {
            "mes": 5,
            "nombre": "Mayo",
        },
        {
            "mes": 6,
            "nombre": "Junio",
        },
        {
            "mes": 7,
            "nombre": "Julio",
        },
        {
            "mes": 8,
            "nombre": "Agosto",
        },
        {
            "mes": 9,
            "nombre": "Septiembre",
        },
        {
            "mes": 10,
            "nombre": "Octubre",
        },
        {
            "mes": 11,
            "nombre": "Noviembre",
        },
        {
            "mes": 12,
            "nombre": "Diciembre",
        },
    ]

    days = (
        '',
        'Uno',
        'Dos',
        'Tres',
        'Cuatro',
        'Cinco',
        'Seis',
        'Siente',
        'Ocho',
        'Nueve',
        'Diez',
        'Once',
        'Doce',
        'Trece',
        'Catorce',
        'Quince',
        'Diecisietes',
        'Diecisiete',
        'Dieciocho',
        'Diecinueve',
        'Veinte',
        'veintiuno',
        'Veintidos',
        'Veintitrés',
        'veinticuatro',
        'veinticinco',
        'veintiséis',
        'veintisiete',
        'Veintiocho',
        'Veintinueve',
        'treinta',
        'Treinta y un'
    )

    weeks = (
        'Lunes',
        'Martes',
        'Miércoles',
        'Jueves',
        'Viernes',
        'Sábado',
        'Domingo',
    )

    dia_semana = [
        {
            "num_dia": 1,
            "nombre": "Lunes",
        },
        {
            "num_dia": 2,
            "nombre": "Martes",
        },
        {
            "num_dia": 3,
            "nombre": "Miércoles",
        },
        {
            "num_dia": 4,
            "nombre": "Jueves",
        },
        {
            "num_dia": 5,
            "nombre": "Viernes",
        },
        {
            "num_dia": 6,
            "nombre": "Sábado",
        },
        {
            "num_dia": 0,
            "nombre": "Domingo",
        }
    ]

    tp_inmu_finca_raiz = [
        {'id': 2, 'label': 'APARTAMENTO'},
        {'id': 3, 'label': 'CASA'},
        {'id': 10, 'label': 'CABAÑA'},
        {'id': 11, 'label': 'CASA CAMPESTRE'},
        {'id': 12, 'label': 'APARTAESTUDIO'},
        {'id': 13, 'label': 'CASA LOTE'},
        {'id': 14, 'label': 'LOTE'},
        {'id': 33, 'label': 'OFICINA'},
        {'id': 38, 'label': 'HABITACION'},
        {'id': 41, 'label': 'LOCAL'},
        {'id': 45, 'label': 'BODEGAS OTRO'},
        {'id': 51, 'label': 'FINCAS OTRO'},
        {'id': 52, 'label': 'FINCA PRODUCCIÓN'},
        {'id': 53, 'label': 'FINCA DESCANSO'},
        {'id': 54, 'label': 'BODEGA ALMACENAMIENTO'},
        {'id': 55, 'label': 'BODEGA INDUSTRIAL'},
        {'id': 56, 'label': 'CONSULTORIO'},
        {'id': 57, 'label': 'EDIFICIO'}
    ]

    tp_inmu_finca_raiz_new = [
        { "id_orbis": 1, "value_fr": "studio" },
        { "id_orbis": 2, "value_fr": "apartment" },
        { "id_orbis": 3, "value_fr": "warehouse" },
        { "id_orbis": 4, "value_fr": "cabin" },
        { "id_orbis": 5, "value_fr": "house" },
        { "id_orbis": 6, "value_fr": "country-house" },
        { "id_orbis": 7, "value_fr": "country-house" },
        { "id_orbis": 8, "value_fr": "commercial" },
        { "id_orbis": 9, "value_fr": "house-lot" },
        { "id_orbis": 10, "value_fr": "consulting-room" },
        { "id_orbis": 11, "value_fr": "building" },
        { "id_orbis": 12, "value_fr": "farm" },
        { "id_orbis": 13, "value_fr": "room" },
        { "id_orbis": 14, "value_fr": "commercial" },
        { "id_orbis": 15, "value_fr": "lot" },
        { "id_orbis": 16, "value_fr": "office" },
        { "id_orbis": 17, "value_fr": "parking" },
    ]
    
    caracteristicas_finca_raiz = [
        { "id_fr": 1, "id_orbis": 5, "label": "AIRE ACONDICIONADO" },
        { "id_fr": 4, "id_orbis": 164, "label": "PISO EN BALDOSA/MÁRMOL" },
        { "id_fr": 5, "id_orbis": 153, "label": "PARQUEADERO VISITANTES" },
        { "id_fr": 7, "id_orbis": 125, "label": "JARDÍN" },
        { "id_fr": 10, "id_orbis": 218, "label": "TERRAZA" },
        { "id_fr": 11, "id_orbis": 82, "label": "DEPÓSITO/BODEGA" },
        { "id_fr": 12, "id_orbis": 93, "label": "EN CONJUNTO CERRADO" },
        { "id_fr": 13, "id_orbis": 24, "label": "ASCENSOR" },
        { "id_fr": 16, "id_orbis": 155, "label": "PATIO" },
        { "id_fr": 17, "id_orbis": 160, "label": "PISCINA" },
        { "id_fr": 19, "id_orbis": 17, "label": "AMOBLADO" },
        { "id_fr": 20, "id_orbis": 63, "label": "COCINA INTEGRAL" },
        { "id_fr": 32, "id_orbis": 29, "label": "BALCÓN" },
        { "id_fr": 100, "id_orbis": 49, "label": "CANCHA DE SQUASH" },
        { "id_fr": 101, "id_orbis": 48, "label": "CANCHA DE TENNIS" },
        { "id_fr": 102, "id_orbis": 50, "label": "CANCHAS DEPORTIVAS" },
        { "id_fr": 103, "id_orbis": 119, "label": "GIMNASIO" },
        { "id_fr": 104, "id_orbis": 127, "label": "JAULA DE GOLF" },
        { "id_fr": 105, "id_orbis": 193, "label": "SALÓN DE JUEGOS" },
        { "id_fr": 106, "id_orbis": 236, "label": "ZONA INFANTIL" },
        { "id_fr": 107, "id_orbis": 240, "label": "ZONAS VERDES" },
        { "id_fr": 108, "id_orbis": 80, "label": "CUARTO DE ESCOLTAS" },
        { "id_fr": 109, "id_orbis": 117, "label": "GARAJE(S)" },
        { "id_fr": 110, "id_orbis": 145, "label": "OFICINA DE NEGOCIOS" },
        { "id_fr": 111, "id_orbis": 190, "label": "SALA DE INTERNET" },
        { "id_fr": 112, "id_orbis": 192, "label": "SALÓN COMUNAL" },
        { "id_fr": 113, "id_orbis": 226, "label": "VIVIENDA BIFAMILIAR" },
        { "id_fr": 114, "id_orbis": 227, "label": "VIVIENDA MULTIFAMILIAR" },
        { "id_fr": 115, "id_orbis": 176, "label": "PORTERÍA / RECEPCIÓN" },
        { "id_fr": 116, "id_orbis": 42, "label": "CALDERA" },
        { "id_fr": 117, "id_orbis": 57, "label": "CIRCUITO CERRADO DE TV" },
        { "id_fr": 118, "id_orbis": 175, "label": "PLANTA ELÉCTRICA" },
        { "id_fr": 119, "id_orbis": 223, "label": "VIGILANCIA" },
        { "id_fr": 120, "id_orbis": 7, "label": "ALARMA" },
        { "id_fr": 121, "id_orbis": 30, "label": "BAÑO AUXILIAR" },
        { "id_fr": 122, "id_orbis": 100, "label": "ESTUDIO" },
        { "id_fr": 123, "id_orbis": 81, "label": "CUARTO DE SERVICIO" },
        { "id_fr": 124, "id_orbis": 120, "label": "HALL DE ALCOBAS" },
        { "id_fr": 125, "id_orbis": 196, "label": "SAUNA / TURCO / JACUZZI" },
        { "id_fr": 126, "id_orbis": 224, "label": "VISTA PANORÁMICA" },
        { "id_fr": 127, "id_orbis": 38, "label": "BARRA ESTILO AMERICANO" },
        { "id_fr": 128, "id_orbis": 44, "label": "CALENTADOR" },
        { "id_fr": 129, "id_orbis": 56, "label": "CHIMENEA" },
        { "id_fr": 130, "id_orbis": 58, "label": "CITÓFONO" },
        { "id_fr": 131, "id_orbis": 65, "label": "COCINA TIPO AMERICANO" },
        { "id_fr": 132, "id_orbis": 69, "label": "COMEDOR AUXILIAR" },
        { "id_fr": 133, "id_orbis": 118, "label": "INSTALACIÓN DE GAS" },
        { "id_fr": 134, "id_orbis": 234, "label": "ZONA DE LAVANDERÍA" },
        { "id_fr": 135, "id_orbis": 206, "label": "SOBRE VÍA PRINCIPAL" },
        { "id_fr": 136, "id_orbis": 228, "label": "ZONA CAMPESTRE" },
        { "id_fr": 137, "id_orbis": 229, "label": "ZONA COMERCIAL" },
        { "id_fr": 138, "id_orbis": 235, "label": "ZONA INDUSTRIAL" },
        { "id_fr": 139, "id_orbis": 238, "label": "ZONA RESIDENCIAL" },
        { "id_fr": 140, "id_orbis": 68, "label": "COLEGIOS/UNIVERSIDADES" },
        { "id_fr": 141, "id_orbis": 219, "label": "TRANS. PÚBLICO CERCANO" },
        { "id_fr": 142, "id_orbis": 154, "label": "PARQUES CERCANOS" },
        { "id_fr": 143, "id_orbis": 209, "label": "SUPERMERCADOS/C.CIALES" },
        { "id_fr": 144, "id_orbis": 87, "label": "DUPLEX" },
        { "id_fr": 145, "id_orbis": 133, "label": "LOFT" },
        { "id_fr": 146, "id_orbis": 156, "label": "PENTHOUSE" },
        { "id_fr": 147, "id_orbis": 223, "label": "VIGILANCIA 24X7" },
        { "id_fr": 148, "id_orbis": 28, "label": "BAHÍA EXTERIOR DE PARQUEO" },
        { "id_fr": 149, "id_orbis": 8, "label": "ALARMA CONTRA INCENDIO" },
        { "id_fr": 150, "id_orbis": 210, "label": "TANQUES DE AGUA" },
        { "id_fr": 151, "id_orbis": 2, "label": "ACCESO PARA TRACTOMULAS" },
        { "id_fr": 152, "id_orbis": 180, "label": "PUERTA ELÉCTRICA" },
        { "id_fr": 153, "id_orbis": 136, "label": "MEZZANINE" },
        { "id_fr": 154, "id_orbis": 79, "label": "CUARTO DE CONDUCTORES" },
        { "id_fr": 155, "id_orbis": 83, "label": "DESPENSA" },
        { "id_fr": 156, "id_orbis": 3, "label": "ACCESO PAVIMENTADO" },
        { "id_fr": 157, "id_orbis": 176, "label": "PORTERÍA/VIGILANCIA" },
        { "id_fr": 158, "id_orbis": 185, "label": "RIO/QUEBRADA CERCANO(A)" },
        { "id_fr": 159, "id_orbis": 55, "label": "CERCA DE ZONA URBANA" },
        { "id_fr": 160, "id_orbis": 19, "label": "ÁRBOLES FRUTALES" },
        { "id_fr": 161, "id_orbis": 40, "label": "BÓSQUE NATIVO" },
        { "id_fr": 162, "id_orbis": 46, "label": "CANCHA DE BALONCESTO" },
        { "id_fr": 163, "id_orbis": 47, "label": "CANCHA DE FUTBOL" },
        { "id_fr": 164, "id_orbis": 117, "label": "GARAJE/PARQUEADERO(S)" },
        { "id_fr": 165, "id_orbis": 158, "label": "PESEBRERA" },
        { "id_fr": 166, "id_orbis": 177, "label": "POZO DE AGUA NATURAL" },
        { "id_fr": 167, "id_orbis": 205, "label": "SÍSTEMA DE RIEGO" },
        { "id_fr": 168, "id_orbis": 232, "label": "ZONA DE CAMPING" },
        { "id_fr": 169, "id_orbis": 128, "label": "KIOSKO" },
        { "id_fr": 170, "id_orbis": 112, "label": "GALPÓN" },
        { "id_fr": 171, "id_orbis": 60, "label": "COCHERA" },
        { "id_fr": 172, "id_orbis": 124, "label": "INVERNADERO" },
        { "id_fr": 173, "id_orbis": 98, "label": "ESTABLO" },
        { "id_fr": 174, "id_orbis": 62, "label": "COCINA EQUIPADA" },
        { "id_fr": 175, "id_orbis": 203, "label": "SERVICIOS PÚBLICOS" },
        { "id_fr": 176, "id_orbis": 233, "label": "ZONA DE HAMACAS" },
        { "id_fr": 177, "id_orbis": 230, "label": "ZONA DE BBQ" },
        { "id_fr": 178, "id_orbis": 234, "label": "SERVICIO DE LAVANDERÍA" },
        { "id_fr": 179, "id_orbis": 31, "label": "BAÑO COMPARTIDO" },
        { "id_fr": 180, "id_orbis": 59, "label": "CLOSET" },
        { "id_fr": 181, "id_orbis": 33, "label": "BAÑO INDEPENDIENTE" },
        { "id_fr": 182, "id_orbis": 200, "label": "SERVICIO DE ALIMENTACIÓN" },
        { "id_fr": 183, "id_orbis": 36, "label": "BAÑOS PÚBLICOS" },
        { "id_fr": 184, "id_orbis": 90, "label": "EN CENTRO COMERCIAL" },
        { "id_fr": 185, "id_orbis": 94, "label": "EN EDIFICIO" },
        { "id_fr": 186, "id_orbis": 229, "label": "EN ZONA COMERCIAL" },
        { "id_fr": 187, "id_orbis": 238, "label": "EN ZONA RESIDENCIAL" },
        { "id_fr": 188, "id_orbis": 110, "label": "FUERA DE CENTRO COMERCIAL" },
        { "id_fr": 189, "id_orbis": 207, "label": "SOBRE VÍA SECUNDARIA" },
        { "id_fr": 190, "id_orbis": 201, "label": "SERVICIO DE INTERNET" },
        { "id_fr": 191, "id_orbis": 165, "label": "PISO EN CEMENTO" },
        { "id_fr": 193, "id_orbis": 222, "label": "VENTILACIÓN NATURAL" },
        { "id_fr": 194, "id_orbis": 134, "label": "LOTE EN CONSTRUCCIÓN" },
        { "id_fr": 195, "id_orbis": 135, "label": "LOTE VACIO" },
        { "id_fr": 196, "id_orbis": 122, "label": "INDUSTRIAL" },
        { "id_fr": 197, "id_orbis": 73, "label": "CON VIVIENDA" },
        { "id_fr": 198, "id_orbis": 72, "label": "CON CERCA ELÉCTRICA" },
        { "id_fr": 199, "id_orbis": 21, "label": "ÁREA RURAL" },
        { "id_fr": 200, "id_orbis": 22, "label": "ÁREA URBANA" },
        { "id_fr": 201, "id_orbis": 97, "label": "ESQUINERO" },
        { "id_fr": 202, "id_orbis": 53, "label": "CERCA A SECTOR COMERCIAL" },
        { "id_fr": 203, "id_orbis": 35, "label": "BAÑOS COMUNALES" },
        { "id_fr": 204, "id_orbis": 89, "label": "EN CASA" },
        { "id_fr": 205, "id_orbis": 220, "label": "UBICADA EN EDIFICIO" },
        { "id_fr": 206, "id_orbis": 88, "label": "EDIFICIO INTELIGENTE" },
        { "id_fr": 207, "id_orbis": 113, "label": "GARAJE CUBIERTO" },
        { "id_fr": 208, "id_orbis": 194, "label": "SALÓN DE CONFERENCIAS" },
        { "id_fr": 209, "id_orbis": 41, "label": "CABLEADO DE RED" },
        { "id_fr": 210, "id_orbis": 67, "label": "COCINETA" },
        { "id_fr": 211, "id_orbis": 69, "label": "COMEDOR" },
        { "id_fr": 212, "id_orbis": 84, "label": "DETECCIÓN DE HUMO" },
        { "id_fr": 213, "id_orbis": 85, "label": "DETECTOR DE METALES" },
        { "id_fr": 214, "id_orbis": 95, "label": "ESCALERA DE EMERGENCIA" },
        { "id_fr": 215, "id_orbis": 111, "label": "GABINETE DE INCENDIOS" },
        { "id_fr": 216, "id_orbis": 162, "label": "PISO EN ALFOMBRA" },
        { "id_fr": 217, "id_orbis": 172, "label": "PISO EN MADERA" },
        { "id_fr": 218, "id_orbis": 179, "label": "PUERTA DE SEGURIDAD" },
        { "id_fr": 219, "id_orbis": 186, "label": "ROCIADORES DE AGUA" },
        { "id_fr": 220, "id_orbis": 212, "label": "TARJETAS MAGNÉTICAS" },
        { "id_fr": 221, "id_orbis": 86, "label": "DOTADO" },
        { "id_fr": 222, "id_orbis": 204, "label": "SHUT DE BASURA" },
        { "id_fr": 223, "id_orbis": 199, "label": "SENSOR DE MOVIMIENTO" },
        { "id_fr": 224, "id_orbis": 71, "label": "CON CASA PREFABRICADA" },
        { "id_fr": 225, "id_orbis": 91, "label": "CON CASA CLUB" },
        { "id_fr": 226, "id_orbis": 70, "label": "CON ADMINISTRADOR" },
        { "id_fr": 228, "id_orbis": 146, "label": "OFICINAS ADMINISTRATIVAS" },
        { "id_fr": 229, "id_orbis": 1, "label": "ACCESO PARA CAMIONES" },
        { "id_fr": 230, "id_orbis": 151, "label": "PARQUEADERO INTERNO" },
        { "id_fr": 231, "id_orbis": 161, "label": "PISO DE ALTA RESISTENCIA" },
        { "id_fr": 232, "id_orbis": 15, "label": "ALTURA LIBRE" },
        { "id_fr": 233, "id_orbis": 16, "label": "ALTURA RESTRINGIDA" },
        { "id_fr": 234, "id_orbis": 208, "label": "SOPORTE DE GRÚAS" },
        { "id_fr": 235, "id_orbis": 61, "label": "COCINA DE LEÑA" },
        { "id_fr": 236, "id_orbis": 107, "label": "FINCA GANADERA" },
        { "id_fr": 237, "id_orbis": 103, "label": "FINCA AGRÍCOLA" },
        { "id_fr": 238, "id_orbis": 105, "label": "FINCA AVÍCOLA" },
        { "id_fr": 239, "id_orbis": 106, "label": "FINCA CAFETERA" },
        { "id_fr": 240, "id_orbis": 104, "label": "FINCA AGROGANADERA" },
        { "id_fr": 241, "id_orbis": 150, "label": "PARQUEADERO INTELIGENTE" },
        { "id_fr": 242, "id_orbis": 96, "label": "ESCALERAS ELÉCTRICAS" },
        { "id_fr": 243, "id_orbis": 221, "label": "VALET PARKING" },
        { "id_fr": 244, "id_orbis": 28, "label": "BAHIAS DE PARQUEO" },
        { "id_fr": 245, "id_orbis": 223, "label": "VIGILANCIA PRIVADA 24*7" },
        { "id_fr": 246, "id_orbis": 92, "label": "EN CONDOMINIO" },
        { "id_fr": 247, "id_orbis": 91, "label": "EN CLUB" },
        { "id_fr": 248, "id_orbis": 78, "label": "CORRALES" },
        { "id_fr": 249, "id_orbis": 198, "label": "SENDEROS ECOLÓGICOS" },
        { "id_fr": 250, "id_orbis": 23, "label": "ASADOR" },
        { "id_fr": 251, "id_orbis": 52, "label": "CASA DE TRABAJADORES" },
        { "id_fr": 252, "id_orbis": 25, "label": "ASCENSOR(ES) INTELIGENTE(S)" },
        { "id_fr": 253, "id_orbis": 75, "label": "CONTROL DE ACCESO DIGITAL" },
        { "id_fr": 254, "id_orbis": 76, "label": "CONTROL DE ACÚSTICA" },
        { "id_fr": 255, "id_orbis": 77, "label": "CONTROL TÉRMICO" },
        { "id_fr": 256, "id_orbis": 132, "label": "LOCALES COMERCIALES" },
        { "id_fr": 257, "id_orbis": 211, "label": "TARJETAS INTELIGENTES" },
        { "id_fr": 258, "id_orbis": 148, "label": "PARQUE INDUSTRIAL" },
        { "id_fr": 259, "id_orbis": 184, "label": "RESTAURANTES" },
        { "id_fr": 260, "id_orbis": 39, "label": "BOMBAS DE GASOLINA" },
        { "id_fr": 261, "id_orbis": 138, "label": "NACIMIENTOS DE AGUA" },
        { "id_fr": 262, "id_orbis": 197, "label": "SEGURIDAD" },
        { "id_fr": 264, "id_orbis": 54, "label": "CERCA CENTRO COMERCIAL" },
        { "id_fr": 265, "id_orbis": 194, "label": "SALÓN DE VIDEOCONFERENCIAS" },
        { "id_fr": 271, "id_orbis": 129, "label": "AIRE LAVADO" },
        { "id_fr": 272, "id_orbis": 224, "label": "PANORÁMICA UN LADO" },
        { "id_fr": 273, "id_orbis": 152, "label": "PARQUEADERO SUBTERRANEO" },
        { "id_fr": 274, "id_orbis": 149, "label": "PARQUEADERO A NIVEL" },
        { "id_fr": 275, "id_orbis": 126, "label": "JARDINES EXTERIORES" },
        { "id_fr": 276, "id_orbis": 182, "label": "REJA DE SEGURIDAD" },
        { "id_fr": 279, "id_orbis": 27, "label": "ASCENSORES COMUNALES" },
        { "id_fr": 280, "id_orbis": 25, "label": "ASCENSOR(ES) INTELIGENTE(S)" },
        { "id_fr": 281, "id_orbis": 35, "label": "BAÑOS COMUNALES" },
        { "id_fr": 282, "id_orbis": 42, "label": "CALDERA" },
        { "id_fr": 283, "id_orbis": 57, "label": "CIRCUITO CERRADO DE TV" },
        { "id_fr": 284, "id_orbis": 75, "label": "CONTROL DE ACCESO DIGITAL" },
        { "id_fr": 285, "id_orbis": 80, "label": "CUARTO DE ESCOLTAS" },
        { "id_fr": 286, "id_orbis": 96, "label": "ESCALERAS ELÉCTRICAS" },
        { "id_fr": 287, "id_orbis": 113, "label": "GARAJE CUBIERTO" },
        { "id_fr": 288, "id_orbis": 132, "label": "LOCALES COMERCIALES" },
        { "id_fr": 289, "id_orbis": 150, "label": "PARQUEADERO INTELIGENTE" },
        { "id_fr": 290, "id_orbis": 153, "label": "PARQUEADERO VISITANTES" },
        { "id_fr": 291, "id_orbis": 175, "label": "PLANTA ELÉCTRICA" },
        { "id_fr": 292, "id_orbis": 181, "label": "PORTERÍA/RECEPCIÓN" },
        { "id_fr": 293, "id_orbis": 193, "label": "SALÓN DE JUEGOS" },
        { "id_fr": 294, "id_orbis": 194, "label": "SALÓN DE VIDEOCONFERENCIAS" },
        { "id_fr": 295, "id_orbis": 210, "label": "TANQUES DE AGUA" },
        { "id_fr": 296, "id_orbis": 211, "label": "TARJETAS INTELIGENTES" },
        { "id_fr": 297, "id_orbis": 212, "label": "TARJETAS MAGNÉTICAS" },
        { "id_fr": 298, "id_orbis": 218, "label": "TERRAZA" },
        { "id_fr": 299, "id_orbis": 220, "label": "UBICADA EN EDIFICIO" },
        { "id_fr": 300, "id_orbis": 88, "label": "EDIFICIO INTELIGENTE" },
        { "id_fr": 301, "id_orbis": 53, "label": "PASAJE COMERCIAL" },
        { "id_fr": 304, "id_orbis": 155, "label": "PATIO INTERNO" },
        { "id_fr": 305, "id_orbis": 76, "label": "CONTROL DE ACÚSTICA" },
        { "id_fr": 306, "id_orbis": 77, "label": "CONTROL TÉRMICO" },
        { "id_fr": 307, "id_orbis": 31, "label": "BAÑOS MIXTOS" }
    ]

    list_errores_finca_raiz = [
        { "code": -101, "msg": "Las credenciales del header no son válidas" },
        { "code": -102, "msg": "Nombre de usuario de OV no válido" },
        { "code": -103, "msg": "Nro de Ref no informado" },
        { "code": -104, "msg": "Barrio no informado" },
        { "code": -105, "msg": "Teléfono erroneo" },
        { "code": -106, "msg": "Email erroneo" },
        { "code": -107, "msg": "Precio erroneo" },
        { "code": -108, "msg": "Area no informada" },
        { "code": -109, "msg": "Habitaciones erroneas" },
        { "code": -110, "msg": "Baños erroneos" },
        { "code": -111, "msg": "Tipo de inmueble erroneo" },
        { "code": -112, "msg": "Ubicación erronea" },
        { "code": -113, "msg": "Tipo de Oferta erroneo" },
        { "code": -114, "msg": "Estado de conservacion erroneo" },
        { "code": -115, "msg": "Antigüedad erronea" },
        { "code": -116, "msg": "Nro de piso" },
        { "code": -117, "msg": "IDEstado erroneo" },
        { "code": -118, "msg": "Extras inválidas" },
        { "code": -119, "msg": "Imágenes inválidas" },
        { "code": -120, "msg": "Inmobiliaria sin cupo" },
        { "code": -121, "msg": "Tipo de Clima erroneo" },
        { "code": -122, "msg": "Estrato erroneo" },
        { "code": -123, "msg": "Telefono 2 erroneo" },
        { "code": -124, "msg": "Telefono 3 erroneo" },
        { "code": -125, "msg": "AddressViewType erroneo" },
        { "code": -126, "msg": "Valor de latitud erroneo" },
        { "code": -127, "msg": "Valor de longitud erroneo" },
        { "code": -129, "msg": "Usuario Inactivo" },
        { "code": -130, "msg": "Nro de Ref no existe" },
        { "code": -131, "msg": "Agente no válido" },
        { "code": -132, "msg": "Proyecto Nuevo" },
        { "code": -133, "msg": "Comentario no informado" },
        { "code": -134, "msg": "El contrato asociado a este aviso esta deshabilitado" },
        { "code": -135, "msg": "Una de las multimedias enviadas tiene la URL en NULL" },
        { "code": -136, "msg": "Cliente no asociado al integrador" },
        { "code": -137, "msg": "El integrador ya gasto su máximo de peticiones diarias" },
        { "code": -138, "msg": "La ip desde donde se accede no esta asociada a este integrador" },
        { "code": -139, "msg": "Está tratando de integrar en una hora que no tiene permiso" },
        { "code": -200, "msg": "Error actualizando aviso" },
        { "code": -300, "msg": "Error genérico" },
        { "code": -501, "msg": "Ventana de mantenimiento" }
    ]

    caracteristicas_properati = [
        'BALCÓN',
        'AIRES ACONDICIONADOS',
        'ALARMA',
        'CIRCUITO CERRADO DE TV',
        'ZONA DE CAFETERIA',
        'PISO EN ALFOMBRA',
        'DEPOSITO/BODEGA',
        'CLOSETS',
        'CONDOMINIO',
        'SALÓN COMUNAL',
        'COMEDOR',
        'LAVAPLATOS',
        'ASCENSOR',
        'EXTRACTOR',
        'CHIMENEA',
        'COCINA INTEGRAL',
        'AMOBLADO',
        'JARDÍN',
        'CONJ.CERRADO',
        'KIOSKO',
        'PLANTA ELÉCTRICA',
        'ASADOR',
        'PARQUEADERO VISITANTES',
        'GIMNASIO',
        'CALEFACCION TOTAL ED',
        'GARAJE CUBIERTO',
        'GALPÓN',
        'SERVICIO DE INTERNET',
        'SISTEMA DE RIEGO',
        'COCINA TRADICIONAL',
        'SERVICIO LAVANDERÍA',
        'SALA-COMEDOR',
        'SALA',
        'CERCA CENTRO COMERCIAL',
        'SALÓN DE VIDEOCONFERENCIAS',
        'BAR',
        'GAS NATURAL',
        'HORNO',
        'ACCESO PAVIMENTADO',
        'PERMITE MASCOTAS',
        'ZONA INFANTIL',
        'TANQUES DE AGUA',
        'SAUNA/TURCO/JACUZZI',
        'COLEGIOS/UNIVERSIDADES',
        'BAÑO DE SERVICIO',
        'ALC DE SERV SIN BAÑO',
        'CANCHA DE FUTBOL',
        'CANCHAS DEPORTIVAS',
        'ESTUDIO',
        'PORTERÍA/VIGILANCIA',
        'PISCINAS',
        'CANCHA DE TENNIS',
        'TERRAZA',
        'VENTILACIÓN NATURAL',
        'LAVADORA',
        'CALENTADOR ELECTRICO'
    ]

    tp_inmu_100_cuadras = [
        { "value": 10, "label": "APARTAMENTO"},
        { "value": 11, "label": "CASA"},
        { "value": 12, "label": "FINCA"},
        { "value": 13, "label": "OFICINA"},
        { "value": 14, "label": "CONSULTORIO"},
        { "value": 15, "label": "BODEGA"},
        { "value": 16, "label": "LOCAL"},
        { "value": 17, "label": "LOTE"},
        { "value": 21, "label": "EDIFICIO"},
        { "value": 29, "label": "APARTAESTUDIO"},
        { "value": 37, "label": "PARQUEADERO"},
        { "value": 39, "label": "DEPÓSITO"},
        { "value": 38, "label": "CASA CAMPESTRE"},
        { "value": 36, "label": "SUITE" }
    ]

    estrato_100_cuadras = [
        { "value": 1, "label": 2 },
        { "value": 2, "label": 3 },
        { "value": 3, "label": 4 },
        { "value": 4, "label": 5 },
        { "value": 5, "label": 6 },
        { "value": 6, "label": 1 }
    ]

    tp_pisos_100_cuadras = [
        { "value": 1, "label": "PISO EN ALFOMBRA" },
        { "value": 2, "label": "PISO EN BALDOSA" },
        { "value": 3, "label": "PISO EN CERAMICA" },
        { "value": 4, "label": "PISOS EN MADERA" },
        { "value": 6, "label": "PISO EN MARMOL" },
        { "value": 7, "label": "PISOS PORCELANATO" },
        { "value": 8, "label": "OTRO" }
    ]

    tp_canlentador_100_cuadras = [
        { "value": 1, "label": "CALENTADOR A GAS" },
        { "value": 2, "label": "CALENTADOR ELECTRICO" },
        { "value": 3, "label": "NO TIENE" }
    ]

    carac_100_cuadras = [
        { "label": "PISCINA PRIVADA" }, #privatePool
        { "label": "CUARTO DE SERVICIO" }, #serviceRoom
        { "label": "BAÑO DE SERVICIO" }, #serviceBathroom
        { "label": "ZONA DE LAVANDERIA" }, #laundryZone
        # { "value": 234, "label": "floorTypes" }, #floorTypes
        { "label": "CHIMENEA" }, #chimney
        { "label": "PERMITE MASCOTAS" }, #allowPets
        # { "value": 157, "label": "heaterType" }, #heaterType
        { "label": "AIRES ACONDICIONADOS" }, #airConditioner
        { "label": "NÚMERO DE TERRAZAS" }, #terracesNumber
        { "label": "ÁREA DE TERRAZAS" }, #terraceArea
        { "label": "NIVELES/PISOS" }, #floorsNumber
        { "label": "ASCENSORES" }, #elevatorsNumber
        { "label": "PORTERÍA/VIGILANCIA" }, #vigilance
        { "label": "NUMERO DE PARQUEADERO DE VISITANTES" }, #numParkingVisitors
        { "label": "RECEPCIÓN" }, #reception
        { "label": "CIRCUITO CERRADO DE TV" }, #closedCircuitTv
        { "label": "PLANTA ELÉCTRICA" }, #electricPlant
        { "label": "SALÓN COMUNAL" }, #communalLiving
        { "label": "ZONA INFANTIL" }, #childrenZone
        { "label": "ZONAS VERDES" }, #greenZones
        { "label": "PISCINAS" }, #communalPool
        { "label": "GIMNASIO" }, #gym
        { "label": "ZONA SOCIAL" }, #socialVenue
        { "label": "AMOBLADO" }, #furnished
    ]

    codigos_localidad_100_cuadras = [
        { "id": 1, "cod_dane": 91263 },
        { "id": 2, "cod_dane": 91405 },
        { "id": 3, "cod_dane": 91407 },
        { "id": 4, "cod_dane": 76403 },
        { "id": 6, "cod_dane": 91460 },
        { "id": 7, "cod_dane": 91530 },
        { "id": 8, "cod_dane": 91536 },
        { "id": 9, "cod_dane": 91540 },
        { "id": 10, "cod_dane": 54553 },
        { "id": 11, "cod_dane": 91798 },
        { "id": 14, "cod_dane": 5004 },
        { "id": 17, "cod_dane": 5031 },
        { "id": 20, "cod_dane": 5038 },
        { "id": 21, "cod_dane": 5040 },
        { "id": 22, "cod_dane": 5044 },
        { "id": 58, "cod_dane": 5113 },
        { "id": 59, "cod_dane": 5120 },
        { "id": 60, "cod_dane": 5125 },
        { "id": 80, "cod_dane": 5134 },
        { "id": 81, "cod_dane": 5138 },
        { "id": 82, "cod_dane": 5142 },
        { "id": 83, "cod_dane": 5145 },
        { "id": 84, "cod_dane": 5147 },
        { "id": 85, "cod_dane": 5150 },
        { "id": 86, "cod_dane": 5154 },
        { "id": 87, "cod_dane": 5172 },
        { "id": 88, "cod_dane": 5190 },
        { "id": 89, "cod_dane": 5101 },
        { "id": 90, "cod_dane": 5197 },
        { "id": 91, "cod_dane": 68207 },
        { "id": 92, "cod_dane": 47205 },
        { "id": 94, "cod_dane": 5234 },
        { "id": 95, "cod_dane": 5237 },
        { "id": 96, "cod_dane": 5240 },
        { "id": 97, "cod_dane": 5250 },
        { "id": 99, "cod_dane": 5697 },
        { "id": 100, "cod_dane": 5264 },
        { "id": 108, "cod_dane": 5282 },
        { "id": 109, "cod_dane": 5284 },
        { "id": 110, "cod_dane": 5306 },
        { "id": 137, "cod_dane": 5310 },
        { "id": 138, "cod_dane": 50313 },
        { "id": 139, "cod_dane": 68320 },
        { "id": 502, "cod_dane": 17486 },
        { "id": 691, "cod_dane": 25099 },
        { "id": 697, "cod_dane": 25126 },
        { "id": 758, "cod_dane": 25320 },
        { "id": 822, "cod_dane": 25489 },
        { "id": 1481, "cod_dane": 54405 },
        { "id": 1482, "cod_dane": 54874 },
        { "id": 2449, "cod_dane": 5266 },
        { "id": 2462, "cod_dane": 5631 },
        { "id": 2479, "cod_dane": 5380 },
        { "id": 3330, "cod_dane": 52473 },
        { "id": 3354, "cod_dane": 15131 },
        { "id": 3366, "cod_dane": 5212 },
        { "id": 3594, "cod_dane": 25843 },
        { "id": 3595, "cod_dane": 23001 },
        { "id": 4918, "cod_dane": 25175 },
        { "id": 4919, "cod_dane": 63130 },
        { "id": 4923, "cod_dane": 63401 },
        { "id": 4951, "cod_dane": 76364 },
        { "id": 4952, "cod_dane": 68276 },
        { "id": 4991, "cod_dane": 25214 },
        { "id": 4999, "cod_dane": 5318 },
        { "id": 5082, "cod_dane": 91001 },
        { "id": 5150, "cod_dane": 99001 },
        { "id": 5180, "cod_dane": 86001 },
        { "id": 5244, "cod_dane": 5607 },
        { "id": 5247, "cod_dane": 25758 },
        { "id": 5248, "cod_dane": 8758 },
        { "id": 5250, "cod_dane": 41530 },
        { "id": 5252, "cod_dane": 68307 },
        { "id": 5253, "cod_dane": 25875 },
        { "id": 5255, "cod_dane": 70221 },
        { "id": 5259, "cod_dane": 25743 },
        { "id": 5261, "cod_dane": 5376 },
        { "id": 5263, "cod_dane": 8296 },
        { "id": 5265, "cod_dane": 25817 },
        { "id": 5268, "cod_dane": 25377 },
        { "id": 5269, "cod_dane": 5656 },
        { "id": 5271, "cod_dane": 94884 },
        { "id": 5282, "cod_dane": 63190 },
        { "id": 5284, "cod_dane": 63272 },
        { "id": 5286, "cod_dane": 63470 },
        { "id": 5288, "cod_dane": 63690 },
        { "id": 5290, "cod_dane": 73275 },
        { "id": 5292, "cod_dane": 76126 },
        { "id": 5294, "cod_dane": 25035 },
        { "id": 5296, "cod_dane": 68418 },
        { "id": 5298, "cod_dane": 5042 },
        { "id": 5300, "cod_dane": 25430 },
        { "id": 5302, "cod_dane": 76400 },
        { "id": 5327, "cod_dane": 5674 },
        { "id": 5332, "cod_dane": 25799 },
        { "id": 5334, "cod_dane": 25815 },
        { "id": 5336, "cod_dane": 5148 },
        { "id": 5344, "cod_dane": 5308 },
        { "id": 5346, "cod_dane": 5440 },
        { "id": 5348, "cod_dane": 68547 },
        { "id": 5353, "cod_dane": 76377 },
        { "id": 5355, "cod_dane": 41298 },
        { "id": 5357, "cod_dane": 25785 },
        { "id": 5359, "cod_dane": 25002 },
        { "id": 5361, "cod_dane": 8832 },
        { "id": 5363, "cod_dane": 54003 },
        { "id": 5372, "cod_dane": 50006 },
        { "id": 5374, "cod_dane": 41006 },
        { "id": 5386, "cod_dane": 20011 },
        { "id": 5388, "cod_dane": 85010 },
        { "id": 5394, "cod_dane": 52019 },
        { "id": 5396, "cod_dane": 76020 },
        { "id": 5398, "cod_dane": 76036 },
        { "id": 5400, "cod_dane": 17050 },
        { "id": 5402, "cod_dane": 25053 },
        { "id": 5420, "cod_dane": 5002 },
        { "id": 5422, "cod_dane": 73483 },
        { "id": 5424, "cod_dane": 17013 },
        { "id": 5425, "cod_dane": 5021 },
        { "id": 5427, "cod_dane": 47030 },
        { "id": 5429, "cod_dane": 15022 },
        { "id": 5431, "cod_dane": 73024 },
        { "id": 5433, "cod_dane": 73026 },
        { "id": 5435, "cod_dane": 5030 },
        { "id": 5440, "cod_dane": 73030 },
        { "id": 5442, "cod_dane": 5034 },
        { "id": 5450, "cod_dane": 5036 },
        { "id": 5453, "cod_dane": 25040 },
        { "id": 5455, "cod_dane": 17042 },
        { "id": 5457, "cod_dane": 76041 },
        { "id": 5470, "cod_dane": 73043 },
        { "id": 5480, "cod_dane": 25599 },
        { "id": 5482, "cod_dane": 68051 },
        { "id": 5484, "cod_dane": 5051 },
        { "id": 5493, "cod_dane": 15051 },
        { "id": 5494, "cod_dane": 13052 },
        { "id": 5498, "cod_dane": 63001 },
        { "id": 5499, "cod_dane": 73055 },
        { "id": 5504, "cod_dane": 73067 },
        { "id": 5508, "cod_dane": 76054 },
        { "id": 5510, "cod_dane": 76054 },
        { "id": 5512, "cod_dane": 27075 },
        { "id": 5514, "cod_dane": 66075 },
        { "id": 5516, "cod_dane": 8078 },
        { "id": 5518, "cod_dane": 68077 },
        { "id": 5520, "cod_dane": 68077 },
        { "id": 5524, "cod_dane": 68079 },
        { "id": 5534, "cod_dane": 20045 },
        { "id": 5536, "cod_dane": 17088 },
        { "id": 5538, "cod_dane": 52083 },
        { "id": 5541, "cod_dane": 66088 },
        { "id": 5545, "cod_dane": 5086 },
        { "id": 5547, "cod_dane": 25086 },
        { "id": 5549, "cod_dane": 5091 },
        { "id": 5551, "cod_dane": 68092 },
        { "id": 5556, "cod_dane": 68092 },
        { "id": 5558, "cod_dane": 25095 },
        { "id": 5559, "cod_dane": 54099 },
        { "id": 5561, "cod_dane": 76100 },
        { "id": 5579, "cod_dane": 15106 },
        { "id": 5583, "cod_dane": 15106 },
        { "id": 5597, "cod_dane": 70110 },
        { "id": 5599, "cod_dane": 76113 },
        { "id": 5601, "cod_dane": 25123 },
        { "id": 5603, "cod_dane": 25769 },
        { "id": 5605, "cod_dane": 76122 },
        { "id": 5607, "cod_dane": 73124 },
        { "id": 5609, "cod_dane": 25781 },
        { "id": 5611, "cod_dane": 25386 },
        { "id": 5613, "cod_dane": 19130 },
        { "id": 5627, "cod_dane": 68132 },
        { "id": 5629, "cod_dane": 19142 },
        { "id": 5635, "cod_dane": 25286 },
        { "id": 5644, "cod_dane": 25269 },
        { "id": 5654, "cod_dane": 23090 },
        { "id": 5679, "cod_dane": 17877 },
        { "id": 5680, "cod_dane": 52612 },
        { "id": 5683, "cod_dane": 73449 },
        { "id": 5684, "cod_dane": 17174 },
        { "id": 5694, "cod_dane": 63594 },
        { "id": 5697, "cod_dane": 68755 },
        { "id": 5723, "cod_dane": 73411 },
        { "id": 5724, "cod_dane": 73200 },
        { "id": 5725, "cod_dane": 25851 },
        { "id": 5726, "cod_dane": 25506 },
        { "id": 5731, "cod_dane": 73873 },
        { "id": 5733, "cod_dane": 50325 },
        { "id": 5734, "cod_dane": 15600 },
        { "id": 5736, "cod_dane": 73408 },
        { "id": 5737, "cod_dane": 68190 },
        { "id": 5743, "cod_dane": 25530 },
        { "id": 5745, "cod_dane": 19300 },
        { "id": 5752, "cod_dane": 53801 },
        { "id": 5777, "cod_dane": 76233 },
        { "id": 5857, "cod_dane": 8433 },
        { "id": 5861, "cod_dane": 25867 },
        { "id": 5864, "cod_dane": 25772 },
        { "id": 5866, "cod_dane": 15238 },
        { "id": 5868, "cod_dane": 73148 },
        { "id": 5870, "cod_dane": 76606 },
        { "id": 5873, "cod_dane": 41396 },
        { "id": 5874, "cod_dane": 25295 },
        { "id": 5879, "cod_dane": 25307 },
        { "id": 5880, "cod_dane": 15759 },
        { "id": 5882, "cod_dane": 25899 },
        { "id": 5883, "cod_dane": 66001 },
        { "id": 5884, "cod_dane": 73001 },
        { "id": 5885, "cod_dane": 63001 },
        { "id": 5894, "cod_dane": 68229 },
        { "id": 5895, "cod_dane": 68679 },
        { "id": 5896, "cod_dane": 68855 },
        { "id": 5898, "cod_dane": 41524 },
        { "id": 5901, "cod_dane": 76520 },
        { "id": 5902, "cod_dane": 73443 },
        { "id": 5903, "cod_dane": 44090004 },
        { "id": 5904, "cod_dane": 47001002 },
        { "id": 5907, "cod_dane": 85410 },
        { "id": 5908, "cod_dane": 68895 },
        { "id": 5909, "cod_dane": 70001 },
        { "id": 5910, "cod_dane": 25805 },
        { "id": 5912, "cod_dane": 50110 },
        { "id": 5913, "cod_dane": 68464 },
        { "id": 5914, "cod_dane": 15572 },
        { "id": 5915, "cod_dane": 15368 },
        { "id": 5919, "cod_dane": 25488 },
        { "id": 5924, "cod_dane": 8634 },
        { "id": 5927, "cod_dane": 68872 },
        { "id": 5933, "cod_dane": 23660 },
        { "id": 5938, "cod_dane": 15516 },
        { "id": 6114, "cod_dane": 25260 },
        { "id": 6217, "cod_dane": 44001 },
        { "id": 6218, "cod_dane": 17873 },
        { "id": 6219, "cod_dane": 54518 },
        { "id": 6220, "cod_dane": 19290 },
        { "id": 6221, "cod_dane": 85300 },
        { "id": 6222, "cod_dane": 5001 },
        { "id": 6226, "cod_dane": 52473 },
        { "id": 6227, "cod_dane": 68615 },
        { "id": 6228, "cod_dane": 76001 },
        { "id": 6229, "cod_dane": 73675 },
        { "id": 6230, "cod_dane": 68001 },
        { "id": 6231, "cod_dane": 5347 },
        { "id": 6232, "cod_dane": 50001 },
        { "id": 6233, "cod_dane": 54172 },
        { "id": 6234, "cod_dane": 8520 },
        { "id": 6235, "cod_dane": 19573 },
        { "id": 6236, "cod_dane": 27001 },
        { "id": 6237, "cod_dane": 5809 },
        { "id": 6238, "cod_dane": 17541 },
        { "id": 6239, "cod_dane": 68705 },
        { "id": 6240, "cod_dane": 52480 },
        { "id": 6241, "cod_dane": 66687 },
        { "id": 6242, "cod_dane": 68250 },
        { "id": 6243, "cod_dane": 5686 },
        { "id": 6244, "cod_dane": 18860 },
        { "id": 6245, "cod_dane": 63212 },
        { "id": 6246, "cod_dane": 81736 },
        { "id": 6247, "cod_dane": 76834 },
        { "id": 6248, "cod_dane": 76248 },
        { "id": 6249, "cod_dane": 66400 },
        { "id": 6250, "cod_dane": 25148 },
        { "id": 6251, "cod_dane": 19001 },
        { "id": 6252, "cod_dane": 85001 },
        { "id": 6253, "cod_dane": 76111 },
        { "id": 6254, "cod_dane": 15664 },
        { "id": 6255, "cod_dane": 25394 },
        { "id": 6256, "cod_dane": 25245 },
        { "id": 6257, "cod_dane": 52254 },
        { "id": 6258, "cod_dane": 20013 },
        { "id": 6259, "cod_dane": 41615 },
        { "id": 6260, "cod_dane": 73563 },
        { "id": 6261, "cod_dane": 5890 },
        { "id": 6262, "cod_dane": 66440 },
        { "id": 6263, "cod_dane": 25518 },
        { "id": 6264, "cod_dane": 41551 },
        { "id": 6265, "cod_dane": 5670 },
        { "id": 6266, "cod_dane": 5501 },
        { "id": 6267, "cod_dane": 25438 },
        { "id": 6268, "cod_dane": 68872 },
        { "id": 6269, "cod_dane": 8372 },
        { "id": 6270, "cod_dane": 54498 },
        { "id": 6271, "cod_dane": 52240 },
        { "id": 6272, "cod_dane": 25398 },
        { "id": 6273, "cod_dane": 76306 },
        { "id": 6274, "cod_dane": 52356 },
        { "id": 6275, "cod_dane": 5045 },
        { "id": 6277, "cod_dane": 25200 },
        { "id": 6278, "cod_dane": 8849 },
        { "id": 6279, "cod_dane": 68669 },
        { "id": 6280, "cod_dane": 73283 },
        { "id": 6281, "cod_dane": 23678 },
        { "id": 6282, "cod_dane": 15425 },
        { "id": 6284, "cod_dane": 50313 },
        { "id": 6285, "cod_dane": 19473 },
        { "id": 6286, "cod_dane": 19473 },
        { "id": 6287, "cod_dane": 41132 },
        { "id": 6288, "cod_dane": 41020 },
        { "id": 6289, "cod_dane": 5792 },
        { "id": 6290, "cod_dane": 13836 },
        { "id": 6291, "cod_dane": 15837 },
        { "id": 6292, "cod_dane": 5591 },
        { "id": 6293, "cod_dane": 5390 },
        { "id": 6294, "cod_dane": 66456 },
        { "id": 6296, "cod_dane": 25151 },
        { "id": 6297, "cod_dane": 25797 },
        { "id": 6298, "cod_dane": 68572 },
        { "id": 6299, "cod_dane": 23574 },
        { "id": 6300, "cod_dane": 47189 },
        { "id": 6301, "cod_dane": 54660 },
        { "id": 6302, "cod_dane": 94884 },
        { "id": 6303, "cod_dane": 41206 },
        { "id": 6304, "cod_dane": 52685 },
        { "id": 6305, "cod_dane": 25898 },
        { "id": 6306, "cod_dane": 76863 },
        { "id": 6307, "cod_dane": 15322 },
        { "id": 6309, "cod_dane": 17665 },
        { "id": 6310, "cod_dane": 76606 },
        { "id": 6311, "cod_dane": 85162 },
        { "id": 6312, "cod_dane": 19698 },
        { "id": 6313, "cod_dane": 76895 },
        { "id": 6314, "cod_dane": 76622 },
        { "id": 6315, "cod_dane": 73268 },
        { "id": 6316, "cod_dane": 5364 },
        { "id": 6317, "cod_dane": 5885 },
        { "id": 6318, "cod_dane": 19845 },
        { "id": 6319, "cod_dane": 15183 },
        { "id": 6320, "cod_dane": 73547 },
        { "id": 6325, "cod_dane": 13620 },
        { "id": 6326, "cod_dane": 76109 },
        { "id": 6327, "cod_dane": 44090 },
        { "id": 6328, "cod_dane": 73168 },
        { "id": 6330, "cod_dane": 23672 },
        { "id": 6331, "cod_dane": 76497 },
        { "id": 6332, "cod_dane": 25506 },
        { "id": 6336, "cod_dane": 73854 },
        { "id": 6337, "cod_dane": 8549 },
        { "id": 6338, "cod_dane": 8685 },
        { "id": 6339, "cod_dane": 47745 },
        { "id": 6340, "cod_dane": 25645 },
        { "id": 6341, "cod_dane": 15204 },
        { "id": 6342, "cod_dane": 76563 },
        { "id": 6343, "cod_dane": 5579 },
        { "id": 6344, "cod_dane": 54261 },
        { "id": 6345, "cod_dane": 70670 },
        { "id": 6346, "cod_dane": 13838 },
        { "id": 6350, "cod_dane": 41359 },
        { "id": 6352, "cod_dane": 81794 },
        { "id": 6354, "cod_dane": 76845 },
        { "id": 6355, "cod_dane": 52001 },
        { "id": 6356, "cod_dane": 66318 },
        { "id": 6357, "cod_dane": 13657 },
        { "id": 6358, "cod_dane": 76869 },
        { "id": 6359, "cod_dane": 5690 },
        { "id": 6360, "cod_dane": 68720 },
        { "id": 6361, "cod_dane": 23162 },
        { "id": 6362, "cod_dane": 5425 },
        { "id": 6363, "cod_dane": 86755 },
        { "id": 6364, "cod_dane": 8558 },
        { "id": 6365, "cod_dane": 73678 },
        { "id": 6366, "cod_dane": 81001 },
        { "id": 6367, "cod_dane": 68235 },
        { "id": 6369, "cod_dane": 13001 },
        { "id": 6370, "cod_dane": 8001 },
        { "id": 6374, "cod_dane": 13673 },
        { "id": 6376, "cod_dane": 18094 },
        { "id": 6378, "cod_dane": 15686 },
        { "id": 6379, "cod_dane": 15776 },
        { "id": 6380, "cod_dane": 15362 },
        { "id": 6381, "cod_dane": 15491 },
        { "id": 6384, "cod_dane": 70110 },
        { "id": 6385, "cod_dane": 41885 },
        { "id": 6387, "cod_dane": 47001 },
        { "id": 6390, "cod_dane": 68121 },
        { "id": 6391, "cod_dane": 70820 },
        { "id": 6395, "cod_dane": 63302 },
        { "id": 6398, "cod_dane": 52356 },
        { "id": 6399, "cod_dane": 41013 },
        { "id": 6400, "cod_dane": 23555 },
        { "id": 6401, "cod_dane": 25154 },
        { "id": 6407, "cod_dane": 25299 },
        { "id": 6408, "cod_dane": 44430 },
        { "id": 6411, "cod_dane": 68655 },
        { "id": 6412, "cod_dane": 20710 },
        { "id": 6413, "cod_dane": 50689 },
        { "id": 6414, "cod_dane": 15806 },
        { "id": 6416, "cod_dane": 76275 },
        { "id": 6417, "cod_dane": 5658 },
        { "id": 6418, "cod_dane": 68820 },
        { "id": 6419, "cod_dane": 70823 },
        { "id": 6420, "cod_dane": 54673 },
        { "id": 6421, "cod_dane": 25293 },
        { "id": 6422, "cod_dane": 5490 },
        { "id": 6423, "cod_dane": 20228 },
        { "id": 6424, "cod_dane": 25426 },
        { "id": 6425, "cod_dane": 25572 },
        { "id": 6426, "cod_dane": 68549 },
        { "id": 6427, "cod_dane": 70713 },
        { "id": 6428, "cod_dane": 68147 },
        { "id": 6429, "cod_dane": 54245 },
        { "id": 6430, "cod_dane": 15808 },
        { "id": 6466, "cod_dane": 27006 },
        { "id": 6467, "cod_dane": 85250 },
        { "id": 6470, "cod_dane": 68250 },
        { "id": 6475, "cod_dane": 47555 },
        { "id": 6477, "cod_dane": 76670 },
        { "id": 6547, "cod_dane": 50226 },
        { "id": 6548, "cod_dane": 17867 },
        { "id": 6549, "cod_dane": 17446 },
        { "id": 6550, "cod_dane": 23090 },
        { "id": 6551, "cod_dane": 52083 },
        { "id": 6552, "cod_dane": 20238 },
        { "id": 6553, "cod_dane": 25307 },
        { "id": 6554, "cod_dane": 73352 },
        { "id": 6555, "cod_dane": 15599 },
        { "id": 6556, "cod_dane": 63548 },
        { "id": 6558, "cod_dane": 73585 },
        { "id": 6559, "cod_dane": 15224 },
        { "id": 6560, "cod_dane": 41791 },
        { "id": 6565, "cod_dane": 50251 },
        { "id": 6566, "cod_dane": 95025 },
        { "id": 6567, "cod_dane": 19807 },
        { "id": 6568, "cod_dane": 41668 },
        { "id": 6569, "cod_dane": 5756 },
        { "id": 6570, "cod_dane": 15104 },
        { "id": 6571, "cod_dane": 15720 },
        { "id": 6572, "cod_dane": 15494 },
        { "id": 6573, "cod_dane": 25841 },
        { "id": 6574, "cod_dane": 68397 },
        { "id": 6575, "cod_dane": 50350 },
        { "id": 6576, "cod_dane": 68745 },
        { "id": 6577, "cod_dane": 76400 },
        { "id": 6580, "cod_dane": 25407 },
        { "id": 6581, "cod_dane": 68872 },
        { "id": 6582, "cod_dane": 19824 },
        { "id": 6583, "cod_dane": 5642 },
        { "id": 6584, "cod_dane": 41001 },
        { "id": 6586, "cod_dane": 68324 },
        { "id": 6589, "cod_dane": 15272 },
        { "id": 6590, "cod_dane": 25224 },
        { "id": 6591, "cod_dane": 20060 },
        { "id": 6592, "cod_dane": 5604 },
        { "id": 6597, "cod_dane": 25322 },
        { "id": 6598, "cod_dane": 70771 },
        { "id": 6600, "cod_dane": 25372 },
        { "id": 6601, "cod_dane": 66572 },
        { "id": 6602, "cod_dane": 8137 },
        { "id": 6603, "cod_dane": 15778 },
        { "id": 6604, "cod_dane": 66045 },
        { "id": 6605, "cod_dane": 52838 },
        { "id": 6606, "cod_dane": 76736 },
        { "id": 6607, "cod_dane": 25779 },
        { "id": 6608, "cod_dane": 76890 },
        { "id": 6609, "cod_dane": 76616 },
        { "id": 6610, "cod_dane": 76823 },
        { "id": 6611, "cod_dane": 19701 },
        { "id": 6613, "cod_dane": 44560 },
        { "id": 6614, "cod_dane": 17272 },
        { "id": 6615, "cod_dane": 41078 },
        { "id": 6616, "cod_dane": 41872 },
        { "id": 6617, "cod_dane": 15172 },
        { "id": 6618, "cod_dane": 99773 },
        { "id": 6619, "cod_dane": 68320 },
        { "id": 6624, "cod_dane": 52260 },
        { "id": 6625, "cod_dane": 68669 },
        { "id": 6631, "cod_dane": 68872 },
        { "id": 6632, "cod_dane": 25873 },
        { "id": 6635, "cod_dane": 25793 },
        { "id": 6637, "cod_dane": 25592 },
        { "id": 6638, "cod_dane": 19110 },
        { "id": 6640, "cod_dane": 68468 },
        { "id": 6642, "cod_dane": 5361 },
        { "id": 5646, "cod_dane": 68406 }
    ]

    tp_inm_arriendalo = [
        {"value": 1,"label": "APARTAMENTO"},
        {"value": 2,"label": "CASA"},
        {"value": 3,"label": "APARTAESTUDIO"},
        {"value": 4,"label": "LOCAL"},
        {"value": 5,"label": "BODEGA"},
        {"value": 6,"label": "OFICINA"},
        {"value": 7,"label": "LOTE"},
        {"value": 8,"label": "FINCA"},
        {"value": 9,"label": "EDIFICIO"},
        {"value": 10,"label": "CASA LOTE"},
        {"value": 11,"label": "PARQUEADERO"},
        {"value": 12,"label": "CASA CAMPESTRE"},
        {"value": 13,"label": "CASA LOCAL"},
        {"value": 14,"label": "CASA CONDOMINIO"},
        {"value": 17,"label": "HACIENDA"},
        {"value": 18,"label": "PREDIO"},
        {"value": 19,"label": "HOTEL"},
        {"value": 20,"label": "CASA RECREO"},
        {"value": 21,"label": "CASA PARA COMERCIO"},
        {"value": 22,"label": "CASA - APARTAMENTO"},
        {"value": 23,"label": "APARTAMENTO CON LOCAL"},
        {"value": 24,"label": "BODEGA CON LOCAL"},
        {"value": 25,"label": "CONSULTORIO"},
        {"value": 26,"label": "PARCELA"},
        {"value": 27,"label": "CABAÑA"},
        {"value": 28,"label": "CASA LOTE"},
        {"value": 29,"label": "PENTHOUSE"},
        {"value": 30,"label": "APARTAMENTO AMOBLADO"},
        {"value": 31,"label": "CASA AMOBLADA"},
        {"value": 32,"label": "CASA EN CONJUNTO"},
        {"value": 33,"label": "TERRAZA"},
        {"value": 35,"label": "CHALET"},
        {"value": 36,"label": "FINCA - HOTELES"},
        {"value": 37,"label": "LOTE DE PLAYA"},
        {"value": 38,"label": "HOSTAL"},
        {"value": 39,"label": "DUPLEX"},
        {"value": 40,"label": "ATICO"},
        {"value": 41,"label": "BUNGALOW"},
        {"value": 42,"label": "GALPON INDUSTRIAL"},
        {"value": 43,"label": "CASA DE PLAYA"},
        {"value": 44,"label": "PISO"},
        {"value": 46,"label": "CORTIJO"},
        {"value": 47,"label": "ISLA"},
        {"value": 48,"label": "NAVE INDUSTRIAL"},
        {"value": 50,"label": "PROYECTO"},
        {"value": 51,"label": "CASA NEGOCIO"},
        {"value": 52,"label": "CASA QUINTA"},
        {"value": 53,"label": "LOFT"}
    ]

    caracteristicas_arriendelo = [
        {"value": 1,"label": "BAÑO AUXILIAR"},
        {"value": 2,"label": "BAÑO DE SERVICIO"},
        {"value": 3,"label": "PISO EN CERÁMICA"},
        {"value": 4,"label": "COCINA SEMI-INTEGRAL"},
        {"value": 5,"label": "GAS NATURAL"},
        {"value": 6,"label": "SALA-COMEDOR"},
        {"value": 7,"label": "COMEDOR INDEPENDIENTE"},
        {"value": 8,"label": "BALCÓN"},
        {"value": 9,"label": "VISTA EXTERIOR"},
        {"value": 10,"label": "FAMILY ROOM"},
        {"value": 11,"label": "CUARTO DE SERVICIO"},
        {"value": 12,"label": "ESTUDIO"},
        {"value": 13,"label": "ILUMINACIÓN NATURAL"},
        {"value": 14,"label": "CLOSETS"},
        {"value": 15,"label": "DEPÓSITO/BODEGA"},
        {"value": 16,"label": "DIVISIONES"},
        {"value": 17,"label": "ZONA DE ROPAS"},
        {"value": 18,"label": "ZONA RESIDENCIAL"},
        {"value": 19,"label": "SOBRE VÍA SECUNDARIA"},
        {"value": 20,"label": "ACCESO PAVIMENTADO"},
        {"value": 21,"label": "SUPERMERCADOS/C.CIALES"},
        {"value": 22,"label": "PARQUES CERCANOS"},
        {"value": 23,"label": "TRANS. PÚBLICO CERCANO"},
        {"value": 24,"label": "GARAJE/PARQUEADERO(S)"},
        {"value": 25,"label": "PRECIO NEGOCIABLE"},
        {"value": 26,"label": "INSTALACIÓN DE GAS"},
        {"value": 27,"label": "VISTA INTERIOR"},
        {"value": 28,"label": "HALL"},
        {"value": 29,"label": "ESTADO OBRA BLANCA"},
        {"value": 30,"label": "PATIO"},
        {"value": 31,"label": "CABLEADO DE RED"},
        {"value": 32,"label": "CIRCUITO CERRADO DE TV"},
        {"value": 33,"label": "FACHADA PINTURA"},
        {"value": 34,"label": "SOBRE VÍA PRINCIPAL"},
        {"value": 35,"label": "USADO"},
        {"value": 36,"label": "NUEVO"},
        {"value": 37,"label": "BOMBAS DE GASOLINA"},
        {"value": 38,"label": "COLEGIOS/UNIVERSIDADES"},
        {"value": 39,"label": "PARQUEADERO INTERNO"},
        {"value": 40,"label": "COCINA A GAS"},
        {"value": 41,"label": "COCINA INTEGRAL"},
        {"value": 42,"label": "CONJ.CERRADO"},
        {"value": 43,"label": "VIGILANCIA 24X7"},
        {"value": 44,"label": "CANCHA DE FUTBOL"},
        {"value": 45,"label": "PISCINAS"},
        {"value": 46,"label": "CITÓFONO"},
        {"value": 47,"label": "ASCENSOR"},
        {"value": 48,"label": "PORTERÍA/VIGILANCIA"},
        {"value": 49,"label": "SHUT DE BASURA"},
        {"value": 50,"label": "SERVICIOS INDEPENDIENTES"},
        {"value": 51,"label": "ÁREA URBANA"},
        {"value": 52,"label": "CERCA DE ZONA URBANA"},
        {"value": 53,"label": "CALENTADOR A GAS"},
        {"value": 54,"label": "CANCHA DE BALONCESTO"},
        {"value": 55,"label": "ASADOR"},
        {"value": 56,"label": "PUERTA DE SEGURIDAD"},
        {"value": 57,"label": "ESCALERA DE EMERGENCIA"},
        {"value": 58,"label": "FACHADA LADRILLO A LA VISTA"},
        {"value": 59,"label": "ZONA COMERCIAL"},
        {"value": 60,"label": "SENDERO PEATONAL"},
        {"value": 61,"label": "JARDÍN"},
        {"value": 62,"label": "RESTAURANTES"},
        {"value": 63,"label": "AMOBLADO"},
        {"value": 64,"label": "AIRE ACONDICIONADO CENTRAL"},
        {"value": 65,"label": "PERSIANAS"},
        {"value": 66,"label": "UBICADA EN EDIFICIO"},
        {"value": 67,"label": "TARJETAS MAGNÉTICAS"},
        {"value": 68,"label": "GARAJE CUBIERTO"},
        {"value": 69,"label": "AUDITORIO"},
        {"value": 70,"label": "OFICINA DE NEGOCIOS"},
        {"value": 71,"label": "GABINETE DE INCENDIOS"},
        {"value": 72,"label": "BAÑOS PÚBLICOS"},
        {"value": 73,"label": "BLACKOUT"},
        {"value": 74,"label": "PISO DE ALTA RESISTENCIA"},
        {"value": 75,"label": "CORTINAS PESADAS"},
        {"value": 76,"label": "CONTROL ACCESO DIGITAL"},
        {"value": 77,"label": "PARQUEADERO VISITANTES"},
        {"value": 78,"label": "SENSOR DE MOVIMIENTO"},
        {"value": 79,"label": "ASCENSOR INTELIGENTE"},
        {"value": 80,"label": "SALÓN COMUNAL"},
        {"value": 81,"label": "SALÓN DE VIDEOCONFERENCIAS"},
        {"value": 82,"label": "ALARMA"},
        {"value": 83,"label": "PLANTA ELÉCTRICA"},
        {"value": 84,"label": "SOBRE CARRERA"},
        {"value": 85,"label": "CORPORATIVO"},
        {"value": 86,"label": "AIRE ACONDICIONADO MINISPLIT"},
        {"value": 87,"label": "CON CALEFACCIÓN"},
        {"value": 88,"label": "BAHIAS DE PARQUEO"},
        {"value": 89,"label": "PARQUEADERO INTELIGENTE"},
        {"value": 90,"label": "CUARTO DE ESCOLTAS"},
        {"value": 91,"label": "OFICINAS ADMINISTRATIVAS"},
        {"value": 92,"label": "EDIFICIO INTELIGENTE"},
        {"value": 93,"label": "USO SUELO COMERCIAL"},
        {"value": 94,"label": "MODERNO"},
        {"value": 95,"label": "SERVICIOS PÚBLICOS"},
        {"value": 96,"label": "CERCA A SECTOR COMERCIAL"},
        {"value": 97,"label": "PUERTA ELÉCTRICA"},
        {"value": 98,"label": "DETENCIÓN DE HUMO"},
        {"value": 99,"label": "TANQUES DE AGUA"},
        {"value": 100,"label": "GABINETES COCINA"},
        {"value": 101,"label": "EXTRACTOR"},
        {"value": 102,"label": "DIVISIONES BAÑOS"},
        {"value": 103,"label": "HABITACIÓN DE SERVICIO"},
        {"value": 105,"label": "ZONA SOCIAL"},
        {"value": 106,"label": "SAUNA/TURCO/JACUZZI"},
        {"value": 107,"label": "AGUA INSTALADA"},
        {"value": 108,"label": "LUZ MONOFÁSICA"},
        {"value": 109,"label": "PISOS EN MADERA"},
        {"value": 110,"label": "LUZ BIFÁSICA"},
        {"value": 111,"label": "PISOS EN BALDOSA - CERAMICA"},
        {"value": 112,"label": "LOCKER"},
        {"value": 113,"label": "ZONAS VERDES"},
        {"value": 114,"label": "PARQUEADERO DOBLE CUBIERTO"},
        {"value": 115,"label": "PISOS EN BALDOSA"},
        {"value": 116,"label": "LUZ TRIFÁSICA"},
        {"value": 117,"label": "PISO EN CEMENTO"},
        {"value": 118,"label": "TELÉFONO"},
        {"value": 119,"label": "COCINA TRADICIONAL"},
        {"value": 120,"label": "PISO EN GRANITO"},
        {"value": 121,"label": "PISOS EN GRANITO - BALDOSIN"},
        {"value": 122,"label": "PISO EN BALDOSÍN"},
        {"value": 123,"label": "PISOS EN GRANITO PULIDO"},
        {"value": 124,"label": "1 NIVEL"},
        {"value": 125,"label": "2 NIVELES"},
        {"value": 126,"label": "3 NIVELES"},
        {"value": 127,"label": "PISOS EN TABLETA"},
        {"value": 128,"label": "SALA INDEPENDIENTE"},
        {"value": 129,"label": "ZONA SOCIAL"},
        {"value": 130,"label": "ZONA JUEGOS"},
        {"value": 131,"label": "PISOS PORCELANATO"},
        {"value": 132,"label": "PISO EN MARMOL"},
        {"value": 133,"label": "PISOS EN TABLÓN"},
        {"value": 134,"label": "SEGURIDAD"},
        {"value": 135,"label": "4 NIVELES"},
        {"value": 136,"label": "5 NIVELES"},
        {"value": 137,"label": "SIN COCINA"},
        {"value": 138,"label": "AIRE ACONDICIONADO"},
        {"value": 139,"label": "BIBLIOTECA/ESTUDIO"},
        {"value": 140,"label": "HALL  DE ALCOBAS"},
        {"value": 141,"label": "VISTA PANORÁMICA"},
        {"value": 142,"label": "CALENTADOR"},
        {"value": 143,"label": "CHIMENEA"},
        {"value": 144,"label": "BARRA ESTILO AMERICANO"},
        {"value": 145,"label": "COCINA TIPO AMERICANO"},
        {"value": 146,"label": "COMEDOR AUXILIAR"},
        {"value": 147,"label": "ZONA DE LAVANDERÍA"},
        {"value": 148,"label": "DESPENSA"},
        {"value": 149,"label": "CUARTO DE CONDUCTORES"},
        {"value": 150,"label": "HOSPEDAJE TURISMO"},
        {"value": 151,"label": "BAÑO EN HABITACIÓN PRINCIPAL"},
        {"value": 152,"label": "ARMARIOS EMPOTRADOS"},
        {"value": 153,"label": "COCINA EQUIPADA"},
        {"value": 154,"label": "DOBLE VENTANA"},
        {"value": 155,"label": "VIVIENDA BIFAMILIAR"},
        {"value": 156,"label": "VIVIENDA UNIFAMILIAR"},
        {"value": 157,"label": "VIVIENDA TRIFAMILIAR"},
        {"value": 158,"label": "ADOSADO"},
        {"value": 159,"label": "REMODELADO"},
        {"value": 160,"label": "SAUNA/TURCO/JACUZZI"},
        {"value": 161,"label": "SAUNA/TURCO/JACUZZI"},
        {"value": 162,"label": "TRASTERO"},
        {"value": 163,"label": "CANCHA DE SQUASH"},
        {"value": 164,"label": "CANCHA DE TENNIS"},
        {"value": 165,"label": "CANCHAS DEPORTIVAS"},
        {"value": 166,"label": "GIMNASIO"},
        {"value": 167,"label": "JAULA DE GOLF"},
        {"value": 168,"label": "ZONA INFANTIL"},
        {"value": 169,"label": "SALA DE INTERNET"},
        {"value": 170,"label": "TERRAZA"},
        {"value": 171,"label": "VIVIENDA MULTIFAMILIAR"},
        {"value": 172,"label": "CONJ.CERRADO"},
        {"value": 173,"label": "ACCESO PAVIMENTADO"},
        {"value": 174,"label": "KIOSKO"},
        {"value": 175,"label": "RIO/QUEBRADA CERCANO(A)"},
        {"value": 176,"label": "ÁRBOLES FRUTALES"},
        {"value": 177,"label": "BOSQUE NATIVO"},
        {"value": 178,"label": "ESTABLO"},
        {"value": 179,"label": "GALPÓN"},
        {"value": 180,"label": "INVERNADERO"},
        {"value": 181,"label": "PESEBRERA"},
        {"value": 182,"label": "POZO DE AGUA NATURAL"},
        {"value": 183,"label": "SISTEMA DE RIEGO"},
        {"value": 184,"label": "ZONA DE CAMPING"},
        {"value": 185,"label": "ZONA CAMPESTRE"},
        {"value": 186,"label": "ZONA INDUSTRIAL"},
        {"value": 187,"label": "CENTROS COMERCIALES"},
        {"value": 188,"label": "PLAYAS"},
        {"value": 189,"label": "ÁREAS TURÍSTICAS"},
        {"value": 190,"label": "CALLES DE TOSCA"},
        {"value": 191,"label": "LAGO"},
        {"value": 192,"label": "GARITA DE ENTRADA"},
        {"value": 193,"label": "MONTAÑA"},
        {"value": 194,"label": "CLUB SOCIAL"},
        {"value": 195,"label": "BUNGALOW / PAREADO"},
        {"value": 196,"label": "PISTA DE PADEL"},
        {"value": 197,"label": "BARBACOA / PARRILLA / QUINCHO"},
        {"value": 198,"label": "LAGUNA"},
        {"value": 199,"label": "CLUB HOUSE"},
        {"value": 200,"label": "VIGILANCIA NOCTURNA"},
        {"value": 201,"label": "ZONA JUEGOS"},
        {"value": 202,"label": "ZONA DE BBQ"},
        {"value": 203,"label": "VIGILANCIA ELECTRÓNICA"},
        {"value": 204,"label": "VIGILANCIA DIURNA"},
        {"value": 205,"label": "SIN VIGILANCIA"},
        {"value": 206,"label": "PISOS EN TIERRA"},
        {"value": 207,"label": "BAÑO TURCO (EN CONSTRUCCIÓN)"},
        {"value": 208,"label": "SAUNA (EN CONSTRUCCIÓN)"},
        {"value": 209,"label": "GIMNASIO (EN CONSTRUCCIÓN)"},
        {"value": 210,"label": "PISCINA NIÑOS (EN CONSTRUCCIÓN)"},
        {"value": 211,"label": "PISCINA ADULTOS (EN CONSTRUCCIÓN)"},
        {"value": 212,"label": "SALA DE PING PONG"},
        {"value": 213,"label": "BBQ (EN CONSTRUCCIÓN)"},
        {"value": 214,"label": "ACCESO SILLA DE RUEDAS"},
        {"value": 215,"label": "MANTENIMIENTO ÁREAS COMUNES"},
        {"value": 216,"label": "EN PROCESO DE ENTREGA"},
        {"value": 217,"label": "ZONA SOCIAL NO DISPONIBLE"},
        {"value": 218,"label": "SALA DE CINE"},
        {"value": 219,"label": "ZONA SOCIAL PISCINA"},
        {"value": 220,"label": "CANCHA"},
        {"value": 221,"label": "CANCHA SINTÉTICA DE NIÑOS"},
        {"value": 222,"label": "SALÓN JUEGO DE NIÑOS"},
        {"value": 223,"label": "TERRAZA SOLÁRIUM"},
        {"value": 224,"label": "SALA DE ESTAR"},
        {"value": 225,"label": "GIMNASIO AL AIRE LIBRE"},
        {"value": 226,"label": "PISCINA PARA NIÑOS Y ADULTOS"},
        {"value": 227,"label": "ZONA DE NIÑOS SALÓN DE REUNIONES"},
        {"value": 228,"label": "PISCINA PARA NIÑOS"},
        {"value": 229,"label": "PISCINA PARA ADULTOS"},
        {"value": 230,"label": "CANCHA MULTIPLE"},
        {"value": 231,"label": "ZONA SOCIAL (EN CONSTRUCCIÓN)"},
        {"value": 232,"label": "JUEGOS DE NIÑOS"},
        {"value": 233,"label": "JUEGOS DE MESA"},
        {"value": 234,"label": "HORNO"},
        {"value": 235,"label": "PERRERA"},
        {"value": 236,"label": "ZONAS HÚMEDAS"},
        {"value": 237,"label": "ORATORIO"},
        {"value": 238,"label": "GUARDERÍA"},
        {"value": 239,"label": "SALA DE TV"},
        {"value": 240,"label": "SALÓN DE JUEGOS PARA ADULTOS"},
        {"value": 241,"label": "CICLO RUTA"},
        {"value": 242,"label": "PISCINA (EN REMODELACIÓN)"},
        {"value": 243,"label": "CANCHAS DEPORTIVAS"},
        {"value": 244,"label": "PISCINA CON TOBOGAN"},
        {"value": 245,"label": "SALÓN DE TAREAS"},
        {"value": 246,"label": "CAPILLA"},
        {"value": 247,"label": "EN CENTRO COMERCIAL"},
        {"value": 248,"label": "BAÑOS COMUNALES"},
        {"value": 249,"label": "SALA DE MASAJES"},
        {"value": 250,"label": "CANCHAS POLIDEPORTIVAS"},
        {"value": 251,"label": "PARQUEADERO COMUNAL"},
        {"value": 252,"label": "PORTERÍA 24 HORAS"},
        {"value": 253,"label": "ÁREA DE TERRAZAS"},
        {"value": 254,"label": "SENDEROS ECOLÓGICOS"},
        {"value": 255,"label": "ZONA PARA BICICLETAS"},
        {"value": 256,"label": "ASCENSORES COMUNALES"},
        {"value": 257,"label": "MONTACOCHES"},
        {"value": 258,"label": "TIENDA"},
        {"value": 259,"label": "HIDROPISCINA"},
        {"value": 260,"label": "CAFETERÍA EN EL PRIMER PISO"},
        {"value": 261,"label": "TERRAZA BBQ"},
        {"value": 262,"label": "JUEGOS DE NIÑOS EN ZONA SOCIAL"},
        {"value": 263,"label": "ALARMA CONTRA INCENDIOS"},
        {"value": 264,"label": "VIGILANCIA"},
        {"value": 265,"label": "VIDEOCITÓFONO"},
        {"value": 266,"label": "1 CLOSET"},
        {"value": 267,"label": "2 CLOSETS"},
        {"value": 268,"label": "3 CLOSETS"},
        {"value": 269,"label": "4 CLOSETS"},
        {"value": 270,"label": "5 CLOSETS"},
        {"value": 271,"label": "6 CLOSETS"},
        {"value": 272,"label": "7 CLOSETS"},
        {"value": 273,"label": "8 CLOSETS"},
        {"value": 274,"label": "9 CLOSETS"},
        {"value": 275,"label": "10 CLOSETS"},
        {"value": 276,"label": "1 COMEDOR"},
        {"value": 277,"label": "2 COMEDORES"},
        {"value": 278,"label": "3 COMEDORES"},
        {"value": 279,"label": "4 COMEDORES"},
        {"value": 280,"label": "1 SALA"},
        {"value": 281,"label": "2 SALAS"},
        {"value": 282,"label": "3 SALAS"},
        {"value": 283,"label": "4 SALAS"},
        {"value": 284,"label": "MINI CANCHAS"},
        {"value": 285,"label": "ALC DE SERV CON BAÑO"},
        {"value": 286,"label": "DUPLEX"},
        {"value": 287,"label": "ANTEJARDÍN"},
        {"value": 288,"label": "2 GARAJES/PARQUEADERO(S)"},
        {"value": 289,"label": "COMEDOR"},
        {"value": 290,"label": "SALA"},
        {"value": 291,"label": "IGLESIAS CERCANAS"},
        {"value": 292,"label": "BANCOS CERCANOS"},
        {"value": 293,"label": "NOTARÍAS CERCANAS"},
        {"value": 294,"label": "ACCESO PARA CAMIONES"},
        {"value": 295,"label": "ACCESO PARA TRACTOMULAS"},
        {"value": 296,"label": "NACIMIENTOS DE AGUA"},
        {"value": 297,"label": "ESQUINERO"},
        {"value": 298,"label": "ÁREA RURAL"},
        {"value": 299,"label": "COCINA DE LEÑA"},
        {"value": 300,"label": "ALTURA LIBRE"},
        {"value": 301,"label": "ALTURA RESTRINGIDA"},
        {"value": 302,"label": "TANQUES DE RIEGO"},
        {"value": 303,"label": "JAULA DE GOLF"},
        {"value": 304,"label": "LOCALES COMERCIALES"},
        {"value": 305,"label": "CONTROL TÉRMICO"},
        {"value": 306,"label": "SERVICIO DE INTERNET"},
        {"value": 307,"label": "SALÓN DE VIDEOCONFERENCIAS"},
        {"value": 308,"label": "CORRALES"},
        {"value": 309,"label": "CONTROL ACÚSTICO"},
        {"value": 310,"label": "COCHERA"},
        {"value": 311,"label": "CALDERAS"},
        {"value": 312,"label": "ZONA DE HAMACAS"},
        {"value": 313,"label": "VENTILACIÓN NATURAL"},
        {"value": 314,"label": "SOPORTE DE GRUAS"},
        {"value": 315,"label": "MEZZANINE"},
        {"value": 316,"label": "LOTE VACIO"},
        {"value": 317,"label": "LOTE EN CONSTRUCCIÓN"},
        {"value": 318,"label": "FUERA DE CENTRO COMERCIAL"},
        {"value": 319,"label": "ESCALERAS ELÉCTRICAS"},
        {"value": 320,"label": "CASA DE TRABAJADORES"},
        {"value": 321,"label": "FINCA CAFETERA"},
        {"value": 322,"label": "FINCA GANADERA"},
        {"value": 323,"label": "FINCA AVÍCOLA"},
        {"value": 324,"label": "FINCA AGROGANADERA"},
        {"value": 325,"label": "CON VIVIENDA"},
        {"value": 326,"label": "COCINETA"},
        {"value": 327,"label": "CON CASA CLUB"},
        {"value": 328,"label": "CON CASA PREFABRICADA"},
        {"value": 329,"label": "EN CASA"},
        {"value": 330,"label": "CON ADMINISTRADOR"},
        {"value": 331,"label": "ROCIADORES DE AGUA"},
        {"value": 332,"label": "SALA DE JUNTAS" }
    ]

    prefijos_telefono = [
        {
            "nombre": "Afganistán (+93)",
            "name": "Afghanistan",
            "nom": "Afghanistan",
            "iso2": "AF",
            "iso3": "AFG",
            "phone_code": "+93",
            "url": "https://flagcdn.com/w40/af.png",
        },
        {
            "nombre": "Albania (+355)",
            "name": "Albania",
            "nom": "Albanie",
            "iso2": "AL",
            "iso3": "ALB",
            "phone_code": "+355",
            "url": "https://flagcdn.com/w40/al.png",
        },
        {
            "nombre": "Alemania (+49)",
            "name": "Germany",
            "nom": "Allemagne",
            "iso2": "DE",
            "iso3": "DEU",
            "phone_code": "+49",
            "url": "https://flagcdn.com/w40/de.png",
        },
        {
            "nombre": "Andorra (+376)",
            "name": "Andorra",
            "nom": "Andorra",
            "iso2": "AD",
            "iso3": "AND",
            "phone_code": "+376",
            "url": "https://flagcdn.com/w40/ad.png",
        },
        {
            "nombre": "Angola (+244)",
            "name": "Angola",
            "nom": "Angola",
            "iso2": "AO",
            "iso3": "AGO",
            "phone_code": "+244",
            "url": "https://flagcdn.com/w40/ao.png",
        },
        {
            "nombre": "Anguila (+1 264)",
            "name": "Anguilla",
            "nom": "Anguilla",
            "iso2": "AI",
            "iso3": "AIA",
            "phone_code": "+1 264",
            "url": "https://flagcdn.com/w40/ai.png",
        },
        {
            "nombre": "Antártida (+672)",
            "name": "Antarctica",
            "nom": "L Antarctique",
            "iso2": "AQ",
            "iso3": "ATA",
            "phone_code": "+672",
            "url": "https://flagcdn.com/w40/aq.png",
        },
        {
            "nombre": "Antigua y Barbuda (+1 268)",
            "name": "Antigua and Barbuda",
            "nom": "Antigua et Barbuda",
            "iso2": "AG",
            "iso3": "ATG",
            "phone_code": "+1 268",
            "url": "https://flagcdn.com/w40/ag.png",
        },
        {
            "nombre": "Arabia Saudita (+966)",
            "name": "Saudi Arabia",
            "nom": "Arabie Saoudite",
            "iso2": "SA",
            "iso3": "SAU",
            "phone_code": "+966",
            "url": "https://flagcdn.com/w40/sa.png",
        },
        {
            "nombre": "Argelia (+213)",
            "name": "Algeria",
            "nom": "Algérie",
            "iso2": "DZ",
            "iso3": "DZA",
            "phone_code": "+213",
            "url": "https://flagcdn.com/w40/dz.png",
        },
        {
            "nombre": "Argentina (+54)",
            "name": "Argentina",
            "nom": "Argentine",
            "iso2": "AR",
            "iso3": "ARG",
            "phone_code": "+54",
            "url": "https://flagcdn.com/w40/ar.png",
        },
        {
            "nombre": "Armenia (+374)",
            "name": "Armenia",
            "nom": "L Arménie",
            "iso2": "AM",
            "iso3": "ARM",
            "phone_code": "+374",
            "url": "https://flagcdn.com/w40/am.png",
        },
        {
            "nombre": "Aruba (+297)",
            "name": "Aruba",
            "nom": "Aruba",
            "iso2": "AW",
            "iso3": "ABW",
            "phone_code": "+297",
            "url": "https://flagcdn.com/w40/aw.png",
        },
        {
            "nombre": "Australia (+61)",
            "name": "Australia",
            "nom": "Australie",
            "iso2": "AU",
            "iso3": "AUS",
            "phone_code": "+61",
            "url": "https://flagcdn.com/w40/au.png",
        },
        {
            "nombre": "Austria (+43)",
            "name": "Austria",
            "nom": "Autriche",
            "iso2": "AT",
            "iso3": "AUT",
            "phone_code": "+43",
            "url": "https://flagcdn.com/w40/at.png",
        },
        {
            "nombre": "Azerbaiyán (+994)",
            "name": "Azerbaijan",
            "nom": "L Azerbaïdjan",
            "iso2": "AZ",
            "iso3": "AZE",
            "phone_code": "+994",
            "url": "https://flagcdn.com/w40/az.png",
        },
        {
            "nombre": "Bélgica (+32)",
            "name": "Belgium",
            "nom": "Belgique",
            "iso2": "BE",
            "iso3": "BEL",
            "phone_code": "+32",
            "url": "https://flagcdn.com/w40/be.png",
        },
        {
            "nombre": "Bahamas (+1 242)",
            "name": "Bahamas",
            "nom": "Bahamas",
            "iso2": "BS",
            "iso3": "BHS",
            "phone_code": "+1 242",
            "url": "https://flagcdn.com/w40/bs.png",
        },
        {
            "nombre": "Bahrein (+973)",
            "name": "Bahrain",
            "nom": "Bahreïn",
            "iso2": "BH",
            "iso3": "BHR",
            "phone_code": "+973",
            "url": "https://flagcdn.com/w40/bh.png",
        },
        {
            "nombre": "Bangladesh (+880)",
            "name": "Bangladesh",
            "nom": "Bangladesh",
            "iso2": "BD",
            "iso3": "BGD",
            "phone_code": "+880",
            "url": "https://flagcdn.com/w40/bd.png",
        },
        {
            "nombre": "Barbados (+1 246)",
            "name": "Barbados",
            "nom": "Barbade",
            "iso2": "BB",
            "iso3": "BRB",
            "phone_code": "+1 246",
            "url": "https://flagcdn.com/w40/bb.png",
        },
        {
            "nombre": "Belice (+501)",
            "name": "Belize",
            "nom": "Belize",
            "iso2": "BZ",
            "iso3": "BLZ",
            "phone_code": "+501",
            "url": "https://flagcdn.com/w40/bz.png",
        },
        {
            "nombre": "Benín (+229)",
            "name": "Benin",
            "nom": "Bénin",
            "iso2": "BJ",
            "iso3": "BEN",
            "phone_code": "+229",
            "url": "https://flagcdn.com/w40/bj.png",
        },
        {
            "nombre": "Bhután (+975)",
            "name": "Bhutan",
            "nom": "Le Bhoutan",
            "iso2": "BT",
            "iso3": "BTN",
            "phone_code": "+975",
            "url": "https://flagcdn.com/w40/bt.png",
        },
        {
            "nombre": "Bielorrusia (+375)",
            "name": "Belarus",
            "nom": "Biélorussie",
            "iso2": "BY",
            "iso3": "BLR",
            "phone_code": "+375",
            "url": "https://flagcdn.com/w40/by.png",
        },
        {
            "nombre": "Birmania (+95)",
            "name": "Myanmar",
            "nom": "Myanmar",
            "iso2": "MM",
            "iso3": "MMR",
            "phone_code": "+95",
            "url": "https://flagcdn.com/w40/mm.png",
        },
        {
            "nombre": "Bolivia (+591)",
            "name": "Bolivia",
            "nom": "Bolivie",
            "iso2": "BO",
            "iso3": "BOL",
            "phone_code": "+591",
            "url": "https://flagcdn.com/w40/bo.png",
        },
        {
            "nombre": "Bosnia y Herzegovina (+387)",
            "name": "Bosnia and Herzegovina",
            "nom": "Bosnie Herzégovine",
            "iso2": "BA",
            "iso3": "BIH",
            "phone_code": "+387",
            "url": "https://flagcdn.com/w40/ba.png",
        },
        {
            "nombre": "Botsuana (+267)",
            "name": "Botswana",
            "nom": "Botswana",
            "iso2": "BW",
            "iso3": "BWA",
            "phone_code": "+267",
            "url": "https://flagcdn.com/w40/bw.png",
        },
        {
            "nombre": "Brasil (+55)",
            "name": "Brazil",
            "nom": "Brésil",
            "iso2": "BR",
            "iso3": "BRA",
            "phone_code": "+55",
            "url": "https://flagcdn.com/w40/br.png",
        },
        {
            "nombre": "Brunéi (+673)",
            "name": "Brunei",
            "nom": "Brunei",
            "iso2": "BN",
            "iso3": "BRN",
            "phone_code": "+673",
            "url": "https://flagcdn.com/w40/bn.png",
        },
        {
            "nombre": "Bulgaria (+359)",
            "name": "Bulgaria",
            "nom": "Bulgarie",
            "iso2": "BG",
            "iso3": "BGR",
            "phone_code": "+359",
            "url": "https://flagcdn.com/w40/bg.png",
        },
        {
            "nombre": "Burkina Faso (+226)",
            "name": "Burkina Faso",
            "nom": "Burkina Faso",
            "iso2": "BF",
            "iso3": "BFA",
            "phone_code": "+226",
            "url": "https://flagcdn.com/w40/bf.png",
        },
        {
            "nombre": "Burundi (+257)",
            "name": "Burundi",
            "nom": "Burundi",
            "iso2": "BI",
            "iso3": "BDI",
            "phone_code": "+257",
            "url": "https://flagcdn.com/w40/bi.png",
        },
        {
            "nombre": "Cabo Verde (+238)",
            "name": "Cape Verde",
            "nom": "Cap Vert",
            "iso2": "CV",
            "iso3": "CPV",
            "phone_code": "+238",
            "url": "https://flagcdn.com/w40/cv.png",
        },
        {
            "nombre": "Camboya (+855)",
            "name": "Cambodia",
            "nom": "Cambodge",
            "iso2": "KH",
            "iso3": "KHM",
            "phone_code": "+855",
            "url": "https://flagcdn.com/w40/kh.png",
        },
        {
            "nombre": "Camerún (+237)",
            "name": "Cameroon",
            "nom": "Cameroun",
            "iso2": "CM",
            "iso3": "CMR",
            "phone_code": "+237",
            "url": "https://flagcdn.com/w40/cm.png",
        },
        {
            "nombre": "Canadá (+1)",
            "name": "Canada",
            "nom": "Canada",
            "iso2": "CA",
            "iso3": "CAN",
            "phone_code": "+1",
            "url": "https://flagcdn.com/w40/ca.png",
        },
        {
            "nombre": "Chad (+235)",
            "name": "Chad",
            "nom": "Tchad",
            "iso2": "TD",
            "iso3": "TCD",
            "phone_code": "+235",
            "url": "https://flagcdn.com/w40/td.png",
        },
        {
            "nombre": "Chile (+56)",
            "name": "Chile",
            "nom": "Chili",
            "iso2": "CL",
            "iso3": "CHL",
            "phone_code": "+56",
            "url": "https://flagcdn.com/w40/cl.png",
        },
        {
            "nombre": "China (+86)",
            "name": "China",
            "nom": "Chine",
            "iso2": "CN",
            "iso3": "CHN",
            "phone_code": "+86",
            "url": "https://flagcdn.com/w40/cn.png",
        },
        {
            "nombre": "Chipre (+357)",
            "name": "Cyprus",
            "nom": "Chypre",
            "iso2": "CY",
            "iso3": "CYP",
            "phone_code": "+357",
            "url": "https://flagcdn.com/w40/cy.png",
        },
        {
            "nombre": "Ciudad del Vaticano (+39)",
            "name": "Vatican City State",
            "nom": "Cité du Vatican",
            "iso2": "VA",
            "iso3": "VAT",
            "phone_code": "+39",
            "url": "https://flagcdn.com/w40/va.png",
        },
        {
            "nombre": "Colombia (+57)",
            "name": "Colombia",
            "nom": "Colombie",
            "iso2": "CO",
            "iso3": "COL",
            "phone_code": "+57",
            "url": "https://flagcdn.com/w40/co.png",
        },
        {
            "nombre": "Comoras (+269)",
            "name": "Comoros",
            "nom": "Comores",
            "iso2": "KM",
            "iso3": "COM",
            "phone_code": "+269",
            "url": "https://flagcdn.com/w40/km.png",
        },
        {
            "nombre": "República del Congo (+242)",
            "name": "Republic of the Congo",
            "nom": "République du Congo",
            "iso2": "CG",
            "iso3": "COG",
            "phone_code": "+242",
            "url": "https://flagcdn.com/w40/cg.png",
        },
        {
            "nombre": "República Democrática del Congo (+243)",
            "name": "Democratic Republic of the Congo",
            "nom": "République démocratique du Congo",
            "iso2": "CD",
            "iso3": "COD",
            "phone_code": "+243",
            "url": "https://flagcdn.com/w40/cd.png",
        },
        {
            "nombre": "Corea del Norte (+850)",
            "name": "North Korea",
            "nom": "Corée du Nord",
            "iso2": "KP",
            "iso3": "PRK",
            "phone_code": "+850",
            "url": "https://flagcdn.com/w40/kp.png",
        },
        {
            "nombre": "Corea del Sur (+82)",
            "name": "South Korea",
            "nom": "Corée du Sud",
            "iso2": "KR",
            "iso3": "KOR",
            "phone_code": "+82",
            "url": "https://flagcdn.com/w40/kr.png",
        },
        {
            "nombre": "Costa de Marfil (+225)",
            "name": "Ivory Coast",
            "nom": "Côte d Ivoire",
            "iso2": "CI",
            "iso3": "CIV",
            "phone_code": "+225",
            "url": "https://flagcdn.com/w40/ci.png",
        },
        {
            "nombre": "Costa Rica (+506)",
            "name": "Costa Rica",
            "nom": "Costa Rica",
            "iso2": "CR",
            "iso3": "CRI",
            "phone_code": "+506",
            "url": "https://flagcdn.com/w40/cr.png",
        },
        {
            "nombre": "Croacia (+385)",
            "name": "Croatia",
            "nom": "Croatie",
            "iso2": "HR",
            "iso3": "HRV",
            "phone_code": "+385",
            "url": "https://flagcdn.com/w40/hr.png",
        },
        {
            "nombre": "Cuba (+53)",
            "name": "Cuba",
            "nom": "Cuba",
            "iso2": "CU",
            "iso3": "CUB",
            "phone_code": "+53",
            "url": "https://flagcdn.com/w40/cu.png",
        },
        {
            "nombre": "Curazao (+5999)",
            "name": "Curaçao",
            "nom": "Curaçao",
            "iso2": "CW",
            "iso3": "CWU",
            "phone_code": "+5999",
            "url": "https://flagcdn.com/w40/cw.png",
        },
        {
            "nombre": "Dinamarca (+45)",
            "name": "Denmark",
            "nom": "Danemark",
            "iso2": "DK",
            "iso3": "DNK",
            "phone_code": "+45",
            "url": "https://flagcdn.com/w40/dk.png",
        },
        {
            "nombre": "Dominica (+1 767)",
            "name": "Dominica",
            "nom": "Dominique",
            "iso2": "DM",
            "iso3": "DMA",
            "phone_code": "+1 767",
            "url": "https://flagcdn.com/w40/dm.png",
        },
        {
            "nombre": "Ecuador (+593)",
            "name": "Ecuador",
            "nom": "Equateur",
            "iso2": "EC",
            "iso3": "ECU",
            "phone_code": "+593",
            "url": "https://flagcdn.com/w40/ec.png",
        },
        {
            "nombre": "Egipto (+20)",
            "name": "Egypt",
            "nom": "Egypte",
            "iso2": "EG",
            "iso3": "EGY",
            "phone_code": "+20",
            "url": "https://flagcdn.com/w40/eg.png",
        },
        {
            "nombre": "El Salvador (+503)",
            "name": "El Salvador",
            "nom": "El Salvador",
            "iso2": "SV",
            "iso3": "SLV",
            "phone_code": "+503",
            "url": "https://flagcdn.com/w40/sv.png",
        },
        {
            "nombre": "Emiratos Árabes Unidos (+971)",
            "name": "United Arab Emirates",
            "nom": "Emirats Arabes Unis",
            "iso2": "AE",
            "iso3": "ARE",
            "phone_code": "+971",
            "url": "https://flagcdn.com/w40/ae.png",
        },
        {
            "nombre": "Eritrea (+291)",
            "name": "Eritrea",
            "nom": "Erythrée",
            "iso2": "ER",
            "iso3": "ERI",
            "phone_code": "+291",
            "url": "https://flagcdn.com/w40/er.png",
        },
        {
            "nombre": "Eslovaquia (+421)",
            "name": "Slovakia",
            "nom": "Slovaquie",
            "iso2": "SK",
            "iso3": "SVK",
            "phone_code": "+421",
            "url": "https://flagcdn.com/w40/sk.png",
        },
        {
            "nombre": "Eslovenia (+386)",
            "name": "Slovenia",
            "nom": "Slovénie",
            "iso2": "SI",
            "iso3": "SVN",
            "phone_code": "+386",
            "url": "https://flagcdn.com/w40/si.png",
        },
        {
            "nombre": "España (+34)",
            "name": "Spain",
            "nom": "Espagne",
            "iso2": "ES",
            "iso3": "ESP",
            "phone_code": "+34",
            "url": "https://flagcdn.com/w40/es.png",
        },
        {
            "nombre": "Estados Unidos de América (+1)",
            "name": "United States of America",
            "nom": "États Unis d Amérique",
            "iso2": "US",
            "iso3": "USA",
            "phone_code": "+1",
            "url": "https://flagcdn.com/w40/us.png",
        },
        {
            "nombre": "Estonia (+372)",
            "name": "Estonia",
            "nom": "L Estonie",
            "iso2": "EE",
            "iso3": "EST",
            "phone_code": "+372",
            "url": "https://flagcdn.com/w40/ee.png",
        },
        {
            "nombre": "Etiopía (+251)",
            "name": "Ethiopia",
            "nom": "Ethiopie",
            "iso2": "ET",
            "iso3": "ETH",
            "phone_code": "+251",
            "url": "https://flagcdn.com/w40/et.png",
        },
        {
            "nombre": "Filipinas (+63)",
            "name": "Philippines",
            "nom": "Philippines",
            "iso2": "PH",
            "iso3": "PHL",
            "phone_code": "+63",
            "url": "https://flagcdn.com/w40/ph.png",
        },
        {
            "nombre": "Finlandia (+358)",
            "name": "Finland",
            "nom": "Finlande",
            "iso2": "FI",
            "iso3": "FIN",
            "phone_code": "+358",
            "url": "https://flagcdn.com/w40/fi.png",
        },
        {
            "nombre": "Fiyi (+679)",
            "name": "Fiji",
            "nom": "Fidji",
            "iso2": "FJ",
            "iso3": "FJI",
            "phone_code": "+679",
            "url": "https://flagcdn.com/w40/fj.png",
        },
        {
            "nombre": "Francia (+33)",
            "name": "France",
            "nom": "France",
            "iso2": "FR",
            "iso3": "FRA",
            "phone_code": "+33",
            "url": "https://flagcdn.com/w40/fr.png",
        },
        {
            "nombre": "Gabón (+241)",
            "name": "Gabon",
            "nom": "Gabon",
            "iso2": "GA",
            "iso3": "GAB",
            "phone_code": "+241",
            "url": "https://flagcdn.com/w40/ga.png",
        },
        {
            "nombre": "Gambia (+220)",
            "name": "Gambia",
            "nom": "Gambie",
            "iso2": "GM",
            "iso3": "GMB",
            "phone_code": "+220",
            "url": "https://flagcdn.com/w40/gm.png",
        },
        {
            "nombre": "Georgia (+995)",
            "name": "Georgia",
            "nom": "Géorgie",
            "iso2": "GE",
            "iso3": "GEO",
            "phone_code": "+995",
            "url": "https://flagcdn.com/w40/ge.png",
        },
        {
            "nombre": "Ghana (+233)",
            "name": "Ghana",
            "nom": "Ghana",
            "iso2": "GH",
            "iso3": "GHA",
            "phone_code": "+233",
            "url": "https://flagcdn.com/w40/gh.png",
        },
        {
            "nombre": "Gibraltar (+350)",
            "name": "Gibraltar",
            "nom": "Gibraltar",
            "iso2": "GI",
            "iso3": "GIB",
            "phone_code": "+350",
            "url": "https://flagcdn.com/w40/gi.png",
        },
        {
            "nombre": "Granada (+1 473)",
            "name": "Grenada",
            "nom": "Grenade",
            "iso2": "GD",
            "iso3": "GRD",
            "phone_code": "+1 473",
            "url": "https://flagcdn.com/w40/gd.png",
        },
        {
            "nombre": "Grecia (+30)",
            "name": "Greece",
            "nom": "Grèce",
            "iso2": "GR",
            "iso3": "GRC",
            "phone_code": "+30",
            "url": "https://flagcdn.com/w40/gr.png",
        },
        {
            "nombre": "Groenlandia (+299)",
            "name": "Greenland",
            "nom": "Groenland",
            "iso2": "GL",
            "iso3": "GRL",
            "phone_code": "+299",
            "url": "https://flagcdn.com/w40/gl.png",
        },
        {
            "nombre": "Guadalupe (+590)",
            "name": "Guadeloupe",
            "nom": "Guadeloupe",
            "iso2": "GP",
            "iso3": "GLP",
            "phone_code": "+590",
            "url": "https://flagcdn.com/w40/gp.png",
        },
        {
            "nombre": "Guam (+1 671)",
            "name": "Guam",
            "nom": "Guam",
            "iso2": "GU",
            "iso3": "GUM",
            "phone_code": "+1 671",
            "url": "https://flagcdn.com/w40/gu.png",
        },
        {
            "nombre": "Guatemala (+502)",
            "name": "Guatemala",
            "nom": "Guatemala",
            "iso2": "GT",
            "iso3": "GTM",
            "phone_code": "+502",
            "url": "https://flagcdn.com/w40/gt.png",
        },
        {
            "nombre": "Guayana Francesa (+594)",
            "name": "French Guiana",
            "nom": "Guyane française",
            "iso2": "GF",
            "iso3": "GUF",
            "phone_code": "+594",
            "url": "https://flagcdn.com/w40/gf.png",
        },
        {
            "nombre": "Guernsey (+44)",
            "name": "Guernsey",
            "nom": "Guernesey",
            "iso2": "GG",
            "iso3": "GGY",
            "phone_code": "+44",
            "url": "https://flagcdn.com/w40/gg.png",
        },
        {
            "nombre": "Guinea (+224)",
            "name": "Guinea",
            "nom": "Guinée",
            "iso2": "GN",
            "iso3": "GIN",
            "phone_code": "+224",
            "url": "https://flagcdn.com/w40/gn.png",
        },
        {
            "nombre": "Guinea Ecuatorial (+240)",
            "name": "Equatorial Guinea",
            "nom": "Guinée Equatoriale",
            "iso2": "GQ",
            "iso3": "GNQ",
            "phone_code": "+240",
            "url": "https://flagcdn.com/w40/gq.png",
        },
        {
            "nombre": "Guinea Bissau (+245)",
            "name": "Guinea Bissau",
            "nom": "Guinée Bissau",
            "iso2": "GW",
            "iso3": "GNB",
            "phone_code": "+245",
            "url": "https://flagcdn.com/w40/gw.png",
        },
        {
            "nombre": "Guyana (+592)",
            "name": "Guyana",
            "nom": "Guyane",
            "iso2": "GY",
            "iso3": "GUY",
            "phone_code": "+592",
            "url": "https://flagcdn.com/w40/gy.png",
        },
        {
            "nombre": "Haití (+509)",
            "name": "Haiti",
            "nom": "Haïti",
            "iso2": "HT",
            "iso3": "HTI",
            "phone_code": "+509",
            "url": "https://flagcdn.com/w40/ht.png",
        },
        {
            "nombre": "Honduras (+504)",
            "name": "Honduras",
            "nom": "Honduras",
            "iso2": "HN",
            "iso3": "HND",
            "phone_code": "+504",
            "url": "https://flagcdn.com/w40/hn.png",
        },
        {
            "nombre": "Hong kong (+852)",
            "name": "Hong Kong",
            "nom": "Hong Kong",
            "iso2": "HK",
            "iso3": "HKG",
            "phone_code": "+852",
            "url": "https://flagcdn.com/w40/hk.png",
        },
        {
            "nombre": "Hungría (+36)",
            "name": "Hungary",
            "nom": "Hongrie",
            "iso2": "HU",
            "iso3": "HUN",
            "phone_code": "+36",
            "url": "https://flagcdn.com/w40/hu.png",
        },
        {
            "nombre": "India (+91)",
            "name": "India",
            "nom": "Inde",
            "iso2": "IN",
            "iso3": "IND",
            "phone_code": "+91",
            "url": "https://flagcdn.com/w40/in.png",
        },
        {
            "nombre": "Indonesia (+62)",
            "name": "Indonesia",
            "nom": "Indonésie",
            "iso2": "ID",
            "iso3": "IDN",
            "phone_code": "+62",
            "url": "https://flagcdn.com/w40/id.png",
        },
        {
            "nombre": "Irán (+98)",
            "name": "Iran",
            "nom": "Iran",
            "iso2": "IR",
            "iso3": "IRN",
            "phone_code": "+98",
            "url": "https://flagcdn.com/w40/ir.png",
        },
        {
            "nombre": "Irak (+964)",
            "name": "Iraq",
            "nom": "Irak",
            "iso2": "IQ",
            "iso3": "IRQ",
            "phone_code": "+964",
            "url": "https://flagcdn.com/w40/iq.png",
        },
        {
            "nombre": "Irlanda (+353)",
            "name": "Ireland",
            "nom": "Irlande",
            "iso2": "IE",
            "iso3": "IRL",
            "phone_code": "+353",
            "url": "https://flagcdn.com/w40/ie.png",
        },
        # {
        #     "nombre": "Isla Bouvet",
        #     "name": "Bouvet Island",
        #     "nom": "Bouvet Island",
        #     "iso2": "BV",
        #     "iso3": "BVT",
        #     "phone_code": "",
        #     "url": "https://flagcdn.com/w40/bv.png",
        # },
        {
            "nombre": "Isla de Man (+44)",
            "name": "Isle of Man",
            "nom": "Ile de Man",
            "iso2": "IM",
            "iso3": "IMN",
            "phone_code": "+44",
            "url": "https://flagcdn.com/w40/im.png",
        },
        {
            "nombre": "Isla de Navidad (+61)",
            "name": "Christmas Island",
            "nom": "Christmas Island",
            "iso2": "CX",
            "iso3": "CXR",
            "phone_code": "+61",
            "url": "https://flagcdn.com/w40/cx.png",
        },
        {
            "nombre": "Isla Norfolk (+672)",
            "name": "Norfolk Island",
            "nom": "Île de Norfolk",
            "iso2": "NF",
            "iso3": "NFK",
            "phone_code": "+672",
            "url": "https://flagcdn.com/w40/nf.png",
        },
        {
            "nombre": "Islandia (+354)",
            "name": "Iceland",
            "nom": "Islande",
            "iso2": "IS",
            "iso3": "ISL",
            "phone_code": "+354",
            "url": "https://flagcdn.com/w40/is.png",
        },
        {
            "nombre": "Islas Bermudas (+1 441)",
            "name": "Bermuda Islands",
            "nom": "Bermudes",
            "iso2": "BM",
            "iso3": "BMU",
            "phone_code": "+1 441",
            "url": "https://flagcdn.com/w40/bm.png",
        },
        {
            "nombre": "Islas Caimán (+1 345)",
            "name": "Cayman Islands",
            "nom": "Iles Caïmans",
            "iso2": "KY",
            "iso3": "CYM",
            "phone_code": "+1 345",
            "url": "https://flagcdn.com/w40/ky.png",
        },
        {
            "nombre": "Islas Cocos (Keeling (+61))",
            "name": "Cocos (Keeling) Islands",
            "nom": "Cocos (Keeling)",
            "iso2": "CC",
            "iso3": "CCK",
            "phone_code": "+61",
            "url": "https://flagcdn.com/w40/cc.png",
        },
        {
            "nombre": "Islas Cook (+682)",
            "name": "Cook Islands",
            "nom": "Iles Cook",
            "iso2": "CK",
            "iso3": "COK",
            "phone_code": "+682",
            "url": "https://flagcdn.com/w40/ck.png",
        },
        {
            "nombre": "Islas de Åland (+358)",
            "name": "Åland Islands",
            "nom": "Îles Åland",
            "iso2": "AX",
            "iso3": "ALA",
            "phone_code": "+358",
            "url": "https://flagcdn.com/w40/ax.png",
        },
        {
            "nombre": "Islas Feroe (+298)",
            "name": "Faroe Islands",
            "nom": "Iles Féro",
            "iso2": "FO",
            "iso3": "FRO",
            "phone_code": "+298",
            "url": "https://flagcdn.com/w40/fo.png",
        },
        {
            "nombre": "Islas Georgias del Sur y Sandwich del Sur (+500)",
            "name": "South Georgia and the South Sandwich Islands",
            "nom": "Géorgie du Sud et les Îles Sandwich du Sud",
            "iso2": "GS",
            "iso3": "SGS",
            "phone_code": "+500",
            "url": "https://flagcdn.com/w40/gs.png",
        },
        # {
        #     "nombre": "Islas Heard y McDonald",
        #     "name": "Heard Island and McDonald Islands",
        #     "nom": "Les îles Heard et McDonald",
        #     "iso2": "HM",
        #     "iso3": "HMD",
        #     "phone_code": "",
        #     "url": "https://flagcdn.com/w40/hm.png",
        # },
        {
            "nombre": "Islas Maldivas (+960)",
            "name": "Maldives",
            "nom": "Maldives",
            "iso2": "MV",
            "iso3": "MDV",
            "phone_code": "+960",
            "url": "https://flagcdn.com/w40/mv.png",
        },
        {
            "nombre": "Islas Malvinas (+500)",
            "name": "Falkland Islands (Malvinas)",
            "nom": "Iles Falkland (Malvinas)",
            "iso2": "FK",
            "iso3": "FLK",
            "phone_code": "+500",
            "url": "https://flagcdn.com/w40/fk.png",
        },
        {
            "nombre": "Islas Marianas del Norte (+1 670)",
            "name": "Northern Mariana Islands",
            "nom": "Iles Mariannes du Nord",
            "iso2": "MP",
            "iso3": "MNP",
            "phone_code": "+1 670",
            "url": "https://flagcdn.com/w40/mp.png",
        },
        {
            "nombre": "Islas Marshall (+692)",
            "name": "Marshall Islands",
            "nom": "Iles Marshall",
            "iso2": "MH",
            "iso3": "MHL",
            "phone_code": "+692",
            "url": "https://flagcdn.com/w40/mh.png",
        },
        {
            "nombre": "Islas Pitcairn (+870)",
            "name": "Pitcairn Islands",
            "nom": "Iles Pitcairn",
            "iso2": "PN",
            "iso3": "PCN",
            "phone_code": "+870",
            "url": "https://flagcdn.com/w40/pn.png",
        },
        {
            "nombre": "Islas Salomón (+677)",
            "name": "Solomon Islands",
            "nom": "Iles Salomon",
            "iso2": "SB",
            "iso3": "SLB",
            "phone_code": "+677",
            "url": "https://flagcdn.com/w40/sb.png",
        },
        {
            "nombre": "Islas Turcas y Caicos (+1 649)",
            "name": "Turks and Caicos Islands",
            "nom": "Iles Turques et Caïques",
            "iso2": "TC",
            "iso3": "TCA",
            "phone_code": "+1 649",
            "url": "https://flagcdn.com/w40/tc.png",
        },
        {
            "nombre": "Islas Ultramarinas Menores de Estados Unidos (+246)",
            "name": "United States Minor Outlying Islands",
            "nom": "États Unis Îles mineures éloignées",
            "iso2": "UM",
            "iso3": "UMI",
            "phone_code": "+246",
            "url": "https://flagcdn.com/w40/um.png",
        },
        {
            "nombre": "Islas Vírgenes Británicas (+1 284)",
            "name": "Virgin Islands",
            "nom": "Iles Vierges",
            "iso2": "VG",
            "iso3": "VGB",
            "phone_code": "+1 284",
            "url": "https://flagcdn.com/w40/vg.png",
        },
        {
            "nombre": "Islas Vírgenes de los Estados Unidos (+1 340)",
            "name": "United States Virgin Islands",
            "nom": "Îles Vierges américaines",
            "iso2": "VI",
            "iso3": "VIR",
            "phone_code": "+1 340",
            "url": "https://flagcdn.com/w40/vi.png",
        },
        {
            "nombre": "Israel (+972)",
            "name": "Israel",
            "nom": "Israël",
            "iso2": "IL",
            "iso3": "ISR",
            "phone_code": "+972",
            "url": "https://flagcdn.com/w40/il.png",
        },
        {
            "nombre": "Italia (+39)",
            "name": "Italy",
            "nom": "Italie",
            "iso2": "IT",
            "iso3": "ITA",
            "phone_code": "+39",
            "url": "https://flagcdn.com/w40/it.png",
        },
        {
            "nombre": "Jamaica (+1 876)",
            "name": "Jamaica",
            "nom": "Jamaïque",
            "iso2": "JM",
            "iso3": "JAM",
            "phone_code": "+1 876",
            "url": "https://flagcdn.com/w40/jm.png",
        },
        {
            "nombre": "Japón (+81)",
            "name": "Japan",
            "nom": "Japon",
            "iso2": "JP",
            "iso3": "JPN",
            "phone_code": "+81",
            "url": "https://flagcdn.com/w40/jp.png",
        },
        {
            "nombre": "Jersey (+44)",
            "name": "Jersey",
            "nom": "Maillot",
            "iso2": "JE",
            "iso3": "JEY",
            "phone_code": "+44",
            "url": "https://flagcdn.com/w40/je.png",
        },
        {
            "nombre": "Jordania (+962)",
            "name": "Jordan",
            "nom": "Jordan",
            "iso2": "JO",
            "iso3": "JOR",
            "phone_code": "+962",
            "url": "https://flagcdn.com/w40/jo.png",
        },
        {
            "nombre": "Kazajistán (+7)",
            "name": "Kazakhstan",
            "nom": "Le Kazakhstan",
            "iso2": "KZ",
            "iso3": "KAZ",
            "phone_code": "+7",
            "url": "https://flagcdn.com/w40/kz.png",
        },
        {
            "nombre": "Kenia (+254)",
            "name": "Kenya",
            "nom": "Kenya",
            "iso2": "KE",
            "iso3": "KEN",
            "phone_code": "+254",
            "url": "https://flagcdn.com/w40/ke.png",
        },
        {
            "nombre": "Kirguistán (+996)",
            "name": "Kyrgyzstan",
            "nom": "Kirghizstan",
            "iso2": "KG",
            "iso3": "KGZ",
            "phone_code": "+996",
            "url": "https://flagcdn.com/w40/kg.png",
        },
        {
            "nombre": "Kiribati (+686)",
            "name": "Kiribati",
            "nom": "Kiribati",
            "iso2": "KI",
            "iso3": "KIR",
            "phone_code": "+686",
            "url": "https://flagcdn.com/w40/ki.png",
        },
        {
            "nombre": "Kuwait (+965)",
            "name": "Kuwait",
            "nom": "Koweït",
            "iso2": "KW",
            "iso3": "KWT",
            "phone_code": "+965",
            "url": "https://flagcdn.com/w40/kw.png",
        },
        {
            "nombre": "Líbano (+961)",
            "name": "Lebanon",
            "nom": "Liban",
            "iso2": "LB",
            "iso3": "LBN",
            "phone_code": "+961",
            "url": "https://flagcdn.com/w40/lb.png",
        },
        {
            "nombre": "Laos (+856)",
            "name": "Laos",
            "nom": "Laos",
            "iso2": "LA",
            "iso3": "LAO",
            "phone_code": "+856",
            "url": "https://flagcdn.com/w40/la.png",
        },
        {
            "nombre": "Lesoto (+266)",
            "name": "Lesotho",
            "nom": "Lesotho",
            "iso2": "LS",
            "iso3": "LSO",
            "phone_code": "+266",
            "url": "https://flagcdn.com/w40/ls.png",
        },
        {
            "nombre": "Letonia (+371)",
            "name": "Latvia",
            "nom": "La Lettonie",
            "iso2": "LV",
            "iso3": "LVA",
            "phone_code": "+371",
            "url": "https://flagcdn.com/w40/lv.png",
        },
        {
            "nombre": "Liberia (+231)",
            "name": "Liberia",
            "nom": "Liberia",
            "iso2": "LR",
            "iso3": "LBR",
            "phone_code": "+231",
            "url": "https://flagcdn.com/w40/lr.png",
        },
        {
            "nombre": "Libia (+218)",
            "name": "Libya",
            "nom": "Libye",
            "iso2": "LY",
            "iso3": "LBY",
            "phone_code": "+218",
            "url": "https://flagcdn.com/w40/ly.png",
        },
        {
            "nombre": "Liechtenstein (+423)",
            "name": "Liechtenstein",
            "nom": "Liechtenstein",
            "iso2": "LI",
            "iso3": "LIE",
            "phone_code": "+423",
            "url": "https://flagcdn.com/w40/li.png",
        },
        {
            "nombre": "Lituania (+370)",
            "name": "Lithuania",
            "nom": "La Lituanie",
            "iso2": "LT",
            "iso3": "LTU",
            "phone_code": "+370",
            "url": "https://flagcdn.com/w40/lt.png",
        },
        {
            "nombre": "Luxemburgo (+352)",
            "name": "Luxembourg",
            "nom": "Luxembourg",
            "iso2": "LU",
            "iso3": "LUX",
            "phone_code": "+352",
            "url": "https://flagcdn.com/w40/lu.png",
        },
        {
            "nombre": "México (+52)",
            "name": "Mexico",
            "nom": "Mexique",
            "iso2": "MX",
            "iso3": "MEX",
            "phone_code": "+52",
            "url": "https://flagcdn.com/w40/mx.png",
        },
        {
            "nombre": "Mónaco (+377)",
            "name": "Monaco",
            "nom": "Monaco",
            "iso2": "MC",
            "iso3": "MCO",
            "phone_code": "+377",
            "url": "https://flagcdn.com/w40/mc.png",
        },
        {
            "nombre": "Macao (+853)",
            "name": "Macao",
            "nom": "Macao",
            "iso2": "MO",
            "iso3": "MAC",
            "phone_code": "+853",
            "url": "https://flagcdn.com/w40/mo.png",
        },
        {
            "nombre": "Macedônia (+389)",
            "name": "Macedonia",
            "nom": "Macédoine",
            "iso2": "MK",
            "iso3": "MKD",
            "phone_code": "+389",
            "url": "https://flagcdn.com/w40/mk.png",
        },
        {
            "nombre": "Madagascar (+261)",
            "name": "Madagascar",
            "nom": "Madagascar",
            "iso2": "MG",
            "iso3": "MDG",
            "phone_code": "+261",
            "url": "https://flagcdn.com/w40/mg.png",
        },
        {
            "nombre": "Malasia (+60)",
            "name": "Malaysia",
            "nom": "Malaisie",
            "iso2": "MY",
            "iso3": "MYS",
            "phone_code": "+60",
            "url": "https://flagcdn.com/w40/my.png",
        },
        {
            "nombre": "Malawi (+265)",
            "name": "Malawi",
            "nom": "Malawi",
            "iso2": "MW",
            "iso3": "MWI",
            "phone_code": "+265",
            "url": "https://flagcdn.com/w40/mw.png",
        },
        {
            "nombre": "Mali (+223)",
            "name": "Mali",
            "nom": "Mali",
            "iso2": "ML",
            "iso3": "MLI",
            "phone_code": "+223",
            "url": "https://flagcdn.com/w40/ml.png",
        },
        {
            "nombre": "Malta (+356)",
            "name": "Malta",
            "nom": "Malte",
            "iso2": "MT",
            "iso3": "MLT",
            "phone_code": "+356",
            "url": "https://flagcdn.com/w40/mt.png",
        },
        {
            "nombre": "Marruecos (+212)",
            "name": "Morocco",
            "nom": "Maroc",
            "iso2": "MA",
            "iso3": "MAR",
            "phone_code": "+212",
            "url": "https://flagcdn.com/w40/ma.png",
        },
        {
            "nombre": "Martinica (+596)",
            "name": "Martinique",
            "nom": "Martinique",
            "iso2": "MQ",
            "iso3": "MTQ",
            "phone_code": "+596",
            "url": "https://flagcdn.com/w40/mq.png",
        },
        {
            "nombre": "Mauricio (+230)",
            "name": "Mauritius",
            "nom": "Iles Maurice",
            "iso2": "MU",
            "iso3": "MUS",
            "phone_code": "+230",
            "url": "https://flagcdn.com/w40/mu.png",
        },
        {
            "nombre": "Mauritania (+222)",
            "name": "Mauritania",
            "nom": "Mauritanie",
            "iso2": "MR",
            "iso3": "MRT",
            "phone_code": "+222",
            "url": "https://flagcdn.com/w40/mr.png",
        },
        {
            "nombre": "Mayotte (+262)",
            "name": "Mayotte",
            "nom": "Mayotte",
            "iso2": "YT",
            "iso3": "MYT",
            "phone_code": "+262",
            "url": "https://flagcdn.com/w40/yt.png",
        },
        {
            "nombre": "Micronesia (+691)",
            "name": "Estados Federados de",
            "nom": "Federados Estados de",
            "iso2": "FM",
            "iso3": "FSM",
            "phone_code": "+691",
            "url": "https://flagcdn.com/w40/fm.png",
        },
        {
            "nombre": "Moldavia (+373)",
            "name": "Moldova",
            "nom": "Moldavie",
            "iso2": "MD",
            "iso3": "MDA",
            "phone_code": "+373",
            "url": "https://flagcdn.com/w40/md.png",
        },
        {
            "nombre": "Mongolia (+976)",
            "name": "Mongolia",
            "nom": "Mongolie",
            "iso2": "MN",
            "iso3": "MNG",
            "phone_code": "+976",
            "url": "https://flagcdn.com/w40/mn.png",
        },
        {
            "nombre": "Montenegro (+382)",
            "name": "Montenegro",
            "nom": "Monténégro",
            "iso2": "ME",
            "iso3": "MNE",
            "phone_code": "+382",
            "url": "https://flagcdn.com/w40/me.png",
        },
        {
            "nombre": "Montserrat (+1 664)",
            "name": "Montserrat",
            "nom": "Montserrat",
            "iso2": "MS",
            "iso3": "MSR",
            "phone_code": "+1 664",
            "url": "https://flagcdn.com/w40/ms.png",
        },
        {
            "nombre": "Mozambique (+258)",
            "name": "Mozambique",
            "nom": "Mozambique",
            "iso2": "MZ",
            "iso3": "MOZ",
            "phone_code": "+258",
            "url": "https://flagcdn.com/w40/mz.png",
        },
        {
            "nombre": "Namibia (+264)",
            "name": "Namibia",
            "nom": "Namibie",
            "iso2": "NA",
            "iso3": "NAM",
            "phone_code": "+264",
            "url": "https://flagcdn.com/w40/na.png",
        },
        {
            "nombre": "Nauru (+674)",
            "name": "Nauru",
            "nom": "Nauru",
            "iso2": "NR",
            "iso3": "NRU",
            "phone_code": "+674",
            "url": "https://flagcdn.com/w40/nr.png",
        },
        {
            "nombre": "Nepal (+977)",
            "name": "Nepal",
            "nom": "Népal",
            "iso2": "NP",
            "iso3": "NPL",
            "phone_code": "+977",
            "url": "https://flagcdn.com/w40/np.png",
        },
        {
            "nombre": "Nicaragua (+505)",
            "name": "Nicaragua",
            "nom": "Nicaragua",
            "iso2": "NI",
            "iso3": "NIC",
            "phone_code": "+505",
            "url": "https://flagcdn.com/w40/ni.png",
        },
        {
            "nombre": "Niger (+227)",
            "name": "Niger",
            "nom": "Niger",
            "iso2": "NE",
            "iso3": "NER",
            "phone_code": "+227",
            "url": "https://flagcdn.com/w40/ne.png",
        },
        {
            "nombre": "Nigeria (+234)",
            "name": "Nigeria",
            "nom": "Nigeria",
            "iso2": "NG",
            "iso3": "NGA",
            "phone_code": "+234",
            "url": "https://flagcdn.com/w40/ng.png",
        },
        {
            "nombre": "Niue (+683)",
            "name": "Niue",
            "nom": "Niou",
            "iso2": "NU",
            "iso3": "NIU",
            "phone_code": "+683",
            "url": "https://flagcdn.com/w40/nu.png",
        },
        {
            "nombre": "Noruega (+47)",
            "name": "Norway",
            "nom": "Norvège",
            "iso2": "NO",
            "iso3": "NOR",
            "phone_code": "+47",
            "url": "https://flagcdn.com/w40/no.png",
        },
        {
            "nombre": "Nueva Caledonia (+687)",
            "name": "New Caledonia",
            "nom": "Nouvelle Calédonie",
            "iso2": "NC",
            "iso3": "NCL",
            "phone_code": "+687",
            "url": "https://flagcdn.com/w40/nc.png",
        },
        {
            "nombre": "Nueva Zelanda (+64)",
            "name": "New Zealand",
            "nom": "Nouvelle Zélande",
            "iso2": "NZ",
            "iso3": "NZL",
            "phone_code": "+64",
            "url": "https://flagcdn.com/w40/nz.png",
        },
        {
            "nombre": "Omán (+968)",
            "name": "Oman",
            "nom": "Oman",
            "iso2": "OM",
            "iso3": "OMN",
            "phone_code": "+968",
            "url": "https://flagcdn.com/w40/om.png",
        },
        {
            "nombre": "Países Bajos (+31)",
            "name": "Netherlands",
            "nom": "Pays Bas",
            "iso2": "NL",
            "iso3": "NLD",
            "phone_code": "+31",
            "url": "https://flagcdn.com/w40/nl.png",
        },
        {
            "nombre": "Pakistán (+92)",
            "name": "Pakistan",
            "nom": "Pakistan",
            "iso2": "PK",
            "iso3": "PAK",
            "phone_code": "+92",
            "url": "https://flagcdn.com/w40/pk.png",
        },
        {
            "nombre": "Palau (+680)",
            "name": "Palau",
            "nom": "Palau",
            "iso2": "PW",
            "iso3": "PLW",
            "phone_code": "+680",
            "url": "https://flagcdn.com/w40/pw.png",
        },
        {
            "nombre": "Palestina (+970)",
            "name": "Palestine",
            "nom": "La Palestine",
            "iso2": "PS",
            "iso3": "PSE",
            "phone_code": "+970",
            "url": "https://flagcdn.com/w40/ps.png",
        },
        {
            "nombre": "Panamá (+507)",
            "name": "Panama",
            "nom": "Panama",
            "iso2": "PA",
            "iso3": "PAN",
            "phone_code": "+507",
            "url": "https://flagcdn.com/w40/pa.png",
        },
        {
            "nombre": "Papúa Nueva Guinea (+675)",
            "name": "Papua New Guinea",
            "nom": "Papouasie Nouvelle Guinée",
            "iso2": "PG",
            "iso3": "PNG",
            "phone_code": "+675",
            "url": "https://flagcdn.com/w40/pg.png",
        },
        {
            "nombre": "Paraguay (+595)",
            "name": "Paraguay",
            "nom": "Paraguay",
            "iso2": "PY",
            "iso3": "PRY",
            "phone_code": "+595",
            "url": "https://flagcdn.com/w40/py.png",
        },
        {
            "nombre": "Perú (+51)",
            "name": "Peru",
            "nom": "Pérou",
            "iso2": "PE",
            "iso3": "PER",
            "phone_code": "+51",
            "url": "https://flagcdn.com/w40/pe.png",
        },
        {
            "nombre": "Polinesia Francesa (+689)",
            "name": "French Polynesia",
            "nom": "Polynésie française",
            "iso2": "PF",
            "iso3": "PYF",
            "phone_code": "+689",
            "url": "https://flagcdn.com/w40/pf.png",
        },
        {
            "nombre": "Polonia (+48)",
            "name": "Poland",
            "nom": "Pologne",
            "iso2": "PL",
            "iso3": "POL",
            "phone_code": "+48",
            "url": "https://flagcdn.com/w40/pl.png",
        },
        {
            "nombre": "Portugal (+351)",
            "name": "Portugal",
            "nom": "Portugal",
            "iso2": "PT",
            "iso3": "PRT",
            "phone_code": "+351",
            "url": "https://flagcdn.com/w40/pt.png",
        },
        {
            "nombre": "Puerto Rico (+1)",
            "name": "Puerto Rico",
            "nom": "Porto Rico",
            "iso2": "PR",
            "iso3": "PRI",
            "phone_code": "+1",
            "url": "https://flagcdn.com/w40/pr.png",
        },
        {
            "nombre": "Qatar (+974)",
            "name": "Qatar",
            "nom": "Qatar",
            "iso2": "QA",
            "iso3": "QAT",
            "phone_code": "+974",
            "url": "https://flagcdn.com/w40/qa.png",
        },
        {
            "nombre": "Reino Unido (+44)",
            "name": "United Kingdom",
            "nom": "Royaume Uni",
            "iso2": "GB",
            "iso3": "GBR",
            "phone_code": "+44",
            "url": "https://flagcdn.com/w40/gb.png",
        },
        {
            "nombre": "República Centroafricana (+236)",
            "name": "Central African Republic",
            "nom": "République Centrafricaine",
            "iso2": "CF",
            "iso3": "CAF",
            "phone_code": "+236",
            "url": "https://flagcdn.com/w40/cf.png",
        },
        {
            "nombre": "República Checa (+420)",
            "name": "Czech Republic",
            "nom": "République Tchèque",
            "iso2": "CZ",
            "iso3": "CZE",
            "phone_code": "+420",
            "url": "https://flagcdn.com/w40/cz.png",
        },
        {
            "nombre": "República Dominicana (+1 809)",
            "name": "Dominican Republic",
            "nom": "République Dominicaine",
            "iso2": "DO",
            "iso3": "DOM",
            "phone_code": "+1 809",
            "url": "https://flagcdn.com/w40/do.png",
        },
        {
            "nombre": "República de Sudán del Sur (+211)",
            "name": "South Sudan",
            "nom": "Soudan du Sud",
            "iso2": "SS",
            "iso3": "SSD",
            "phone_code": "+211",
            "url": "https://flagcdn.com/w40/ss.png",
        },
        {
            "nombre": "Reunión (+262)",
            "name": "Réunion",
            "nom": "Réunion",
            "iso2": "RE",
            "iso3": "REU",
            "phone_code": "+262",
            "url": "https://flagcdn.com/w40/re.png",
        },
        {
            "nombre": "Ruanda (+250)",
            "name": "Rwanda",
            "nom": "Rwanda",
            "iso2": "RW",
            "iso3": "RWA",
            "phone_code": "+250",
            "url": "https://flagcdn.com/w40/rw.png",
        },
        {
            "nombre": "Rumanía (+40)",
            "name": "Romania",
            "nom": "Roumanie",
            "iso2": "RO",
            "iso3": "ROU",
            "phone_code": "+40",
            "url": "https://flagcdn.com/w40/ro.png",
        },
        {
            "nombre": "Rusia (+7)",
            "name": "Russia",
            "nom": "La Russie",
            "iso2": "RU",
            "iso3": "RUS",
            "phone_code": "+7",
            "url": "https://flagcdn.com/w40/ru.png",
        },
        {
            "nombre": "Sahara Occidental (+212)",
            "name": "Western Sahara",
            "nom": "Sahara Occidental",
            "iso2": "EH",
            "iso3": "ESH",
            "phone_code": "+212",
            "url": "https://flagcdn.com/w40/eh.png",
        },
        {
            "nombre": "Samoa (+685)",
            "name": "Samoa",
            "nom": "Samoa",
            "iso2": "WS",
            "iso3": "WSM",
            "phone_code": "+685",
            "url": "https://flagcdn.com/w40/ws.png",
        },
        {
            "nombre": "Samoa Americana (+1 684)",
            "name": "American Samoa",
            "nom": "Les Samoa américaines",
            "iso2": "AS",
            "iso3": "ASM",
            "phone_code": "+1 684",
            "url": "https://flagcdn.com/w40/as.png",
        },
        {
            "nombre": "San Bartolomé (+590)",
            "name": "Saint Barthélemy",
            "nom": "Saint Barthélemy",
            "iso2": "BL",
            "iso3": "BLM",
            "phone_code": "+590",
            "url": "https://flagcdn.com/w40/bl.png",
        },
        {
            "nombre": "San Cristóbal y Nieves (+1 869)",
            "name": "Saint Kitts and Nevis",
            "nom": "Saint Kitts et Nevis",
            "iso2": "KN",
            "iso3": "KNA",
            "phone_code": "+1 869",
            "url": "https://flagcdn.com/w40/kn.png",
        },
        {
            "nombre": "San Marino (+378)",
            "name": "San Marino",
            "nom": "San Marino",
            "iso2": "SM",
            "iso3": "SMR",
            "phone_code": "+378",
            "url": "https://flagcdn.com/w40/sm.png",
        },
        {
            "nombre": "San Martín (Francia (+1 599))",
            "name": "Saint Martin (French part)",
            "nom": "Saint-Martin (partie française)",
            "iso2": "MF",
            "iso3": "MAF",
            "phone_code": "+1 599",
            "url": "https://flagcdn.com/w40/mf.png",
        },
        {
            "nombre": "San Pedro y Miquelón (+508)",
            "name": "Saint Pierre and Miquelon",
            "nom": "Saint Pierre et Miquelon",
            "iso2": "PM",
            "iso3": "SPM",
            "phone_code": "+508",
            "url": "https://flagcdn.com/w40/pm.png",
        },
        {
            "nombre": "San Vicente y las Granadinas (+1 784)",
            "name": "Saint Vincent and the Grenadines",
            "nom": "Saint Vincent et Grenadines",
            "iso2": "VC",
            "iso3": "VCT",
            "phone_code": "+1 784",
            "url": "https://flagcdn.com/w40/vc.png",
        },
        {
            "nombre": "Santa Elena (+290)",
            "name": "Ascensión y Tristán de Acuña",
            "nom": "Ascensión y Tristan de Acuña",
            "iso2": "SH",
            "iso3": "SHN",
            "phone_code": "+290",
            "url": "https://flagcdn.com/w40/sh.png",
        },
        {
            "nombre": "Santa Lucía (+1 758)",
            "name": "Saint Lucia",
            "nom": "Sainte Lucie",
            "iso2": "LC",
            "iso3": "LCA",
            "phone_code": "+1 758",
            "url": "https://flagcdn.com/w40/lc.png",
        },
        {
            "nombre": "Santo Tomé y Príncipe (+239)",
            "name": "Sao Tome and Principe",
            "nom": "Sao Tomé et Principe",
            "iso2": "ST",
            "iso3": "STP",
            "phone_code": "+239",
            "url": "https://flagcdn.com/w40/st.png",
        },
        {
            "nombre": "Senegal (+221)",
            "name": "Senegal",
            "nom": "Sénégal",
            "iso2": "SN",
            "iso3": "SEN",
            "phone_code": "+221",
            "url": "https://flagcdn.com/w40/sn.png",
        },
        {
            "nombre": "Serbia (+381)",
            "name": "Serbia",
            "nom": "Serbie",
            "iso2": "RS",
            "iso3": "SRB",
            "phone_code": "+381",
            "url": "https://flagcdn.com/w40/rs.png",
        },
        {
            "nombre": "Seychelles (+248)",
            "name": "Seychelles",
            "nom": "Les Seychelles",
            "iso2": "SC",
            "iso3": "SYC",
            "phone_code": "+248",
            "url": "https://flagcdn.com/w40/sc.png",
        },
        {
            "nombre": "Sierra Leona (+232)",
            "name": "Sierra Leone",
            "nom": "Sierra Leone",
            "iso2": "SL",
            "iso3": "SLE",
            "phone_code": "+232",
            "url": "https://flagcdn.com/w40/sl.png",
        },
        {
            "nombre": "Singapur (+65)",
            "name": "Singapore",
            "nom": "Singapour",
            "iso2": "SG",
            "iso3": "SGP",
            "phone_code": "+65",
            "url": "https://flagcdn.com/w40/sg.png",
        },
        {
            "nombre": "Sint Maarten (+1 721)",
            "name": "Sint Maarten",
            "nom": "Saint Martin",
            "iso2": "SX",
            "iso3": "SMX",
            "phone_code": "+1 721",
            "url": "https://flagcdn.com/w40/sx.png",
        },
        {
            "nombre": "Siria (+963)",
            "name": "Syria",
            "nom": "Syrie",
            "iso2": "SY",
            "iso3": "SYR",
            "phone_code": "+963",
            "url": "https://flagcdn.com/w40/sy.png",
        },
        {
            "nombre": "Somalia (+252)",
            "name": "Somalia",
            "nom": "Somalie",
            "iso2": "SO",
            "iso3": "SOM",
            "phone_code": "+252",
            "url": "https://flagcdn.com/w40/so.png",
        },
        {
            "nombre": "Sri lanka (+94)",
            "name": "Sri Lanka",
            "nom": "Sri Lanka",
            "iso2": "LK",
            "iso3": "LKA",
            "phone_code": "+94",
            "url": "https://flagcdn.com/w40/lk.png",
        },
        {
            "nombre": "Sudáfrica (+27)",
            "name": "South Africa",
            "nom": "Afrique du Sud",
            "iso2": "ZA",
            "iso3": "ZAF",
            "phone_code": "+27",
            "url": "https://flagcdn.com/w40/za.png",
        },
        {
            "nombre": "Sudán (+249)",
            "name": "Sudan",
            "nom": "Soudan",
            "iso2": "SD",
            "iso3": "SDN",
            "phone_code": "+249",
            "url": "https://flagcdn.com/w40/sd.png",
        },
        {
            "nombre": "Suecia (+46)",
            "name": "Sweden",
            "nom": "Suède",
            "iso2": "SE",
            "iso3": "SWE",
            "phone_code": "+46",
            "url": "https://flagcdn.com/w40/se.png",
        },
        {
            "nombre": "Suiza (+41)",
            "name": "Switzerland",
            "nom": "Suisse",
            "iso2": "CH",
            "iso3": "CHE",
            "phone_code": "+41",
            "url": "https://flagcdn.com/w40/ch.png",
        },
        {
            "nombre": "Surinám (+597)",
            "name": "Suriname",
            "nom": "Surinam",
            "iso2": "SR",
            "iso3": "SUR",
            "phone_code": "+597",
            "url": "https://flagcdn.com/w40/sr.png",
        },
        {
            "nombre": "Svalbard y Jan Mayen (+47)",
            "name": "Svalbard and Jan Mayen",
            "nom": "Svalbard et Jan Mayen",
            "iso2": "SJ",
            "iso3": "SJM",
            "phone_code": "+47",
            "url": "https://flagcdn.com/w40/sj.png",
        },
        {
            "nombre": "Swazilandia (+268)",
            "name": "Swaziland",
            "nom": "Swaziland",
            "iso2": "SZ",
            "iso3": "SWZ",
            "phone_code": "+268",
            "url": "https://flagcdn.com/w40/sz.png",
        },
        {
            "nombre": "Tayikistán (+992)",
            "name": "Tajikistan",
            "nom": "Le Tadjikistan",
            "iso2": "TJ",
            "iso3": "TJK",
            "phone_code": "+992",
            "url": "https://flagcdn.com/w40/tj.png",
        },
        {
            "nombre": "Tailandia (+66)",
            "name": "Thailand",
            "nom": "Thaïlande",
            "iso2": "TH",
            "iso3": "THA",
            "phone_code": "+66",
            "url": "https://flagcdn.com/w40/th.png",
        },
        {
            "nombre": "Taiwán (+886)",
            "name": "Taiwan",
            "nom": "Taiwan",
            "iso2": "TW",
            "iso3": "TWN",
            "phone_code": "+886",
            "url": "https://flagcdn.com/w40/tw.png",
        },
        {
            "nombre": "Tanzania (+255)",
            "name": "Tanzania",
            "nom": "Tanzanie",
            "iso2": "TZ",
            "iso3": "TZA",
            "phone_code": "+255",
            "url": "https://flagcdn.com/w40/tz.png",
        },
        {
            "nombre": "Territorio Británico del Océano Índico (+246)",
            "name": "British Indian Ocean Territory",
            "nom": "Territoire britannique de l océan Indien",
            "iso2": "IO",
            "iso3": "IOT",
            "phone_code": "+246",
            "url": "https://flagcdn.com/w40/io.png",
        },
        # {
        #     "nombre": "Territorios Australes y Antárticas Franceses",
        #     "name": "French Southern Territories",
        #     "nom": "Terres australes françaises",
        #     "iso2": "TF",
        #     "iso3": "ATF",
        #     "phone_code": "",
        #     "url": "https://flagcdn.com/w40/tf.png",
        # },
        {
            "nombre": "Timor Oriental (+670)",
            "name": "East Timor",
            "nom": "Timor Oriental",
            "iso2": "TL",
            "iso3": "TLS",
            "phone_code": "+670",
            "url": "https://flagcdn.com/w40/tl.png",
        },
        {
            "nombre": "Togo (+228)",
            "name": "Togo",
            "nom": "Togo",
            "iso2": "TG",
            "iso3": "TGO",
            "phone_code": "+228",
            "url": "https://flagcdn.com/w40/tg.png",
        },
        {
            "nombre": "Tokelau (+690)",
            "name": "Tokelau",
            "nom": "Tokélaou",
            "iso2": "TK",
            "iso3": "TKL",
            "phone_code": "+690",
            "url": "https://flagcdn.com/w40/tk.png",
        },
        {
            "nombre": "Tonga (+676)",
            "name": "Tonga",
            "nom": "Tonga",
            "iso2": "TO",
            "iso3": "TON",
            "phone_code": "+676",
            "url": "https://flagcdn.com/w40/to.png",
        },
        {
            "nombre": "Trinidad y Tobago (+1 868)",
            "name": "Trinidad and Tobago",
            "nom": "Trinidad et Tobago",
            "iso2": "TT",
            "iso3": "TTO",
            "phone_code": "+1 868",
            "url": "https://flagcdn.com/w40/tt.png",
        },
        {
            "nombre": "Tunez (+216)",
            "name": "Tunisia",
            "nom": "Tunisie",
            "iso2": "TN",
            "iso3": "TUN",
            "phone_code": "+216",
            "url": "https://flagcdn.com/w40/tn.png",
        },
        {
            "nombre": "Turkmenistán (+993)",
            "name": "Turkmenistan",
            "nom": "Le Turkménistan",
            "iso2": "TM",
            "iso3": "TKM",
            "phone_code": "+993",
            "url": "https://flagcdn.com/w40/tm.png",
        },
        {
            "nombre": "Turquía (+90)",
            "name": "Turkey",
            "nom": "Turquie",
            "iso2": "TR",
            "iso3": "TUR",
            "phone_code": "+90",
            "url": "https://flagcdn.com/w40/tr.png",
        },
        {
            "nombre": "Tuvalu (+688)",
            "name": "Tuvalu",
            "nom": "Tuvalu",
            "iso2": "TV",
            "iso3": "TUV",
            "phone_code": "+688",
            "url": "https://flagcdn.com/w40/tv.png",
        },
        {
            "nombre": "Ucrania (+380)",
            "name": "Ukraine",
            "nom": "L Ukraine",
            "iso2": "UA",
            "iso3": "UKR",
            "phone_code": "+380",
            "url": "https://flagcdn.com/w40/ua.png",
        },
        {
            "nombre": "Uganda (+256)",
            "name": "Uganda",
            "nom": "Ouganda",
            "iso2": "UG",
            "iso3": "UGA",
            "phone_code": "+256",
            "url": "https://flagcdn.com/w40/ug.png",
        },
        {
            "nombre": "Uruguay (+598)",
            "name": "Uruguay",
            "nom": "Uruguay",
            "iso2": "UY",
            "iso3": "URY",
            "phone_code": "+598",
            "url": "https://flagcdn.com/w40/uy.png",
        },
        {
            "nombre": "Uzbekistán (+998)",
            "name": "Uzbekistan",
            "nom": "L Ouzbékistan",
            "iso2": "UZ",
            "iso3": "UZB",
            "phone_code": "+998",
            "url": "https://flagcdn.com/w40/uz.png",
        },
        {
            "nombre": "Vanuatu (+678)",
            "name": "Vanuatu",
            "nom": "Vanuatu",
            "iso2": "VU",
            "iso3": "VUT",
            "phone_code": "+678",
            "url": "https://flagcdn.com/w40/vu.png",
        },
        {
            "nombre": "Venezuela (+58)",
            "name": "Venezuela",
            "nom": "Venezuela",
            "iso2": "VE",
            "iso3": "VEN",
            "phone_code": "+58",
            "url": "https://flagcdn.com/w40/ve.png",
        },
        {
            "nombre": "Vietnam (+84)",
            "name": "Vietnam",
            "nom": "Vietnam",
            "iso2": "VN",
            "iso3": "VNM",
            "phone_code": "+84",
            "url": "https://flagcdn.com/w40/vn.png",
        },
        {
            "nombre": "Wallis y Futuna (+681)",
            "name": "Wallis and Futuna",
            "nom": "Wallis et Futuna",
            "iso2": "WF",
            "iso3": "WLF",
            "phone_code": "+681",
            "url": "https://flagcdn.com/w40/wf.png",
        },
        {
            "nombre": "Yemen (+967)",
            "name": "Yemen",
            "nom": "Yémen",
            "iso2": "YE",
            "iso3": "YEM",
            "phone_code": "+967",
            "url": "https://flagcdn.com/w40/ye.png",
        },
        {
            "nombre": "Yibuti (+253)",
            "name": "Djibouti",
            "nom": "Djibouti",
            "iso2": "DJ",
            "iso3": "DJI",
            "phone_code": "+253",
            "url": "https://flagcdn.com/w40/dj.png",
        },
        {
            "nombre": "Zambia (+260)",
            "name": "Zambia",
            "nom": "Zambie",
            "iso2": "ZM",
            "iso3": "ZMB",
            "phone_code": "+260",
            "url": "https://flagcdn.com/w40/zm.png",
        },
        {
            "nombre": "Zimbabue (+263)",
            "name": "Zimbabwe",
            "nom": "Zimbabwe",
            "iso2": "ZW",
            "iso3": "ZWE",
            "phone_code": "+263",
            "url": "https://flagcdn.com/w40/zw.png",
        }
    ]

    caracteristicas_metrocuadrado = [
        {
            "amenity": "lifts",
            "required": False,
            "name": "nroAscensores",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-4"
            ],
            "carac_id": [
                26
            ],
            "view_inmu": False
        },
        {
            "amenity": "bodyguardRoom",
            "required": False,
            "name": "conCuartoEscoltas",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                80
            ],
            "view_inmu": False
        },
        {
            "amenity": "basketballCourt",
            "required": False,
            "name": "conCanchaBasket",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": ["true|false"],
            "carac_id": [46],
            "view_inmu": False
        },
        {
            "amenity": "cctv",
            "required": False,
            "name": "conCircuitoCerradoTV",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": ["true|false"],
            "carac_id": [57],
            "view_inmu": False
        },
        {
            "amenity": "builtTime",
            "required": True,
            "name": "tiempoConstruido",
            "tipo_inmueble": [
                {
                    "required": True,
                    "tipo_inmueble": 1
                },
                {
                    "required": True,
                    "tipo_inmueble": 2
                },
                {
                    "required": True,
                    "tipo_inmueble": 5
                },
                {
                    "required": True,
                    "tipo_inmueble": 16
                },
                {
                    "required": True,
                    "tipo_inmueble": 9
                },
                {
                    "required": True,
                    "tipo_inmueble": 15
                },
                {
                    "required": True,
                    "tipo_inmueble": 10
                },
                {
                    "required": True,
                    "tipo_inmueble": 8
                },
                {
                    "required": True,
                    "tipo_inmueble": 14
                },
                {
                    "required": True,
                    "tipo_inmueble": 4
                },
                {
                    "required": True,
                    "tipo_inmueble": 6
                },
                {
                    "required": True,
                    "tipo_inmueble": 7
                },
                {
                    "required": True,
                    "tipo_inmueble": 12
                },
                {
                    "required": True,
                    "tipo_inmueble": 3
                },
                {
                    "required": True,
                    "tipo_inmueble": 11
                },
                {
                    "required": True,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "range",
            "restrictions": [
                {
                    "value": [
                        0,
                        5
                    ],
                    "label": "Entre 0 y 5 años"
                },
                {
                    "value": [
                        5,
                        10
                    ],
                    "label": "Entre 5 y 10 años"
                },
                {
                    "value": [
                        10,
                        20
                    ],
                    "label": "Entre 10 y 20 años"
                },
                {
                    "value": [
                        20,
                        9999
                    ],
                    "label": "Más de 20 años"
                }
            ],
            "carac_id": [
                18
            ],
            "view_inmu": False
        },
        {
            "amenity": "rooms",
            "required": True,
            "name": "nroCuartos",
            "tipo_inmueble": [
                {
                    "required": True,
                    "tipo_inmueble": 2
                },
                {
                    "required": True,
                    "tipo_inmueble": 5
                },
                {
                    "required": True,
                    "tipo_inmueble": 4
                },
                {
                    "required": True,
                    "tipo_inmueble": 6
                },
                {
                    "required": True,
                    "tipo_inmueble": 7
                },
                {
                    "required": True,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                },
                {
                    "required": True,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-5"
            ],
            "carac_id": [
                13
            ],
            "view_inmu": False
        },
        {
            "amenity": "bathrooms",
            "required": True,
            "name": "nroBanos",
            "tipo_inmueble": [
                {
                    "required": True,
                    "tipo_inmueble": 2
                },
                {
                    "required": True,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": True,
                    "tipo_inmueble": 4
                },
                {
                    "required": True,
                    "tipo_inmueble": 6
                },
                {
                    "required": True,
                    "tipo_inmueble": 7
                },
                {
                    "required": True,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                },
                {
                    "required": True,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-5"
            ],
            "carac_id": [
                34
            ],
            "view_inmu": False
        },
        {
            "amenity": "garages",
            "required": True,
            "name": "nroGarajes",
            "tipo_inmueble": [
                {
                    "required": True,
                    "tipo_inmueble": 2
                },
                {
                    "required": True,
                    "tipo_inmueble": 5
                },
                {
                    "required": True,
                    "tipo_inmueble": 16
                },
                {
                    "required": True,
                    "tipo_inmueble": 10
                },
                {
                    "required": True,
                    "tipo_inmueble": 8
                },
                {
                    "required": True,
                    "tipo_inmueble": 14
                },
                {
                    "required": True,
                    "tipo_inmueble": 4
                },
                {
                    "required": True,
                    "tipo_inmueble": 6
                },
                {
                    "required": True,
                    "tipo_inmueble": 7
                },
                {
                    "required": True,
                    "tipo_inmueble": 12
                },
                {
                    "required": True,
                    "tipo_inmueble": 3
                },
                {
                    "required": True,
                    "tipo_inmueble": 11
                },
                {
                    "required": True,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": "0-100",
            "carac_id": [
                301
            ],
            "view_inmu": False
        },
        {
            "amenity": "dinningRoomType",
            "required": False,
            "name": "tipoComedor",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "multiple",
            "restrictions": [
                {
                    "value": 69,
                    "label": "Comedor Independiente"
                },
                {
                    "value": 191,
                    "label": "Sala Comedor"
                }
            ],
            "carac_id": [
                69,
                191
            ],
            "view_inmu": False
        },
        {
            "amenity": "gasInstallationType",
            "required": False,
            "name": "instalacionGas",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "unique",
            "restrictions": [
                {
                    "value": 118,
                    "label": "Natural"
                }
            ],
            "carac_id": [
                118
            ],
            "view_inmu": False
        },
        {
            "amenity": "heaterType",
            "required": False,
            "name": "tipoCalentador",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "multiple",
            "restrictions": [
                {
                    "value": 44,
                    "label": "Gas"
                },
                {
                    "value": 45,
                    "label": "Electrico"
                },
                {
                    "value": 42,
                    "label": "Caldera"
                }
            ],
            "carac_id": [
                44,
                45,
                42
            ],
            "view_inmu": False
        },
        {
            "amenity": "studyOrLibrary",
            "required": False,
            "name": "conEstudioBiblioteca",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                100
            ],
            "view_inmu": False
        },
        {
            "amenity": "terraceOrBalcony",
            "required": False,
            "name": "terrazaBalcon",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "multiple",
            "restrictions": [
                {
                    "value": 218,
                    "label": "Terraza"
                },
                {
                    "value": 29,
                    "label": "Balcón"
                }
            ],
            "carac_id": [
                218,
                29
            ],
            "view_inmu": False
        },
        {
            "amenity": "terraceOrBalconyArea",
            "required": False,
            "name": "areaTerraza",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-9999999.99"
            ],
            "carac_id": [
                20
            ],
            "view_inmu": False
        },
        {
            "amenity": "closedComplex",
            "required": False,
            "name": "enConjuntoCerrado",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                93
            ],
            "view_inmu": False
        },
        {
            "amenity": "laundryArea",
            "required": False,
            "name": "conZonaLavanderia",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                234
            ],
            "view_inmu": False
        },
        {
            "amenity": "furnished",
            "required": False,
            "name": "conMuebles",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                137
            ],
            "view_inmu": False
        },
        {
            "amenity": "floorNumber",
            "required": False,
            "name": "nroPiso",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-999"
            ],
            "carac_id": [
                140,
                171
            ],
            "view_inmu": False
        },
        {
            "amenity": "serviceRoom",
            "required": False,
            "name": "conCuartoServicio",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                81
            ],
            "view_inmu": False
        },
        {
            "amenity": "chimney",
            "required": False,
            "name": "conChimenea",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                56
            ],
            "view_inmu": False
        },
        {
            "amenity": "airConditioned",
            "required": False,
            "name": "conAireAcondicionado",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                6
            ],
            "view_inmu": False
        },
        {
            "amenity": "cytophone",
            "required": False,
            "name": "conCitofono",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                58
            ],
            "view_inmu": False
        },
        {
            "amenity": "flooringType",
            "required": False,
            "name": "tipoPiso",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "multiple",
            "restrictions": [
                {
                    "value": 165,
                    "label": "Cemento"
                },
                {
                    "value": 168,
                    "label": "Marmol"
                },
                {
                    "value": 164,
                    "label": "Baldosa"
                },
                {
                    "value": 164,
                    "label": "Baldosa"
                },
                {
                    "value": 166,
                    "label": "Cerámica"
                },
                {
                    "value": 172,
                    "label": "Madera"
                },
                {
                    "value": 174,
                    "label": "Porcelanato"
                }
            ],
            "carac_id": [
                165,
                168,
                164,
                166,
                172,
                174
            ],
            "view_inmu": False
        },
        {
            "amenity": "wardrobes",
            "required": False,
            "name": "nroClosets",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-4"
            ],
            "carac_id": [
                59
            ],
            "view_inmu": False
        },
        {
            "amenity": "hall",
            "required": False,
            "name": "conHall",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                120
            ],
            "view_inmu": False
        },
        {
            "amenity": "jacuzzi",
            "required": False,
            "name": "conJacuzzi",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                196
            ],
            "view_inmu": False
        },
        {
            "amenity": "securityDoors",
            "required": False,
            "name": "conPuertasSeguridad",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                179
            ],
            "view_inmu": False
        },
        {
            "amenity": "alarm",
            "required": False,
            "name": "conAlarma",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                7
            ],
            "view_inmu": False
        },
        {
            "amenity": "panoramicView",
            "required": False,
            "name": "conVistaPanoramica",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                224
            ],
            "view_inmu": False
        },
        {
            "amenity": "pool",
            "required": False,
            "name": "conPiscina",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                160
            ],
            "view_inmu": False
        },
        {
            "amenity": "tennisCourt",
            "required": False,
            "name": "conCanchaTenis",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                48
            ],
            "view_inmu": False
        },
        {
            "amenity": "squashCourt",
            "required": False,
            "name": "conCanchaSquash",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                49
            ],
            "view_inmu": False
        },
        {
            "amenity": "soccerField",
            "required": False,
            "name": "conCanchaFutbol",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                47
            ],
            "view_inmu": False
        },
        {
            "amenity": "elevator",
            "required": False,
            "name": "ascensor",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                24
            ],
            "view_inmu": False
        },
        {
            "amenity": "heater",
            "required": False,
            "name": "conCalefaccion",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                43
            ],
            "view_inmu": False
        },
        {
            "amenity": "greenArea",
            "required": False,
            "name": "conZonasVerdes",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                240
            ],
            "view_inmu": False
        },
        {
            "amenity": "childrenArea",
            "required": False,
            "name": "conZonaNinos",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                236
            ],
            "view_inmu": False
        },
        {
            "amenity": "bbqArea",
            "required": False,
            "name": "conZonaBbq",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                230
            ],
            "view_inmu": False
        },
        {
            "amenity": "communityHall",
            "required": False,
            "name": "conSalonComunal",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                192
            ],
            "view_inmu": False
        },
        {
            "amenity": "gym",
            "required": False,
            "name": "conGimnasio",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                119
            ],
            "view_inmu": False
        },
        {
            "amenity": "surveillanceType",
            "required": False,
            "name": "tipoVigilancia",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "unique",
            "restrictions": [
                {
                    "value": 223,
                    "label": "24hrs"
                }
            ],
            "carac_id": [
                223
            ],
            "view_inmu": False
        },
        {
            "amenity": "onMainStreet",
            "required": False,
            "name": "sobreViaPrincipal",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                206
            ],
            "view_inmu": False
        },
        {
            "amenity": "onSecondaryRoad",
            "required": False,
            "name": "sobreViaSecundaria",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                207
            ],
            "view_inmu": False
        },
        {
            "amenity": "nearbyShoppingCenter",
            "required": False,
            "name": "cercaCentroComercial",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                54
            ],
            "view_inmu": False
        },
        {
            "amenity": "nearbyPark",
            "required": False,
            "name": "cercaParque",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                154
            ],
            "view_inmu": False
        },
        {
            "amenity": "nearbyPublicTransport",
            "required": False,
            "name": "cercaTransportePublico",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                219
            ],
            "view_inmu": False
        },
        {
            "amenity": "nearbySchoolCollege",
            "required": False,
            "name": "cercaColegioUniversidad",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                68
            ],
            "view_inmu": False
        },
        {
            "amenity": "woodenFloor",
            "required": False,
            "name": "conPisoMadera_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                172
            ],
            "view_inmu": False
        },
        {
            "amenity": "carpetedFloor",
            "required": False,
            "name": "conPisoAlfombra_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                162
            ],
            "view_inmu": False
        },
        {
            "amenity": "tiledFloor",
            "required": False,
            "name": "conPisoBaldosa_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                164
            ],
            "view_inmu": False
        },
        {
            "amenity": "porcelainTiledFloor",
            "required": False,
            "name": "conPisoPorcelanato_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                174
            ],
            "view_inmu": False
        },
        {
            "amenity": "fullKitchen",
            "required": False,
            "name": "conCocinaIntegral_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                63
            ],
            "view_inmu": False
        },
        {
            "amenity": "americanKitchen",
            "required": False,
            "name": "conCocinaAmericana_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                65
            ],
            "view_inmu": False
        },
        {
            "amenity": "serviceBathroom",
            "required": False,
            "name": "conBanoServicio_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                32
            ],
            "view_inmu": False
        },
        {
            "amenity": "visitorParkingLot",
            "required": False,
            "name": "conParqueaderoVisitantes_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                153
            ],
            "view_inmu": False
        },
        {
            "amenity": "terrace",
            "required": False,
            "name": "conTerraza_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                218
            ],
            "view_inmu": False
        },
        {
            "amenity": "golfCage",
            "required": False,
            "name": "conJaulaGolf_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                127
            ],
            "view_inmu": False
        },
        {
            "amenity": "twoFamilyHome",
            "required": False,
            "name": "viviendaBifamiliar",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                226
            ],
            "view_inmu": False
        },
        {
            "amenity": "auxiliaryBathroom",
            "required": False,
            "name": "banosAuxiliar",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                30
            ],
            "view_inmu": False
        },
        {
            "amenity": "gateHouse",
            "required": False,
            "name": "porteria",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                176
            ],
            "view_inmu": False
        },
        {
            "amenity": "ruralZone",
            "required": False,
            "name": "zonaCampestre",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                228
            ],
            "view_inmu": False
        },
        {
            "amenity": "shoppingZone",
            "required": False,
            "name": "zonaComercial",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                229
            ],
            "view_inmu": False
        },
        {
            "amenity": "residentialZone",
            "required": False,
            "name": "zonaResidencial",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                238
            ],
            "view_inmu": False
        },
        {
            "amenity": "houseType",
            "required": False,
            "name": "tipoCasa",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 5
                }
            ],
            "validate": "unique",
            "restrictions": [
                {
                    "value": 92,
                    "label": "Condominio"
                }
            ],
            "carac_id": [
                92
            ],
            "view_inmu": False
        },
        {
            "amenity": "corner",
            "required": False,
            "name": "esEsquinero",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                97
            ],
            "view_inmu": False
        },
        {
            "amenity": "levels",
            "required": False,
            "name": "nroNiveles",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 5
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-5"
            ],
            "carac_id": [
                140
            ],
            "view_inmu": False
        },
        {
            "amenity": "innerGarden",
            "required": False,
            "name": "conJardinInterior",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 5
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                125
            ],
            "view_inmu": False
        },
        {
            "amenity": "garden",
            "required": False,
            "name": "conJardin",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                126
            ],
            "view_inmu": False
        },
        {
            "amenity": "courtyard",
            "required": False,
            "name": "patio",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                155
            ],
            "view_inmu": False
        },
        {
            "amenity": "officeType",
            "required": False,
            "name": "tipoOficina",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 16
                }
            ],
            "validate": "multiple",
            "restrictions": [
                {
                    "value": 89,
                    "label": "Casa"
                },
                {
                    "value": 94,
                    "label": "Edificio"
                }
            ],
            "carac_id": [
                89,
                94
            ],
            "view_inmu": False
        },
        {
            "amenity": "officeNumber",
            "required": False,
            "name": "nroOficina",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 16
                }
            ],
            "validate": "number",
            "restrictions": [
                "[a-zA-Z1-9][a-zA-Z0-9-]+"
            ],
            "carac_id": [
                145
            ],
            "view_inmu": False
        },
        {
            "amenity": "buildingRating",
            "required": False,
            "name": "calificacionOficina",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 16
                }
            ],
            "validate": "unique",
            "restrictions": [
                {
                    "value": 94,
                    "label": "Edificio inteligente"
                }
            ],
            "carac_id": [
                88
            ],
            "view_inmu": False
        },
        {
            "amenity": "kitchenette",
            "required": False,
            "name": "conCocineta_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                67
            ],
            "view_inmu": False
        },
        {
            "amenity": "electricPlant",
            "required": False,
            "name": "conPlantaElectrica_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                175
            ],
            "view_inmu": False
        },
        {
            "amenity": "publicBathroom",
            "required": False,
            "name": "banosPublicos",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                36
            ],
            "view_inmu": False
        },
        {
            "amenity": "inShoppingCenter",
            "required": False,
            "name": "ubicadoCetroComercial",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                90
            ],
            "view_inmu": False
        },
        {
            "amenity": "industrialZone",
            "required": False,
            "name": "zonaIndustrial",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                235
            ],
            "view_inmu": False
        },
        {
            "amenity": "lotType",
            "required": False,
            "name": "tipoLote",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                }
            ],
            "validate": "multiple",
            "restrictions": [
                {
                    "value": 134,
                    "label": "Lote en construcción"
                },
                {
                    "value": 135,
                    "label": "Lote vacío"
                }
            ],
            "carac_id": [
                134,
                135
            ],
            "view_inmu": False
        },
        {
            "amenity": "ravineBoundary",
            "required": False,
            "name": "enLinderoRioQuebrada_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                185
            ],
            "view_inmu": False
        },
        {
            "amenity": "withHouse",
            "required": False,
            "name": "conVivienda",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                73
            ],
            "view_inmu": False
        },
        {
            "amenity": "emptyLot",
            "required": False,
            "name": "loteVacio",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                135
            ],
            "view_inmu": False
        },
        {
            "amenity": "establishmentType",
            "required": False,
            "name": "tipoLocal",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                }
            ],
            "validate": "multiple",
            "restrictions": [
                {
                    "value": 90,
                    "label": "En centro comercial"
                },
                {
                    "value": 110,
                    "label": "Afueras centro comercial"
                }
            ],
            "carac_id": [
                90,
                110
            ],
            "view_inmu": False
        },
        {
            "amenity": "truckAccess",
            "required": False,
            "name": "accesoCamiones",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                1
            ],
            "view_inmu": False
        },
        {
            "amenity": "restrictedHeight",
            "required": False,
            "name": "alturaRestringina",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                16
            ],
            "view_inmu": False
        },
        {
            "amenity": "unobstructedHeight",
            "required": False,
            "name": "alturaLibre",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                15
            ],
            "view_inmu": False
        },
        {
            "amenity": "countryside",
            "required": False,
            "name": "areaRural",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                21
            ],
            "view_inmu": False
        },
        {
            "amenity": "urbanArea",
            "required": False,
            "name": "areaUrbana",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                22
            ],
            "view_inmu": False
        },
        {
            "amenity": "fuelPump",
            "required": False,
            "name": "bombaGasolina",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                39
            ],
            "view_inmu": False
        },
        {
            "amenity": "restaurants",
            "required": False,
            "name": "restaurantes",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                184
            ],
            "view_inmu": False
        },
        {
            "amenity": "warehouseType",
            "required": False,
            "name": "tipoBodega",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "unique",
            "restrictions": [
                {
                    "value": 122,
                    "label": "Industrial"
                }
            ],
            "carac_id": [
                122
            ],
            "view_inmu": False
        },
        {
            "amenity": "hasOffices",
            "required": False,
            "name": "conOficinas",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                145
            ],
            "view_inmu": False
        },
        {
            "amenity": "waterTank",
            "required": False,
            "name": "conTanquesAgua_o",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                210
            ],
            "view_inmu": False
        },
        {
            "amenity": "trailerDoor",
            "required": False,
            "name": "conPuertaTractomulas-cb",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                2
            ],
            "view_inmu": False
        },
        {
            "amenity": "administrativeOffices",
            "required": False,
            "name": "oficinasAdministrativas",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 3
                }
            ],
            "validate": "boolean",
            "restrictions": [
                "true|false"
            ],
            "carac_id": [
                146
            ],
            "view_inmu": False
        },
        {
            "amenity": "builtArea",
            "required": True,
            "name": "areaConstruida",
            "tipo_inmueble": [
                {
                    "required": True,
                    "tipo_inmueble": 1
                },
                {
                    "required": True,
                    "tipo_inmueble": 2
                },
                {
                    "required": True,
                    "tipo_inmueble": 5
                },
                {
                    "required": True,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": True,
                    "tipo_inmueble": 10
                },
                {
                    "required": True,
                    "tipo_inmueble": 8
                },
                {
                    "required": True,
                    "tipo_inmueble": 14
                },
                {
                    "required": True,
                    "tipo_inmueble": 4
                },
                {
                    "required": True,
                    "tipo_inmueble": 6
                },
                {
                    "required": True,
                    "tipo_inmueble": 7
                },
                {
                    "required": True,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": True,
                    "tipo_inmueble": 11
                },
                {
                    "required": True,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-9999999.99"
            ],
            "carac_id": [
                "area_construida"
            ],
            "view_inmu": True
        },
        {
            "amenity": "area",
            "required": True,
            "name": "area",
            "tipo_inmueble": [
                {
                    "required": True,
                    "tipo_inmueble": 1
                },
                {
                    "required": True,
                    "tipo_inmueble": 2
                },
                {
                    "required": True,
                    "tipo_inmueble": 5
                },
                {
                    "required": True,
                    "tipo_inmueble": 16
                },
                {
                    "required": True,
                    "tipo_inmueble": 9
                },
                {
                    "required": True,
                    "tipo_inmueble": 15
                },
                {
                    "required": True,
                    "tipo_inmueble": 10
                },
                {
                    "required": True,
                    "tipo_inmueble": 8
                },
                {
                    "required": True,
                    "tipo_inmueble": 14
                },
                {
                    "required": True,
                    "tipo_inmueble": 4
                },
                {
                    "required": True,
                    "tipo_inmueble": 6
                },
                {
                    "required": True,
                    "tipo_inmueble": 7
                },
                {
                    "required": True,
                    "tipo_inmueble": 12
                },
                {
                    "required": True,
                    "tipo_inmueble": 3
                },
                {
                    "required": True,
                    "tipo_inmueble": 11
                },
                {
                    "required": True,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-9999999.99"
            ],
            "carac_id": [
                "area_total"
            ],
            "view_inmu": True
        },
        {
            "amenity": "registrationNumber",
            "required": False,
            "name": "matricula",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 2
                },
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 16
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 10
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                },
                {
                    "required": False,
                    "tipo_inmueble": 3
                },
                {
                    "required": False,
                    "tipo_inmueble": 11
                },
                {
                    "required": False,
                    "tipo_inmueble": 1
                }
            ],
            "validate": "number",
            "restrictions": [
                "[a-zA-Z1-9][a-zA-Z0-9-]+"
            ],
            "carac_id": [
                "matricula"
            ],
            "view_inmu": True
        },
        {
            "amenity": "lotArea",
            "required": False,
            "name": "areaLote",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                },
                {
                    "required": False,
                    "tipo_inmueble": 8
                },
                {
                    "required": False,
                    "tipo_inmueble": 14
                },
                {
                    "required": False,
                    "tipo_inmueble": 4
                },
                {
                    "required": False,
                    "tipo_inmueble": 6
                },
                {
                    "required": False,
                    "tipo_inmueble": 7
                },
                {
                    "required": False,
                    "tipo_inmueble": 12
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-9999999.99"
            ],
            "carac_id": [
                "area_libre"
            ],
            "view_inmu": True
        },
        {
            "amenity": "width",
            "required": False,
            "name": "ancho",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-9999999.99"
            ],
            "carac_id": [
                "frente"
            ],
            "view_inmu": True
        },
        {
            "amenity": "depth",
            "required": False,
            "name": "fondo",
            "tipo_inmueble": [
                {
                    "required": False,
                    "tipo_inmueble": 5
                },
                {
                    "required": False,
                    "tipo_inmueble": 9
                },
                {
                    "required": False,
                    "tipo_inmueble": 15
                }
            ],
            "validate": "number",
            "restrictions": [
                "1-9999999.99"
            ],
            "carac_id": [
                "fondo"
            ],
            "view_inmu": True
        }
    ]

    tipos_inmuebles_metrocuadrado = [
        {
            "id": 1,
            "text": "Apartamento",
            "tp_inmu_orbis": [2]
        },
        {
            "id": 2,
            "text": "Casa",
            "tp_inmu_orbis": [5]
        },
        {
            "id": 3,
            "text": "Oficina",
            "tp_inmu_orbis": [16]
        },
        {
            "id": 4,
            "text": "Lote o Casalote",
            "tp_inmu_orbis": [9, 15]
        },
        {
            "id": 5,
            "text": "Consultorio",
            "tp_inmu_orbis": [10]
        },
        {
            "id": 6,
            "text": "Local Comercial",
            "tp_inmu_orbis": [8, 14]
        },
        {
            "id": 7,
            "text": "Finca",
            "tp_inmu_orbis": [4, 6, 7, 12]
        },
        {
            "id": 8,
            "text": "Bodega",
            "tp_inmu_orbis": [3]
        },
        {
            "id": 9,
            "text": "Edificio de Apartamentos",
            "tp_inmu_orbis": [11]
        },
        {
            "id": 12,
            "text": "Apartahoteles",
            "tp_inmu_orbis": [13]
        },
        {
            "id": 13,
            "text": "Otros",
            "tp_inmu_orbis": [17]
        },
        {
            "id": 14,
            "text": "Apartaestudio",
            "tp_inmu_orbis": [1]
        }
    ]

    caracteristicas_proppit = [
        {"value_dgi" : 29, "label_dgi" : 'BALCÓN', "value_proppit": 'balcony'},
        {"value_dgi" : 5, "label_dgi" : 'AIRE ACONDICIONADO', "value_proppit": 'air conditioning'},
        {"value_dgi" : 7, "label_dgi" : 'ALARMA', "value_proppit": 'alarm'},
        {"value_dgi" : 117, "label_dgi" : 'PARQUEADERO', "value_proppit": 'car park'},
        {"value_dgi" : 236, "label_dgi" : 'ZONA INFANTIL', "value_proppit": "children's area"},
        {"value_dgi" : 63, "label_dgi" : 'COCINA INTEGRAL', "value_proppit": "equipped kitchen"},
        {"value_dgi" : 56, "label_dgi" : 'CHIMENEA', "value_proppit": "fireplace"},
        {"value_dgi" : 125, "label_dgi" : 'JARDÍN', "value_proppit": "garden"},
        {"value_dgi" : 23, "label_dgi" : 'ASADOR', "value_proppit": "grill"},
        {"value_dgi" : 119, "label_dgi" : 'GIMNASIO', "value_proppit": "gym"},
        {"value_dgi" : 176, "label_dgi" : 'PORTERÍA/VIGILANCIA', "value_proppit": "guardhouse"},
        {"value_dgi" : 45, "label_dgi" : 'CALENTADOR ELECTRICO', "value_proppit": "heating"},
        {"value_dgi" : 201, "label_dgi" : 'SERVICIO DE INTERNET', "value_proppit": "internet"},
        {"value_dgi" : 196, "label_dgi" : 'JACUZZI', "value_proppit": "jacuzzi"},
        {"value_dgi" : 24, "label_dgi" : 'ASCENSOR', "value_proppit": "lift"},
        {"value_dgi" : 118, "label_dgi" : 'GAS NATURAL', "value_proppit": "natural gas"},
        {"value_dgi" : 224, "label_dgi" : 'VISTA PANORÁMICA', "value_proppit": "panoramic view"},
        {"value_dgi" : 81, "label_dgi" : 'CUARTO DE SERVICIO', "value_proppit": "service room"},
        {"value_dgi" : 160, "label_dgi" : 'PISCINAS', "value_proppit": "swimming pool"},
        {"value_dgi" : 48, "label_dgi" : 'CANCHA DE TENNIS', "value_proppit": "tennis court"},
        {"value_dgi" : 218, "label_dgi" : 'TERRAZA', "value_proppit": "terrace"},
        {"value_dgi" : 210, "label_dgi" : 'TANQUES DE AGUA', "value_proppit": "water tank"},
        {"value_dgi" : 155, "label_dgi" : 'PATIO', "value_proppit": "yard"},
        {"value_dgi" : 82, "label_dgi" : 'DEPOSITO/BODEGA', "value_proppit": "cellar"},
        {"value_dgi" : 59, "label_dgi" : 'CLOSETS', "value_proppit": "built-in wardrobe"}
    ]

    cercanos_proppit = [
        {"value_dgi" : 68, "label_dgi" : 'COLEGIOS/UNIVERSIDADES', "value_proppit": 'near schools'},
        {"value_dgi" : 209, "label_dgi" : 'SUPERMERCADOS/C.CIALES', "value_proppit": 'near schools'},
        {"value_dgi" : 154, "label_dgi" : 'PARQUES CERCANOS', "value_proppit": 'near park'},
        {"value_dgi" : 206, "label_dgi" : 'SOBRE VÍA PRINCIPAL', "value_proppit": 'near mainstreet'},
    ]