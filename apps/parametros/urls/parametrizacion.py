"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from apps.parametros.views.parametrizacion import *

router = DefaultRouter()
router.register(r'procesos', ProcesoViewSet, basename='proceso')
router.register(r'mes', ConfMesViewSet, basename='mes')
router.register(r'anio', ConfAnioViewSet, basename='anio')
router.register(r'parametros', ParametrosViewSet, basename='parametros')
router.register(r'parametroswhatsapp', ParametrosWhatsappViewSet, basename='parametroswhatsapp')
router.register(r'generador_consultas', GeneradorConsultasViewSet, basename='generador_consultas')
router.register(r'ciudad_empresa', CiudadEmpresaViewSet, basename='ciudad_empresa')
router.register(r'mes_anio', MesAnioViewSet, basename='mes_anio')
router.register(r'afiliado', AfiliadosViewSet, basename='afiliado')

urlpatterns = [
    path('', include(router.urls))
]
