import json

from rest_framework import serializers

from django.conf import settings
from django.shortcuts import get_object_or_404
from django.db.models import Value, F, CharField
from django.db.models.functions import Concat

from apps.utils.history import getHistorymodel

from apps.nomina.models.contratos import Cargo, ContratoNomina, DatosAportes, DatosEmergencia, DatosPago, ComposicionFamiliar, ContratoNominaNovedades, ContratoNovedadesPeriodos
from apps.nomina.models.parametrizacion import NivelRiesgo, NominaParametros, Periodo
from apps.contabilidad.models.pago import Banco, TipoCuenta, FormaPagoElectro, MedioPagoElectro
from apps.nomina.models.entidades import Entidad
from apps.public.models import Archivo

class CargoModelSerializer(serializers.ModelSerializer):
    
    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            {'db': 'nombre', 'label': 'Nombre'},
            {'db': 'estado', 'label': 'Estado'},
            {'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        list_principal = getHistorymodel(obj, campos)
        
        return list_principal

    class Meta:
        """Meta class."""
        model = Cargo
        fields = ("id", "nombre", "estado", "uc", "um", "history")

class DatosPagoCreateSerializer(serializers.Serializer):
    banco = serializers.PrimaryKeyRelatedField(queryset=Banco.objects.all())
    tipo_cuenta = serializers.PrimaryKeyRelatedField(queryset=TipoCuenta.objects.all())
    numero_cuenta = serializers.CharField(max_length=30)
    forma_pago = serializers.PrimaryKeyRelatedField(queryset=FormaPagoElectro.objects.all())
    medio_pago = serializers.PrimaryKeyRelatedField(queryset=MedioPagoElectro.objects.all())


class DatosAportesCreateSerializer(serializers.Serializer):
    entidad_salud = serializers.PrimaryKeyRelatedField(queryset=Entidad.objects.all())
    porcentaje_salud = serializers.DecimalField(max_digits=12, decimal_places=2)
    entidad_pension = serializers.PrimaryKeyRelatedField(queryset=Entidad.objects.all(), required=False, allow_null=True)
    porcentaje_pension = serializers.DecimalField(max_digits=12, decimal_places=2, required=False, allow_null=True)
    caja_compensacion = serializers.PrimaryKeyRelatedField(queryset=Entidad.objects.all(), required=False, allow_null=True)
    arl = serializers.PrimaryKeyRelatedField(queryset=Entidad.objects.all())
    porcentaje_arl = serializers.DecimalField(max_digits=12, decimal_places=3)
    nivel_riesgo = serializers.PrimaryKeyRelatedField(queryset=NivelRiesgo.objects.all())

class DatosEmergenciaCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    nombre = serializers.CharField(max_length=150)
    celular = serializers.CharField(max_length=20)
    parentesco = serializers.CharField(max_length=80, required=False, allow_null=True)
    eliminado = serializers.BooleanField(default=False)

class ComposicionFamiliarCreateSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False, allow_null=True)
    nombre = serializers.CharField(max_length=150)
    edad = serializers.IntegerField(required=False, allow_null=True)
    parentesco = serializers.CharField(max_length=80, required=False, allow_null=True)
    eliminado = serializers.BooleanField(default=False)

class ContratoNominaCreateSerializer(serializers.ModelSerializer):
    data_persona = serializers.DictField(write_only=True)
    datos_pago = DatosPagoCreateSerializer(write_only=True)
    datos_aportes = DatosAportesCreateSerializer(write_only=True)
    datos_emergencia = DatosEmergenciaCreateSerializer(many=True, write_only=True, required=False)
    composicion_familiar = ComposicionFamiliarCreateSerializer(many=True, write_only=True, required=False)

    class Meta:
        model = ContratoNomina
        fields = (
            "data_persona",
            "fecha_ingreso",
            "cargo",
            "centro_costo",
            "jefe",
            "sueldo",
            "tipo_contrato",
            "numero_meses",
            "fecha_vencimiento",
            "tipo_trabajador",
            "subtipo_trabajador",
            "fecha_retiro",
            "auxilio_transporte",
            "alto_riesgo_pension",
            "salario_integral",
            "salario_promedio",
            "salario_minimo",
            "estado",
            "medio_auxilio_transporte",
            "contrato_medio_tiempo",
            "datos_pago",
            "datos_aportes",
            "datos_emergencia",
            "composicion_familiar",
        )

