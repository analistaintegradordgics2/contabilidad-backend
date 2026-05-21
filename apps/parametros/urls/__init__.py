from django.urls import path, include

urlpatterns = [
    path('ubicacion/', include('apps.parametros.urls.ubicacion')),
    path('parametrizacion/', include('apps.parametros.urls.parametrizacion')),
]