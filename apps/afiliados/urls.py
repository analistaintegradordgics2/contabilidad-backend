"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from apps.afiliados.views.afiliado import AfiliadoViewSet
from apps.afiliados.views.facturacion import AfiliadoCausacionViewSet
from apps.afiliados.views.cupon import CuponViewSet
from apps.afiliados.views.recaudo import RecaudoViewSet

router = DefaultRouter()
router.register(r'afiliado', AfiliadoViewSet, basename='afiliado')
router.register(r'causacion', AfiliadoCausacionViewSet, basename='causacion')
router.register(r'cupones', CuponViewSet, basename='cupones')
router.register(r'recaudos', RecaudoViewSet, basename='recaudos')

urlpatterns = [
    path('', include(router.urls))
]
