from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from django.core.paginator import Paginator
from apps.contabilidad.models.documento import Documentos, Mov
from apps.contabilidad.serializers.documento import *
from apps.contabilidad.services.documento_service import *
from apps.contabilidad.services.documento_cierre_service import *
import pdb
from django.db.models import Q, Sum, F


class DocumentoViewSet(ModelViewSet):

    queryset = Documentos.objects.all().order_by('-id')
    serializer_class = DocumentoSerializer

    def create(self, request):
        try:

            documento = DocumentoService.crear(
                request.data,
                request.user.id
            )
            return Response(
                documento,
                status=status.HTTP_201_CREATED
            )

        except Exception as e:

            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=False, methods=['get'], url_path='buscar/(?P<id>[^/.]+)')
    def buscar(self, request, id= None):

        iddocumento = id

        documento = Documentos.objects.filter(
            id=iddocumento
        ).first()

        if not documento:
            return Response(
                {'error': 'Documento no encontrado'},
                status=404
            )

        return Response(
            DocumentoDetailSerializer(documento).data
        )

    @action(detail=True, methods=['get'])
    def auditoria(self, request, pk=None):

        auditorias = DocumentosBita.objects.filter(
            documentos_id=pk
        ).select_related(
            'usuario',
            'estado'
        ).order_by('id')

        serializer = DocumentoBitacoraSerializer(
            auditorias,
            many=True
        )

        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def filtro_documentos(self, request):

        qs = Documentos.objects.select_related(
            'personas',
            'tipo_documento'
        )
        
        search = request.GET.get('buscar')
        if search != "" and search != None:
            qs = qs.filter(
                (Q(personas__documento__icontains=search) | Q(personas__n_completo__icontains=search) | Q(numero__icontains=search) | Q(detalle__icontains=search)),
                fecha__range=[request.GET.get('fecha_inicio'), request.GET.get('fecha_fin')]
            )

        tipo_documento = request.GET.get('tipo_documento')

        if tipo_documento:
            qs = qs.filter(
                tipo_documento__fuentes=tipo_documento
            )

        tipo_busqueda = request.GET.get('tipobusqueda')

        if tipo_busqueda:
            qs = qs.filter( tipo_documento_id=tipo_busqueda)
            
        documento = request.GET.get('documento')

        if documento:
            qs = qs.filter(
                numero__icontains=documento
            )

        usuario = request.GET.get('usuario')

        if usuario:
            qs = qs.filter(
                uc_id=usuario
            )

        fecha_inicio = request.GET.get('fecha_inicio')

        if fecha_inicio:
            qs = qs.filter(
                fecha__gte=fecha_inicio
            )

        fecha_fin = request.GET.get('fecha_fin')

        if fecha_fin:
            qs = qs.filter(
                fecha__lte=fecha_fin
            )

        estados = request.GET.getlist('estado[]')
        if estados:
            qs = qs.filter(
                estado__in=estados
            )

        paginator = Paginator(qs.order_by("-id"), 10)
        page_number = 1
        page_obj = paginator.get_page(1)

        serializer = DocumentoListSerializer(
            page_obj,
            many=True
        )
        # pdb.set_trace()
        results = {
            'count': len(qs),
            'results': serializer.data
        }

        return Response(results, status=status.HTTP_200_OK)
    
    @action(methods=['patch'], detail=True, url_path='cerrar')
    def cerrar(self, request, pk=None):
        try:
            doc = DocumentoCierreService.cerrar(pk, request.user.id)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DocumentoDetailSerializer(doc).data)

    @action(methods=['patch'], detail=True, url_path='reabrir')
    def reabrir(self, request, pk=None):
        try:
            doc = DocumentoCierreService.reabrir(pk, request.user.id)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DocumentoDetailSerializer(doc).data)

    @action(methods=['patch'], detail=True, url_path='anular')
    def anular(self, request, pk=None):
        observacion = request.data.get('observacion')
        try:
            doc = DocumentoCierreService.anular(pk, request.user.id, observacion)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(DocumentoDetailSerializer(doc).data)