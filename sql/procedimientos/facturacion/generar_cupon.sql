CREATE OR REPLACE FUNCTION public.generar_cupon(
    in_afiliado_id integer[],
    in_usuario_id  integer
)
RETURNS TABLE (
    out_cupon_id integer,
    out_cupon_numero character varying
)
LANGUAGE plpgsql
AS $function$
DECLARE
    rec record;
    
    v_out_id integer;
    v_out_numero character varying;

    v_tipo_documento_cupon integer;
    v_dia_cobro_sinrecargo integer;
    v_dia1_cobro_conrecargo integer;
    v_porc_recargo1 character varying;
    v_iva_general integer;
    
    v_persona_id integer;
    v_afiliado_id integer;
    v_nombre_afiliado character varying;
    v_direccion_afiliado character varying;
    v_telefono_afiliado character varying;
    v_ciudad_afiliado character varying;
    
    v_numero_tipodoc integer;
    v_ndigitos_tipodoc integer;
    v_prefijo_tipodoc character varying;
    
    v_numero_cupon character varying;

    v_subtotal numeric;
    v_iva numeric;
    v_gtotal numeric;

    v_fecha1 date;
    v_fecha2 date;
    v_valor2 numeric;
    v_mes_id integer;
    v_anio_id integer;
BEGIN

    -- ═══════════════ Parámetros ═══════════════
    SELECT valor::integer INTO v_tipo_documento_cupon FROM parametros_parametros WHERE parametro = 'tipo_documento_cupon';
    SELECT valor::integer INTO v_dia_cobro_sinrecargo FROM parametros_parametros WHERE parametro = 'dia_cobro_sinrecargo';
    SELECT valor::integer INTO v_dia1_cobro_conrecargo FROM parametros_parametros WHERE parametro = 'dia1_cobro_conrecargo';
    SELECT valor INTO v_porc_recargo1 FROM parametros_parametros WHERE parametro = 'porc_recargo1';
    SELECT valor::integer INTO v_iva_general FROM parametros_parametros WHERE parametro = 'iva_general';

    SELECT
	    COALESCE(ctd.numero,0),
	    COALESCE(ctd.ndigitos,0),
	    COALESCE(ctd.prefijo,'')
	INTO
	    v_numero_tipodoc,
	    v_ndigitos_tipodoc,
	    v_prefijo_tipodoc
	FROM contabilidad_tipos_documentos ctd
	WHERE ctd.id = v_tipo_documento_cupon
	FOR UPDATE;

    FOREACH v_afiliado_id IN ARRAY in_afiliado_id LOOP
        
        v_iva := 0;
        v_subtotal := 0;
        v_gtotal := 0;

        -- ═══════════════ Datos del Afiliado ═══════════════
        SELECT persona_id INTO v_persona_id
        FROM afiliados_afiliado
        WHERE id = v_afiliado_id AND activo = true;

        IF v_persona_id IS NULL THEN
            RAISE EXCEPTION 'Afiliado % no existe o no está activo', v_afiliado_id;
        END IF;

        select 
            (case when pc.id = 1 then 
                ltrim(pp.n_completo) 
            else 
                case when pp.p_apellido <> null or pp.p_apellido <> '' then 
                    ltrim(concat(pp.p_apellido,' ' , pp.s_apellido ,' ', pp.p_nombre , ' ', pp.s_nombre)) 
                else ltrim(pp.n_completo) end 
            end) as n_completo,
            COALESCE(
                (
                    select td.descripcion from personas_direccion td 
                    left join personas_tipocontacto ttc  on ttc.id = td.tipo_id 
                    where ttc.nombre = 'Residencial' and td.persona_id = pp.id
                    limit 1
                )
                ,
                (
                    select  td.descripcion from personas_direccion td 
                    left join personas_tipocontacto ttc  on ttc.id = td.tipo_id 
                    where  td.persona_id = pp.id
                    limit 1
                )
            ) as direccion,
            COALESCE(
                (
                    select  tt.valor from personas_telefono tt 
                    left join personas_tipocontacto ttc2  on ttc2.id = tt.tipo_id 
                    where ttc2.nombre = 'Residencial' and tt.persona_id = pp.id
                    limit 1
                )
                ,
                (
                    select  tt.valor from personas_telefono tt 
                    left join personas_tipocontacto ttc2  on ttc2.id = tt.tipo_id 
                    where tt.persona_id = pp.id
                    limit 1
                )
            ) as telefono,
            RTRIM(COALESCE(
                (
                    select  uc.nombre from personas_direccion td 
                    left join personas_tipocontacto ttc  on ttc.id = td.tipo_id 
                    left join parametros_ubicacion_ciudades uc on uc.id = td.ciudad_id 
                    where ttc.nombre = 'Residencial' and td.persona_id = pp.id
                    limit 1
                )	
                ,
                (
                    select  uc.nombre from personas_direccion td 
                    left join personas_tipocontacto ttc  on ttc.id = td.tipo_id 
                    left join parametros_ubicacion_ciudades uc on uc.id = td.ciudad_id 
                    where  td.persona_id = pp.id
                    limit 1
                )
            )) as ciudadres
        into v_nombre_afiliado, v_direccion_afiliado, v_telefono_afiliado, v_ciudad_afiliado
        from personas_persona pp
        left join personas_personatributario ppt on pp.id = ppt.persona_id
        left join personas_contribuyente pc on pc.id = ppt.contribuyente_id
        where pp.id = v_persona_id;

        -- ═══════════════ Calcular el nuevo nro de cupon ═══════════════
        v_numero_tipodoc := v_numero_tipodoc + 1;

        UPDATE contabilidad_tipos_documentos
        SET numero = v_numero_tipodoc
        WHERE id = v_tipo_documento_cupon;

        v_numero_cupon := concat(
            rtrim(v_prefijo_tipodoc),
            lpad(v_numero_tipodoc::text, v_ndigitos_tipodoc, '0')
        );

        select 
            coalesce(sum(acc.valor), 0), 
            coalesce(sum(
                case when cc.iva then acc.valor * (v_iva_general / 100) else 0 end
            ), 0)
        into v_subtotal, v_iva
        FROM afiliados_afiliado_concepto_causacion acc
        JOIN afiliados_concepto_causacion cc ON cc.id = acc.concepto_id
        WHERE acc.afiliado_id = v_afiliado_id
        AND cc.activo  = true;

        v_gtotal := v_subtotal + v_iva;

        -- ═══════════════ Fechas y valores ═══════════════
        v_fecha1 := make_date(EXTRACT(YEAR FROM CURRENT_DATE)::integer, EXTRACT(MONTH FROM CURRENT_DATE)::integer, v_dia_cobro_sinrecargo);
        v_fecha2 := make_date(EXTRACT(YEAR FROM CURRENT_DATE)::integer, EXTRACT(MONTH FROM CURRENT_DATE)::integer, v_dia1_cobro_conrecargo);

        v_valor2 := v_gtotal + v_gtotal * (v_porc_recargo1::float / 100);

        -- ═══════════════ Mes y año ═══════════════
        v_mes_id := (select id from parametros_mes where numero = case when EXTRACT(MONTH FROM CURRENT_DATE) < 10 then concat('0',EXTRACT(MONTH FROM CURRENT_DATE)::varchar) else EXTRACT(MONTH FROM CURRENT_DATE)::varchar end);
        v_anio_id := (select id from parametros_anio where nombre = EXTRACT(YEAR FROM CURRENT_DATE));

        -- ═══════════════ Insertar cupon ═══════════════
        INSERT INTO contabilidad_cupones (
            fecha,
            numero,
            estado,
            nombre,
            direccion,
            telefono,
            ciudad,
            subtotal,
            iva,
            gran_total,
            fecha1,
            fecha2,
            pfecha2,
            valor1,
            valor2,
            afiliado_id,
            anio_id,
            mes_id,
            usuario_id,
            eliminado,
            unica_fecha          
        ) VALUES (
            CURRENT_DATE,
            v_numero_cupon,
            true,
            v_nombre_afiliado,
            v_direccion_afiliado,
            v_telefono_afiliado,
            v_ciudad_afiliado,
            v_subtotal,
            v_iva,
            v_gtotal,
            v_fecha1,
            v_fecha2,
            v_porc_recargo1,
            v_gtotal,
            v_valor2,
            v_afiliado_id,
            v_anio_id,
            v_mes_id,
            in_usuario_id,
            false,
            false
        ) RETURNING id, numero INTO v_out_id, v_out_numero;

        FOR rec IN (
            SELECT
                acc.detalle,
                acc.valor,
                cc.iva,
                cc.concepto_id
            FROM afiliados_afiliado_concepto_causacion acc
            JOIN afiliados_concepto_causacion cc ON cc.id = acc.concepto_id
            WHERE acc.afiliado_id = v_afiliado_id
            AND cc.activo  = true
        ) LOOP

            -- ═══════════════ Insertar detalle cupon ═══════════════
            INSERT INTO contabilidad_detalle_cupones (
                cupon_id,
                cantidad,
                detalle,
                valor,
                piva,
                concepto_id
            ) VALUES (
                v_out_id,
                '1',
                rec.detalle,
                rec.valor,
                case when rec.iva is true then v_iva_general else 0 end,
                rec.concepto_id
            );
        END LOOP;

        out_cupon_id := v_out_id;
        out_cupon_numero := v_out_numero;

        RETURN NEXT;

    END LOOP;

END;
$function$;