from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

urlpatterns = [
   path('admin/', admin.site.urls),
    path('api/', include([
        path('', include('apps.accounts.urls')),
        path('public/', include(('apps.public.urls', 'public'), namespace='public')),
        path('personas/', include(('apps.personas.urls', 'personas'), namespace='personas')),
        path('parametros/', include(('apps.parametros.urls', 'parametros'), namespace='parametros')),
        path('contabilidad/', include(('apps.contabilidad.urls', 'contabilidad'), namespace='contabilidad'))
     
    ])),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
