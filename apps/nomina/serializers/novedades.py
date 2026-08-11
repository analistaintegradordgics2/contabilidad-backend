from rest_framework import serializers
from django.db.models import Q

from apps.nomina.models.novedades import TipoNovedad, TipoValorNovedad, GrupoNomina, SubGrupoNomina, Novedad, NovedadesCentroCosto
from apps.nomina.models.parametrizacion import BaseLiquidacionNovedad

from apps.nomina.serializers.parametrizacion import BaseLiquidacionNovedadSerializer


class TipoNovedadSerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta class."""
        model = TipoNovedad
        fields = ("id", "nombre", "estado")

class TipoValorNovedadSerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta class."""
        model = TipoValorNovedad
        fields = ("id", "nombre", "valor", "estado")

class SubGrupoNominaSerializer(serializers.ModelSerializer):
    
    class Meta:
        """Meta class."""
        model = SubGrupoNomina
        fields = ("id", "nombre", "codigo", "estado", "grupo_nomina")

class GrupoNominaSerializer(serializers.ModelSerializer):
    
    sub_grupo_nomina = serializers.SerializerMethodField('get_sub_grupo_nomina', read_only=True)
    def get_sub_grupo_nomina(self, obj):
        try :
            return SubGrupoNominaSerializer(SubGrupoNomina.objects.filter(grupo_nomina_id=obj.id), many=True).data
        except :
            return []

    class Meta:
        """Meta class."""
        model = GrupoNomina
        fields = ("id", "nombre", "estado", "sub_grupo_nomina")

class NovedadSerializer(serializers.ModelSerializer):

    base_liquidacion_empleado = serializers.SerializerMethodField('get_base_liquidacion_empleado', read_only=True)
    def get_base_liquidacion_empleado(self, obj):
        try :
            return BaseLiquidacionNovedadSerializer(BaseLiquidacionNovedad.objects.filter(novedades_id=obj.id, base_liquidacion__tipo=1), many=True).data
        except :
            return []
    
    base_liquidacion_empresa = serializers.SerializerMethodField('get_base_liquidacion_empresa', read_only=True)
    def get_base_liquidacion_empresa(self, obj):
        try :
            return BaseLiquidacionNovedadSerializer(BaseLiquidacionNovedad.objects.filter(novedades_id=obj.id, base_liquidacion__tipo=2), many=True).data
        except :
            return []
    
    centro_costos = serializers.SerializerMethodField('get_centro_costos', read_only=True)
    def get_centro_costos(self, obj):
        model = []
        try :
            for item in NovedadesCentroCosto.objects.filter(novedades_id=obj.id) :
                model.append({
                    "id": item.id,
                    "centro_costos": item.centro_costos_id,
                    "entidades_centro_costos": item.entidades_centro_costos_id,
                    "mayor_cta_credito": item.mayor_cta_credito_id,
                    "mayor_cta_debito": item.mayor_cta_debito_id,
                    "novedades": item.novedades_id,
                    "eliminado": item.eliminado
                })
        except :
            pass

        return model
    
    foraneas = serializers.SerializerMethodField('get_foraneas', read_only=True)
    def get_foraneas(self, obj):
        try :
            filtros = self.context["filtros"]
            novedadccosto = NovedadesCentroCosto.objects.filter(Q(centro_costos_id=filtros["centro_costos"]) | Q(entidades_centro_costos__centro_costos_id=filtros["centro_costos"]), novedades_id=obj.id).first()
            
            centro_costos = None
            mayor_cta_debito = None
            mayor_cta_credito = None

            if novedadccosto.centro_costos_id != None :
                centro_costos = "{} - {}".format(novedadccosto.centro_costos.codigo, novedadccosto.centro_costos.nombre)
            elif novedadccosto.entidades_centro_costos_id != None :
                centro_costos = "{} - {}".format(novedadccosto.entidades_centro_costos.centro_costos.codigo, novedadccosto.entidades_centro_costos.centro_costos.nombre)
            else :
                pass
            
            if novedadccosto.mayor_cta_debito_id != None :
                mayor_cta_debito = "{} - {}".format(novedadccosto.mayor_cta_debito.codigol, novedadccosto.mayor_cta_debito.nombrel)
            elif novedadccosto.entidades_centro_costos_id != None :
                mayor_cta_debito = "{} - {}".format(novedadccosto.entidades_centro_costos.mayor_cta_debito.codigol, novedadccosto.entidades_centro_costos.mayor_cta_debito.nombrel)
            else :
                pass
            
            if novedadccosto.mayor_cta_credito_id != None :
                mayor_cta_credito = "{} - {}".format(novedadccosto.mayor_cta_credito.codigol, novedadccosto.mayor_cta_credito.nombrel)
            elif novedadccosto.entidades_centro_costos_id != None :
                mayor_cta_credito = "{} - {}".format(novedadccosto.entidades_centro_costos.mayor_cta_credito.codigol, novedadccosto.entidades_centro_costos.mayor_cta_credito.nombrel)
            else :
                pass

            return {
                "centro_costo": centro_costos,
                "mayor_cta_debito": mayor_cta_debito,
                "mayor_cta_credito": mayor_cta_credito
            }
        except :
            return {
                "centro_costo": None,
                "mayor_cta_debito": None,
                "mayor_cta_credito": None
            }
    
    tipo_novedad_nombre = serializers.SerializerMethodField('get_tipo_novedad_nombre', read_only=True)
    def get_tipo_novedad_nombre(self, obj):
        try :
            return obj.tipo_novedad.nombre
        except :
            return None
    
    tipo_valor_novedad_nombre = serializers.SerializerMethodField('get_tipo_valor_novedad_nombre', read_only=True)
    def get_tipo_valor_novedad_nombre(self, obj):
        try :
            return obj.tipo_valor_novedad.nombre
        except :
            return None

    class Meta:
        """Meta class."""
        model = Novedad
        fields = ("id","nombre","valor","estado","grupo_nomina","tipo_novedad","tipo_valor_novedad","sub_grupo_nomina", "concepto", "entidad","uc","um", "tipo_novedad_nombre","tipo_valor_novedad_nombre","base_liquidacion_empleado", "base_liquidacion_empresa", "centro_costos", "foraneas", "automatica", "periodo_automatico")