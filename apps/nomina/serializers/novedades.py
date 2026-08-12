from rest_framework import serializers
from django.db.models import Q

from datetime import datetime

from apps.nomina.models.novedades import TipoNovedad, TipoValorNovedad, GrupoNomina, SubGrupoNomina, Novedad, NovedadesCentroCosto
from apps.nomina.models.parametrizacion import BaseLiquidacionNovedad, BaseLiquidacionEmpleado
from apps.contabilidad.models.parametros import CentroCostos
from apps.contabilidad.models.cuenta import Mayor

from apps.utils.history import getHistorymodel
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

class HistoryNovedadesSerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            {'db': 'nombre', 'label': 'Nombre'},
            {'db': 'valor', 'label': 'Valor'},
            {'db': 'estado', 'label': 'Estado'},
            {'db': 'grupo_nomina_id', 'label': 'grupo_nomina', 'nombre_relacion': 'nombre'},
            {'db': 'tipo_novedad_id', 'label': 'tipo_novedad', 'nombre_relacion': 'nombre'},
            {'db': 'tipo_valor_novedad_id', 'label': 'tipo_valor_novedad', 'nombre_relacion': 'nombre'},
            {'db': 'sub_grupo_nomina_id', 'label': 'sub_grupo_nomina', 'nombre_relacion': 'nombre'},
            {'db': 'entidad_id', 'label': 'entidad', 'nombre_relacion': 'nombre'},
            {'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        list_principal = getHistorymodel(obj, campos)

        campos_novedad_centro_costo = [
            {'db': 'centro_costos_id', 'label': 'centro_costo', 'nombre_relacion': 'nombre'},
            {'db': 'mayor_cta_credito_id', 'label': 'cta_credito', 'nombre_relacion': 'codigol'},
            {'db': 'mayor_cta_debito_id', 'label': 'cta_debito', 'nombre_relacion': 'codigol'},
            {'db': 'eliminado', 'label': 'Eliminado centro costo', 'identificar_registro': 'centro_costos', 'nombre_relacion': 'nombre'},
            {'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        obj_novedad_ccosto = NovedadesCentroCosto.objects.filter(novedades_id=obj.id)

        for item in obj_novedad_ccosto:
            list_hijos = getHistorymodel(item, campos_novedad_centro_costo)
            list_principal += list_hijos
        
        campos_base_liqui_novedades = [
            {'db': 'base_liquidacion_id', 'label': 'base_quidacion', 'nombre_relacion': 'nombre'},
            {'db': 'eliminado', 'label': 'Eliminado base liquidacion'},
            {'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        obj_base_liqui_novedades = BaseLiquidacionNovedad.objects.filter(novedades_id=obj.id)

        for item in obj_base_liqui_novedades :
            list_hijos = getHistorymodel(item, campos_base_liqui_novedades)
            list_principal += list_hijos
        
        list_principal = sorted(list_principal, key=lambda x: datetime.strptime(x['fecha_bitacora'],"%d/%m/%Y %H:%M" ), reverse=True)
        
        return list_principal
    
    class Meta:
        """Meta class."""
        model = Novedad
        fields = ("id", "history")

class NovedadBaseLiquidacionEmpleadoCreateSerializer(serializers.Serializer):
    base_liquidacion = serializers.PrimaryKeyRelatedField(
        queryset=BaseLiquidacionEmpleado.objects.all()
    )
    eliminado = serializers.BooleanField(default=False)


class NovedadBaseLiquidacionEmpresaCreateSerializer(serializers.Serializer):
    base_liquidacion = serializers.PrimaryKeyRelatedField(
        queryset=BaseLiquidacionEmpleado.objects.all()
    )
    eliminado = serializers.BooleanField(default=False)


class NovedadCentroCostoCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(
        required=False,
        allow_null=True
    )
    centro_costos = serializers.PrimaryKeyRelatedField(
        queryset=CentroCostos.objects.all()
    )
    mayor_cta_debito = serializers.PrimaryKeyRelatedField(
        queryset=Mayor.objects.all()
    )
    mayor_cta_credito = serializers.PrimaryKeyRelatedField(
        queryset=Mayor.objects.all()
    )
    eliminado = serializers.BooleanField(default=False)

class NovedadCreateSerializer(serializers.ModelSerializer):

    base_liquidacion_empleado = NovedadBaseLiquidacionEmpleadoCreateSerializer(
        many=True,
        write_only=True,
        required=False
    )

    base_liquidacion_empresa = NovedadBaseLiquidacionEmpresaCreateSerializer(
        many=True,
        write_only=True,
        required=False
    )

    centro_costos = NovedadCentroCostoCreateSerializer(
        many=True,
        write_only=True,
        required=False
    )

    class Meta:
        model = Novedad
        fields = (
            "nombre",
            "valor",
            "entidad",
            "grupo_nomina",
            "sub_grupo_nomina",
            "concepto",
            "tipo_novedad",
            "tipo_valor_novedad",
            "base_liquidacion_empleado",
            "base_liquidacion_empresa",
            "estado",
            "centro_costos",
            "automatica",
            "periodo_automatico",
        )