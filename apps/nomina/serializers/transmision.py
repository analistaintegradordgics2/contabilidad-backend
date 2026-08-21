from rest_framework import serializers
from apps.nomina.models.transmision import NominaElectronica, NominaElectronicaValores

class NominaElectronicaValoresSerializer(serializers.ModelSerializer):

    class Meta:
        model = NominaElectronicaValores
        exclude = [
            "nomina_electronica",
        ]


class NominaElectronicaSerializer(serializers.ModelSerializer):

    valores = NominaElectronicaValoresSerializer(
        source="nomina_electronica_valores"
    )

    class Meta:
        model = NominaElectronica
        fields = [
            "id",
            "contrato",
            "fecha_ini_liquidacion",
            "fecha_fin_liquidacion",
            "mes",
            "anio",
            "dias_laborados",
            "tipo_nomina",
            "numero",
            "prefijo",
            "estado",
            "respuesta",
            "data_funcionalidad",
            "valores",
        ]

    def create(self, validated_data):
        valores_data = validated_data.pop("nomina_electronica_valores")

        nomina_electronica = NominaElectronica.objects.create(
            **validated_data
        )

        NominaElectronicaValores.objects.create(
            nomina_electronica=nomina_electronica,
            **valores_data
        )

        return nomina_electronica

    def update(self, instance, validated_data):
        valores_data = validated_data.pop(
            "nomina_electronica_valores",
            None
        )

        instance = super().update(instance, validated_data)

        if valores_data is not None:
            NominaElectronicaValores.objects.update_or_create(
                nomina_electronica=instance,
                defaults=valores_data
            )

        return instance

class NominaElectronicaListSerializer(serializers.ModelSerializer):

    data_contrato = serializers.SerializerMethodField(
        'get_data_contrato',
        read_only=True
    )

    def get_data_contrato(self, obj):
        from apps.nomina.serializers.contratos import ContratosFuncionalidadSerializer
        return ContratosFuncionalidadSerializer(obj.contrato).data

    select = serializers.SerializerMethodField(
        'get_select',
        read_only=True
    )

    def get_select(self, obj):
        return False

    sueldo = serializers.SerializerMethodField()
    sueldo_trabajado = serializers.SerializerMethodField()
    auxilio_transporte = serializers.SerializerMethodField()
    viaticos_salarriales = serializers.SerializerMethodField()
    viaticos_nosalariales = serializers.SerializerMethodField()
    otros_devengados = serializers.SerializerMethodField()
    total_devengados = serializers.SerializerMethodField()
    salud = serializers.SerializerMethodField()
    pension = serializers.SerializerMethodField()
    fondo = serializers.SerializerMethodField()
    arl = serializers.SerializerMethodField()
    otros_deducidos = serializers.SerializerMethodField()
    total_deducido = serializers.SerializerMethodField()
    total = serializers.SerializerMethodField()

    def get_valores(self, obj):
        return getattr(obj, 'nomina_electronica_valores', None)

    def get_sueldo(self, obj):
        valores = self.get_valores(obj)
        return valores.sueldo if valores else 0

    def get_sueldo_trabajado(self, obj):
        valores = self.get_valores(obj)
        return valores.sueldo_trabajado if valores else 0

    def get_auxilio_transporte(self, obj):
        valores = self.get_valores(obj)
        return valores.auxilio_transporte if valores else 0

    def get_viaticos_salarriales(self, obj):
        valores = self.get_valores(obj)
        return valores.viaticos_salarriales if valores else 0

    def get_viaticos_nosalariales(self, obj):
        valores = self.get_valores(obj)
        return valores.viaticos_nosalariales if valores else 0

    def get_otros_devengados(self, obj):
        valores = self.get_valores(obj)
        return valores.otros_devengados if valores else 0

    def get_total_devengados(self, obj):
        valores = self.get_valores(obj)
        return valores.total_devengados if valores else 0

    def get_salud(self, obj):
        valores = self.get_valores(obj)
        return valores.salud if valores else 0

    def get_pension(self, obj):
        valores = self.get_valores(obj)
        return valores.pension if valores else 0

    def get_fondo(self, obj):
        valores = self.get_valores(obj)
        return valores.fondo if valores else 0

    def get_arl(self, obj):
        valores = self.get_valores(obj)
        return valores.arl if valores else 0

    def get_otros_deducidos(self, obj):
        valores = self.get_valores(obj)
        return valores.otros_deducidos if valores else 0

    def get_total_deducido(self, obj):
        valores = self.get_valores(obj)
        return valores.total_deducido if valores else 0

    def get_total(self, obj):
        valores = self.get_valores(obj)
        return valores.total if valores else 0

    class Meta:
        model = NominaElectronica
        fields = [
            "id",
            "contrato",
            "fecha_ini_liquidacion",
            "fecha_fin_liquidacion",
            "mes",
            "anio",
            "dias_laborados",
            "tipo_nomina",
            "numero",
            "prefijo",
            "sueldo",
            "sueldo_trabajado",
            "auxilio_transporte",
            "viaticos_salarriales",
            "viaticos_nosalariales",
            "otros_devengados",
            "total_devengados",
            "salud",
            "pension",
            "fondo",
            "arl",
            "otros_deducidos",
            "total_deducido",
            "total",
            "estado",
            "respuesta",
            "data_funcionalidad",
            "data_contrato",
            "select"
        ]