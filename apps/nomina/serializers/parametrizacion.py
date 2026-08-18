from rest_framework import serializers

from apps.nomina.models.parametrizacion import BaseLiquidacionEmpleado, Periodo, NominaParametros, BaseLiquidacionNovedad, TipoContrato, TipoTrabajador, NivelRiesgo

class BaseLiquidacionEmpleadoSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta class."""
        model = BaseLiquidacionEmpleado
        fields = ("id", "nombre", "tipo", "estado")

class PeriodoSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta class."""
        model = Periodo
        fields = ("id", "nombre", "dias", "estado")

class NominaParametrosSerializer(serializers.ModelSerializer):

    valor = serializers.SerializerMethodField('get_valor', read_only=True)
    def get_valor(self, obj):
        try :
            return int(obj.valor)
        except :
            if obj.valor != None :
                if obj.valor.lower() == "true" or obj.valor.lower() == "false" :
                    if obj.valor.lower() == "true" :
                        return True
                    else :
                        return False
                else :
                    try :
                        return float(obj.valor)
                    except :
                        return obj.valor
            else :
                return obj.valor

    class Meta:
        """Meta class."""
        model = NominaParametros
        fields = ("id", "parametro", "valor", "label", "tipo", "grupo", "orden", "comentario")

class BaseLiquidacionNovedadSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta class."""
        model = BaseLiquidacionNovedad
        fields = ("id", "base_liquidacion", "novedades", "eliminado")

class TipoContratoSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta class."""
        model = TipoContrato
        fields = ("id", "nombre", "estado")

class TipoTrabajadorSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta class."""
        model = TipoTrabajador
        fields = ("id", "nombre", "estado")

class NivelRiesgoSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta class."""
        model = NivelRiesgo
        fields = ("id", "nombre", "valor", "estado")

