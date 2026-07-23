from apps.common_db.db import execute_procedure
from apps.contabilidad.models.documento import Documentos
from apps.parametros.models.parametrizacion import Anio, Mes

import pdb

class FacturaService:

    @staticmethod
    def consulta_fact_electronica(data):
        """
        Consulta facturas electrónicas según filtros.
        
        Args:
            data: Diccionario con los parámetros de filtrado:
                - tiposfacturas: ID del tipo de documento
                - estadosfact: ID del estado de factura
                - persona_id: ID de la persona (opcional)
                - cont_anio: ID del año
                - cont_mes: ID del mes
        
        Returns:
            dict: Datos con facturas y documentos filtrados
        """
        tipo_documento = data['tiposfacturas']
        estadofact = data.get('estadosfact')
        persona_id = data.get('persona_id', 0)

        anio = Anio.objects.only('nombre').get(id=data['cont_anio'])
        mes = Mes.objects.only('numero').get(id=data['cont_mes'])

        sql = "SELECT * FROM getfacturacion_electro(%s, %s, %s, %s, %s);"
        params = [
            anio.nombre,
            mes.numero,
            tipo_documento,
            estadofact or 0,
            persona_id or 0
        ]

        try:
            resultado = execute_procedure(sql=sql, params=params)
            facturas = resultado[0][0] if resultado and resultado[0] else None
        except Exception as e:
            raise Exception(str(e))

        docs = Documentos.objects.filter(
            tipo_documento_id=tipo_documento
        ).values('id', 'estado', 'facturacion_electronica__estado_id', 'fecha')

        return {
            'facturas': facturas or [],
            'abiertos': [d for d in docs if d['estado'] == 4 and d['facturacion_electronica__estado_id'] != 4],
            'rechazadas': [d for d in docs if d['facturacion_electronica__estado_id'] == 3],
            'inconsistentes': [d for d in docs if d['facturacion_electronica__estado_id'] == 6],
            'sin_transmitir': [d for d in docs if d['facturacion_electronica__estado_id'] == 1],
            'errores_validar': [d for d in docs if d['facturacion_electronica__estado_id'] == 5],
        }