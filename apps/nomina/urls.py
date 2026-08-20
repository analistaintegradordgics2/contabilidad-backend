# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from apps.nomina.views.novedades import TipoNovedadViewSet, TipoValorNovedadViewSet, GrupoNominaViewSet, NovedadViewSet
from apps.nomina.views.parametrizacion import BaseLiquidacionEmpleadoViewSet, PeriodoViewSet, NominaParametrosViewSet
from apps.nomina.views.entidades import EntidadViewSet, TipoEntidadViewSet
from apps.nomina.views.contratos import CargoViewSet, TipoContratoViewSet, TipoTrabajadorViewSet, NivelRiesgoViewSet, ContratoNominaViewSet
from apps.nomina.views.liquidacion import LiquidacionesViewSet
from apps.nomina.views.transmision import TransmisionViewSet

router = DefaultRouter()
router.register(r'tipo_novedad', TipoNovedadViewSet, basename='tipo_novedad'),
router.register(r'tipo_valor_novedad', TipoValorNovedadViewSet, basename='tipo_valor_novedad'),
router.register(r'base_liquidacion', BaseLiquidacionEmpleadoViewSet, basename='base_liquidacion'),
router.register(r'grupo_nomina', GrupoNominaViewSet, basename='grupo_nomina'),
router.register(r'entidades', EntidadViewSet, basename='entidades'),
router.register(r'tipo_entidades', TipoEntidadViewSet, basename='tipo_entidades'),
router.register(r'periodo', PeriodoViewSet, basename='periodo'),
router.register(r'cargos', CargoViewSet, basename='cargos'),
router.register(r'parametros', NominaParametrosViewSet, basename='parametros'),
router.register(r'novedades', NovedadViewSet, basename='novedades'),
router.register(r'tipo_contrato', TipoContratoViewSet, basename='tipo_contrato'),
router.register(r'tipo_trabajador', TipoTrabajadorViewSet, basename='tipo_trabajador'),
router.register(r'nivel_riesgo', NivelRiesgoViewSet, basename='nivel_riesgo'),
router.register(r'contrato', ContratoNominaViewSet, basename='contrato'),
router.register(r'liquidaciones', LiquidacionesViewSet, basename='liquidaciones'),
router.register(r'transmision', TransmisionViewSet, basename='transmision'),


urlpatterns = [
    path('', include(router.urls))
]
