from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from django.db.models import Q

from apps.utils.ModelViewSetClass import ModelViewSetClass
from apps.personas.models.persona import Persona
from apps.personas.serializers.persona import PersonaModelSerializer

from .selectors import (
    select_all_personas,
    select_personas,
    select_email_personas,
    buscar_personas_avanzado,
    get_persona_by_id,
    get_personas_por_tipo,
    buscar_personas_table
)

from apps.personas.services.persona_service import PersonaService


class PersonaViewSet(ModelViewSetClass):

    queryset = Persona.objects.all().select_related(
        'ciudad_expedicion',
        'genero',
        'estado_civil'
    ).prefetch_related(
        'telefonos_personas',
        'direcciones_personas',
        'personatributario'
    )

    serializer_class = PersonaModelSerializer
    filter_backends = (SearchFilter, OrderingFilter)
    search_fields = ['n_completo', 'documento']


    # CREAR O ACTUALIZAR

    def create(self, request, *args, **kwargs):
        persona = PersonaService.crear_o_actualizar(request.data, request.user.id)

        return Response(
            PersonaModelSerializer(persona).data,
            status=status.HTTP_200_OK
        )

    @action(methods=['get'], detail=False, url_path='personaid/(?P<idpersona>[^/.]+)')
    def personaid(self, request, idpersona = None):
        query = Persona.objects.filter(pk=idpersona).first()
        serializer = PersonaModelSerializer(query, many=False)
        return Response(serializer.data, status=status.HTTP_200_OK)
    # SELECTS

    @action(methods=['get'], detail=False, url_path='select-all')
    def select_all(self, request):
        return Response(select_all_personas())


    @action(methods=['get'], detail=False, url_path='select')
    def select(self, request):
        search = request.GET.get('search')
        return Response(select_personas(search))


    @action(methods=['get'], detail=False, url_path='select-email')
    def select_email(self, request):
        search = request.GET.get('search')
        return Response(select_email_personas(search))

    # SELECT AVANZADO

    @action(methods=['post'], detail=False, url_path='select-avanzado')
    def select_avanzado(self, request):

        persona_id = request.data.get('id')
        search = request.data.get('search')

        # ID
        if persona_id:
            persona = get_persona_by_id(persona_id)

            return Response([{
                'value': persona.id,
                'label': f"{persona.documento} - {persona.n_completo}",
                'modelo': PersonaModelSerializer(persona).data
            }])

        # búsqueda
        queryset = buscar_personas_avanzado(search)

        return Response([
            {
                'value': item.id,
                'label': f"{item.documento} - {item.n_completo}",
                'modelo': PersonaModelSerializer(item).data
            }
            for item in queryset
        ])

    # PROVEEDORES

    @action(methods=['post'], detail=False, url_path='select-proveedores')
    def select_proveedores(self, request):

        persona_id = request.data.get('id')
        search = request.data.get('search')

        if persona_id:
            persona = get_persona_by_id(persona_id)

            return Response([{
                'value': persona.id,
                'label': f"{persona.documento} - {persona.n_completo}",
                'modelo': PersonaModelSerializer(persona).data
            }])

        queryset = buscar_personas_avanzado(search, tipo_persona=[9])

        return Response([
            {
                'value': item.id,
                'label': f"{item.documento} - {item.n_completo}",
                'modelo': PersonaModelSerializer(item).data
            }
            for item in queryset
        ])


    # POR TIPO PERSONA

    @action(detail=False, methods=['post'], url_path='por-tipo')
    def por_tipo_persona(self, request):

        tipos = request.data.get('tipos_personas', [])

        return Response(get_personas_por_tipo(tipos))
    
    @action(detail=False, methods=['get'], url_path='personanit')
    def personanit(self, request):
        search = request.GET.get('search', None)
        
        if search != None:
            persona = Persona.objects.filter(Q(documento=search) | Q(n_completo__icontains=search))[:5]
            # pdb.set_trace()
            if persona :
                return Response(PersonaModelSerializer(persona, many=True).data, status=status.HTTP_200_OK)
            else:
                return Response('documento disponible')
        else:
            return Response('dato invalido')
    
    @action(methods=['get'], detail=False, url_path='buscar')
    def buscar(self, request):

        search = request.GET.get('search', '')
        estado = int(request.GET.get('estado', 1))

        queryset = buscar_personas_table(
            search=search,
            estado=estado
        )

        page = self.paginate_queryset(queryset)

        if page is not None:
            serializer = PersonaModelSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = PersonaModelSerializer(queryset, many=True)
        return Response(serializer.data)