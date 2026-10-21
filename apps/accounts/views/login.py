from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from rest_framework import status

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny

from apps.accounts.serializers.login import CustomTokenSerializer
from apps.parametros.models.parametrizacion import Parametros

from rest_framework.viewsets import ReadOnlyModelViewSet
from apps.accounts.serializers.login import RegistroIngresoSerializer
from apps.accounts.models import RegistroIngreso

from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAdminUser

class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer
    permission_classes = [AllowAny]

    def obtener_direccion_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        user = getattr(serializer, 'user', None)
        if user:
            RegistroIngreso.objects.create(
                usuario=user,
                direccion_ip=self.obtener_direccion_ip(request),
                agente_usuario=request.META.get('HTTP_USER_AGENT', '')[:1000],
            )

        return Response(serializer.validated_data, status=status.HTTP_200_OK)

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response({"detail": "Sesión cerrada correctamente."}, status=status.HTTP_200_OK)

class DominioView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        try :
            dominio = Parametros.objects.filter(parametro="dominio_empresa").first().valor
        except :
            dominio = "http://localhost:8080/"
        
        return Response(dominio, status=status.HTTP_200_OK)

class RegistrosIngresoViewSet(ReadOnlyModelViewSet):
    """Consulta de auditoría de accesos; no permite modificar los registros."""

    queryset = RegistroIngreso.objects.select_related('usuario').all()
    serializer_class = RegistroIngresoSerializer
    permission_classes = (IsAdminUser,)
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ('usuario__username', 'direccion_ip')
    ordering_fields = ('fecha_ingreso', 'direccion_ip', 'usuario__username')
    ordering = ('-fecha_ingreso',)

    def get_queryset(self):
        queryset = super().get_queryset()
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        if fecha_desde:
            queryset = queryset.filter(fecha_ingreso__date__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_ingreso__date__lte=fecha_hasta)

        return queryset
