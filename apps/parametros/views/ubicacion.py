import pdb

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from apps.parametros.models.ubicacion import Ciudad, Zona, Barrio, TipoVia
from apps.parametros.serializers.ubicacion import CiudadModelSerializer, ZonaModelSerializer, BarrioModelSerializer, TipoViaModelSerializer
from rest_framework.filters import SearchFilter, OrderingFilter
from apps.utils.ModelViewSetClass import ModelViewSetClass
from apps.utils.views import Views
from django.db.models import Q
from apps.utils.render import Render
from apps.utils.querySQL import querySQL
from django.db.models import Func, Value
from django.db.models.functions import Lower


class CiudadViewSet(viewsets.ModelViewSet):
    queryset = Ciudad.objects.all().order_by('nombre')
    serializer_class = CiudadModelSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['nombre']

    @action(methods=['get'], detail=False, url_path='select')
    def select(self, request):
        return Response(Views.select(
            request=request,
            filtro={'nombre__icontains': 'search'},
            model=self.get_queryset(),
            values=['id', 'nombre'],
            limit=10
        ))

    @action(methods=['get'], detail=True, url_path='select-zonas')
    def select_zona(self, request, pk):
        return Response(Views.select(
            request=request,
            filtro={'nombre__icontains': 'search'},
            model=Zona.objects.filter(ciudades_id=pk).order_by('created'),
            values=['id', 'nombre'],
            limit=10
        ))

    @action(methods=['POST'], detail=False, url_path='select_city')
    def select_city(self, request):

        query = Barrio.objects.filter(Q(ciudad_id=request.data['id']) | Q(id=436) ).order_by('created')
        data = self.get_serializer(query, many=True).data
        return Response(data)

    @action(methods=['post'], detail=False, url_path='selectnew')
    def selectnew(self, request):
        queryset = Ciudad.objects.all()
        search = request.data.get('search',None)
        ciudad_id = request.data.get('id', None)
        if ciudad_id:
            queryset = queryset.filter(id = ciudad_id)
        if search:
            queryset = queryset.filter(
                nombre__icontains=search
            )
        serializer = CiudadModelSerializer(queryset, many=True)
        return Response(serializer.data)


class ZonaViewSet(ModelViewSetClass):
    queryset = Zona.objects.all().order_by('nombre')
    serializer_class = ZonaModelSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['nombre']

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = self.get_serializer(query, many=True).data
        return Response(data)
    
    def create(self, request):
        data = request.data
        
        if data["id"] == None :
            zona = Zona()
            validar_zona = Zona.objects.annotate(
                nombre_trimmed=Func(Lower('nombre'), function='TRIM')
            ).filter(nombre_trimmed=data["nombre"].strip().lower(), ciudades_id=data["ciudad"]).first()
            if validar_zona != None:
                return Response({
                    "status": "400",
                    "msg": "La zona ya existe",
                }, status=status.HTTP_200_OK)
        else :
            zona = Zona.objects.get(pk=data["id"])
        
        zona.nombre = data["nombre"].strip()
        zona.ciudades_id = data["ciudad"]
        zona.save()

        data = self.get_serializer(zona).data

        return Response({
            "status": "200",
            "data": data,
        }, status=status.HTTP_200_OK)

    @action(methods=['get'], detail=True, url_path='select-barrios')
    def select_zona(self, request, pk):
        return Response(Views.select(
            request=request,
            filtro={'nombre__icontains': 'search'},
            model=Barrio.objects.filter(zonas_id=pk).order_by('created'),
            values=['id', 'nombre'],
            limit=10
        ))

    @action(methods=['get'], detail=False, url_path='ciudad/(?P<ciudad_id>[^/.]+)')
    def ZonaCiudad(self, request, ciudad_id=None):
        zonas = Zona.objects.filter(ciudades_id=ciudad_id).exclude(nombre__iexact='sin definir').order_by('nombre')
        sin_definir = Zona.objects.filter(ciudades_id=ciudad_id, nombre__iexact='sin definir')
        zonas = list(zonas) + list(sin_definir)
        data = self.get_serializer(zonas, many=True).data
        return Response(data)

    @action(methods=['POST'], detail=False, url_path='exportar')
    def ExportarZonas(self, request):
        data = request.data
        nombre = "Listado de zonas"
        query = []
        if data["ciudad_id"] == None:
            query = self.get_queryset()
        else :
            query = Zona.objects.filter(ciudades_id=data["ciudad_id"]).order_by('nombre')
            ciudad = Ciudad.objects.get(pk=data["ciudad_id"])
            nombre = f"Listado de zonas - Ciudad: {ciudad.nombre}"
        
        model = []
        for item in query :
            model.append({
                "nombre": item.nombre,
                "ciudad": item.ciudades.nombre if item.ciudades != None else None
            })
        
        return Render.export_excel(model, nombre)

