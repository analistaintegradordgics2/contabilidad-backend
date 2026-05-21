# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from apps.contabilidad.views.concepto import ConceptosViewSet
from apps.contabilidad.views.cuenta import MayorViewSet
from apps.contabilidad.views.tipodocumento import TiposDocumentosViewSet


router = DefaultRouter()
router.register(r'concepto', ConceptosViewSet, basename='concepto')
router.register(r'cuenta', MayorViewSet, basename='cuenta')
router.register(r'tipodocumento', TiposDocumentosViewSet, basename='tipodocumento')

urlpatterns = [
    path('', include(router.urls))]