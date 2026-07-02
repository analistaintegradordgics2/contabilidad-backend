"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from apps.afiliados.views.afiliado import AfiliadoViewSet
from apps.afiliados.views.facturacion import AfiliadoCausacionViewSet

router = DefaultRouter()
router.register(r'afiliado', AfiliadoViewSet, basename='afiliado')
router.register(r'causacion', AfiliadoCausacionViewSet, basename='causacion')

urlpatterns = [
    path('', include(router.urls))
]
