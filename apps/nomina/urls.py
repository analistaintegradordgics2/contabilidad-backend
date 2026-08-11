# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from apps.nomina.views.novedades import TipoNovedadViewSet, TipoValorNovedadViewSet, GrupoNominaViewSet, NovedadViewSet
from apps.nomina.views.parametrizacion import BaseLiquidacionEmpleadoViewSet, PeriodoViewSet, NominaParametrosViewSet
from apps.nomina.views.entidades import EntidadViewSet, TipoEntidadViewSet
from apps.nomina.views.contratos import CargoViewSet

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


urlpatterns = [
    path('', include(router.urls))
]
