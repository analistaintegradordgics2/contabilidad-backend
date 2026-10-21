from apps.accounts.views.login import LoginView, LogoutView
from apps.accounts.views.usuario import UsuariosViewSet, UserView
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework.routers import DefaultRouter

from apps.accounts.views.login import RegistrosIngresoViewSet

from django.urls import include, path
from apps.accounts.views.login import DominioView

router = DefaultRouter()
router.register(r'usuarios', UsuariosViewSet, basename='usuarios')
router.register(r'registros-ingreso', RegistrosIngresoViewSet, basename='registros-ingreso')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', LoginView.as_view(), name='login'),  
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('user/', UserView.as_view(), name='user'),
    path("dominio/", DominioView.as_view(), name="dominio")
]