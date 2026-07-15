from apps.afiliados.models.afiliado import Afiliado
from apps.parametros.models.parametrizacion import Parametros
from apps.contabilidad.services.tipodocumento_service import TipoDocumentoService
from apps.parametros.services.parametrizacion_service import ParametrizacionService
from apps.common_db.db import execute_procedure
from django.db import transaction
from apps.afiliados.models.cupon import Cupon
from apps.parametros.services.empresa_service import EmpresaService
from apps.utils.render import Render
from apps.afiliados.serializers.cupon import CuponImprimirModelSerializer
import pdb

class CuponService:

    @staticmethod
    def listar(params:dict, sin_generar=False):

        if sin_generar:
            # Filtrar los cupones que no se han generado en el mes y anio indicados
            queryset = Afiliado.objects.filter(activo=True).exclude(cupon__mes=params.get('mes'), cupon__anio__nombre=params.get('año'))
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
    
    @staticmethod
    def imprimir(cupones_ids):

        empresa = EmpresaService.obtener_datos_empresa()

        cupones = Cupon.objects.filter(id__in=cupones_ids)
        serializer = CuponImprimirModelSerializer(cupones, many=True)

        nombre = "cupones"
        params = {
            'cupones': serializer.data,
            'empresa': empresa
        }

        return Render.render_pdfkit('pdf/afiliados/cupon.html', params, nombre)

