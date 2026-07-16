from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.afiliados.services.recaudo_service import RecaudoService

class RecaudoViewSet(viewsets.ModelViewSet):
    
    def list(self, request, *args, **kwargs):
        try:
            return Response(RecaudoService.listar(), status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': f"Error inesperado: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)