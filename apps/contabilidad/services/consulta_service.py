from rest_framework.response import Response
from django.db import transaction
from apps.common_db.db import execute_procedure
from rest_framework import status
from apps.contabilidad.models.cuenta import Mayor
import pdb

class ConsultaService:

    @staticmethod
    def filtro_aux(model, filtro=None):
        if model['tipo'] == 1:
            # codigo clasificado por nit
            try:
                with transaction.atomic():
                    sql = """
                        select * from getauxiliarnit(%s, %s, %s, %s, %s, %s);
                    """
                    params = [
                        model['año'],
                        model['mesini'],
                        model['mesfin'],
                        model['codigo'],
                        1 if filtro['incnitsinsal'] == True else 0,
                        1 if filtro['incnitsinmov'] == True else 0,
                    ]
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)
            if resultado and resultado[0][0] is not None:
                return resultado[0][0][0]
            return []

        elif model['tipo'] == 2:
            # codigo y nit
            try:
                with transaction.atomic():
                    sql = """
                        select json_agg(json_build_object(
                            'id', id,
                            'tipo', tipo,
                            'numero', numero,
                            'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                            'docref', docref,
                            'concepto', concepto,
                            'detalle', detalle,
                            'valor_db', valor_db,
                            'valor_cr', valor_cr,
                            'saldo', saldo,
                            'color', color,
                            'fuentes_id', fuentes_id,
                            'ordenf', ordenf,
                            'base', base,
                            'mov_id', mov_id,
                            'mayor_id', mayor_id)) from getauxcodnit(%s, %s, %s, %s, %s);
                    """
                    params = [
                        model['codigo'],
                        model['persona'],
                        model['año'],
                        model['mesini'],
                        model['mesfin'],
                    ]
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []

        elif model['tipo'] == 3:
            # codigo
            try:
                with transaction.atomic():
                    if model['ccosto'] == True:
                        sql = """
                            select json_agg(json_build_object(
                                'id', id,
                                'tipo', tipo,
                                'numero', numero,
                                'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                'docref', docref,
                                'concepto', concepto,
                                'nits', nits,
                                'nombre', nombre,
                                'detalle', detalle,
                                'valor_db', valor_db,
                                'valor_cr', valor_cr,
                                'saldo', saldo,
                                'color', color,
                                'fuentes_id', fuentes_id,
                                'orden', orden,
                                'ordenf', ordenf,
                                'centro_costos_id', centro_costos_id,
                                'base', base)) from getauxiliarcodigocc(%s, %s, %s, %s, %s, %s);
                        """
                        params = [
                            model['año'],
                            model['mesini'],
                            model['mesfin'],
                            model['codigonom']['nombre1'] if model['codigonom']['nombre1'] is not None else '0',
                            model['codigonom']['nombre2'] if model['codigonom']['nombre2'] is not None else model['codigonom']['nombre1'],
                            model['idcc'],
                        ]
                    else:
                        if model['rango_fecha'] == False:
                            sql = """
                                select json_agg(json_build_object(
                                    'id', id,
                                    'tipo', tipo,
                                    'numero', numero,
                                    'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                    'docref', docref,
                                    'concepto', concepto,
                                    'nits', nits,
                                    'nombre', nombre,
                                    'detalle', detalle,
                                    'valor_db', valor_db,
                                    'valor_cr', valor_cr,
                                    'saldo', saldo,
                                    'color', color,
                                    'fuentes_id', fuentes_id,
                                    'orden', orden,
                                    'ordenf', ordenf,
                                    'base', base)) from getauxiliarcodigo(%s, %s, %s, %s, %s);
                            """
                            params = [
                                model['año'],
                                model['mesini'],
                                model['mesfin'],
                                model['codigonom']['nombre1'] if model['codigonom']['nombre1'] is not None else '0',
                                model['codigonom']['nombre2'] if model['codigonom']['nombre2'] is not None else model['codigonom']['nombre1'],
                            ]
                        else:
                            sql = """
                                select json_agg(json_build_object(
                                    'id', id,
                                    'tipo', tipo,
                                    'numero', numero,
                                    'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                    'docref', docref,
                                    'concepto', concepto,
                                    'nits', nits,
                                    'nombre', nombre,
                                    'detalle', detalle,
                                    'valor_db', valor_db,
                                    'valor_cr', valor_cr,
                                    'saldo', saldo,
                                    'color', color,
                                    'fuentes_id', fuentes_id,
                                    'orden', orden,
                                    'ordenf', ordenf,
                                    'base', base)) from getauxiliarcodigorango(%s, %s, %s, %s);
                            """
                            params = [
                                model['fechaini'],
                                model['fechafin'],
                                model['codigonom']['nombre1'] if model['codigonom']['nombre1'] is not None else '0',
                                model['codigonom']['nombre2'] if model['codigonom']['nombre2'] is not None else model['codigonom']['nombre1'],
                            ]
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []

        elif model['tipo'] == 4:
            try:
                with transaction.atomic():
                    if model['ccosto'] == True:
                        sql = """
                            select json_agg(json_build_object(
                                'id', id,
                                'tipo', tipo,
                                'numero', numero,
                                'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                'docref', docref,
                                'concepto', concepto,
                                'nits', nits,
                                'detalle', detalle,
                                'valor_db', valor_db,
                                'valor_cr', valor_cr,
                                'saldo', saldo,
                                'color', color,
                                'fuentes_id', fuentes_id,
                                'orden', orden,
                                'ordenf', ordenf,
                                'centro_costos_id', centro_costos_id,
                                'base', base)) from getauxiliarnitcc(%s, %s, %s, %s, %s);
                        """
                        params = [
                            model['año'],
                            model['mesini'],
                            model['mesfin'],
                            model['persona'],
                            model['idcc'],
                        ]
                    else:
                        sql = """
                            select json_agg(json_build_object(
                                'id', id,
                                'tipo', tipo,
                                'numero', numero,
                                'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                                'docref', docref,
                                'concepto', concepto,
                                'detalle', detalle,
                                'valor_db', valor_db,
                                'valor_cr', valor_cr,
                                'saldo', saldo,
                                'color', color,
                                'fuentes_id', fuentes_id,
                                'base', base)) from getauxiliarper(%s, %s, %s, %s);
                        """
                        params = [
                            model['año'],
                            model['mesini'],
                            model['mesfin'],
                            model['persona'],
                        ]

                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []

        elif model['tipo'] == 5:
            try:
                with transaction.atomic():
                    sql = """
                        select json_agg(json_build_object(
                            'id', id,
                            'tipo', tipo,
                            'numero', numero,
                            'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                            'docref', docref,
                            'concepto', concepto,
                            'detalle', detalle,
                            'valor_db', valor_db,
                            'valor_cr', valor_cr,
                            'saldo', saldo,
                            'color', color,
                            'fuentes_id', fuentes_id,
                            'observa', observa,
                            'base', base)) from getauxiliarperdet(%s, %s, %s, %s);
                    """
                    params = [
                        model['año'],
                        model['mesini'],
                        model['mesfin'],
                        model['persona'],
                    ]
                    pdb.set_trace()
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []

        elif model['tipo'] == 7:
            # codigo, nit y concepto (persona opcional)
            mayordesde = Mayor.objects.filter(codigol=model['codigonom']['nombre1']).first()
            mayorhasta = (
                Mayor.objects.filter(codigol=model['codigonom']['nombre2']).first()
                if model['codigonom']['nombre2'] is not None
                else mayordesde
            )

            persona_val = model.get('persona', None)
            persona_param = None if (persona_val is None or persona_val == '' or persona_val == 0) else persona_val

            try:
                with transaction.atomic():
                    sql = """
                        select json_agg(json_build_object(
                            'id', id,
                            'tipo', tipo,
                            'numero', numero,
                            'fecha', to_char(date(fecha), 'dd/mm/yyyy'),
                            'docref', docref,
                            'concepto', concepto,
                            'detalle', detalle,
                            'valor_db', valor_db,
                            'valor_cr', valor_cr,
                            'saldo', saldo,
                            'color', color,
                            'fuentes_id', fuentes_id,
                            'ordenf', ordenf,
                            'base', base,
                            'inmueble_id', inmueble_id,
                            'direccion', direccion,
                            'mov_id', mov_id,
                            'mayor_id', mayor_id,
                            'pagado', pagado)) from getauxcodnitconc(%s, %s, %s, %s, %s, %s, %s);
                    """
                    params = [
                        mayordesde.codigol,
                        mayorhasta.codigol,
                        persona_param,
                        model['año'],
                        model['mesini'],
                        model['mesfin'],
                        model['concepto'],
                    ]
                    resultado = execute_procedure(sql=sql, params=params)
            except Exception:
                return Response("Error en el proceso por favor revisar.", status=status.HTTP_404_NOT_FOUND)

            if resultado and resultado[0][0] is not None:
                return resultado[0][0]
            return []