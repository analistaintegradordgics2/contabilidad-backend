from .views import LoginView, UserView
from rest_framework_simplejwt.views import TokenRefreshView

from django.urls import include, path
from apps.accounts.views import DominioView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),  
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    path('user/', UserView.as_view(), name='user'),
    path("dominio/", DominioView.as_view(), name="dominio")
]