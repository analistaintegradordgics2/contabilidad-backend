from datetime import timedelta
import json
import os
import pdb

from django.db import connection
from django.db.models import Count, Q
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import Group, Permission, User

from apps.public.models import Archivo, Menu, PermisosMenuAcciones
from apps.public.serializers import ArchivosSerializer, MenuDinamicoSerializer, PermisosMenuAccionesSerializer
from apps.public.services.grupo_service import GrupoService


class DashboardViewSet(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        hoy = timezone.now().date()
        limite_superior = hoy + timedelta(days=5)
        resoluciones = []

        return Response({
            "resoluciones": resoluciones
        }, status=status.HTTP_200_OK)


class MenuDinamicoViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.filter(menu_padre_id=None).order_by('orden')
    serializer_class = MenuDinamicoSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = MenuDinamicoSerializer(query, many=True).data
        return Response(data)

    @action(detail=False, methods=['GET'], url_path='listar')
    def listar(self, request, user_id=None):
        data = GrupoService.obtener_grupos_lista()
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='grupos/(?P<user_id>[^/.]+)')
    def Grupos(self, request, user_id=None):
        data = GrupoService.obtener_detalle_grupos(user_id=user_id)
        if data is None:
            return Response("Usuario no encontrado.", status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='acciones')
    def Acciones(self, request, *args, **kwargs):
        query = PermisosMenuAcciones.objects.all().order_by("menu_id")
        data = PermisosMenuAccionesSerializer(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='permisos_casos')
    def PermisosCasos(self, request, *args, **kwargs):
        permisos_casos = []
        for item in Permission.objects.filter(
            codename__in=[
                "view_ver_casos",
                "view_crear_casos",
                "view_finalizar_casos",
                "view_crear_seguimientos_casos",
                "view_todas_las_notificaciones",
                "view_editar_casos"
            ]
        ):
            nombre = None
            orden = None
            if item.codename == "view_ver_casos":
                nombre = "Ver Casos"
                orden = 1
            elif item.codename == "view_crear_casos":
                nombre = "Crear Casos"
                orden = 2
            elif item.codename == "view_finalizar_casos":
                nombre = "Finalizar Casos"
                orden = 3
            elif item.codename == "view_crear_seguimientos_casos":
                nombre = "Crear Seguimientos a Casos"
                orden = 4
            elif item.codename == "view_todas_las_notificaciones":
                nombre = "Ver todas las notificaciones"
                orden = 5
            elif item.codename == "view_editar_casos":
                nombre = "Editar Caso"
                orden = 6

            permisos_casos.append({
                "id": item.id,
                "nombre": nombre,
                "orden": orden,
                "select": False
            })

        return Response(permisos_casos, status=status.HTTP_200_OK)


class GruposViewSet(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        """Lista todos los grupos disponibles."""
        grupos = GrupoService.obtener_grupos_lista()
        return Response(grupos, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='detalle/(?P<user_id>[^/.]+)')
    def detalle(self, request, user_id=None):
        """
        Retorna todos los grupos con sus menus y acciones.
        Si user_id != '0', marca cuales grupos y acciones ya tiene asignados el usuario.
        """
        data = GrupoService.obtener_detalle_grupos(user_id=user_id)
        if data is None:
            return Response("Usuario no encontrado.", status=status.HTTP_404_NOT_FOUND)
        return Response(data, status=status.HTTP_200_OK)
