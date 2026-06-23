"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from apps.personas.views.persona.viewsets import *
from apps.personas.views.contacto import *
from apps.personas.views.tributario import *
from apps.personas.views.clasificacion import *


router = DefaultRouter()
router.register(r'personas', PersonaViewSet, basename='personas')
router.register(r'tipo_persona', TipoPersonaViewSet, basename='tipo_persona')
# router.register(r'persona_tipo_persona', PersonaTipoPersonaViewSet, basename='persona_tipo_persona')
router.register(r'tipo_documento', TipoDocumentoViewSet, basename='tipo_documento')
router.register(r'generos', GenerosViewSet, basename='generos')
router.register(r'estado_civil', EstadoCivilViewSet, basename='estado_civil')
router.register(r'regimen', RegimenTributarioViewSet, basename='regimen')
router.register(r'tipo_contacto', TipoContactoViewSet, basename='tipo_contacto')
router.register(r'contribuyente', ContribuyenteViewSet, basename='contribuyentes')
router.register(r'tributario', TributarioViewSet, basename='tributarios')
router.register(r'telefono', TelefonoViewSet, basename='telefono')
router.register(r'usuarios', UsuariosViewSet, basename='usuarios')

urlpatterns = [
    path('', include(router.urls))
]
