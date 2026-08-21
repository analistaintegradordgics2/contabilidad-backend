-- DROP FUNCTION public.getfacturacion_electro(int4, int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getfacturacion_electro(in_anio integer, in_mes integer, tipodoc integer, estadofact integer, in_personaid integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
DECLARE
        ------------------------------------------------------------------------------------------------------------------------
        --  Variables locales adicionales
        ------------------------------------------------------------------------------------------------------------------------

        obj json[];
        cont record;
        subtotal float;
        mes_texto varchar(2);
        saldo_ant json;
        contmes int;
        mes_numero int;
        mes_nit varchar;
        estado_nombre varchar;
        lcFdir text;
        lcFCiudad text;
        lcFMovil text;
        lcFtel text;
        lcFnombre text;

        -- Variables para manejo de cont_estadofact_id / numero_generado vía contabilidad_factelectronicadocumento
        lnEstadoFactAntes integer;
        lbFaltaDireccion boolean;
        lbFaltaMovil boolean;
        lbFaltaCiudad boolean;
        lbFaltaEmail boolean;
        lbExisteFactElectronica boolean;
begin

        ------------------------------------------------------Parametros necesarios para utilizar en el proceso ----------------------------------------------------------


        for cont in
            select
                    ltrim(doc.numero,(select ctd.prefijo from contabilidad_tipos_documentos ctd where ctd.id = doc.tipo_documento_id))::numeric as solo_numero,
                    doc.id as id,
                    doc.id as contrato_id,
                    doc.fecha as fecha,
                    doc.numero as numero,
                    COALESCE(cfe.estado_id, 1) as estado_fact_id,
                    doc.estado as estado,
                    doc.subtotal as valor_subtotal,
                    doc.gtotal as gtotal,
                    doc.iva as iva,
                    doc.detalle as detalle,
                    cfe.numero_generado as numero_generado,
                    cfe.numero_generado as documento_generado,
                    cfe.observacion as observacion_electronica,
                    doc.tipo_documento_id as tipo_documento_id,
                    per.email as email,
                    doc.personas_id as personas,
                    doc.referencia as referencia,
                    doc.ciudad as ciudad,
                    doc.direccion as direccion,
                    ltrim(doc.movil) as movil,
                    ltrim(doc.telefono) as telefono,
                    (case when doc.estado = 1 then
                            'Abierto'
                    else
                            case when  doc.estado = 2 then
                                    'Cerrado'
                            else
                                    case when doc.estado = 3 then
                                            'Anulado'
                                    else
                                            case when doc.estado = 4 then
                                                    'Reabierto'
                                            end
                                    end
                            end
                    end) as estado_documento,
                    (select es.nombre from contabilidad_estadofactelectro es where es.id = COALESCE(cfe.estado_id, 1)) as estado_fact,
                    (case when per.p_apellido  <> null or per.p_apellido <> '' then
                            ltrim(concat(per.p_apellido,' ' , per.s_apellido ,' ', per.p_nombre , ' ', per.s_nombre))
                    else ltrim(per.n_completo) end) as nombre,
                    per.documento as documento,
                    cfe.webservice,
                    (select tp.tipo_electronica from contabilidad_tipos_documentos tp where id = doc.tipo_documento_id limit 1) as tipo_electronica,
                    doc.prteiva as prteiva,
                    doc.prteica as prteica,
                    doc.prtefte as prtefte

            from cont_documentos doc
            inner join personas_persona per on per.id = doc.personas_id
            left join lateral (
                select cf.estado_id, cf.numero_generado, cf.observacion, cf.webservice
                from contabilidad_factelectronicadocumento cf
                where cf.documento_id = doc.id
                order by cf.id desc
                limit 1
            ) cfe on true
            where doc.tipo_documento_id = tipodoc
            and EXTRACT(month FROM doc.fecha) = in_mes
            and EXTRACT(year FROM doc.fecha) = in_anio
            and (case when estadofact > 0 then COALESCE(cfe.estado_id, 1) = estadofact else 1=1 end)

            order by solo_numero asc

        loop

            lnEstadoFactAntes := cont.estado_fact_id;
            lbFaltaDireccion := false;
            lbFaltaMovil := false;
            lbFaltaCiudad := false;
            lbFaltaEmail := false;

            select tp.n_completo,
                COALESCE(
                    (
                        select  ltrim(td.descripcion) from personas_direccion td
                        where td.incluir_a_factura = true and td.persona_id = tp.id
                        LIMIT 1

                    )
                    ,
                    (
                        select  ltrim(td.descripcion) from personas_direccion td
                        left join personas_tipocontacto ttc  on ttc.id = td.tipo_id
                        where  td.persona_id = tp.id
                        LIMIT 1
                    )
                ) as direccion,
                COALESCE(
                    (
                        select  ltrim(tt.valor) from personas_telefono tt
                        left join personas_tipocontacto ttc2  on ttc2.id = tt.tipo_id
                        where ttc2.nombre = 'Residencial' and tt.persona_id = tp.id and COALESCE(tt.eliminado,false) is false
                        LIMIT 1
                    )
                    ,
                    (
                        select  ltrim(tt.valor) from personas_telefono tt
                        left join personas_tipocontacto ttc2  on ttc2.id = tt.tipo_id
                        where tt.persona_id = tp.id and COALESCE(tt.eliminado,false) is false
                        limit 1
                    )
                ) as telefono,
                RTRIM(COALESCE(
                    (
                        select  ltrim(uc.nombre) from personas_direccion td
                        left join personas_tipocontacto ttc  on ttc.id = td.tipo_id
                        left join parametros_ubicacion_ciudades uc on uc.id = td.ciudad_id
                        where ttc.nombre = 'Residencial' and td.persona_id = tp.id
                        limit 1
                    )
                    ,
                    (
                        select  ltrim(uc.nombre) from personas_direccion td
                        left join personas_tipocontacto ttc  on ttc.id = td.tipo_id
                        left join parametros_ubicacion_ciudades uc on uc.id = td.ciudad_id
                        where  td.persona_id = tp.id
                        limit 1
                    )
                )) as ciudadres,
                COALESCE(
                    (
                        select  ltrim(tt.valor) from personas_telefono tt
                        left join personas_tipocontacto ttc2  on ttc2.id = tt.tipo_id
                        where ttc2.nombre = 'Residencial' and tt.persona_id = tp.id and COALESCE(tt.eliminado,false) is false
                        limit 1
                    )
                    ,
                    (
                        select  ltrim(tt.valor) from personas_telefono tt
                        left join personas_tipocontacto ttc2  on ttc2.id = tt.tipo_id
                        where tt.persona_id = tp.id and COALESCE(tt.eliminado,false) is false
                        limit 1
                    )
                ) as movil
                into lcFnombre, lcFdir, lcFtel, lcFCiudad, lcFMovil
                from personas_persona tp
                where tp.id = cont.personas;


            if lcFdir is not null and  lcFdir <> '' then
                if ltrim(cont.direccion) is null or ltrim(cont.direccion) = '' then
                    update cont_documentos
                    set direccion = lcFdir
                    where id = cont.id;
                end if;
            else
                if ltrim(cont.direccion) is null or ltrim(cont.direccion) = '' then
                    lbFaltaDireccion := true;
                end if;
            end if;

            if lcFMovil is not null and lcFMovil <> '' then
                if ltrim(cont.movil) is null or ltrim(cont.movil) = '' then
                    update cont_documentos
                    set movil = lcFMovil
                    where id = cont.id;
                end if;
            else
                if ltrim(cont.movil) is null or ltrim(cont.movil) = '' then
                    lbFaltaMovil := true;
                end if;
            end if;

            if lcFCiudad is not null and lcFCiudad <> '' then
                if ltrim(cont.ciudad) is null or ltrim(cont.ciudad) = '' then
                    update cont_documentos
                    set ciudad = lcFCiudad
                    where id = cont.id;
                end if;
            else
                if ltrim(cont.ciudad) is null or ltrim(cont.ciudad) = '' then
                    lbFaltaCiudad := true;
                end if;
            end if;

            if ltrim(cont.email) is null or ltrim(cont.email) = '' then
                lbFaltaEmail := true;
            end if;

            -- Si falta algún dato requerido y el estado actual es "Sin transmitir" (1), pasar a "Inconsistente" (6)
            -- Si todos los datos están completos y el estado actual es "Inconsistente" (6), resetear a "Sin transmitir" (1)
            IF (lbFaltaDireccion OR lbFaltaMovil OR lbFaltaCiudad OR lbFaltaEmail) THEN

                IF lnEstadoFactAntes = 1 THEN

                    select exists(
                        select 1 from contabilidad_factelectronicadocumento
                        where documento_id = cont.id
                    ) into lbExisteFactElectronica;

                    if lbExisteFactElectronica then
                        update contabilidad_factelectronicadocumento
                        set estado_id = 6,
                            modified = now()
                        where documento_id = cont.id;
                    else
                        insert into contabilidad_factelectronicadocumento(documento_id, estado_id, created, modified)
                        values (cont.id, 6, now(), now());
                    end if;

                    lnEstadoFactAntes := 6;
                END IF;

            ELSE

                IF lnEstadoFactAntes = 6 THEN

                    select exists(
                        select 1 from contabilidad_factelectronicadocumento
                        where documento_id = cont.id
                    ) into lbExisteFactElectronica;

                    if lbExisteFactElectronica then
                        update contabilidad_factelectronicadocumento
                        set estado_id = 1,
                            modified = now()
                        where documento_id = cont.id;
                    else
                        insert into contabilidad_factelectronicadocumento(documento_id, estado_id, created, modified)
                        values (cont.id, 1, now(), now());
                    end if;

                    lnEstadoFactAntes := 1;
                END IF;

            END IF;

            IF (
                (estadofact = 0 OR lnEstadoFactAntes = estadofact)
                AND (in_personaid = 0 OR cont.personas = in_personaid)
            ) THEN
                obj := obj || json_build_object(
                'nombre', cont.nombre,
                'documento', cont.documento,
                'email',cont.email,
                'fecha',cont.fecha,
                'id',cont.id,
                'direccion', cont.direccion,
                'ciudad', cont.ciudad,
                'numero',cont.numero,
                'contrato', null,
                'estado_fact_id', lnEstadoFactAntes,
                'estado',cont.estado,
                'subtotal',cont.valor_subtotal,
                'iva',cont.iva,
                'gtotal',cont.gtotal,
                'estado_fact', (select es.nombre from contabilidad_estadofactelectro es where es.id = lnEstadoFactAntes),
                'detalle',cont.detalle,
                'numero_generado',cont.numero_generado,
                'observacion_electronica',cont.observacion_electronica,
                'tipo_documento_id',cont.tipo_documento_id,
                'personas',cont.personas,
                'documento_generado',cont.documento_generado,
                'referencia',cont.referencia,
                'estado_documento',cont.estado_documento,
                'sol_numero',cont.solo_numero::numeric,
                'webservice', cont.webservice,
                'tipo_electronica', cont.tipo_electronica,
                'reteiva', case when cont.prteiva > 0 then (select case when cdf.prteiva > 0 then round(round(cdf.valor * (cdf.prteiva / 100)) * (case when cdf.piva > 0 then (cdf.piva/100) else 1 end)) else round(round(cdf.valor * (cont.prteiva / 100)) * (case when cdf.piva is not null then (cdf.piva/100) else 1 end)) end from contabilidad_detallefacturas cdf where documentos_id = cont.id and cdf.prteiva is not null limit 1) else 0 end,
                'reteica', case when cont.prteica > 0 then (select case when cdf.prteica > 0 then round(cdf.valor * (cdf.prteica / 100)) else round(cdf.valor * (cont.prteica / 100)) end from contabilidad_detallefacturas cdf where documentos_id = cont.id and cdf.prteica is not null limit 1) else 0 end,
                'retefuente', case when cont.prtefte > 0 then (select case when cdf.prtefuente > 0 then round(cdf.valor * (cdf.prtefuente / 100)) else round(cdf.valor * (cont.prtefte / 100)) end from contabilidad_detallefacturas cdf where documentos_id = cont.id and cdf.prtefuente is not null limit 1) else 0 end
                );
            END IF;

        end loop;

        return array_to_json(obj);


END
$function$
;