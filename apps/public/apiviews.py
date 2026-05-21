from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
# from apps.contabilidad.models import Documentos, Mov
import json
# import requests
import pdb

class ApiViews(viewsets.ModelViewSet):
    permission_classes = ()

    @action(detail=False, methods=['GET'], url_path='noti_orbis')
    def get_noti_orbis(self, request):
        response = requests.get("http://159.89.17.247/api/noticia_aleatoria_orbis_web/")
        return Response(response.json(), status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET','POST'], url_path='cheques')
    def get_cheques(self, request):
        if request.method == 'GET':
            fecha_inicio = request.GET.get("fecha_inicio", None)
            fecha_fin = request.GET.get("fecha_fin", None)
            numero_documento = request.GET.get("numero_documento", None)
            filtros = {}
            if numero_documento != None :
                filtros["numero"] = numero_documento
            elif fecha_inicio != None and fecha_fin != None :
                filtros["tipo_documentos__fuentes_id"] = 2
                filtros["fpago"] = 2
                filtros["fecha__range"] = [fecha_inicio, fecha_fin]
            else :
                return Response("Rango de fecha invalido.", status=status.HTTP_400_BAD_REQUEST)
            documentos = []
            for item in Documentos.objects.filter(**filtros) :
                movimiento = []
                for item2 in Mov.objects.filter(documentos_id=item.id) :
                    movimiento.append({
                        "codigo": item2.mayor.codigol,
                        "nombre": item2.personas.n_completo,
                        "concepto": item2.concepto.codigo,
                        "detalle": item2.concepto.detalle,
                        "valor_db": item2.valor_db,
                        "valor_cr": item2.valor_cr
                    })
                documentos.append({
                    "id": item.id,
                    "fecha": item.fecha,
                    "cheque_num": item.ncheque,
                    "titular": item.personas.n_completo,
                    "beneficiario": item.beneficiario.n_completo if item.beneficiario_id != None else item.personas.n_completo,
                    "valor": item.total,
                    "impreso": item.impresion_cheque if item.impresion_cheque != None else False,
                    "fecha_impresion": item.fecha_impresion_cheque,
                    "documento": item.numero,
                    "detalle": item.detalle,
                    "movimiento": movimiento
                })
            return Response(documentos, status=status.HTTP_200_OK)
        else :
            try :
                for data in request.data :
                    docu = Documentos.objects.get(pk=data["id"])
                    docu.impresion_cheque = True
                    docu.fecha_impresion_cheque = data["fecha_impresion"]
                    docu.save()
                return Response({"response": "Documentos actualizados correctamente.", "status": 200}, status=status.HTTP_200_OK)
            except Exception as inst:
                return Response({"response": inst, "status": 400 }, status=status.HTTP_400_BAD_REQUEST)