# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from apps.contabilidad.views.concepto import ConceptosViewSet
from apps.contabilidad.views.cuenta import MayorViewSet
from apps.contabilidad.views.pago import PagoViewSet
from apps.contabilidad.views.tipodocumento import TiposDocumentosViewSet
from apps.contabilidad.views.documento import DocumentoViewSet
from apps.contabilidad.views.consulta import ConsultasViewSet
from apps.contabilidad.views.parametros import ParametrosViewSet, CentroCostosViewSet
from apps.contabilidad.views.factura import EstadosFactViewSet, TransmisionFacturaViewSet
from apps.contabilidad.views.plantilla import PlantillaDocumentoViewSet
from apps.contabilidad.views.tributario import ReglaTributariaViewSet, VariableContableViewSet, ConceptoReglaTributariaViewSet


router = DefaultRouter()
router.register(r'concepto', ConceptosViewSet, basename='concepto')
router.register(r'cuenta', MayorViewSet, basename='cuenta')
router.register(r'bancos', PagoViewSet, basename='bancos')
router.register(r'tipodocumento', TiposDocumentosViewSet, basename='tipodocumento')
router.register(r'documentos', DocumentoViewSet, basename='documentos')
router.register(r'consultas', ConsultasViewSet, basename='consultas')
router.register(r'parametros', ParametrosViewSet, basename='parametros')
router.register(r'estadosfact', EstadosFactViewSet, basename='estadosfact')
router.register(r'transmisionfact', TransmisionFacturaViewSet, basename='transmisionfact')
router.register(r'plantilla', PlantillaDocumentoViewSet, basename='plantilla')
router.register(r'reglas-tributarias', ReglaTributariaViewSet, basename='reglastributarias')
router.register(r'variables-contables', VariableContableViewSet, basename='variablescontables')
router.register(r'concepto-reglas', ConceptoReglaTributariaViewSet, basename='conceptoreglas')
router.register(r'centrocostos', CentroCostosViewSet, basename='centrocostos')

urlpatterns = [
    path('', include(router.urls))]
