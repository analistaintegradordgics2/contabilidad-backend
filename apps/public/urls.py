"""Users URLs."""

# Django
from django.urls import include, path

# Django REST Framework
from rest_framework.routers import DefaultRouter

# Views
from apps.public.views import DashboardViewSet, MenuDinamicoViewSet, GruposViewSet
from apps.public.apiviews import ApiViews

router = DefaultRouter()
router.register(r'dashboard', DashboardViewSet, basename='dashboard')
# router.register(r'archivos', ArchivoViewSet, basename='archivos')
router.register(r'menu', MenuDinamicoViewSet, basename='menu')
router.register(r'grupos', GruposViewSet, basename='grupos')
router.register(r'rest', ApiViews, basename='restful')

urlpatterns = [
    path('', include(router.urls)),
]
