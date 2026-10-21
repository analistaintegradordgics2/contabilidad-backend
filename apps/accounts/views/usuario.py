from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework import status

# from django.contrib.auth.models import User
from apps.accounts.serializers.usuario import UsuariosSerializer, UserFindSerializer
from apps.accounts.services.usuario_service import UsuarioService
from apps.utils.ModelViewSetClass import ModelViewSetClass

from apps.personas.models.persona import Persona
from apps.personas.serializers.persona import PersonaModelSerializer

from django.contrib.auth import get_user_model

from django.shortcuts import get_object_or_404

User = get_user_model()

class UsuariosViewSet(ModelViewSetClass):
    queryset = User.objects.all()
    serializer_class = UsuariosSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['username', 'first_name']

    def list(self, request, *args, **kwargs):
        users = User.objects.filter(is_staff=False)
        return Response(UsuariosSerializer(users, many=True).data)

    @action(methods=['GET'], detail=False, url_path='all_users')
    def all_users(self, request) :
        usuarios = []

        for item in User.objects.all() :
            usuarios.append({
                "id": item.id,
                "username": item.username
            })

        return Response(usuarios, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):

        instance = self.get_queryset()
        user = User.objects.get(pk=kwargs['pk'])
        item = get_object_or_404(instance, id=kwargs['pk'])

        # persona = Persona.objects.get(usuario=user.id)
        persona = Persona.objects.filter(usuario=user.id).first()

        return Response({
            'persona': PersonaModelSerializer(persona).data,
            'usuario': UsuariosSerializer(item).data,
        }, status=status.HTTP_200_OK)

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserFindSerializer(request.user)
        return Response(serializer.data)

    def post(self, request, *args, **kwargs):
        try:
            user, persona = UsuarioService.crear_o_actualizar(
                request.data, request.user
            )
        except Exception as e:
            return Response(
                {"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST
            )

        return Response({
            "user_id": user.id,
            "persona_id": persona.id
        }, status=status.HTTP_201_CREATED)