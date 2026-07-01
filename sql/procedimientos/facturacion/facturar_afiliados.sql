CREATE OR REPLACE FUNCTION public.facturar_afiliados(
    in_afiliado_id integer,
    in_mes         integer,
    in_anio        integer,
    in_usuario_id  integer
)
RETURNS TABLE (
    out_documento_id   integer,
    out_numero         character varying,
    out_tipo_factura   integer
)
LANGUAGE plpgsql
AS $function$
DECLARE
    rec             record;
    v_persona_id    integer;
    v_fecha         date;
    v_cta_cartera   integer;
    v_iva_general   numeric;
    v_preconta      json;
    v_detalle_fac   json;
    v_subtotal      numeric;
    v_iva_total     numeric;
    v_out_id        integer;
    v_out_doc       character varying;
    v_facturacion_id integer;
BEGIN

    -- ─── Parámetros globales ───
    -- SELECT valor::integer INTO v_cta_cartera
    -- FROM conf_parametros WHERE parametro = 'cta_cartera_afiliados_id';

    -- SELECT valor::numeric INTO v_iva_general
    -- FROM conf_parametros WHERE parametro = 'iva_general';

    -- IF v_cta_cartera IS NULL THEN
    --     RAISE EXCEPTION 'Falta parámetro: cta_cartera_afiliados_id';
    -- END IF;

    -- Datos del Afiliado
    SELECT persona_id INTO v_persona_id
    FROM afiliados_afiliado
    WHERE id = in_afiliado_id AND activo = true;

    IF v_persona_id IS NULL THEN
        RAISE EXCEPTION 'Afiliado % no existe o no está activo', in_afiliado_id;
    END IF;

    v_fecha := MAKE_DATE(in_anio, in_mes, 1);

    -- ══════════════════════════════════════════
    -- For principal — una fila por cada grupo a facturar
    -- Agrupados:    GROUP BY tipo_factura_id (agrupar=true)
    -- Individuales: GROUP BY acc.id          (agrupar=false)
    -- ══════════════════════════════════════════
    FOR rec IN (

        -- ─── Agrupados: una fila por tipo_factura ───
        SELECT
            'agrupado'              AS modo,
            cc.tipo_factura_id,
            NULL::integer           AS acc_id_individual,
            json_agg(json_build_object(
                'acc_id',       acc.id,
                'valor',        acc.valor,
                'detalle',      acc.detalle,
                'concepto_id',  cc.concepto_id,
                'nombre',       cc.nombre,
                'mayor_id',     cc.mayor_id,
                'iva',          cc.iva,
                'cta_iva_id',   cc.cta_iva_id,
                'iva_incluido', cc.iva_incluido,
                'es_retencion', cc.es_retencion
            )) AS conceptos
        FROM afiliados_afiliado_concepto_causacion acc
        JOIN afiliados_concepto_causacion cc ON cc.id = acc.concepto_id
        JOIN afiliados_afiliado a            ON a.id  = acc.afiliado_id
        WHERE acc.afiliado_id = in_afiliado_id
        AND cc.activo  = true
        AND cc.agrupar = true
        AND (

            cc.es_retencion = false

            OR

            aplica_retencion(
                v_persona_id,
                cc.tipo_retencion_id
            )

        )
        GROUP BY cc.tipo_factura_id

        UNION ALL

        -- ─── Individuales: una fila por concepto ───
        SELECT
            'individual'            AS modo,
            cc.tipo_factura_id,
            acc.id                  AS acc_id_individual,
            json_build_array(json_build_object(
                'acc_id',       acc.id,
                'valor',        acc.valor,
                'detalle',      acc.detalle,
                'concepto_id',  cc.concepto_id,
                'nombre',       cc.nombre,
                'mayor_id',     cc.mayor_id,
                'iva',          cc.iva,
                'cta_iva_id',   cc.cta_iva_id,
                'iva_incluido', cc.iva_incluido,
                'es_retencion', cc.es_retencion
            )) AS conceptos
        FROM afiliados_afiliado_concepto_causacion acc
        JOIN afiliados_concepto_causacion cc ON cc.id = acc.concepto_id
        JOIN afiliados_afiliado a            ON a.id  = acc.afiliado_id
        WHERE acc.afiliado_id = in_afiliado_id
        AND cc.activo  = true
        AND cc.agrupar = false
        AND (
            cc.es_retencion = false

            OR

            aplica_retencion(
                v_persona_id,
                cc.tipo_retencion_id
            )
        )

    ) LOOP

        -- ══════════════════════════════════════════
        -- Construir detalle_fac y calcular totales
        -- (igual para agrupados e individuales)
        -- ══════════════════════════════════════════

        SELECT
            json_agg(json_build_object(
                'concepto', (c->>'concepto_id')::integer,
                'cantidad', 1,
                'detalle',  (c->>'nombre') || COALESCE(': ' || (c->>'detalle'), ''),
                'piva',     CASE WHEN (c->>'iva')::boolean THEN 19 ELSE 0 END,
                'valor',    CASE WHEN (c->>'es_retencion')::boolean THEN -(c->>'valor')::numeric
                                 ELSE (c->>'valor')::numeric END,
                'orden',    ordinality
            ) ORDER BY ordinality),
            COALESCE(SUM(
                CASE WHEN (c->>'es_retencion')::boolean
                     THEN -(c->>'valor')::numeric
                     ELSE  (c->>'valor')::numeric END
            ), 0),
            COALESCE(SUM(
                CASE
                    WHEN NOT (c->>'iva')::boolean OR (c->>'es_retencion')::boolean THEN 0
                    WHEN (c->>'iva_incluido')::boolean
                    THEN (c->>'valor')::numeric - ((c->>'valor')::numeric / (1 + 19/100))
                    ELSE (c->>'valor')::numeric * (19/100)
                END
            ), 0)
        INTO v_detalle_fac, v_subtotal, v_iva_total
        FROM json_array_elements(rec.conceptos) WITH ORDINALITY AS t(c, ordinality);

        -- ══════════════════════════════════════════
        -- Construir preconta (movimientos contables)
        -- ══════════════════════════════════════════

        SELECT json_agg(mov) INTO v_preconta
        FROM (

            -- Crédito/débito por cada concepto según es_retencion
            SELECT json_build_object(
                'mov_id',        0,
                'mayor_id',      (c->>'mayor_id')::integer,
                'persona_id',    v_persona_id,
                'concepto_id',   (c->>'concepto_id')::integer,
                'detalle',       c->>'nombre',
                'valor_db',      CASE WHEN (c->>'es_retencion')::boolean THEN (c->>'valor')::numeric ELSE 0 END,
                'valor_cr',      CASE WHEN (c->>'es_retencion')::boolean THEN 0 ELSE (c->>'valor')::numeric END,
                'cc_id', null, 'base', 0, 'docref', '', 'nittercero_id', null
            ) AS mov
            FROM json_array_elements(rec.conceptos) AS c

            UNION ALL

            -- Crédito IVA por concepto que lo tenga
            SELECT json_build_object(
                'mov_id',        0,
                'mayor_id',      (c->>'cta_iva_id')::integer,
                'persona_id',    v_persona_id,
                'concepto_id',   (c->>'concepto_id')::integer,
                'detalle',       'IVA ' || (c->>'nombre'),
                'valor_db',      0,
                'valor_cr',      CASE
                                    WHEN (c->>'iva_incluido')::boolean
                                    THEN (c->>'valor')::numeric - ((c->>'valor')::numeric / (1 + 19/100))
                                    ELSE (c->>'valor')::numeric * (19/100)
                                 END,
                'cc_id', null, 'base', 0, 'docref', ''
            )
            FROM json_array_elements(rec.conceptos) AS c
            WHERE (c->>'iva')::boolean = true
            AND   (c->>'es_retencion')::boolean = false

            UNION ALL

            -- Débito único a cartera por el total neto
            SELECT json_build_object(
                'mov_id',        0,
                'mayor_id',      958,
                'persona_id',    v_persona_id,
                'concepto_id',   null,
                'detalle',       'Facturación período ' || in_mes || '/' || in_anio,
                'valor_db',      v_subtotal + v_iva_total,
                'valor_cr',      0,
                'cc_id', null, 'base', 0, 'docref', ''
            )

        ) sub;

        -- ══════════════════════════════════════════
        -- Llamar add_factura
        -- ══════════════════════════════════════════
        SELECT af.out_id, af.out_documento
        INTO v_out_id, v_out_doc
        FROM addfacturas(
            0::integer,
            rec.tipo_factura_id::integer,
            v_fecha::date,
            v_fecha::date,
            v_persona_id::integer,
            ''::varchar,
            v_subtotal::numeric,
            0::numeric,
            0::numeric,
            v_subtotal::numeric,
            v_iva_total::numeric,
            (v_subtotal + v_iva_total)::numeric,
            0::numeric,
            0::numeric,
            0::numeric,
            0::numeric,
            0::numeric,
            0::numeric,
            0::numeric,
            CASE rec.modo
                WHEN 'agrupado'   THEN 'Facturación agrupada período ' || in_mes || '/' || in_anio
                WHEN 'individual' THEN (rec.conceptos->0->>'nombre') || ' - período ' || in_mes || '/' || in_anio
            END::varchar,
            in_usuario_id::integer,
            NULL::integer,
            NULL::integer,
            v_preconta::json,
            v_detalle_fac::json,
            false::boolean
        ) af;

        -- ══════════════════════════════════════════
        -- Registrar en tabla de seguimiento
        -- ══════════════════════════════════════════
        INSERT INTO afiliados_facturacionafiliados (
            created, modified,
            afiliado_id, concepto_causacion_afiliado_id,
            documento_id, periodo_mes, periodo_anio, valor
        )
        SELECT NOW(), NOW(), in_afiliado_id, (c->>'acc_id')::integer,
               v_out_id, in_mes, in_anio, (c->>'valor')::numeric
        FROM json_array_elements(rec.conceptos) AS c;

        INSERT INTO afiliados_facturacionafiliados (
            created,
            modified,
            afiliado_id,
            documento_id,
            mes,
            anio,
            fecha
        )
        VALUES (
            NOW(),
            NOW(),
            in_afiliado_id,
            v_out_id,
            in_mes,
            in_anio,
            v_fecha
        )
        RETURNING id
        INTO v_facturacion_id;

        INSERT INTO afiliados_facturaciondetalleafiliados (
            created,
            modified,
            facturacion_id,
            concepto_causacion_afiliado_id,
            valor
        )
        SELECT
            NOW(),
            NOW(),
            v_facturacion_id,
            (c->>'acc_id')::integer,
            (c->>'valor')::numeric
        FROM json_array_elements(rec.conceptos) c;


        out_documento_id := v_out_id;
        out_numero       := v_out_doc;
        out_tipo_factura := rec.tipo_factura_id;
        RETURN NEXT;

    END LOOP;

END;
$function$;