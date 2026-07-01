from django.shortcuts import render
from apps.utils.render import Render
from django.db.models import Q
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from apps.parametros.serializers.parametrizacion import *
from apps.parametros.models.parametrizacion import *
from rest_framework.decorators import action
from cryptography.fernet import Fernet
import pdb, json, requests, uuid, random, os, errno
from imap_tools import MailBox, AND, A
from django.db import transaction, connection
# from apps.utils.funciones import Funciones
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
import io, re, unicodedata
from config import settings
import requests
# Create your views here.
class ProcesoViewSet(viewsets.ModelViewSet):
    queryset = Procesos.objects.all()
    serializer_class = ProcesoModelSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_queryset()
        item = get_object_or_404(instance, codigo=kwargs['pk'])
        serializer = ProcesoModelSerializer(item)
        return Response(serializer.data, status=status.HTTP_200_OK)

class ConfMesViewSet(viewsets.ModelViewSet):
    queryset = Mes.objects.all()
    serializer_class = ConfMesModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = ConfMesModelSerializer(query, many=True).data
        return Response(data)

class ConfAnioViewSet(viewsets.ModelViewSet):
    queryset = Anio.objects.all()
    serializer_class = ConfAnioModelSerializer

    def list(self, request, *args, **kwargs):
        query = self.get_queryset()
        data = ConfAnioModelSerializer(query, many=True).data
        return Response(data)