class ContratoNominaArchivoSerializer(serializers.Serializer):
    src = serializers.FileField()

    def validate(self, validated_data):
        validated_data['name'] = validated_data['src'].name
        self.context['archivo'] = validated_data
        return validated_data

    def save(self, **kwargs):
        contrato = get_object_or_404(ContratoNomina, pk=kwargs['contrato_id'])
        t1 = Archivo(content_object=contrato, uc=kwargs['uc'], **self.context['archivo'])
        t1.save()
        return contrato.archivos.all()

    class Meta:
        """Meta class."""
        fields = ('name', 'src')

class ContratoNominaListSerializer(serializers.ModelSerializer):
    
    persona = serializers.SerializerMethodField('get_persona', read_only=True)
    def get_persona(self, obj):
        return {
            "documento": obj.persona.documento if obj.persona != None else None,
            "n_completo": obj.persona.n_completo if obj.persona != None else None,
        }

    foraneas = serializers.SerializerMethodField('get_foraneas', read_only=True)
    def get_foraneas(self, obj):

        return {
            "centro_costos": "{} - {}".format(obj.centro_costo.codigo, obj.centro_costo.nombre),
        }
    
    class Meta:
        """Meta class."""
        model = ContratoNomina
        fields = (
            "id",
            "fecha_ingreso",
            "persona",
            "foraneas",
            "estado",
            "centro_costo_id",
        )

class DatosEmergenciaSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosEmergencia
        fields = '__all__'

class ComposicionFamiliarSerializer(serializers.ModelSerializer):
    class Meta:
        model = ComposicionFamiliar
        fields = '__all__'

class DatosPagoSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosPago
        fields = '__all__'

class DatosAporteSerializer(serializers.ModelSerializer):
    class Meta:
        model = DatosAportes
        fields = '__all__'

class ContratoNovedadesPeriodosSerializer(serializers.ModelSerializer):

    class Meta:
        """Meta class."""
        model = ContratoNovedadesPeriodos
        fields = ("id", "valor", "mes", "anio", "fecha_ini", "fecha_fin", "contrato_novedades", "periodo", "contrato", "vacaciones")

class ContratoNominaNovedadesSerializer(serializers.ModelSerializer):

    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            { 'db': 'descripcion', 'label': 'descripcion' },
            { 'db': 'fecha_inicial', 'label': 'fecha_inicial' },
            { 'db': 'fecha_final', 'label': 'fecha_final' },
            { 'db': 'valor', 'label': 'valor' },
            { 'db': 'novedad_id', 'label': 'Novedad', 'nombre_relacion':'nombre' },
            { 'db': 'eliminado', 'label': 'Novedad Eliminada' },
            { 'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username' } # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        list_principal = getHistorymodel(obj, campos)

        return list_principal
    
    tipo_valor_novedad = serializers.SerializerMethodField('get_tipo_valor_novedad', read_only=True)
    def get_tipo_valor_novedad(self, obj):
        try :
            return obj.centro_costos_novedades.novedades.tipo_valor_novedad_id
        except :
            return None
    
    es_ausentismo = serializers.SerializerMethodField('get_es_ausentismo', read_only=True)
    def get_es_ausentismo(self, obj):
        try:
            es_ausen = False
            ausentismos = NominaParametros.objects.filter(parametro="ausentismo").first()

            if ausentismos != None :
                for item in json.loads(ausentismos.valor) :
                    if obj.novedad_id == item :
                        es_ausen = True
            
            return es_ausen
        except:
            return False

    novedades_periodo = serializers.SerializerMethodField('get_novedades_periodo', read_only=True)
    def get_novedades_periodo(self, obj):
        nove_per = ContratoNovedadesPeriodos.objects.filter(contrato_novedades_id=obj.id)
        return ContratoNovedadesPeriodosSerializer(nove_per, many=True).data
        
    foraneas = serializers.SerializerMethodField('get_foraneas', read_only=True)
    def get_foraneas(self, obj):
        from apps.utils.util import NumeroA
        numero = NumeroA()
        return {
            "fecha_inicial": numero.format_fecha(obj.fecha_inicial, 1),
            "fecha_final": numero.format_fecha(obj.fecha_final, 1),
            "fecha_reintegro": numero.format_fecha(obj.fecha_reintegro, 1) if obj.fecha_reintegro != None else None,
            "dias_laborados": (obj.periodo_fin_vacaciones - obj.periodo_ini_vacaciones).days if obj.vacaciones == True else None,
            "automatica": obj.novedad.automatica,
            "periodo_automatico": obj.novedad.periodo_automatico_id if obj.novedad.periodo_automatico_id != None else None,
        }

    id = serializers.IntegerField(
        required=False,
        allow_null=True
    )

    class Meta:
        """Meta class."""
        model = ContratoNominaNovedades
        fields = (
            "id",
            "created",
            "descripcion",
            "fecha_inicial",
            "fecha_final",
            "valor",
            "contrato",
            "uc",
            "um",
            "history",
            "eliminado",
            "novedad",
            "tipo_valor_novedad",
            "porcentaje_liquidacion",
            "es_ausentismo",
            "periodo_fin_vacaciones",
            "periodo_ini_vacaciones",
            "fecha_reintegro",
            "vacaciones",
            "vacaciones_liquidadas",
            "novedades_periodo",
            "foraneas"
        )
        read_only_fields = (
            "centro_costos_novedades",
        )


