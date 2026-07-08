from apps.afiliados.services.afiliado_service import AfiliadoService
from apps.parametros.models.parametrizacion import Parametros
from apps.contabilidad.services.tipodocumento_service import TipoDocumentoService
from apps.parametros.services.parametrizacion_service import ParametrizacionService
from apps.common_db.db import execute_procedure
from django.db import transaction
from apps.contabilidad.models.cupon import Cupon
import pdb

class CuponService:

    @staticmethod
    def listar(params:dict, sin_generar=False):

        if sin_generar:
            # Filtrar los cupones que no se han generado en el mes y anio indicados
            aservice = AfiliadoService()
            queryset = aservice.afiliados_facturacion(params, sin_facturar=True)
        else:
            # Filtrar los cupones que se han generado en el mes y anio indicados
            mes = params.get('mes')
            anio = params.get('año')
            queryset = Cupon.objects.filter(mes=mes, anio__nombre=anio, estado=True)
            pass

        return queryset
    
    @staticmethod
    def parametros():
        tipo_fuente_cupones = Parametros.objects.get(parametro="tipo_fuente_cupones")
        parametros = Parametros.objects.filter(cupon=True).order_by("orden")
        tipos_documento = TipoDocumentoService.filtro({"id": tipo_fuente_cupones.valor})
        return parametros, tipos_documento
    
    @staticmethod
    def GuardarParametros(request_data, user=None):
        ParametrizacionService.GuardarParametros(request_data['parametros'], user)
        for item in request_data.get('tipos_documento', []):
            TipoDocumentoService.crear_o_actualizar(item, item.get('id'))

    @staticmethod
    def generar(request_data, user=None):
        
        sql = "select * from generar_cupon(array[%s], %s);"
        params = [request_data['afiliado_id'], user]

        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)
        
        if resultado is not None and len(resultado) > 0:
            return list(map(lambda x: {
                'id': x[0],
                'numero': x[1],
            }, resultado))
        return []

