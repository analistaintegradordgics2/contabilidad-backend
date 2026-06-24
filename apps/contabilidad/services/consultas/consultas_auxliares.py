from abc import ABC, abstractmethod
from apps.common_db.db import execute_procedure
from django.db import transaction
from apps.contabilidad.models.cuenta import Mayor

class IConsultaAuxliar(ABC):
    @abstractmethod
    def ejecutar(self, model: dict, filtro: dict = None) -> list:
        pass

class ConsultaCodigoPorNit(IConsultaAuxliar):
    # codigo clasificado por nit
    
    def ejecutar(self, model: dict, filtro: dict = None) -> list:
        sql = """ select * from getauxiliarnit(%s, %s, %s, %s, %s, %s); """
        params = [
            model['año'],
            model['mesini'],
            model['mesfin'],
            model['codigo'],
            1 if filtro['incnitsinsal'] == True else 0,
            1 if filtro['incnitsinmov'] == True else 0,
        ]

        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)
        
        if resultado and resultado[0][0] is not None:
            return resultado[0][0][0]
        return []
        
class ConsultaCodigoYNit(IConsultaAuxliar):
    # codigo y nit
    
    def ejecutar(self, model: dict, filtro: dict = None) -> list:
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
        
        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)
        
        if resultado and resultado[0][0] is not None:
            return resultado[0][0]
        return []
    
class ConsultaCodigo(IConsultaAuxliar):
    # codigo
    
    def ejecutar(self, model: dict, filtro: dict = None) -> list:
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
        
        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)
        
        if resultado and resultado[0][0] is not None:
            return resultado[0][0]
        return []
    
class ConsultaNitCuenta(IConsultaAuxliar):
    # nit y cuenta
    
    def ejecutar(self, model: dict, filtro: dict = None) -> list:
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
        
        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)
        
        if resultado and resultado[0][0] is not None:
            return resultado[0][0]
        return []
    
class ConsultaNit(IConsultaAuxliar):
    # nit
    
    def ejecutar(self, model: dict, filtro: dict = None) -> list:
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
        
        with transaction.atomic():
            resultado = execute_procedure(sql=sql, params=params)
        
        if resultado and resultado[0][0] is not None:
            return resultado[0][0]
        return []
    
class ConsultaCodigoNitConcepto(IConsultaAuxliar):
    # codigo, nit y concepto (persona opcional)
    def ejecutar(self, model, filtro = None):
        mayordesde = Mayor.objects.filter(codigo=model['codigonom']['nombre1']).first()
        mayorhasta = (
            Mayor.objects.filter(codigo=model['codigonom']['nombre2']).first()
            if model['codigonom']['nombre2'] is not None
            else mayordesde
        )

        persona_val = model.get('persona', None)
        persona_param = None if (persona_val is None or persona_val == '' or persona_val == 0) else persona_val
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
                'mayor_id', mayor_id)) from getauxcodnitconc(%s, %s, %s, %s, %s, %s, %s);
        """
        # pdb.set_trace()
        params = [
            mayordesde.codigo,
            mayorhasta.codigo,
            persona_param,
            model['año'],
            model['mesini'],
            model['mesfin'],
            model['concepto'],
        ]
        
        resultado = execute_procedure(sql=sql, params=params)

        if resultado and resultado[0][0] is not None:
            return resultado[0][0]
        return []