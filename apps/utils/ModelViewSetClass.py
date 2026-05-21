from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from django.http import JsonResponse
from rest_framework import status
from django.http import HttpResponse, JsonResponse
from apps.utils.dates import Fecha
import pdb


class ModelViewSetClass(viewsets.ModelViewSet):
    '''
    permite filtrar información de la tabla por varios campos
    '''

    @action(methods=['post'], detail=False, url_path='filterto')
    def filterTo(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(**request.data)
        serializer = self.get_serializer(queryset, many=True)

        if len(serializer.data) == 0:
            response = Response([])
            return response
        else:
            return Response(serializer.data)

    @action(methods=['post'], detail=False, url_path='filtertopag')
    def filterToPag(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset()).filter(**request.data)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        request.data['delete'] = Fecha.dateSystem()
        # set partial=True to update a data partially
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_404_NOT_FOUND)
    
    @action(methods=['get'], detail=False,url_path='search/(?P<value>[^/.]+)')
    def search(self, request, value=None):

        queryset = self.filter_queryset(self.get_queryset_filter(value))

        serializer = self.get_serializer(queryset, many=True)
        if len(serializer.data)==0:
            response = JsonResponse({'status': 'false', 'message': 'No existen datos.'})
            return response
        return Response(serializer.data)
