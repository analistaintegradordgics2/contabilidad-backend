from django.db import connection
from apps.parametros.models.parametrizacion import Parametros
from datetime import datetime
from apps.contabilidad.models.tipodocumento import ResolucionFacturacion, TiposDocumentos
from django.db.models import F
import pdb, calendar

class querySQL:

    # Nelson Lugo
    def getPUC() :
        try:
            db = connection.cursor()
            sql= """
                SELECT json_agg(json_build_object('id',may.id, 'label',concat(may."codigo",' - ',may."nombre"), 'codigo',may."codigo",'tipo',may.tipo,'estado', may.estado, 'children',
                    (
                        SELECT json_agg(json_build_object('id',may2.id, 'label',concat(may2."codigo",' - ',may2."nombre"), 'codigo',may2."codigo",'tipo',may2.tipo,'estado', may2.estado,
                        'children',
                        (
                            SELECT json_agg(json_build_object('id',may4.id, 'label',concat(may4."codigo",' - ',may4."nombre"), 'codigo',may4."codigo",'tipo',may4.tipo,'estado', may4.estado,
                            'children',
                        (
                            SELECT json_agg(json_build_object('id',may6.id, 'label',concat(may6."codigo",' - ',may6."nombre"), 'codigo',may6."codigo",'tipo',may6.tipo,'estado', may6.estado,
                            'children',
                        (
                            SELECT json_agg(json_build_object('id',may8.id, 'label',concat(may8."codigo",' - ',may8."nombre"), 'codigo',may8."codigo",'tipo',may8.tipo,'estado', may8.estado,
                            'children',
                        (
                            SELECT json_agg(json_build_object('id',may10.id, 'label',concat(may10."codigo",' - ',may10."nombre"), 'codigo',may10."codigo",'tipo',may10.tipo,'estado', may10.estado,
                            'children',
                        (
                            SELECT json_agg(json_build_object('id',may12.id, 'label',concat(may12."codigo",' - ',may12."nombre"), 'codigo',may12."codigo",'tipo',may12.tipo, 'estado', may12.estado) ORDER BY may12."codigo") 
                            FROM public.contabilidad_mayor as may12
                            where length(may12."codigo") = 12
                            and may12."codigo" like  ('' || may10."codigo" || '%')
                        )
                        ) ORDER BY may10."codigo") 
                            FROM public.contabilidad_mayor as may10
                            where length(may10."codigo") = 10
                            and may10."codigo" like  ('' || may8."codigo" || '%')
                        )
                        ) ORDER BY may8."codigo") 
                            FROM public.contabilidad_mayor as may8
                            where length(may8."codigo") = 8
                            and may8."codigo" like  ('' || may6."codigo" || '%')
                        )
                        ) ORDER BY may6."codigo") 
                            FROM public.contabilidad_mayor as may6
                            where length(may6."codigo") = 6
                            and may6."codigo" like  ('' || may4."codigo" || '%')
                        )
                        ) ORDER BY may4."codigo") 
                            FROM public.contabilidad_mayor as may4
                            where length(may4."codigo") = 4
                            and may4."codigo" like  ('' || may2."codigo" || '%')
                        )
                        ) ORDER BY may2."codigo")  
                        FROM public.contabilidad_mayor as may2
                        where length(may2."codigo") = 2 
                        and may2."codigo" like  ('' || may."codigo" || '%')
                    ))) from (
                        select * FROM public.contabilidad_mayor as may where length(may."codigo") = 1 order by may."codigo" ) as may
            """
            db.execute(sql)
        except: 
            return []
        finally:
            resultado = db.fetchall()
            db.close()
            return resultado[0][0]
    
    # Nelson Lugo
    def getCuentasAuxiliares(cuentaMayor) :
        try:
            db = connection.cursor()
            sql= """
                select 
                    json_agg(json_build_object(
                        'id', my.id,
                        'codigo', my.codigo,
                        'estado', my.estado,
                        'saldo', case when my.saldo is null then 0 else my.saldo end
                )) 
                from (
                    select 
                        cm.id as id,
                        cm."codigo" as codigo,
                        cm.estado as estado,
                        cs.sal03 as saldo 
                    from contabilidad_mayor cm 
                    left join cont_saldos cs on cs.mayor_id = cm.id 
                    where cm."codigo" > '{}'
                    and cm."codigo" <= '{}99'
                    order by cm."codigo"
                ) as my;
                """.format(cuentaMayor, cuentaMayor)
            db.execute(sql)
        except: 
            return []
        finally:
            resultado = db.fetchall()
            db.close()
            return resultado[0][0]

    # Nelson Lugo
    def validar_rango_resolucion(tipo_documento_id:int, num_facturas:int):

        if num_facturas < 0 :
            return {
                "disponibles": 0,
                "msg": "Número de facturas a facturar no enviadas",
                "status": False,
                'tipo_factura_id': tipo_documento_id
            }
        
        tipo_documento = TiposDocumentos.objects.filter(id=tipo_documento_id, estado=True).first()
        if not tipo_documento:
            return {
                "disponibles": 0,
                "msg": "No se encontro el tipo de documento o se encuentra facturar inactivo",
                "status": False,
                'tipo_factura': tipo_documento_id
            }

        facturas_disponibles = tipo_documento.resoluciones.filter(tipo_documento_id=tipo_documento_id).annotate(facturas_disponibles=F('rango_final') - F('consecutivo_actual')).values_list('facturas_disponibles', flat=True)
        resultado = facturas_disponibles[0]
        
        if resultado <= 0 :
            return {
                "disponibles": resultado,
                "msg": "Numeración agotada, por favor solicite nueva resolución para {}.".format(tipo_documento.nombre.capitalize()),
                "status": False,
                'tipo_factura_id': tipo_documento_id
            }

        total = resultado - num_facturas

        if total < 0 :
            return {
                "disponibles": resultado,
                "msg": "Numeración insuficiente para {}. Cantidad de facturas disponibles: {}".format(tipo_documento.nombre.capitalize(), resultado),
                "status": False,
                'tipo_factura_id': tipo_documento_id
            }

        return {
            "disponibles": resultado,
            "msg": "Cantidad de facturas disponibles para {}: {}".format(tipo_documento.nombre.capitalize(), total),
            "status": True,
            'tipo_factura_id': tipo_documento_id
        }

    # Nelson Lugo
    def consulta_de_documentos(filtros) :
        doc_id = None
        tipo_consulta = filtros["tipoconsulta"]
        try :
            # pdb.set_trace()
            fecha_inicio = datetime.strptime(filtros["fecha_inicio"], "%Y-%m-%d").strftime("%Y-%m-%d")
            fecha_fin = datetime.strptime(filtros["fecha_fin"], "%Y-%m-%d").strftime("%Y-%m-%d")
            tipo_fuente = filtros["tipo_documento"]
            tipo_documento = filtros["tipobusqueda"]
        except :
            pass
            
        try :
            doc_id = filtros["id"]
        except :
            pass

        if doc_id != None :
            # El doc_id debe llegar de la siguiente forma: [1,2,3,4,5]
            ids = ', '.join(map(str, doc_id))
            sql_filtros = f" where cd.id in ({ids})"
        elif not filtros.get("documento", None) in ["", None] :
            documento = filtros["documento"].split(";")
            if len(documento) > 1 :
                # Rango de documento
                sql_filtros = f" where cd.numero between '{documento[0]}' and '{documento[1]}'"

                if tipo_documento != 0 :
                    sql_filtros += f" and ctd.id = {tipo_documento}"
            else :
                # Un documento
                sql_filtros = f" where cd.numero = '{documento[0]}'"
        else :
            sql_filtros = f" where cd.fecha between '{fecha_inicio}' and '{fecha_fin}'"

            if len(filtros.get("estado", [])) > 0 :
                sql_filtros += " and cd.estado in ("
                for i, item in enumerate(filtros.get("estado", [])) :
                    sql_filtros += str(item)
                    if (i + 1) < len(filtros.get("estado", [])) :
                        sql_filtros += ", "
                    else :
                        sql_filtros += ")"
            
            sql_filtros += f" and cf.id = {tipo_fuente}"

            if tipo_documento != 0 :
                sql_filtros += f" and ctd.id = {tipo_documento}"
            
            if filtros.get("usuario", 0) != 0 :
                sql_filtros += f' and cd.conf_usuarios_id = {filtros["usuario"]}'
        
        mov = ""
        encabezado = ""
        fpago = ""
        if tipo_consulta == 1 :
            # Listado de documentos
            encabezado = "null as enca"
            mov = "'[]'::json as mov"
            fpago = """
                    (case when cd.fpago = '1' 
                        then 'EFECTIVO' 
                    when cd.fpago = '2' 
                        then 'CHEQUE' 
                    when cd.fpago = '3' 
                        then 'TRANSFERENCIA' 
                    end) as fpago
                """
        else :
            # Documento contable
            fpago = "null as fpago"
            encabezado = """
                ( case 
                    when cf.id = 1 then
                        json_build_object(
                            'tipo', concat(ctd.tipo, ' - ', ctd.nombre),
                            'concepto', (select concat(cc.codigo, ' - ', cc.nombre) from contabilidad_conceptos cc where cc.id = cd.concepto_id),
                            'persona', concat(tp.documento, ' - ', tp.n_completo),
                            'fecha', cd.fecha,
                            'efectivo', coalesce(pefectivo.valor, 0)::int,
                            'consignacion', coalesce(pconsig.valor, 0)::int,
                            'cheque', coalesce(pcheque.valor, 0)::int,
                            'tarjeta', coalesce(ptarjeta.valor, 0)::int,
                            'total', coalesce(cd.total, 0)::int,
                            'detalle', coalesce(cd.detalle, '')
                        )
                    when cf.id = 2 then
                        json_build_object(
                            'tipo', concat(ctd.tipo, ' - ', ctd.nombre),
                            'concepto', (select concat(cc.codigo, ' - ', cc.nombre) from contabilidad_conceptos cc where cc.id = cd.concepto_id),
                            'persona', concat(tp.documento, ' - ', tp.n_completo),
                            'fecha', cd.fecha,
                            'efectivo', coalesce(pefectivo.valor, 0)::int,
                            'consignacion', coalesce(pconsig.valor, 0)::int,
                            'cheque', coalesce(pcheque.valor, 0)::int,
                            'total', coalesce(cd.total, 0)::int,
                            'cta_orig', coalesce((select cc.nombre from contabilidad_cuentabancaria cc where cc.id = ptransf.cuenta_origen_id), ''),
                            'cta_dest', coalesce(ptransf.cuenta_destino, ''),
                            'detalle', coalesce(cd.detalle, ''),
                            'banco', coalesce((select cb.nombre from conf_bancos cb where cb.id = ptransf.banco_destino_id limit 1), '')
                        )
                    when cf.id = 3 then
                        json_build_object(
                            'tipo', concat(ctd.tipo, ' - ', ctd.nombre),
                            'fecha', cd.fecha,
                            'concepto', (select concat(cc.codigo, ' - ', cc.nombre) from contabilidad_conceptos cc where cc.id = cd.concepto_id),
                            'doc_ref', (case when lower(cd.referencia) <> 'none' then coalesce(cd.referencia, '') else '' end),
                            'detalle', coalesce(cd.detalle, '')
                        )
                    when cf.id = 4 then
                        json_build_object(
                            'tipo', concat(ctd.tipo, ' - ', ctd.nombre),
                            'fecha', cd.fecha,
                            'concepto', (select concat(cc.codigo, ' - ', cc.nombre) from contabilidad_conceptos cc where cc.id = cd.concepto_id),
                            'doc_ref', (case when lower(cd.referencia) <> 'none' then coalesce(cd.referencia, '') else '' end),
                            'detalle', coalesce(cd.detalle, ''),
                            --'nofactura_proveedor', coalesce(cd.nofactura_proveedor, null),
                            'doc_soporte', case when cd.tipo_documento_id = (select cp.valor::integer from parametros_parametros cp where cp.parametro = 'doc_soporte_id') then true else false end
                        )
                    end
                ) as enca
            """

            mov = """
                (
                    select (
                        coalesce(json_agg(json_build_object(
                            'codigo', mov.codigo,
                            'cuenta', mov.cuenta,
                            'nombre', mov.nombre,
                            'concepto', mov.concepto,
                            'detalle', mov.detalle,
                            'debito', mov.debito,
                            'credito', mov.credito
                        )), '[]'::json)
                    ) from (
                        select 
                            cy."codigo" as codigo,
                            cy."nombre" as cuenta,
                            concat('[', tp2.documento, '] ', tp2.n_completo) as nombre,
                            (select cc.codigo from contabilidad_conceptos cc where cc.id = cm.concepto_id limit 1) as concepto,
                            cm.detalle as detalle,
                            cm.valor_db::integer as debito,
                            cm.valor_cr::integer as credito
                        from contabilidad_mov cm 
                        inner join contabilidad_mayor cy on cy.id = cm.mayor_id
                        inner join personas_persona tp2 on tp2.id = cm.persona_id
                        where cm.documento_id = cd.id
                        order by cm.id asc
                    ) as mov
                ) as mov
            """
        
        sql = """
            select 
                json_agg(json_build_object(
                    'tipo', obj.tipo,
                    'auto', (case when obj.automatico is true then 'SI' else 'NO' end), 
                    'numero', obj.numero,
                    'fecha', obj.fecha,
                    'nombre', obj.n_completo,
                    'documento', obj.documento,
                    'detalle', obj.detalle,
                    'total', obj.total,
                    'estado', (
                        case when obj.estado = 1 then
                            'ABIERTO'
                        when obj.estado = 2 then
                            'CERRADO'
                        when obj.estado = 3 then
                            'ANULADO'
                        else 
                            'REABIERTO'
                        end
                    ),
                    'usuario', obj.usuario,
                    'fuente', obj.fuente,
                    'mov', obj.mov,
                    'enca', obj.enca,
                    'fpago', obj.fpago
            )) 
            from (
                select 
                    ctd.tipo,
                    cd.numero,
                    cd.fecha,
                    tp.n_completo,
                    tp.documento,
                    cd.detalle,
                    (case when cd.total is not null then cd.total else (case when cd.gtotal is not null then cd.gtotal else 0 end) end) total,
                    cd.id,
                    cd.estado,
                    coalesce(cd.automatico, false) as automatico,
                    (select concat(au.first_name, ' ', au.last_name) from accounts_usuario au where au.id = cd.uc_id) as usuario,
                    cf.id as fuente,
                    {},
                    {},
                    {}
                from cont_documentos cd 
                inner join contabilidad_tipos_documentos ctd on ctd.id = cd.tipo_documento_id 
                inner join contabilidad_fuentes cf on cf.id = ctd.fuentes_id
                inner join personas_persona tp on tp.id = cd.personas_id
                left join lateral (
                    select pe.*
                    from contabilidad_pagodocumento cpd
                    inner join contabilidad_pagoefectivo pe on pe.pago_id = cpd.id
                    where cpd.documento_id = cd.id
                    and cpd.forma_pago_id = 1  -- Efectivo
                    limit 1
                ) pefectivo on true
                left join lateral (
                    select pc.*
                    from contabilidad_pagodocumento cpd
                    inner join contabilidad_pagoconsignacion pc on pc.pago_id = cpd.id
                    where cpd.documento_id = cd.id
                    and cpd.forma_pago_id = 2  -- Consignación
                    limit 1
                ) pconsig on true
                left join lateral (
                    select pp.*
                    from contabilidad_pagodocumento cpd
                    inner join contabilidad_pagotarjeta pp on pp.pago_id = cpd.id
                    where cpd.documento_id = cd.id
                    and cpd.forma_pago_id = 3  -- Tarjeta
                    limit 1
                ) ptarjeta on true
                left join lateral (
                    select pch.*
                    from contabilidad_pagodocumento cpd
                    inner join contabilidad_pagocheque pch on pch.pago_id = cpd.id
                    where cpd.documento_id = cd.id
                    and cpd.forma_pago_id = 4  -- Cheque
                    limit 1
                ) pcheque on true
                left join lateral (
                    select pt.*
                    from contabilidad_pagodocumento cpd
                    inner join contabilidad_pagotransferencia pt on pt.pago_id = cpd.id
                    where cpd.documento_id = cd.id
                    and cpd.forma_pago_id = 5  -- Transferencia
                    limit 1
                ) ptransf on true
                {}
                order by cd.id desc
            ) as obj
        """.format(encabezado, mov, fpago, sql_filtros)

        db = connection.cursor()
        db.execute(sql)
        # pdb.set_trace()
        resultado = db.fetchall()
        db.close()
        gran_total = 0
        try :
            resultado = resultado[0][0]
            if resultado != None :
                for item in resultado :
                    valor_db = 0
                    valor_cr = 0
                    gran_total += item["total"]
                    if tipo_consulta == 2 :
                        for mov in item["mov"] :
                            valor_db += mov["debito"]
                            valor_cr += mov["credito"]
                    item["total_db"] = valor_db
                    item["total_cr"] = valor_cr
                    item["gran_total"] = gran_total
            else :
                resultado = []
        except :
            resultado = []
        
        return resultado
    
    def total_novedades_mes(mes, anio, periodo) :
        sql = f"""
            select 
                coalesce(json_agg(json_build_object(
                    'novedad', obj.novedad,
                    'documento', obj.documento,
                    'n_completo', obj.n_completo,
                    'descripcion', obj.descripcion,
                    'valor', obj.valor,
                    'base', obj.base,
                    'fecha_inicio', obj.fecha_inicio,
                    'fecha_final', obj.fecha_final,
                    'registrada_por', obj.registrada_por,
                    'automatica', obj.automatica,
                    'periodo', '{periodo}'
                )), '[]')
            from (
                select
                    nn.nombre as novedad,
                    tp.documento,
                    tp.n_completo,
                    nc.descripcion,
                    nc.valor,
                    nt.nombre as base,
                    to_char(nc.fecha_inicial, 'DD/MM/YYYY HH:MI AM') as fecha_inicio,
                    to_char(nc.fecha_final, 'DD/MM/YYYY HH:MI AM') as fecha_final,
                    (select concat(au.first_name, ' ', au.last_name) from accounts_usuario au where au.id = nc.uc_id) as registrada_por,
                    nn.automatica
                from nomina_contratonominanovedades nc 
                inner join nomina_novedades nn on nn.id = nc.novedad_id
                inner join nomina_tipovalornovedad nt on nt.id = nn.tipo_valor_novedad_id
                inner join nomina_contrato nc2 on nc2.id = nc.contrato_id
                inner join personas_persona tp on tp.id = nc2.personas_id
                where extract(month from nc.fecha_inicial) = {mes}
                and extract(year from nc.fecha_inicial) = {anio}
                order by n_completo asc
            ) as obj;
        """
        db = connection.cursor()
        db.execute(sql)
        resultado = db.fetchall()
        db.close()
        try :
            resultado = resultado[0][0]
        except :
            resultado = []
        
        return resultado

    def consulta_basica_inmueble(direccion) :
        sql = f"""
            select coalesce(json_agg(json_build_object(
                'id', obj.id,
                'direccion', obj.direccion,
                'ciudad', obj.ciudad,
                'barrio', obj.barrio,
                'tipo_inmueble', obj.tipo_inmueble
            )), '[]')
            from (
                select
                    ii.id,
                    ii.direccion,
                    uc.nombre as ciudad,
                    ub.nombre as barrio,
                    iti.nombre as tipo_inmueble
                from inmueble_inmuebles ii
                left join parametros_ubicacion_ciudades uc on uc.id = ii.ciudad_id
                left join parametros_ubicacion_barrios ub on ub.id = ii.barrio_id
                left join inmueble_tipos_inmuebles iti on iti.id = ii.tipo_inmueble_id
                where lower(ii.direccion) like '%{direccion}%'
                order by ii.direccion asc
            ) as obj;
        """
        db = connection.cursor()
        db.execute(sql)
        resultado = db.fetchall()
        db.close()
        try :
            resultado = resultado[0][0]
        except :
            resultado = []
        
        return resultado
    
    def consulta_barrios(ciudad_id=None) :
        ciudad_id = "NULL" if ciudad_id is None else ciudad_id
        sql = f"""
            select coalesce(json_agg(json_build_object(
                'id', obj.id,
                'nombre', obj.nombre,
                'zonas_id', obj.zonas_id,
                'zonas', lower(obj.zonas),
                'ciudad_id', obj.ciudad_id,
                'ciudad', obj.ciudad
            )), '[]') from
            (
                select
                    ub.id,
                    ub.nombre,
                    ub.zonas_id,
                    uz.nombre as zonas,
                    ub.ciudad_id,
                    uc.nombre as ciudad
                from parametros_ubicacion_barrios ub
                left join parametros_ubicacion_ciudades uc on uc.id = ub.ciudad_id
                left join parametros_ubicacion_zonas uz on uz.id = ub.zonas_id
                where ({ciudad_id} is null or ub.ciudad_id = {ciudad_id})
                order by ub.nombre
            ) as obj;
        """

        db = connection.cursor()
        db.execute(sql)
        resultado = db.fetchall()
        db.close()
        
        try :
            resultado = resultado[0][0]
        except :
            resultado = []
        
        return resultado

    def personas_asociadas_a_un_inmueble(inmueble_id) :
        sql = f"""
            select coalesce(json_agg(resultado), '[]'::json) as resultado_json
            from (
                select 
                    tp.id,
                    'arrendatario' as tipo_relacion,
                    tp.documento,
                    tp.n_completo as persona,
                    concat(tp.documento, ' - ', tp.n_completo) as documento_persona,
                    concat(tp.documento, ' - ', tp.n_completo, ' [Arrendatario]') as documento_persona_relacion
                from inmueble_inmuebles ii
                inner join contrato_contratos cc on ii.id = cc.inmueble_id
                inner join solicitud_solicitudes ss on cc.solicitud_id = ss.id
                inner join personas_persona tp on ss.solicitante_id = tp.id
                where ii.id = {inmueble_id}
                union all
                select 
                    tp2.id,
                    'propietario' as tipo_relacion,
                    tp2.documento,
                    tp2.n_completo as persona,
                    concat(tp2.documento, ' - ', tp2.n_completo) as documento_persona,
                    concat(tp2.documento, ' - ', tp2.n_completo, ' [Propietario]') as documento_persona_relacion
                from inmueble_inmuebles ii
                inner join inmueble_propietarios ip on ii.id = ip.inmueble_id
                inner join personas_persona tp2 on ip.persona_id = tp2.id
                where ii.id = {inmueble_id}
                union all
                select 
                    tp3.id,
                    'codeudor' as tipo_relacion,
                    tp3.documento,
                    tp3.n_completo as persona,
                    concat(tp3.documento, ' - ', tp3.n_completo) as documento_persona,
                    concat(tp3.documento, ' - ', tp3.n_completo, ' [Codeudor]') as documento_persona_relacion
                from inmueble_inmuebles ii
                inner join contrato_contratos cc on ii.id = cc.inmueble_id
                inner join solicitud_solicitudes ss on cc.solicitud_id = ss.id
                inner join solicitud_solicitudes_codeudores ssc on ss.id = ssc.solicitud_id
                inner join personas_persona tp3 on ssc.codeudor_id = tp3.id
                where ii.id = {inmueble_id}
            ) as resultado;
        """
        db = connection.cursor()
        db.execute(sql)
        resultado = db.fetchall()
        db.close()
        
        try :
            resultado = resultado[0][0]
        except :
            resultado = []
        
        return resultado
    
    def ciudades_inmuebles_disponibles() :
        sql = f"""
            select coalesce(json_agg(data order by data.nombre asc), '[]'::json)
            from (
                select
                    uc.id,
                    uc.nombre, 
                    count(ii.id) as disponibles
                from ubicacion_ciudades uc
                left join inmueble_inmuebles ii on ii.ciudad_id = uc.id and ii.estado_actual_id = 1
                where lower(uc.nombre) <> 'sin ciudad'
                and trim(uc.nombre) <> ''
                group by uc.id, uc.nombre
                having count(ii.id) > 0
            ) as data;
        """
        db = connection.cursor()
        db.execute(sql)
        resultado = db.fetchall()
        db.close()
        try :
            resultado = resultado[0][0]
        except :
            resultado = []
        
        return resultado

    def barrios_inmuebles_disponibles() :
        sql = f"""
            select coalesce(json_agg(data), '[]'::json)
            from (
                select
                    ub.id,
                    lower(trim(ub.nombre)) as barrio, 
                    lower(trim(uc.nombre)) as ciudad,
                    count(ii.id) as disponibles
                from ubicacion_barrios ub
                left join ubicacion_ciudades uc on uc.id = ub.ciudad_id 
                left join inmueble_inmuebles ii on ii.barrio_id = ub.id and ii.estado_actual_id = 1
                where lower(ub.nombre) <> 'sin definir'
                and trim(ub.nombre) <> ''
                group by ub.id, ub.nombre, uc.nombre
                having count(ii.id) > 0
                order by ub.nombre asc
            ) as data;
        """
        db = connection.cursor()
        db.execute(sql)
        resultado = db.fetchall()
        db.close()
        try :
            resultado = resultado[0][0]
        except :
            resultado = []
        
        return resultado

    def informe_desocupaciones_programadas(fecha_ini, fecha_fin) :
        concepto_canon = int(Parametros.objects.filter(parametro='contrato_concepto_canon').first().valor)
        sql = f"""
            select
                json_agg(json_build_object(
                    'id', cc.id,
                    'contrato', cc.numero_contrato,
                    'inmueble_id', cc.inmueble_id,
                    'direccion', ii.direccion,
                    'ciudad_inmueble', (select ub.nombre from ubicacion_ciudades ub where ub.id = ii.ciudad_id),
                    'observcion_inmueble', ii.observacion,
                    'documento', sol.documento,
                    'arrendatario', sol.n_completo,
                    'telefono', (select tt.valor from tercero_telefonos tt where tt.persona_id = sol.id limit 1),
                    'correo_arrendatario', sol.email,
                    'documento_propietario', prop.documento,
                    'nombre_propietario', prop.n_completo,
                    'telefono_propietario', (select tt.valor from tercero_telefonos tt where tt.persona_id = prop.id limit 1),
                    'correo_propietario', prop.email,
                    'documento_administracion', admon.documento,
                    'nombre_administracion', admon.n_completo,
                    'canon', (select coalesce(ccc.valor::integer, 0) from contrato_contrato_conceptos ccc where ccc.contrato_id = cc.id and ccc.concepto_id = {concepto_canon} limit 1),
                    'valor_admon', coalesce(cc.admon_neta, 0),
                    'fecha_desocupacion', cc.fecha_desocupacion,
                    'obj_estado', (select json_build_object(
                        'id', pep.id,
                        'nombre', pep.nombre,
                        'color', pep.color,
                        'color_letra', pep.color_letra
                    ) from public_estados_procesos pep where pep.id = cc.estado_id) 
                ) order by cc.fecha_desocupacion asc)
            from contrato_contratos cc
            inner join solicitud_solicitudes ss on ss.id = cc.solicitud_id
            inner join personas_persona sol on sol.id = ss.solicitante_id
            inner join inmueble_inmuebles ii on ii.id = cc.inmueble_id
            inner join consignacion_consignaciones con on con.inmueble_id = ii.id and con.estado_actual_id <> 17
            inner join inmueble_propietarios ip on ip.inmueble_id = ii.id and ip.consignacion_id = con.id and ip.activo is true
            inner join personas_persona prop on prop.id = ip.persona_id
            left join personas_persona admon on admon.id = ii.administracion_id
            where cc.fecha_desocupacion between '{fecha_ini}' and '{fecha_fin}'
        """

        db = connection.cursor()
        db.execute(sql)
        resultado = db.fetchall()
        db.close()
        try :
            resultado = resultado[0][0]
        except :
            resultado = []
        
        return resultado
    
    def historico_contratos_persona(persona_id) :
        sql = f"""
            -- cte principal que incluye todos los datos necesarios
            with 
            -- deudores: agrupa por id_deudor e id_solicitud para evitar repetidos
            deudores as (
                select 
                    ssc.codeudor_id,
                    ssc.solicitud_id
                from solicitud_solicitudes_codeudores ssc
                where ssc.codeudor_id = {persona_id}
                group by ssc.codeudor_id, ssc.solicitud_id
            ),
            -- propietarios: agrupa por id_persona e id_inmueble para evitar repetidos
            propietarios as (
                select
                    ip.persona_id,
                    ip.inmueble_id
                from inmueble_propietarios ip
                where ip.persona_id = {persona_id}
                group by ip.persona_id, ip.inmueble_id
            ),
            -- contratos de arrendatarios: agrupa por # contrato e inmueble
            contratos_arrendatario as (
                select
                    max(cc.id) as id
                from contrato_contratos cc
                inner join solicitud_solicitudes ss on ss.id = cc.solicitud_id
                where ss.solicitante_id = {persona_id}
                and exists (select * from solicitud_historicalsolicitud shs where shs.estado_id = 9 and shs.id = ss.id) -- Validar si esa solicitud si pasó a estado en contrato y no fue rechazado o desistido
                group by cc.numero_contrato, cc.inmueble_id
            ),
            -- contratos de deudores: agrupa por # contrato e inmueble
            contratos_deudor as (
                select
                    max(cc.id) as id
                from contrato_contratos cc
                inner join deudores deu on deu.solicitud_id = cc.solicitud_id
                group by cc.numero_contrato, cc.inmueble_id
            ),
            -- contratos de propietarios: agrupa por # contrato e inmueble
            contratos_propietario as (
                select
                    max(cc.id) as id
                from contrato_contratos cc
                inner join propietarios pr on pr.inmueble_id = cc.inmueble_id
                group by cc.numero_contrato, cc.inmueble_id
            ),
            -- unión de todos los resultados
            resultado_union as (
                -- consulta 1: arrendatarios
                select
                    ii.id as id_inmueble,
                    concat('[', cc.inmueble_id, '] - ', ii.direccion) as inmueble,
                    (select pep.nombre from public_estados_procesos pep where pep.id = ii.estado_actual_id) as estado,
                    (
                        select ctc.nombre
                        from consignacion_consignaciones con
                        inner join consignacion_tipos_consignaciones ctc on ctc.id = con.tipo_consignacion_id
                        where con.inmueble_id = ii.id
                        order by con.id desc 
                        limit 1
                    ) as tipo_consignacion,
                    cc.numero_contrato,
                    (select pep.nombre from public_estados_procesos pep where pep.id = cc.estado_id) as estado_contrato,
                    'arrendatario' as tipo_relacion
                from contrato_contratos cc
                inner join inmueble_inmuebles ii on ii.id = cc.inmueble_id
                where cc.id in (select con.id from contratos_arrendatario con)

                union all

                -- consulta 2: deudores
                select
                    ii.id as id_inmueble,
                    concat('[', cc.inmueble_id, '] - ', ii.direccion) as inmueble,
                    (select pep.nombre from public_estados_procesos pep where pep.id = ii.estado_actual_id) as estado,
                    (
                        select ctc.nombre
                        from consignacion_consignaciones con
                        inner join consignacion_tipos_consignaciones ctc on ctc.id = con.tipo_consignacion_id
                        where con.inmueble_id = ii.id
                        order by con.id desc 
                        limit 1
                    ) as tipo_consignacion,
                    cc.numero_contrato,
                    (select pep.nombre from public_estados_procesos pep where pep.id = cc.estado_id) as estado_contrato,
                    'deudor' as tipo_relacion
                from contrato_contratos cc
                inner join inmueble_inmuebles ii on ii.id = cc.inmueble_id
                where cc.id in (select con.id from contratos_deudor con)

                union all

                -- consulta 3: propietarios
                select
                    ii.id as id_inmueble,
                    concat('[', cc.inmueble_id, '] - ', ii.direccion) as inmueble,
                    (select pep.nombre from public_estados_procesos pep where pep.id = ii.estado_actual_id) as estado,
                    (
                        select ctc.nombre
                        from consignacion_consignaciones con
                        inner join consignacion_tipos_consignaciones ctc on ctc.id = con.tipo_consignacion_id
                        where con.inmueble_id = ii.id
                        order by con.id desc 
                        limit 1
                    ) as tipo_consignacion,
                    cc.numero_contrato,
                    (select pep.nombre from public_estados_procesos pep where pep.id = cc.estado_id) as estado_contrato,
                    'propietario' as tipo_relacion
                from contrato_contratos cc
                inner join inmueble_inmuebles ii on ii.id = cc.inmueble_id
                where cc.id in (select con.id from contratos_propietario con)
            )

            -- convertir el resultado a un array de objetos json
            select coalesce(json_agg(
                json_build_object(
                    'inmueble_id', id_inmueble, 
                    'inmueble', inmueble,
                    'estado', estado,
                    'tipo_consignacion', tipo_consignacion,
                    'numero_contrato', numero_contrato,
                    'estado_contrato', estado_contrato,
                    'tipo_relacion', tipo_relacion
                ) order by tipo_relacion, inmueble
            ), '[]') as contratos_array
            from resultado_union;
        """
        db = connection.cursor()
        db.execute(sql)
        resultado = db.fetchall()
        db.close()
        try :
            resultado = resultado[0][0]
        except :
            resultado = []
        
        return resultado
