from rest_framework import serializers
from cryptography.fernet import Fernet
from apps.parametros.models.parametrizacion import *
import pdb, json

class ParametrosModelSerializer(serializers.ModelSerializer):        

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
                    return obj.valor
            else :
                return obj.valor

    valor2 = serializers.SerializerMethodField('get_valor2', read_only=True)
    def get_valor2(self, obj):
        if obj.tipo_tab == "5" :
            # Para desencriptar las contraseñas
            if obj.valor2 != None :
                return Fernet(obj.key.encode('utf-8')).decrypt(obj.valor2.encode('utf-8')).decode()
            else :
                return obj.valor2
        else :
            return obj.valor2

    class Meta:
        model  = Parametros
        fields = ('id','parametro','valor','label','tipo','url','decimales','option_label','rules', 'valor2', 'tipo_tab', 'orden','cupon', 'requerido')

class ParametrosSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parametros
        fields = [
            'id', 'parametro', 'valor', 'label', 'tipo', 'url',
            'decimales', 'option_label', 'rules', 'activo','valor2',
            'tipo_tab', 'orden', 'key', 'cupon', 'comentario',
            'imagen_membrete', 'requerido'
        ]

class Parametro_ProcesoModelSerializer(serializers.ModelSerializer):  

    parametros = ParametrosModelSerializer(many=False, read_only=True)
    class Meta:
        model  = ParametroProceso   
        fields = ('id','parametros','proceso')

class ProcesoModelSerializer(serializers.ModelSerializer):

    procesos_parametros = Parametro_ProcesoModelSerializer(many=True, read_only=True)

    class Meta:
        model  = Procesos
        fields = ('id','nombre','codigo','procesos_parametros')

class ConfMesModelSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Mes
        fields = ('id','nombre', 'numero')

class ConfAnioModelSerializer(serializers.ModelSerializer):
    nombre_texto = serializers.SerializerMethodField('get_nombre', read_only=True)
    def get_nombre(self, obj):

        return str(obj.nombre)

    class Meta:
        model  = Anio
        fields = ('id','nombre','cierre',"nombre_texto", "salario_minimo", "aux_transporte")

class ParametrosWhatsappSerializer(serializers.ModelSerializer):

    disable = serializers.SerializerMethodField('get_disable', read_only=True)
    def get_disable(self, obj):
        return True
    
    class Meta:
        model  = ParametrosWhatsapp
        fields = ('id', 'parametro', 'valor', 'disable')

class GeneradorConsultasSerializer(serializers.ModelSerializer):

    foraneas = serializers.SerializerMethodField('get_foraneas', read_only=True)
    def get_foraneas(self, obj):

        if obj.modulo_id != None :
            modulo = obj.modulo.name
        else :
            gc = GeneradorConsultas.objects.get(pk=obj.consulta_base_id)
            modulo = gc.modulo.name

        return {
            "created": obj.created.strftime("%d/%m/%Y %I:%M %p"),
            "modified": obj.modified.strftime("%d/%m/%Y %I:%M %p"),
            "modulo": modulo
        }

    nombre_modulo = serializers.SerializerMethodField('get_nombre_modulo', read_only=True)
    def get_nombre_modulo(self, obj):

        if obj.modulo_id != None :
            return "{} - Modulo: {}".format(obj.nombre, obj.modulo.name)
        else :
            return "{}".format(obj.nombre)

    
    valor = serializers.SerializerMethodField('get_valor', read_only=True)
    def get_valor(self, obj):
        try:
            if obj.valor != None :
                data = json.loads(obj.valor)
                data["filter"] = []

                return data
            else :
                return None
        except:
            pass
    class Meta:
        model  = GeneradorConsultas
        fields = [
            'id',
            'nombre',
            'valor',
            'estado',
            'modulo_id',
            'uc_id',
            'um_id',
            'consulta_base_id',
            'observacion',
            'tipo',
            'script_sql',
            'foraneas',
            'nombre_modulo',
            'tipo_excel'
        ]

class MesAnioSerializer(serializers.ModelSerializer):

    class Meta:
        model  = MesAnio
        fields = [
            'id',
            'parametro',
            'valor',
            'valor2',
            'tipo',
            'anio',
            'mes'
        ]
