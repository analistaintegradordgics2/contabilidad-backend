from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
# from apps.utils.ModelViewSetClass import ModelViewSetClass
from django.db.models import Count
# from apps.utils.fechas import Fecha
# Create your views here.
from apps.public.models import Archivo, Menu, PermisosMenuAcciones
from apps.public.serializers import ArchivosSerializer, MenuDinamicoSerializer, PermisosMenuAccionesSerializer
import pdb, errno, os
from django.db import connection
from datetime import timedelta
from django.contrib.auth.models import User, Permission, Group
# from apps.contabilidad.models import TiposDocumentos
# from apps.utils.funciones import Funciones
import json

# Create your views here.
class DashboardViewSet(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        hoy = timezone.now().date()
        limite_superior = hoy + timedelta(days=5)
        resoluciones = []
        # for item in TiposDocumentos.objects.filter(Q(fecha_fin_resolucion__range=(hoy, limite_superior)) | Q(fecha_fin_resolucion__lt=hoy), estado__iexact='activo').order_by('-fecha_fin_resolucion'):
        #     resoluciones.append({
        #         "id": item.id,
        #         "tipo": item.tipo,
        #         "prefijo": item.prefijo,
        #         "nombre": item.nombre,
        #         "rango": f"{item.numeracion_inicial} de {item.numeracion_final}",
        #         "fecha_fin_resolucion": item.fecha_fin_resolucion,
        #     })

        return Response({
            "resoluciones": resoluciones
        }, status=status.HTTP_200_OK)
    
# class ArchivoViewSet(ModelViewSetClass):
#     queryset = Archivo.objects.all()
#     serializer_class = ArchivosSerializer

#     def destroy(self, request, pk=None, **kwargs):
#         request.data['delete'] = Fecha.dateSystem()
#         # set partial=True to update a data partially
#         object = self.get_object()
#         serializer = self.get_serializer(object, data=request.data, partial=True)
#         if not serializer.is_valid():
#             return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
#         serializer.save()
#         if object.url_s3 != None:
#             resp = Funciones.delete_file_s3(object.src)
#             if resp['status'] != 200:
#                 return Response(resp['msg'], status=resp['status']) 
#         return Response(serializer.data)
    
#     @action(detail=False, methods=['post'], url_path='eliminar_archivos_multiple')
#     def eliminar_archivos_multiple(self, request, user_id=None):

#         data = request.data

#         Archivo.objects.filter(id__in=data).update(delete= Fecha.dateSystem())

#         return Response({'msg': 'Archivos eliminados correctamente', 'status':200})
    
#     @action(detail=False, methods=['post'], url_path='upload_s3')
#     def upload_s3(self, request):
#         data = request.data
#         #request.data['data'] -> {"object_id": row.id, "content_type_id" : 46, "ruta_destino" : ruta_destino}
#         obj_data = json.loads(data['data'])
#         obj_data['user_id'] = request.user.id
#         files = request.FILES
#         archivos = []
#         for k, v in files.items():
#             resp = Funciones.upload_s3("archivo", obj_data['ruta_destino'], v, v.name, obj_data)

#             if resp['status'] != 200:
#                 return Response({'msg': 'Error al subir el archivo', 'status': 400}, status=resp['status']) 

#             archivos.append(resp['archivo'])

#         serializer = ArchivosSerializer(archivos, many=True).data
#         return Response({'msg': 'Archivos subidos correctamente', 'status':200, 'archivos': serializer})



class MenuDinamicoViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.filter(menu_padre_id=None).order_by('orden')
    serializer_class = MenuDinamicoSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = MenuDinamicoSerializer(query, many=True).data
        return Response(data)
    
    @action(detail=False, methods=['GET'], url_path='listar')
    def listar(self, request, user_id=None):
        data = []

        for item in Group.objects.all().order_by("id") :
            data.append({
                "id": item.id,
                "nombre": item.name
            })
        
        return Response(data, status=status.HTTP_200_OK)

    # Nelson Lugo
    @action(detail=False, methods=['GET'], url_path='grupos/(?P<user_id>[^/.]+)')
    def Grupos(self, request, user_id=None):
        data = []
        resultado = None
        user_group = []
        menu_acciones = []

        # Nelson Lugo - Si el id es cero, es para el crear usuario
        if user_id != "0" :
            # Se consulta los grupos que tiene el usuario a editar
            try:
                db = connection.cursor()
                sql= """
                    select 
                        json_agg(json_build_object(
                            'id', aug.id,
                            'user', aug.user_id,
                            'group', aug.group_id
                        ))
                    from auth_user_groups aug where aug.user_id={};
                    """.format(user_id)
                db.execute(sql)
            except: 
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
            finally:
                resultado = db.fetchall()
                db.close()
                try:
                    user_group = resultado[0][0]
                except:
                    pass
        
        # Se consulta los menus y sus acciones de la tabla nueva public_permisos_menu_acciones
        try:
            db = connection.cursor()
            sql= """
                select 
                    ppma.grupo_id as group_id,
                    ppma.permiso_menu as permiso,
                    ppma.menu_id as menu_id,
                    (select pm.titulo from public_menu pm where pm.id=ppma.menu_id) as menu,
                    (select json_agg(json_build_object(
                        'id', ppma2.id,
                        'accion', ppma2.accion,
                        'permiso', (select ap.id from auth_permission ap where ap.codename = ppma2.permiso_accion),
                        'select', false
                    )) as acciones from public_permisos_menu_acciones ppma2 where ppma2.permiso_menu=ppma.permiso_menu)
                from public_permisos_menu_acciones ppma group by ppma.grupo_id, ppma.menu_id, ppma.permiso_menu order by ppma.menu_id;
                """
            db.execute(sql)
        except: 
            return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
        finally:
            resultado = db.fetchall()
            db.close()
            try:
                resultado = list(resultado)
            except:
                pass
        
        # Se consulta para saber el menu a que grupo pertenece
        if resultado != None :
            for ma in resultado :
                obj = list(ma)
                permisos_menus_padres = []
                menu = Menu.objects.get(pk=obj[2])
                menu_padre = 0
                if menu != None :
                    permiso = Permission.objects.filter(codename=menu.permiso).first()
                    if permiso != None :
                        permisos_menus_padres.append(permiso.id)
                while menu_padre != None :
                    menu_padre = Menu.objects.filter(id=menu.menu_padre_id).first()
                    if menu_padre != None :
                        menu = menu_padre
                        permiso = Permission.objects.filter(codename=menu_padre.permiso).first()
                        if permiso != None :
                            permisos_menus_padres.append(permiso.id)

                permiso = Permission.objects.filter(codename=obj[1]).first()
                
                menu_acciones.append({
                    "group_id": obj[0],
                    "permiso_menu_id": permiso.id,
                    "permiso_menu_padre": permisos_menus_padres,
                    "menu": obj[3],
                    "acciones": obj[4],
                    "select": False
                })

        
        # Se valida si el usuario a editar partenece al grupo
        for i,item in enumerate(Group.objects.all().order_by("id")) :
            data.append({
                "id": item.id,
                "nombre": item.name,
                "select": False
            })
            if user_group != None :
                for ug in user_group :
                    if ug['group'] == item.id :
                        data[i]["select"] = True

            array_menus = []
            for ma in menu_acciones :
                if ma["group_id"] == data[i]["id"] :
                    array_menus.append(ma)

            data[i]["menus"] = array_menus
        
        # Nelson Lugo - Si el id es cero, es para el crear usuario
        if user_id != "0" :
            # Se consulta para saber cuales permisos de acciones ya tiene el usuario a editar
            try:
                db = connection.cursor()
                sql= """
                    select json_agg(json_build_object(
                        'id', auup.id,
                        'user', auup.user_id ,
                        'permiso', auup.permission_id 
                    )) 
                    from auth_user_user_permissions auup 
                    where auup.user_id = {};
                    """.format(user_id)
                db.execute(sql)
            except: 
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
            finally:
                resultado = db.fetchall()
                db.close()
                try:
                    if resultado[0][0] != None :
                        obj = list(resultado[0][0])
                        for item in data :
                            for menus in item['menus'] :
                                for acciones in menus['acciones'] :
                                    for auup in obj :
                                        if acciones['permiso'] == auup['permiso'] :
                                            acciones['select'] = True
                                            menus['select'] = True
                except:
                    pass

        return Response(data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='acciones')
    def Acciones(self, request, *args, **kwargs):
        query = PermisosMenuAcciones.objects.all().order_by("menu_id")
        data = PermisosMenuAccionesSerializer(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['GET'], url_path='permisos_casos')
    def PermisosCasos(self, request, *args, **kwargs):
        permisos_casos = []
        for item in Permission.objects.filter(codename__in=["view_ver_casos", "view_crear_casos", "view_finalizar_casos", "view_crear_seguimientos_casos", "view_todas_las_notificaciones", "view_editar_casos"]) :
            nombre = None
            orden = None
            if item.codename == "view_ver_casos" :
                nombre = "Ver Casos"
                orden = 1
            elif item.codename == "view_crear_casos" :
                nombre = "Crear Casos"
                orden = 2
            elif item.codename == "view_finalizar_casos" :
                nombre = "Finalizar Casos"
                orden = 3
            elif item.codename == "view_crear_seguimientos_casos" :
                nombre = "Crear Seguimientos a Casos"
                orden = 4
            elif item.codename == "view_todas_las_notificaciones" :
                nombre = "Ver todas las notificaciones"
                orden = 5
            elif item.codename == "view_editar_casos" :
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
        grupos = []
        for item in Group.objects.all().order_by("id") :
            grupos.append({
                "id": item.id,
                "nombre": item.name
            })
        return Response(grupos, status=status.HTTP_200_OK)
