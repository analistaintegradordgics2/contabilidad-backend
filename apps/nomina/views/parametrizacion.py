import pdb, json
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status

from datetime import datetime
from django.db import transaction

from django.db.models import Q

from apps.nomina.models.parametrizacion import BaseLiquidacionEmpleado, Periodo, NominaParametros
from apps.parametros.models.parametrizacion import Anio
from apps.nomina.serializers.parametrizacion import BaseLiquidacionEmpleadoSerializer, PeriodoSerializer, NominaParametrosSerializer
from apps.nomina.services.nomina_parametros_service import NominaParametrosService


class BaseLiquidacionEmpleadoViewSet(viewsets.ModelViewSet):

    queryset = BaseLiquidacionEmpleado.objects.all()
    serializer_class = BaseLiquidacionEmpleadoSerializer

    def list(self, request, *args, **kwargs):

        estado = request.GET.get("estado", "").lower() == "true"

        if estado == None :
            query = self.get_queryset()
        else :
            query = self.get_queryset().filter(estado=estado)
        
        data = self.serializer_class(query, many=True).data

        return Response(data, status=status.HTTP_200_OK)

class PeriodoViewSet(viewsets.ModelViewSet):

    queryset = Periodo.objects.all()
    serializer_class = PeriodoSerializer

    def list(self, request, *args, **kwargs):

        filtros = request.GET.get("filtros", None)
        query = []
        if filtros != None :
            filtros = json.loads(filtros)
            try :
                if filtros["forma_liquidacion"] == True :
                    forma_liquidacion = NominaParametros.objects.filter(parametro="forma_liquidacion").first()
                    if forma_liquidacion != None :
                        forma_liquidacion = forma_liquidacion.valor
                        if forma_liquidacion == "quincenal" :
                            query = Periodo.objects.filter(~Q(id=3))
                        else :
                            query = Periodo.objects.filter(id=3)
            except :
                query = Periodo.objects.filter(**filtros)
        else :
            query = self.get_queryset()
        data = PeriodoSerializer(query, many=True).data
        return Response(data, status=status.HTTP_200_OK)

class NominaParametrosViewSet(viewsets.ModelViewSet):

    queryset = NominaParametros.objects.all().order_by("orden")
    serializer_class = NominaParametrosSerializer

    def list(self, request, *args, **kwargs):

        filtros = request.GET.get("filtros", None)

        if filtros != None :
            query = NominaParametros.objects.filter(**json.loads(filtros))
        else :
            query = self.get_queryset()
        
        data = NominaParametrosSerializer(query, many=True).data

        # Para parametrizar el salario minimo y aux transporte para el año actual
        anio_actual = datetime.now().strftime("%Y")

        conf_anio = Anio.objects.filter(nombre=anio_actual).order_by("-id").first()

        if conf_anio != None :
            conf_anio = {
                "id": conf_anio.id,
                "anio": conf_anio.nombre,
                "salario_minimo": conf_anio.salario_minimo,
                "aux_transporte": conf_anio.aux_transporte,
                "actualizado": conf_anio.actualizado
            }
        
        return Response({
            "parametros": data,
            "anio": conf_anio
        }, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        NominaParametrosService.crear_o_actualizar(request.data)
        return Response("OK", status=status.HTTP_200_OK)