class ContratoNominaSerializer(serializers.ModelSerializer):

    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            { 'db': 'fecha_ingreso', 'label': 'fecha_ingreso' },
            { 'db': 'jefe', 'label': 'jefe' },
            { 'db': 'sueldo', 'label': 'sueldo' },
            { 'db': 'numero_meses', 'label': 'numero_meses' },
            { 'db': 'fecha_vencimiento', 'label': 'fecha_vencimiento' },
            { 'db': 'subtipo_trabajador', 'label': 'subtipo_trabajador' },
            { 'db': 'fecha_retiro', 'label': 'fecha_retiro' },
            { 'db': 'auxilio_transporte', 'label': 'auxilio_transporte' },
            { 'db': 'alto_riesgo_pension', 'label': 'alto_riesgo_pension' },
            { 'db': 'salario_integral', 'label': 'salario_integral' },
            { 'db': 'salario_promedio', 'label': 'salario_promedio' },
            { 'db': 'salario_minimo', 'label': 'salario_minimo' },
            { 'db': 'estado', 'label': 'estado' },
            { 'db': 'medio_auxilio_transporte', 'label': 'medio_auxilio_transporte' },
            { 'db': 'contrato_medio_tiempo', 'label': 'contrato_medio_tiempo' },
            { 'db': 'cargo_id', 'label': 'cargo', 'nombre_relacion': 'nombre' },
            { 'db': 'centro_costo_id', 'label': 'centro_costo', 'nombre_relacion': 'nombre' },
            { 'db': 'tipo_contrato_id', 'label': 'tipo_contrato', 'nombre_relacion': 'nombre' },
            { 'db': 'tipo_trabajador_id', 'label': 'tipo_trabajador', 'nombre_relacion': 'nombre' },
            { 'db': 'persona_id', 'label': 'persona', 'nombre_relacion': 'n_completo' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        list_principal = getHistorymodel(obj, campos)

        # DatosPago
        campos_datos_pago = [
            { 'db': 'numero_cuenta', 'label': 'numero_cuenta' },
            { 'db': 'banco_id', 'label': 'banco', 'nombre_relacion': 'nombre' },
            { 'db': 'tipo_cuenta_id', 'label': 'tipo_cuenta', 'nombre_relacion': 'nombre' },
            { 'db': 'forma_pago_id', 'label': 'forma_pago', 'nombre_relacion': 'nombre' },
            { 'db': 'medio_pago_id', 'label': 'medio_pago', 'nombre_relacion': 'nombre' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        obj_datos_pago = DatosPago.objects.filter(contrato_id=obj.id).first()
        if obj_datos_pago:
            list_principal += getHistorymodel(obj_datos_pago, campos_datos_pago)

        # DatosAportes
        campos_datos_aportes = [
            { 'db': 'porcentaje_salud', 'label': 'porcentaje_salud' },
            { 'db': 'porcentaje_pension', 'label': 'porcentaje_pension' },
            { 'db': 'porcentaje_arl', 'label': 'porcentaje_arl' },
            { 'db': 'entidad_salud_id', 'label': 'entidad_salud', 'nombre_relacion': 'nombre' },
            { 'db': 'entidad_pension_id', 'label': 'entidad_pension', 'nombre_relacion': 'nombre' },
            { 'db': 'caja_compensacion_id', 'label': 'caja_compensacion', 'nombre_relacion': 'nombre' },
            { 'db': 'arl_id', 'label': 'arl', 'nombre_relacion': 'nombre' },
            { 'db': 'nivel_riesgo_id', 'label': 'nivel_riesgo', 'nombre_relacion': 'nombre' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        obj_datos_aportes = DatosAportes.objects.filter(contrato_id=obj.id).first()
        if obj_datos_aportes:
            list_principal += getHistorymodel(obj_datos_aportes, campos_datos_aportes)

        # DatosEmergencia
        campos_datos_emergencia = [
            { 'db': 'nombre', 'label': 'nombre' },
            { 'db': 'celular', 'label': 'celular' },
            { 'db': 'parentesco', 'label': 'parentesco' },
            { 'db': 'eliminado', 'label': 'eliminado dato de emergencia' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        for item in DatosEmergencia.objects.filter(contrato_id=obj.id):
            list_principal += getHistorymodel(item, campos_datos_emergencia)

        # ComposicionFamiliar
        campos_composicion_familiar = [
            { 'db': 'nombre', 'label': 'nombre' },
            { 'db': 'edad', 'label': 'edad' },
            { 'db': 'parentesco', 'label': 'parentesco' },
            { 'db': 'eliminado', 'label': 'eliminado composicion familiar' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        for item in ComposicionFamiliar.objects.filter(contrato_id=obj.id):
            list_principal += getHistorymodel(item, campos_composicion_familiar)

        return list_principal

    foraneas = serializers.SerializerMethodField('get_foraneas', read_only=True)
    def get_foraneas(self, obj):

        return {
            "centro_costos": "{} - {}".format(obj.centro_costo.codigo, obj.centro_costo.nombre),
            "tipo_contrato": obj.tipo_contrato.nombre if obj.tipo_contrato_id != None else None,
            "fecha_ingreso": obj.fecha_ingreso.strftime("%Y-%m-%d"),
            "cargo": obj.cargo.nombre if obj.cargo_id != None else None,
        }
    
    datos_emergencia = serializers.SerializerMethodField('get_datos_emergencia', read_only=True)
    def get_datos_emergencia(self, obj):
        return DatosEmergenciaSerializer(DatosEmergencia.objects.filter(contrato_id=obj.id), many=True).data
    
    composicion_familiar = serializers.SerializerMethodField('get_composicion_familiar', read_only=True)
    def get_composicion_familiar(self, obj):
        return ComposicionFamiliarSerializer(ComposicionFamiliar.objects.filter(contrato_id=obj.id), many=True).data

    datos_pago = serializers.SerializerMethodField('get_datos_pago', read_only=True)
    def get_datos_pago(self, obj):
        return DatosPagoSerializer(obj.datos_pago_contrato_nomina).data

    datos_aportes = serializers.SerializerMethodField('get_datos_aportes', read_only=True)
    def get_datos_aportes(self, obj):
        return DatosAporteSerializer(obj.datos_aportes_contrato_nomina).data

    data_persona = serializers.SerializerMethodField('get_data_persona', read_only=True)
    def get_data_persona(self, obj):
        from apps.personas.serializers.persona import PersonaModelSerializer
        return PersonaModelSerializer(obj.persona).data
    
    archivos = serializers.SerializerMethodField('get_archivo', read_only=True)
    def get_archivo(self, obj):
        return list(
            obj.archivos.filter(delete=None).values(
                "id",
                "name",
                "tipo",
                "src",
                tsrc=Concat(
                    Value(settings.MEDIA_URL),
                    F('src'),
                    output_field=CharField()
                )
            )
        )   
    
    foto_empleado = serializers.SerializerMethodField('get_foto_empleado', read_only=True)
    def get_foto_empleado(self, obj):
        try:
            archivo = obj.personas.archivos.filter(delete=None, tipo="NOMINA").values("content_type_id", "id", "name", "object_id", "tipo" , "src", url=Concat(Value(settings.MEDIA_URL), F('src'))).first()
            if archivo != None :
                return archivo
            else :
                return {
                    "id": None,
                    "url": None
                }
        except:
            return {
                "id": None,
                "url": None
            }
    
    novedades = serializers.SerializerMethodField('get_novedades', read_only=True)
    def get_novedades(self, obj):
        try :
            return ContratoNominaNovedadesSerializer(ContratoNominaNovedades.objects.filter(contrato_id=obj.id), many=True).data
        except :
            return []
    
    valor_dia = serializers.SerializerMethodField('get_valor_dia', read_only=True)
    def get_valor_dia(self, obj):
        import math
        return math.ceil(float(obj.sueldo) / 30)

    class Meta:
        """Meta class."""
        model = ContratoNomina
        fields = (
            "id",
            "created",
            "fecha_ingreso",
            "jefe",
            "sueldo",
            "numero_meses",
            "fecha_vencimiento",
            "subtipo_trabajador",
            "fecha_retiro",
            "auxilio_transporte",
            "alto_riesgo_pension",
            "salario_integral",
            "salario_promedio",
            "salario_minimo",
            "estado",
            "cargo",
            "centro_costo",
            "tipo_contrato",
            "tipo_trabajador",
            "uc",
            "um",
            "foto_empleado",
            "history",
            "foraneas",
            "datos_emergencia",
            "composicion_familiar",
            "data_persona",
            "archivos",
            "novedades",
            "valor_dia",
            "medio_auxilio_transporte",
            "contrato_medio_tiempo",
            "datos_pago",
            "datos_aportes",
        )

class ContratoNominaNovedadesListCreateSerializer(serializers.Serializer):
    novedades = ContratoNominaNovedadesSerializer(many=True, write_only=True)

class ContratoNovedadesPeriodosCreateSerializer(serializers.ModelSerializer):

    periodo = serializers.PrimaryKeyRelatedField(
        queryset=Periodo.objects.all()
    )

    contrato = serializers.PrimaryKeyRelatedField(
        queryset=ContratoNomina.objects.all()
    )

    contrato_novedades = serializers.PrimaryKeyRelatedField(
        queryset=ContratoNominaNovedades.objects.all()
    )

    class Meta:
        model = ContratoNovedadesPeriodos
        fields = (
            "id",
            "valor",
            "mes",
            "anio",
            "fecha_ini",
            "fecha_fin",
            "contrato_novedades",
            "periodo",
            "contrato",
            "vacaciones",
        )

class ContratoNominaHistorySerializer(serializers.ModelSerializer):
    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            { 'db': 'fecha_ingreso', 'label': 'fecha_ingreso' },
            { 'db': 'jefe', 'label': 'jefe' },
            { 'db': 'sueldo', 'label': 'sueldo' },
            { 'db': 'numero_meses', 'label': 'numero_meses' },
            { 'db': 'fecha_vencimiento', 'label': 'fecha_vencimiento' },
            { 'db': 'subtipo_trabajador', 'label': 'subtipo_trabajador' },
            { 'db': 'fecha_retiro', 'label': 'fecha_retiro' },
            { 'db': 'auxilio_transporte', 'label': 'auxilio_transporte' },
            { 'db': 'alto_riesgo_pension', 'label': 'alto_riesgo_pension' },
            { 'db': 'salario_integral', 'label': 'salario_integral' },
            { 'db': 'salario_promedio', 'label': 'salario_promedio' },
            { 'db': 'salario_minimo', 'label': 'salario_minimo' },
            { 'db': 'estado', 'label': 'estado' },
            { 'db': 'medio_auxilio_transporte', 'label': 'medio_auxilio_transporte' },
            { 'db': 'contrato_medio_tiempo', 'label': 'contrato_medio_tiempo' },
            { 'db': 'cargo_id', 'label': 'cargo', 'nombre_relacion': 'nombre' },
            { 'db': 'centro_costo_id', 'label': 'centro_costo', 'nombre_relacion': 'nombre' },
            { 'db': 'tipo_contrato_id', 'label': 'tipo_contrato', 'nombre_relacion': 'nombre' },
            { 'db': 'tipo_trabajador_id', 'label': 'tipo_trabajador', 'nombre_relacion': 'nombre' },
            { 'db': 'persona_id', 'label': 'persona', 'nombre_relacion': 'n_completo' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        list_principal = getHistorymodel(obj, campos)

        # DatosPago
        campos_datos_pago = [
            { 'db': 'numero_cuenta', 'label': 'numero_cuenta' },
            { 'db': 'banco_id', 'label': 'banco', 'nombre_relacion': 'nombre' },
            { 'db': 'tipo_cuenta_id', 'label': 'tipo_cuenta', 'nombre_relacion': 'nombre' },
            { 'db': 'forma_pago_id', 'label': 'forma_pago', 'nombre_relacion': 'nombre' },
            { 'db': 'medio_pago_id', 'label': 'medio_pago', 'nombre_relacion': 'nombre' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        obj_datos_pago = DatosPago.objects.filter(contrato_id=obj.id).first()
        if obj_datos_pago:
            list_principal += getHistorymodel(obj_datos_pago, campos_datos_pago)

        # DatosAportes
        campos_datos_aportes = [
            { 'db': 'porcentaje_salud', 'label': 'porcentaje_salud' },
            { 'db': 'porcentaje_pension', 'label': 'porcentaje_pension' },
            { 'db': 'porcentaje_arl', 'label': 'porcentaje_arl' },
            { 'db': 'entidad_salud_id', 'label': 'entidad_salud', 'nombre_relacion': 'nombre' },
            { 'db': 'entidad_pension_id', 'label': 'entidad_pension', 'nombre_relacion': 'nombre' },
            { 'db': 'caja_compensacion_id', 'label': 'caja_compensacion', 'nombre_relacion': 'nombre' },
            { 'db': 'arl_id', 'label': 'arl', 'nombre_relacion': 'nombre' },
            { 'db': 'nivel_riesgo_id', 'label': 'nivel_riesgo', 'nombre_relacion': 'nombre' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        obj_datos_aportes = DatosAportes.objects.filter(contrato_id=obj.id).first()
        if obj_datos_aportes:
            list_principal += getHistorymodel(obj_datos_aportes, campos_datos_aportes)

        # DatosEmergencia
        campos_datos_emergencia = [
            { 'db': 'nombre', 'label': 'nombre' },
            { 'db': 'celular', 'label': 'celular' },
            { 'db': 'parentesco', 'label': 'parentesco' },
            { 'db': 'eliminado', 'label': 'eliminado dato de emergencia' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        for item in DatosEmergencia.objects.filter(contrato_id=obj.id):
            list_principal += getHistorymodel(item, campos_datos_emergencia)

        # ComposicionFamiliar
        campos_composicion_familiar = [
            { 'db': 'nombre', 'label': 'nombre' },
            { 'db': 'edad', 'label': 'edad' },
            { 'db': 'parentesco', 'label': 'parentesco' },
            { 'db': 'eliminado', 'label': 'eliminado composicion familiar' },
            { 'db': 'history_date', 'label': 'fecha_bitacora' }, { 'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion': 'username' }
        ]

        for item in ComposicionFamiliar.objects.filter(contrato_id=obj.id):
            list_principal += getHistorymodel(item, campos_composicion_familiar)

        return list_principal
    
    class Meta:
        """Meta class."""
        model = ContratoNomina
        fields = (
            "id",
            "history",
        )

class ContratoNominaNovedadesHistorySerializer(serializers.ModelSerializer):
    
    history = serializers.SerializerMethodField('get_history', read_only=True)
    def get_history(self, obj):
        campos = [
            { 'db': 'descripcion', 'label': 'descripcion' },
            { 'db': 'fecha_inicial', 'label': 'fecha_inicial' },
            { 'db': 'fecha_final', 'label': 'fecha_final' },
            { 'db': 'valor', 'label': 'valor' },
            { 'db': 'novedad_id', 'label': 'Novedad', 'nombre_relacion':'nombre' },
            { 'db': 'eliminado', 'label': 'Novedad Eliminada' },
            { 'db': 'history_date', 'label': 'fecha_bitacora'}, {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username' } # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]

        list_principal = getHistorymodel(obj, campos)

        return list_principal
    
    class Meta:
        """Meta class."""
        model = ContratoNominaNovedades
        fields = (
            "id",
            "history",
        )