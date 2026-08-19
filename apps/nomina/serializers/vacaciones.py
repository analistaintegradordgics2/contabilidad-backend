from rest_framework import serializers
from apps.utils.util import NumeroA

from apps.nomina.models.vacaciones import Vacaciones

class VacacionesSerializer(serializers.ModelSerializer):

    data = serializers.SerializerMethodField('get_data', read_only=True)
    def get_data(self, obj):
        numero = NumeroA()
        return {
            "nombre": obj.contrato.persona.n_completo,
            "documento": obj.contrato.persona.documento,
            "cargo": obj.contrato.cargo.nombre,
            "dias": obj.dias,
            "dias_laborados": (obj.contrato_novedades.fecha_final - obj.contrato_novedades.fecha_inicial).days,
            "fecha_ingreso": obj.contrato.fecha_ingreso.strftime("%Y-%m-%d"),
            "fecha_vacaciones": {
                "fecha_ini": numero.format_fecha(obj.contrato_novedades.fecha_inicial, 1),
                "fecha_fin": numero.format_fecha(obj.contrato_novedades.fecha_final, 1),
                "fecha_reintegro": numero.format_fecha(obj.contrato_novedades.fecha_reintegro, 1),
            },
            "salud": {
                "dias": obj.dias,
                "total": int(obj.salud_total),
                "valor_porcentaje": obj.salud_valor_porcentaje,
            },
            "pension": {
                "dias": obj.dias,
                "total": int(obj.pension_total),
                "valor_porcentaje": obj.pension_valor_porcentaje,
            },
            "periodo_vacaciones": {
                "fecha_ini": obj.contrato_novedades.periodo_ini_vacaciones.strftime("%Y-%m-%d"),
                "fecha_fin": obj.contrato_novedades.periodo_fin_vacaciones.strftime("%Y-%m-%d"),
            },
            "tipo_contrato": obj.contrato.tipo_contrato.nombre,
            "sueldo": int(obj.sueldo),
            "valor_dia": int(obj.valor_dia),
            "subtotal": int(obj.subtotal),
            "total": int(obj.total),
        }

    class Meta:
        """Meta class."""
        model = Vacaciones
        fields = [
            "contrato",
            "contrato_novedades",
            "dias",
            "sueldo",
            "valor_dia",
            "subtotal",
            "salud_valor_porcentaje",
            "salud_total",
            "pension_valor_porcentaje",
            "pension_total",
            "total",
            "data",
        ]