from django.db import transaction

from apps.utils.render import Render

from apps.nomina.models.contratos import ContratoNomina, DatosPago, DatosAportes, DatosEmergencia, ComposicionFamiliar, ContratoNominaNovedades, ContratoNovedadesPeriodos
from apps.nomina.models.novedades import NovedadesCentroCosto
from apps.personas.models.persona import TipoPersona
from apps.personas.services.persona_service import PersonaService
from apps.parametros.services.empresa_service import EmpresaService

class ContratoNominaService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(validated_data, user, instancia=None):
        """
        Crea o actualiza un ContratoNomina con todos sus modelos relacionados.
        Recibe validated_data de ContratoNominaCreateSerializer.
        """
        data_persona = validated_data.pop('data_persona', {})
        datos_pago = validated_data.pop('datos_pago')
        datos_aportes = validated_data.pop('datos_aportes')
        datos_emergencia = validated_data.pop('datos_emergencia', [])
        composicion_familiar = validated_data.pop('composicion_familiar', [])

        tipopersonas = [1]
        if data_persona["id"] != None :
            tipopersonas += list(TipoPersona.objects.filter(personas_tipos_personas_tipo__persona_id=data_persona["id"]).values_list('id', flat=True))

        data_persona['tipos_persona'] = tipopersonas

        if data_persona.get('n_completo', None) is None or data_persona.get('n_completo', '') == '':
            data_persona['n_completo'] = f"{data_persona.get('p_nombre', '')} {data_persona.get('s_nombre', '')} {data_persona.get('p_apellido', '')} {data_persona.get('s_apellido', '')}".replace('  ', ' ')

        persona = PersonaService.crear_o_actualizar({'persona': data_persona}, user.id)
        validated_data['persona'] = persona

        if instancia:
            instancia.um_id = user.id
            for attr, value in validated_data.items():
                setattr(instancia, attr, value)
            instancia.save()
            contrato = instancia
        else:
            validated_data['uc_id'] = user.id
            contrato = ContratoNomina.objects.create(**validated_data)

        # DatosPago — 1:1 con contrato
        dp = DatosPago.objects.filter(contrato=contrato).first()
        if dp:
            dp.banco = datos_pago['banco']
            dp.tipo_cuenta = datos_pago['tipo_cuenta']
            dp.numero_cuenta = datos_pago['numero_cuenta']
            dp.forma_pago = datos_pago['forma_pago']
            dp.medio_pago = datos_pago['medio_pago']
            dp.um_id = user.id
            dp.save()
        else:
            DatosPago.objects.create(
                contrato=contrato,
                banco=datos_pago['banco'],
                tipo_cuenta=datos_pago['tipo_cuenta'],
                numero_cuenta=datos_pago['numero_cuenta'],
                forma_pago=datos_pago['forma_pago'],
                medio_pago=datos_pago['medio_pago'],
                uc_id=user.id
            )

        # DatosAportes — 1:1 con contrato
        da = DatosAportes.objects.filter(contrato=contrato).first()
        if da:
            for attr, value in datos_aportes.items():
                setattr(da, attr, value)
            da.um_id = user.id
            da.save()
        else:
            DatosAportes.objects.create(
                contrato=contrato,
                uc_id=user.id,
                **datos_aportes
            )

        # DatosEmergencia — array
        for item in datos_emergencia:
            item_id = item.pop('id', None)
            if item_id:
                emergencia = DatosEmergencia.objects.filter(pk=item_id).first()
                if emergencia:
                    for attr, value in item.items():
                        setattr(emergencia, attr, value)
                    emergencia.um_id = user.id
                    emergencia.save()
            else:
                DatosEmergencia.objects.create(
                    contrato=contrato,
                    uc_id=user.id,
                    **item
                )

        # ComposicionFamiliar — array
        for item in composicion_familiar:
            item_id = item.pop('id', None)
            if item_id:
                familiar = ComposicionFamiliar.objects.filter(pk=item_id).first()
                if familiar:
                    for attr, value in item.items():
                        setattr(familiar, attr, value)
                    familiar.um_id = user.id
                    familiar.save()
            else:
                ComposicionFamiliar.objects.create(
                    contrato=contrato,
                    uc_id=user.id,
                    **item
                )

        return contrato

    @staticmethod
    def exportar(request_data):
        model = []

        for item in request_data :
            model.append({
                "nro_contrato": item["id"],
                "identificacion": item["persona"]["documento"],
                "nombre": item["persona"]["n_completo"],
                "fecha_ingreso": item["fecha_ingreso"],
                "centro_costo": item["foraneas"]["centro_costos"],
                "estado": item["estado"],
            })
        
        return Render.export_excel(model, "Listado de contratos")

    @staticmethod
    def imprimir(request_data):
        empresa = EmpresaService.obtener_datos_empresa()
    
        data = request_data

        params = {
            'empresa': empresa,
            'data': data
        }

        pdf = Render.render_pdfkit('pdf/nomina/list_contratos.html', params, "Listado de contratos")

        return pdf

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar_novedades(validated_data, user, contrato_id):
        for item in validated_data:
            item_id = item.pop('id', None)
            novedad = item['novedad']  # ya es instancia

            novedad_ccosto = NovedadesCentroCosto.objects.filter(
                novedades=novedad
            ).first()

            if novedad_ccosto:
                item['centro_costos_novedades_id'] = novedad_ccosto.id

            if item_id is None:
                ContratoNominaNovedades.objects.create(
                    contrato_id=contrato_id,
                    uc_id=user.id,
                    **item
                )
            else:
                instancia = ContratoNominaNovedades.objects.filter(pk=item_id).first()
                if instancia:
                    for attr, value in item.items():
                        setattr(instancia, attr, value)
                    instancia.um_id = user.id
                    instancia.save()

        return

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar_novedades_periodos(validated_data, user=None):
        contrato_novedades = [x["contrato_novedades"] for x in validated_data]
        ContratoNovedadesPeriodos.objects.filter(contrato_novedades__in=contrato_novedades).delete()
        
        for item in validated_data :
            ContratoNovedadesPeriodos.objects.create(**item)

        return
    
    @staticmethod
    def listar_novedades(contrato_id):
        data = ContratoNominaNovedades.objects.filter(contrato_id=contrato_id)
        return data