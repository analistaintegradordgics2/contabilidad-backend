from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from apps.accounts.serializers import UserFindSerializer



class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserFindSerializer(request.user)
        return Response(serializer.data)

class CustomTokenSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        # Obtener usuario
        user = self.user

        # Agregar info extra
        data['user'] = {
            "id": user.id,
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }

        data['status'] = 200

        return data


class LoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer

class DominioView(APIView):
    permission_classes = ()

    def get(self, request):
        try :
            dominio = Parametros.objects.filter(parametro="dominio_empresa").first().valor
        except :
            dominio = "http://localhost:8080/"
        
        return Response(dominio, status=status.HTTP_200_OK)
