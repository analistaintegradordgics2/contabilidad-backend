
from rest_framework.routers import DefaultRouter
from apps.parametros.views.ubicacion import CiudadViewSet, ZonaViewSet, BarrioViewSet, TipoViaViewSet

router = DefaultRouter()
router.register(r'ciudades', CiudadViewSet)
router.register(r'zonas', ZonaViewSet)
router.register(r'barrios', BarrioViewSet)
router.register(r'tipovias', TipoViaViewSet)

urlpatterns = router.urls