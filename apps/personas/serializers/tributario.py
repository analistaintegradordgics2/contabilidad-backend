from rest_framework import serializers

from apps.personas.models.tributario import RegimenTributario, Contribuyente, Tributario
import pdb

class RegimenTributarioModelSerializer(serializers.ModelSerializer):
    """RegimenTributario model serializer."""

    class Meta:
        """Meta class."""
        model = RegimenTributario
        fields = ('id', 'nombre')

class ContribuyenteModelSerializer(serializers.ModelSerializer):
    class Meta:
        ordering = ['-id']
        model = Contribuyente
        fields = (
            "id",
            "nombre",
        )

class TributarioModelSerializer(serializers.ModelSerializer):
    class Meta:
        ordering = ['-id']
        model = Tributario
        fields = (
            "id",
            "nombre",
        )