class BarrioViewSet(ModelViewSetClass):
    queryset = Barrio.objects.all()
    serializer_class = BarrioModelSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['nombre']

    def list(self, request, *args, **kwargs):
        result = querySQL.consulta_barrios()
        return Response(result)

    def create(self, request):
        data = request.data

        if data["id"] == None :
            barrio = Barrio()
            validar_barrio = Barrio.objects.annotate(
                nombre_trimmed=Func(Lower('nombre'), function='TRIM')
            ).filter(nombre_trimmed=data["nombre"].strip().lower(), ciudad_id=data["ciudad"]).first()
            if validar_barrio != None:
                return Response({
                    "status": "400",
                    "msg": "El barrio ya existe",
                }, status=status.HTTP_200_OK)
        else :
            barrio = Barrio.objects.get(pk=data["id"])
        
        barrio.nombre = data["nombre"].strip()
        barrio.ciudad_id = data["ciudad"]
        barrio.save()

        data = self.get_serializer(barrio).data

        return Response({
            "status": "200",
            "data": data,
        }, status=status.HTTP_200_OK)

    @action(methods=['GET'], detail=False, url_path='ciudad/(?P<ciudad_id>[^/.]+)')
    def BarrioCiudad(self, request, ciudad_id=None):
        barrios = Barrio.objects.filter(ciudad_id=ciudad_id).exclude(nombre__iexact='sin definir').order_by('nombre')
        sin_definir = Barrio.objects.filter(nombre__iexact='sin definir')
        barrios = list(barrios) + list(sin_definir)
        data = self.get_serializer(barrios, many=True).data
        return Response(data)

    @action(methods=['POST'], detail=False, url_path='exportar')
    def ExportarBarrios(self, request):
        data = request.data
        nombre = "Listado de barrios"
        if data["ciudad_id"] == None:
            result = querySQL.consulta_barrios()
        else :
            ciudad = Ciudad.objects.get(pk=data["ciudad_id"])
            result = querySQL.consulta_barrios(data["ciudad_id"])
            nombre = f"Listado de barrios - Ciudad: {ciudad.nombre}"
        
        model = []
        for item in result :
            model.append({
                "nombre": item["nombre"],
                "ciudad": item["ciudad"],
                "zona": item["zonas"],
            })
        
        return Render.export_excel(model, nombre)
    
    @action(methods=['post'], detail=False, url_path='selectnew')
    def selectnew(self, request):
        queryset = Barrio.objects.all()
        search = request.data.get('search',None)
        barrio_id = request.data.get('id', None)
        if barrio_id:
            queryset = queryset.filter(id = barrio_id)
        if search:
            queryset = queryset.filter(
                nombre__icontains=search
            )
        serializer = BarrioModelSerializer(queryset, many=True)
        return Response(serializer.data)

class TipoViaViewSet(viewsets.ModelViewSet):
    queryset = TipoVia.objects.all().order_by('nombre')
    serializer_class = TipoViaModelSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['nombre']

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = TipoViaModelSerializer(query, many=True).data
        return Response(data)