class ParametrosViewSet(viewsets.ModelViewSet):
    queryset = Parametros.objects.all()
    serializer_class = ParametrosModelSerializer
    pagination_class = None

    @action(methods=['GET'], detail=False, url_path='tarifa_comision_inmobiliaria')
    def tarifa_comision_inmobiliaria(self, request, *args, **kwargs):
        tarifa = Parametros.objects.filter(parametro='tarifa_comision_inmo').first().valor
        return Response(tarifa)
    

    @action(methods=['GET'], detail=False, url_path='listar_portales')
    def listar_portales(self, request, *args, **kwargs):
        query = PortalesSincronizacion.objects.all()
        data = PortalesSerializer(query, many=True).data
        return Response(data)
    
    @action(methods=['GET'], detail=False, url_path='portales_parametro')
    def portales_parametro(self, request, *args, **kwargs):
        portales_par = Parametros.objects.filter(parametro='portales_sincronizar').first().valor
        if portales_par != '[]' :
            query = PortalesSincronizacion.objects.filter(id__in=json.loads(portales_par))
        else :
            query = PortalesSincronizacion.objects.all()
        data = PortalesSerializer(query, many=True).data
        # pdb.set_trace()
        return Response(data)

    def update(self, request, *args, **kwargs):
        parametro = Parametros.objects.get(pk=kwargs['pk'])
        parametro.valor = request.data['valor']
        parametro.save()
        return Response(ParametrosModelSerializer(parametro).data, status=status.HTTP_201_CREATED)

    @action(methods=['POST'], detail=False, url_path='guardartext')
    def guardartext(self, request, *args, **kwargs):
        parametro = Parametros.objects.get(pk=76)
        if request.data['tipo'] == 1 :
            return Response(ParametrosModelSerializer(parametro).data)
        else :
            parametro.valor = request.data['valor']
            parametro.save()
            return Response(ParametrosModelSerializer(parametro).data)

    @action(methods=['GET'], detail=False, url_path='listar')
    def ListaParametrizacion(self, request, *args, **kwargs):
        parametro = Parametros.objects.filter(~Q(tipo_tab=None)).order_by('tipo_tab', 'orden')
        return Response(ParametrosModelSerializer(parametro, many=True).data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='proveedor_facturacion')
    def ProveedorFacturacion(self, request, *args, **kwargs):
        parametro = Parametros.objects.filter(parametro='fact_elec_proveedor').first()
        if not parametro:
            return Response('Parámetro de proveedor de facturación electrónica no encontrado', status=400)
        serializer = ParametrosModelSerializer(parametro)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='pago_total')
    def ParametrizacionPagoTotal(self, request, *args, **kwargs):
        parametro = Parametros.objects.filter(parametro="pago_total").first()
        if not parametro:
            return Response('Parámetro de pago total no encontrado', status=400)
        serializer = ParametrosModelSerializer(parametro)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='save')
    def GuardarParametrizacion(self, request, *args, **kwargs):
        data = request.data
        correos_invalidos = []

        for item in data :
            parametro = Parametros.objects.get(pk=item['id'])
            parametro.uc_id = request.user.id
            parametro.um_id = request.user.id
            tipo_tab = item.get('tipo_tab', None)
            if tipo_tab == "5" :
                pass
                # if item["parametro"] == "smtp_correo_generales" :
                #     parametro.valor = item['valor']
                # elif item["parametro"] == "puerto_smtp_correo_generales" :
                #     parametro.valor = item['valor']
                # elif item["parametro"] == "imap_pop_correo_generales" :
                #     parametro.valor = item['valor']
                # elif item["parametro"] == "puerto_imap_pop_correo_generales" :
                #     parametro.valor = item['valor']
                # else :
                #     # Se encripta las contraseñas para los correos
                #     imap_pop = Parametros.objects.filter(parametro="imap_pop_correo_generales").first().valor
                #     puerto = Parametros.objects.filter(parametro="puerto_imap_pop_correo_generales").first().valor
                #     # pdb.set_trace()
                #     try :
                #         if not item['valor'] in [None, ""] and not item['valor2'] in [None, ""] :
                #             with MailBox(imap_pop if imap_pop != None else "imap.gmail.com", int(puerto) if puerto != None else 587).login(item['valor'], item['valor2']) as mailbox :
                #                 key = Fernet.generate_key()
                #                 crypt = Fernet(key).encrypt(item['valor2'].encode())
                #                 parametro.valor = item['valor']
                #                 parametro.valor2 = crypt.decode('utf-8')
                #                 parametro.key = key.decode('utf-8')
                #     except:
                #         parametro.valor = item['valor']
                #         correos_invalidos.append(item['valor'])
            elif item['parametro'] == 'persona_id_empresa' :
                parametro.valor = item['valor']
                persona = Parametros.objects.filter(parametro="persona_inmobiliaria_id").first()
                if persona :
                    persona.valor = item['valor']
                    persona.save()
            else :
                parametro.valor = item['valor']
            
            parametro.valor2 = item['valor2']
            parametro.save()
        
        # pdb.set_trace()
        if correos_invalidos != []:
            return Response("Credenciales invalidas para el correo: {}.".format(correos_invalidos), status=status.HTTP_200_OK)
        else:
            return Response("OK", status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['POST'], url_path='upload_logo')
    def upload_logo(self, request):
        archivo = request.FILES.get('file')
        nombre_empresa = request.data.get('nombre')

        if not archivo:
            return Response({"error": "No se envió archivo"}, status=400)

        if not nombre_empresa:
            param_nombre = Parametros.objects.filter(parametro="nombre_empresa").first()
            nombre_empresa = param_nombre.valor if param_nombre else None

        if not nombre_empresa:
            return Response({"error": "Debe enviarse el nombre"}, status=400)

        primera_palabra = nombre_empresa.strip().split()[0].lower()
        sigla = unicodedata.normalize('NFKD', primera_palabra).encode('ascii', 'ignore').decode('ascii')
        sigla = re.sub(r'[^a-zA-Z0-9]', '', sigla) or "empresa"

        filename_logo = f"{sigla}_logo.png"
        filename_inicio = f"{sigla}_logo_inicio.png"

        destino = os.path.join(settings.MEDIA_ROOT, "iconos")
        os.makedirs(destino, exist_ok=True)

        path_logo = os.path.join(destino, filename_logo)
        path_inicio = os.path.join(destino, filename_inicio)
        try:
            archivo.seek(0)
            files = {'image_file': (archivo.name, archivo.read(), archivo.content_type)}
            logo_sin_bg = requests.post(
                'https://api.remove.bg/v1.0/removebg',
                files=files,
                data={'size': 'preview'},
                headers={'X-Api-Key': settings.REMOVE_BG_API_KEY},
            )
            if logo_sin_bg.status_code == requests.codes.ok:
                with open(path_logo, 'wb') as out:
                    out.write(logo_sin_bg.content)
            else:
                error_detail = logo_sin_bg.json().get("errors", [{"title": "Unknown error"}])[0].get("title")
                return Response({"error": f"Error en Remove.bg: {error_detail}"},status=502)
            
        except Exception as e:
            return Response(
                {"error": "Error procesando imagen"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
            
        with open(path_inicio, "wb+") as f:
            for chunk in archivo.chunks():
                f.write(chunk)
                        
        # Actualizar/crear parámetros
        parametros_data = [
            ("nombre_logo_empresa", filename_logo, "Nombre del logo de la empresa"),
            ("logoinicio_empresa", filename_inicio, "Logo Perfil Empresa")
        ]

        for parametro, valor, label in parametros_data:
            instancia = Parametros.objects.filter(parametro=parametro).first()
            data = {
                "parametro": parametro,
                "valor": valor,
                "label": label,
                "tipo": "texto",
                "activo": True,
                "comentario": f"Nombre de la imagen para {label}",
                "requerido": True
            }

            if instancia:
                serializer = ParametrosSerializer(instancia, data={"valor": valor}, partial=True)
            else:
                serializer = ParametrosSerializer(data=data)

            serializer.is_valid(raise_exception=True)
            serializer.save()

        return Response({
            "status": "200",
            "logo": f"media/iconos/{filename_logo}"
        })
    
    @action(methods=['GET'], detail=False, url_path='logo')
    def ListarLogo(self, request, *args, **kwargs):
        dominio = Parametros.objects.filter(parametro='dominio_empresa').first().valor
        nombre_logo = Parametros.objects.filter(parametro='nombre_logo_empresa').first().valor
        if not nombre_logo:
            return Response({"logo": None}, status=200)
        logo_url = dominio + 'media/iconos/' + nombre_logo
        return Response({"logo": logo_url}, status=200)
        
    @action(methods=['GET'], detail=False, url_path='filtros')
    def FiltrosParametrizacion(self, request, *args, **kwargs):
        filtros = request.GET.get("filtros", None)
        if filtros != None :
            filtros = json.loads(filtros)
            parametro = Parametros.objects.filter(**filtros)
        else :
            parametro = Parametros.objects.all()

        return Response(ParametrosModelSerializer(parametro, many=True).data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='listar_todos')
    def Listartodos(self, request, *args, **kwargs):
        parametro = Parametros.objects.filter(cupon = True).order_by('orden')
        return Response(ParametrosModelSerializer(parametro, many=True).data, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='actualizar_parametro')
    def actualizar_parametro(self, request, *args, **kwargs):
        for item in request.data :
            parametro = Parametros.objects.filter(parametro=item["parametro"]).first()
            parametro.valor = item["valor"]
            parametro.save()
        return Response("OK", status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='historico/(?P<tipo_parametros>[^/.]+)')
    def ParametrosHistorico(self, request, tipo_parametros=None, *args, **kwargs):
        if tipo_parametros == "general" :
            parametros = Parametros.objects.filter(~Q(tipo_tab=None), cupon=False).order_by("orden")
        elif tipo_parametros == "cupones" :
            parametros = Parametros.objects.filter(cupon=True).order_by("orden")
        else:
            #en personalizado se le envían como un array de params los parametros a incluir en el historico bitacora
            params = request.GET.getlist('parametros[]', [])
            parametros = Parametros.objects.filter(parametro__in=params).order_by("orden")
        
        campos = [
            {'db': 'label', 'label': 'nombre'},
            {'db': 'valor', 'label': 'valor'},
            {'db': 'history_date', 'label': 'fecha_bitacora'},
            {'db': 'history_user_id', 'label': 'usuario_bitacora', 'nombre_relacion':'username'} # ESTOS DOS CAMPOS SON OBLIGATORIOS
        ]
        data = []

        for item in parametros :
            for hist in Funciones.getHistorymodel(item, campos) :
                hist["nombre"] = item.label
                data.append(hist)
        return Response(data, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='listar_general')
    def listar_general(self, request, *args, **kwargs):
        parametro = Parametros.objects.filter().order_by('orden')
        return Response(ParametrosModelSerializer(parametro, many=True).data, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='guardar_parametros_general')
    def guardar_parametros_general(self, request, *args, **kwargs):
        data = request.data

        for item in data['parametros'] :
            parametro = Parametros.objects.get(pk=item['id'])
            parametro.valor = item['valor']
            parametro.uc_id = request.user.id
            parametro.um_id = request.user.id
            parametro.save()

        return Response("OK", status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='filtrar_parametros')
    def FiltrarParametros(self, request, *args, **kwargs):
        data = request.data
        parametros = []
        if data :
            parametros = Parametros.objects.filter(**data).order_by("orden")
        
        return Response(ParametrosModelSerializer(parametros, many=True).data, status=status.HTTP_200_OK)

class ParametrosWhatsappViewSet(viewsets.ModelViewSet):

    def list(self, request, *args, **kwargs):
        parametros = ParametrosWhatsapp.objects.all()
        if len(parametros) > 0 :
            return Response(ParametrosWhatsappSerializer(parametros, many=True).data, status=status.HTTP_200_OK)
        else :
            return Response([
                { "id": None, "parametro": "token", "valor": None, "disable": True},
                { "id": None, "parametro": "cliente_id", "valor": None, "disable": True},
                { "id": None, "parametro": "cupon", "valor": None, "disable": True},
                { "id": None, "parametro": "extracto", "valor": None, "disable": True},
            ], status=status.HTTP_200_OK)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        try :
            for data in request.data :
                
                if data["id"] == None :
                    # Nuevo parametro
                    contizacion = ParametrosWhatsappSerializer(data=data)
                if data["id"] != None :
                    # Actualizar parametro
                    contizacion = ParametrosWhatsappSerializer(ParametrosWhatsapp.objects.get(pk=data["id"]), data=data)
                
                contizacion.is_valid(raise_exception=True)
                contizacion.save()
            return Response({
                "status": 200,
            }, status=status.HTTP_200_OK)
        except :
            return Response({
                "status": 400,
            }, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='bitacora')
    def bitacora(self, request, *args, **kwargs):

        cliente_id = ParametrosWhatsapp.objects.filter(parametro="cliente_id").first()
        
        if cliente_id != None :

            cliente_id = cliente_id.valor

            url = "https://whatsapp.webdgi.site/api/restful/whatsapp/fecha_idtel/"
            # url = "http://localhost:8001/api/restful/whatsapp/fecha_idtel/"

            headers = {
                "Content-type": "application/json"
            }

            payload = {
                "idtel": cliente_id,
                "fecha_ini" : request.GET.get("f_ini"),
                "fecha_fin" : request.GET.get("f_fin")
            }

            response = requests.request("POST", url, headers=headers, json=payload)
            
            if response.status_code == 200 :
                result = response.json()
                return Response({
                    "status": 200,
                    "data": result
                }, status=status.HTTP_200_OK)
        else :
            return Response({
                "status": 400,
                "data": "Por favor revisar la parametrización de whatsapp."
            }, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='exportar_bitacora')
    def exportar_bitacora(self, request, *args, **kwargs):
        model = []
        data = request.data
        for item in data["data"] :

            model.append({
                'fecha': item["fecha_format"],
                'nit': item["nit"],
                'nombre': item["nombre"],
                'numero': item["celular"],
                'tipo_proceso': item["tipo_proceso"],
                'estado': item["estado_format"],
                'mensaje': item["mensaje"],
            })
        
        model.append({
            'fecha': "Exportado por: {} {}".format(request.user.first_name, request.user.last_name)
        })

        dataReturn = Render.export_excel(model,'Bitacora {} - {}'.format(data["model"]["fecha_ini"], data["model"]["fecha_fin"]))

        return dataReturn
    
    @action(methods=['POST'], detail=False, url_path='imprimir_bitacora')
    def imprimir_bitacora(self, request, *args, **kwargs):

        data = request.data

        empresa = {
            'nombre': Parametros.objects.filter(parametro='nombre_empresa').first().valor,
            'nit': Parametros.objects.filter(parametro='nit_empresa').first().valor,
            'direccion': Parametros.objects.filter(parametro='direccion_empresa').first().valor,
            'telefono': Parametros.objects.filter(parametro='telefono_empresa').first().valor,
            'email': Parametros.objects.filter(parametro='email_empresa').first().valor,
            'logo': Parametros.objects.filter(parametro='dominio_empresa').first().valor + 'media/iconos/' + Parametros.objects.filter(parametro='nombre_logo_empresa').first().valor,
        }

        params = {
            'empresa': empresa,
            'filtro': data["model"],
            'data': data["data"]
        }

        pdf = Render.render('pdf/parametrizacion/bitacora_whatsapp.html', params, "bitacora whatsapp")

        return pdf

class GeneradorConsultasViewSet(viewsets.ModelViewSet):

    queryset = GeneradorConsultas.objects.all()
    serializer_class = GeneradorConsultasSerializer

    def list(self, request, *args, **kwargs):
        filtros = request.GET.get("filtros", None)

        if filtros != None :
            data = GeneradorConsultas.objects.filter(**json.loads(filtros)).order_by("id")
        else :
            data = GeneradorConsultas.objects.all().order_by("id")
        
        data = GeneradorConsultasSerializer(data, many=True).data

        return Response(data, status=status.HTTP_200_OK)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Guardar parametrizacion
        data = request.data
        data["columnas"] = [item for item in data["columnas"] if item["select"] == True]

        sql = self.get_consulta_sql(data, 2)

        for item in data["columnas"] :
            item["nombre_completo"] = "{}_{}".format(item["tabla"], item["nombre"])
            item["select"] = False

        if data["id"] == None :
            gc = GeneradorConsultas()
            gc.uc_id = request.user.id
        else :
            gc = GeneradorConsultas.objects.get(pk=data["id"])
            gc.um_id = request.user.id

            for item in GeneradorConsultas.objects.filter(consulta_base_id=gc.id) :
                item_valor = json.loads(item.valor)
                item_valor["data"]["inners"] = data["inners"]
                item.valor = json.dumps(item_valor)
                item.save()
        
        gc.nombre = data["nombre"]
        gc.valor = json.dumps(data)
        gc.script_sql = sql
        gc.modulo_id = data["modulo"]
        gc.observacion = data["observacion"]
        gc.tipo = "parametrizacion"
        gc.save()

        return Response({
            "status": 200,
            "msg": "ok"
        }, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='guardar_consulta')
    def guardar_consulta(self, request, *args, **kwargs):
        # Guardar la consulta
        data = request.data

        sql = self.get_consulta_sql(data["data"], 1)

        if data["id"] == None :
            # Crear
            gc = GeneradorConsultas()
            gc.uc_id = request.user.id
        else :
            # Actualizar
            gc = GeneradorConsultas.objects.get(pk=data["id"])
            gc.um_id = request.user.id
        
        gc.nombre = data["nombre_consulta"]
        gc.valor = json.dumps(data)
        gc.script_sql = sql
        gc.observacion = data["observacion"]
        gc.tipo = "consulta"
        gc.consulta_base_id = data["consulta_base"]
        gc.save()

        return Response({
            "status": 200,
            "msg": "ok"
        }, status=status.HTTP_200_OK)

    def get_columnas(self, tabla, alias) :
        c = connection.cursor()
        sql = """
            select json_agg(json_build_object(
                'nombre', obj.column_name,
                'tabla', '{}',
                'alias', '{}',
                'select', false
            )) from (
                select
                    column_name
                from information_schema.columns
                where table_name = '{}'
            ) obj;
        """.format(tabla, alias, tabla)
        c.execute(sql)
        result = c.fetchall()
        c.close()

        if len(result) > 0 :
            result = result[0][0]
        else :
            result = []
        
        return result
    
    @action(methods=['GET'], detail=False, url_path='list_tablas')
    def list_tablas(self, request, *args, **kwargs):
        # row_number() over () as id
        c = connection.cursor()
        sql = """
            select json_agg(json_build_object(
                'nombre', obj.table_name
            )) from (
                select
                    table_name
                from information_schema.tables
                order by table_name
            ) obj;
        """
        c.execute(sql)
        result = c.fetchall()
        c.close()

        if len(result) > 0 :
            result = result[0][0]
            cont = 1
            for item in result :
                item["alias"] = "tb{}".format(cont)
                cont += 1
        else :
            result = []
        
        return Response({
            "status": 200,
            "data": result
        }, status=status.HTTP_200_OK)
    
    @action(methods=['GET'], detail=False, url_path='list_columnas')
    def list_columnas(self, request, *args, **kwargs):
        params = json.loads(request.GET.get("params", None))

        if params != None :
            result = self.get_columnas(params["tabla"], params["alias"])
        else :
            result = []
        
        return Response({
            "status": 200,
            "data": result
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='buscar_relacion')
    def buscar_relacion(self, request, *args, **kwargs):
        data = request.data
        direccion_relacion = ""

        if data["direccion"] == "right" :
            direccion_relacion = " and tc.table_name = '{}' order by tc.table_name".format(data["tabla"])
        else :
            direccion_relacion = " and ccu.table_name = '{}' order by ccu.table_name".format(data["tabla"])

        c = connection.cursor()
        sql = """
            select 
                json_agg(json_build_object(
                    'table_schema', obj.table_schema,
                    'constraint_name', obj.constraint_name,
                    'table_name', obj.table_name,
                    'column_name', obj.column_name,
                    'foreign_table_schema', obj.foreign_table_schema,
                    'foreign_table_name', obj.foreign_table_name,
                    'foreign_column_name', obj.foreign_column_name
                )) from (
                    select 
                        tc.table_schema,
                        tc.constraint_name,
                        tc.table_name,
                        kcu.column_name,
                        ccu.table_schema as foreign_table_schema,
                        ccu.table_name as foreign_table_name,
                        ccu.column_name as foreign_column_name
                    from information_schema.table_constraints as tc 
                    join information_schema.key_column_usage as kcu
                        on tc.constraint_name = kcu.constraint_name
                        and tc.table_schema = kcu.table_schema
                    join information_schema.constraint_column_usage AS ccu
                        on ccu.constraint_name = tc.constraint_name
                    where tc.constraint_type = 'FOREIGN KEY'
                    and tc.table_schema='public'
                    {}
                ) obj;
        """.format(direccion_relacion)
        c.execute(sql)
        result = c.fetchall()
        c.close()

        data = []

        if len(result) > 0 :
            result = result[0][0]

            if result != None :
                if request.data["direccion"] == "right" :
                    for item in list(set(item["foreign_table_name"] for item in result)) :
                        data.append({
                            "nombre": item,
                            "alias": self.generar_alias()
                        })
                else :
                    for item in result :
                        data.append({
                            "nombre": item["table_name"],
                            "alias": self.generar_alias()
                        })
        
        return Response({
            "status": 200,
            "data": data
        }, status=status.HTTP_200_OK)

    @action(methods=['POST'], detail=False, url_path='generar_consulta')
    def generarConsulta(self, request, *args, **kwargs):
        data = request.data

        tipo_excel = data["tipo_excel"] if "tipo_excel" in data else False
        if data["tipo_consulta"] == 1 :
            sql = self.get_consulta_sql(data["data"], 1)
        else :
            if data["valor"] != None :
                sql = self.get_consulta_sql(data["valor"]["data"], 1)
            else :
                sql = data["script_sql"]
        
        c = connection.cursor()
        c.execute(sql)
        result = c.fetchall()
        c.close()

        data = []
        obj = {}

        if result != None :
            if len(result) > 0 :
                result = result[0][0]

                if result != None :
                    for resu in result :
                        obj = {}
                        for item in [[x, y] for x, y in resu.items()] :
                            if item[1] is True :
                                obj[item[0]] = "SI"
                            elif item[1] is False :
                                obj[item[0]] = "NO"
                            else :
                                obj[item[0]] = item[1] if item[1] != None else ""
                        data.append(obj)
        

        # LeidyB - 15/01/2025 Se realiza esta opcion para el caso de la consulta de inmuebles que se necesita que se genere una hoja por cada tipo.
        if tipo_excel == "hojas" :
            agrupados_por_tipo = {}

            # Agrupar
            for inmueble in data:
                tipo = inmueble["tipo_inmueble"] 
                if tipo not in agrupados_por_tipo:
                    agrupados_por_tipo[tipo] = [] 
                agrupados_por_tipo[tipo].append(inmueble)         
                
        
        return Render.export_excel(agrupados_por_tipo if tipo_excel == "hojas" else data,'GENERADOR DE CONSULTAS', True, True, False, True if tipo_excel == 'hojas' else False)
    
    @action(methods=['POST'], detail=False, url_path='cambiar_estado')
    def cambiarEstado(self, request, *args, **kwargs):
        data = request.data

        gc = GeneradorConsultas.objects.get(pk=data["id"])
        gc.estado = data["estado"]
        gc.save()

        return Response({
            "status": 200,
            "msg": ""
        }, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='consultar_valor_tabla')
    def consultarValorTabla(self, request, *args, **kwargs):
        data = request.data
        c = connection.cursor()
        sql = """
            select
                json_agg(
                    json_build_object(
                        'id', {},
                        'nombre', {}
                    )
                )
            from {};
        """.format(data["columna"], data["columna"], data["tabla"])
        c.execute(sql)
        result = c.fetchall()
        c.close()

        if len(result) > 0 :
            result = result[0][0]
        else :
            result = []

        return Response(result, status=status.HTTP_200_OK)
    
    @action(methods=['POST'], detail=False, url_path='previsualizar_consulta')
    def PrevisualizarConsulta(self, request, *args, **kwargs):
        data = request.data
        data["columnas"] = [item for item in data["columnas"] if item["select"] == True]

        sql = self.get_consulta_sql(data, 2)

        return Response(sql, status=status.HTTP_200_OK)

    def get_consulta_sql(self, model, tipo) :
        #Tipo 1 es para generar sql para el cliente va con estrucctura json y Tipo 2 es para generar sql para desarrolo sin estrucctura json

        # Esta validacion se hace ya que desde el crear consulta base no se envia el array de filtros
        try :
            if len(model["filter"]) > 0 :
                pass
        except :
            model["filter"] = []
        
        tablas_principal = " {} as {} ".format(model["tabla_principal"], model["alias"])
        columnas = ""
        columnas_no_json = ""
        inners = ""
        filter = ""
        alias_foraneas = []
        alias_usados = []
        columnas_select = [item for item in model["columnas"] if item["select"] == True]

        for i, col in enumerate(columnas_select) :
            validate = col["alias"] in set(alias_usados)
            if validate == False :
                alias_usados.append(col["alias"])
            
            complemento = ", \n\t\t" if (i + 1) < len(columnas_select) else ""
            if col["select"] == True :
                if columnas == "" :
                    columnas = """'{}_{}', {}."{}"{}""".format(col["tabla"], col["nombre"], col["alias"], col["nombre"], complemento)
                    columnas_no_json = """{}."{}"{}""".format(col["alias"], col["nombre"], complemento)
                else :
                    columnas = columnas + """'{}_{}', {}."{}"{}""".format(col["tabla"], col["nombre"], col["alias"], col["nombre"], complemento)
                    columnas_no_json = columnas_no_json + """{}."{}"{}""".format(col["alias"], col["nombre"], complemento)
        
        for inner in model["inners"] :
            # Se valida si el inner join tiene otro inner join (hijo) por dentro

            # Se valida si el alias del inner join padre fue utulizado para consultar algun campo
            validate = inner["alias"] in set(alias_usados)
            if validate == True :
                # Se valida que el inner join padre no se haya usado para no reétirlo
                validate = inner["alias"] in set(alias_foraneas)
                if validate == False :
                    alias_foraneas.append(inner["alias"])
                
                # Se agregan los inner join padre
                inners = inners + inner["relacion_foranea"] + " \n\t\t"
            
            if len(inner["inners"]) > 0 :
                for inner2 in inner["inners"] :
                    # Se valida si el alias del inner join hijo fue utulizado para consultar algun campo

                    validate = inner2["alias"] in set(alias_usados)
                    if validate == True :
                        # Se valida que el inner join padre no se haya usado para no reétirlo
                        validate = inner["alias"] in set(alias_foraneas)
                        if validate == False :
                            alias_foraneas.append(inner["alias"])
                            alias_foraneas.append(inner2["alias"])
                        
                        # Se agregan los inner join hijo
                        inners = inners + inner2["relacion_foranea"] + " \n\t\t"
        
        # pdb.set_trace()

        for i, item in enumerate(model["filter"]) :
            valor_filtrar = ""
            campo_a_filtrar = item["campo_a_filtrar"]["alias"] + "." + item["campo_a_filtrar"]["nombre"]
            if item["valor_2"] == None :
                try :
                    # Se cambia lo filtrado a miniscula
                    valor_filtrar = item["clase_filtro"] + " " + "lower({})".format(campo_a_filtrar) + " " + item["tipo_filtro"] + " " + "'{}'".format(item["valor_1"].lower())
                except :
                    valor_filtrar = item["clase_filtro"] + " " + campo_a_filtrar + " " + item["tipo_filtro"] + " " + "'{}'".format(item["valor_1"])
            else :
                if item["tipo_filtro"] == "rango_1" :
                    # Fecha
                    valor_filtrar = item["clase_filtro"] + " " + campo_a_filtrar + " between " + "'{}'".format(item["valor_1"]) + " and " + "'{}'".format(item["valor_2"])
                else :
                    # Valor
                    valor_filtrar = item["clase_filtro"] + " " + campo_a_filtrar + " between " + str(item["valor_1"]) + " and " + str(item["valor_2"])
                
            filter = filter + valor_filtrar + (" \n\t\t" if (i+1) < len(model["filter"]) else "")
        
            # Esta validacion se hace para revisar si no se agrego un inner join que es necesario para hacer un filtro
            for inner in model["inners"] :
                if item["campo_a_filtrar"]["alias"] == inner["alias"] :
                    validate = inner["alias"] in set(alias_foraneas)
                    if validate == False :
                        # Se agrega el inner join
                        inners = inners + inner["relacion_foranea"] + " \n\t\t"
                else :
                    if len(inner["inners"]) > 0 :
                        for inner2 in inner["inners"] :
                            if item["campo_a_filtrar"]["alias"] == inner2["alias"] :
                                validate = inner2["alias"] in set(alias_foraneas)
                                if validate == False :

                                    # Se agrega el inner join
                                    inners = inners + inner["relacion_foranea"] + " \n\t\t"
                                    inners = inners + inner2["relacion_foranea"] + " \n\t\t"
        if tipo == 1 :
            columnas = """
                json_agg(
                    json_build_object(
                        {}
                    )
                )
            """.format(columnas)
        sql = """
            select
                {}
            from 
                {}
            \t{}
            {};
        """.format(columnas if tipo == 1 else columnas_no_json, tablas_principal, inners, filter)
        
        # sql = sql.replace("\n", "")

        try :
            os.makedirs(os.path.join(settings.MEDIA_ROOT, "generador_consultas"))
        except OSError as e :
            if e.errno != errno.EEXIST :
                pass
        
        # Rura del archivo txt
        rutatxt = os.path.join(settings.MEDIA_ROOT, "generador_consultas", "generador_consulta.sql")

        if os.path.exists(rutatxt) == True :
            os.remove(rutatxt)

        with open(rutatxt, "a") as file :
            file.write(sql)

        return sql

    def generar_alias(self) :
        aliass = chr(random.randint(ord('a'), ord('z')))
        aliass += uuid.uuid4().hex[0:3]

        return aliass
    
class CiudadEmpresaViewSet(viewsets.ModelViewSet):

    def list(self, request):
        queryset = Parametros.objects.filter(parametro= 'ciudad_empresa').first().valor
        return Response(queryset, status=status.HTTP_200_OK)

class MesAnioViewSet(viewsets.ModelViewSet):

    queryset = MesAnio.objects.all()
    serializer_class = MesAnioSerializer

    def list(self, request, *args, **kwargs):
        filtros = request.GET.get("filtros", None)

        if filtros != None :
            filtros = json.loads(filtros)
            query = MesAnio.objects.filter(**filtros)
            query = MesAnioSerializer(query, many=True).data
            if len(query) > 0 :
                query = query[0]
            else :
                query = None
        else :
            query = MesAnio.objects.all()
            query = MesAnioSerializer(query, many=True).data

        return Response({
            "status": 200,
            "data": query
        }, status=status.HTTP_200_OK)
    

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        filtros = request.data.get("filtros", None)

        if filtros != None :
            query = MesAnio.objects.filter(**filtros).first()
            data = request.data["data"]
        else :
            data = request.data
            query = MesAnio.objects.filter(parametro=data["parametro"], mes_id=data["mes"], anio_id=data["anio"]).first()

        if query != None :
            query = MesAnioSerializer(query, data=data)
            query.is_valid(raise_exception=True)
            query.save()
        else :
            query = MesAnioSerializer(data=data)
            query.is_valid(raise_exception=True)
            query.save()

        query = query.data
        
        return Response(query, status=status.HTTP_200_OK)

class AfiliadosViewSet(viewsets.ViewSet):

    @action(methods=['GET'], detail=False, url_path='tipo_contrato')
    def tipo_contrato(self, request):
        query = list(TipoContrato.objects.filter(activo=True).values("id", "nombre"))
        return Response(query)

    @action(methods=['GET'], detail=False, url_path='aplicativo')
    def aplicativo(self, request):
        query = list(Aplicativo.objects.filter(activo=True).values("id", "nombre"))
        return Response(query)
    