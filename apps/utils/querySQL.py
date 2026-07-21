from django.db import connection
from apps.contabilidad.models.tipodocumento import TiposDocumentos
from django.db.models import F
from datetime import datetime

class querySQL:

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
            ) as obj;
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