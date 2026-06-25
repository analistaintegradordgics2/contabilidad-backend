from rest_framework import viewsets
from apps.afiliados.serializers.causacion import ConceptoCausacionSerializer
from apps.afiliados.models.causacion import ConceptoCausacion

class AfiliadoCausacionViewSet(viewsets.ModelViewSet):
    queryset = ConceptoCausacion.objects.all()
    serializer_class = ConceptoCausacionSerializer
    pagination_class = None

    def perform_create(self, serializer):
        serializer.save(uc=self.request.user)

    def perform_update(self, serializer):
        serializer.save(um=self.request.user)