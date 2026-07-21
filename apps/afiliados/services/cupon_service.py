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
import pdb, requests

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
        
        sql = "select * from generar_cupon(array[%s], %s, %s, %s);"
        params = [request_data['afiliado_id'], user, request_data['mes'], request_data['año']]

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

        observacion = Parametros.objects.get(parametro="observacion_cupones").valor

        nombre = "cupones"
        params = {
            'cupones': serializer.data,
            'empresa': empresa,
            'observacion': observacion
        }

        return Render.render_pdfkit('pdf/afiliados/cupon.html', params, nombre)
    
    @staticmethod
    def boton_pago(cupones_ids):

        url = "https://pagodgi.webdgi.site/api/restful/add/"

        payload = []

        for cupon_id in cupones_ids:
            cupon = Cupon.objects.get(id=cupon_id)
            cupon_payload = {
                "mes" : cupon.mes.numero,
                "anio" : cupon.anio.nombre,
                "descripcion": cupon.detalle_cupones.first().detalle if cupon.detalle_cupones.count() > 0 else "",
                "ref_1": cupon.numero,
                "ref_2": None,
                "usuario": 1, # TODO: Pendiente
                "valor_1": int(cupon.valor1),
                "fecha_1": cupon.fecha1.strftime("%Y-%m-%d"),
                "valor_2": int(cupon.valor2) if cupon.valor2 else 0,
                "fecha_2": cupon.fecha2.strftime("%Y-%m-%d") if cupon.fecha2 else None,
                "fecha_licencia_alquiler": cupon.afiliado.fecha_inicio.strftime("%Y-%m-%d") if cupon.afiliado.fecha_inicio else None,
                "fecha_licencia_cmcp": cupon.afiliado.fecha_inicio.strftime("%Y-%m-%d") if cupon.afiliado.fecha_inicio else None, # TODO: Pendiente
                "eliminar": False,
                "observacion": None,
                "detalle": list(map(lambda x: {
                    "concepto": x.concepto.id,
                    "detalle": x.detalle,
                    "valor": int(x.valor),
                    "sancion": False
                }, cupon.detalle_cupones.all()))
            }

            payload.append(cupon_payload)

        response = requests.post(url, json=payload)
        # pdb.set_trace()

        return response.json()