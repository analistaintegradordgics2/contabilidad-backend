-- DROP FUNCTION public.addfacturas(in int4, in int4, in date, in date, in int4, in numeric, in numeric, in numeric, in numeric, in numeric, in numeric, in numeric, in numeric, in numeric, in numeric, in numeric, in numeric, in numeric, in varchar, in int4, in int4, in int4, in json, in json, in bool, out int4, out varchar);

CREATE OR REPLACE FUNCTION public.addfacturas(in_id_factura integer, in_tipo_documento integer, in_fecha date, in_fecha_venc date, in_persona_id integer, in_subtotal numeric, in_pdescuento numeric, in_descuento numeric, in_total numeric, in_iva numeric, in_gtotal numeric, in_prtefte numeric, in_prteiva numeric, in_prteica numeric, in_rtefte numeric, in_rteiva numeric, in_rteica numeric, in_retenciones numeric, in_detalle character varying, in_usuario integer, in_forma_pago integer, in_medio_pago integer, in_preconta json, in_detalle_fac json, in_nota_parcial boolean DEFAULT false, OUT out_id integer, OUT out_documento character varying)
 RETURNS record
 LANGUAGE plpgsql
AS $function$
DECLARE
    lnnumero      int;
    lnndigitos    int;
    lcprefijo     varchar(10);
    lnvalidar     int;
    lcnumero      varchar(30);
    lncantidad    integer;
    lnnuevo       int = 0;
    cadenamov     character varying = '';
    pre_i         json;
    det_i         json;
    outmov        int;
    VarEstado     int;
    Vardoc        varchar(50);
    orden_detalle integer default 0;
    centro_costo_general integer default null;
    centro_costo  integer;

    -- Datos de persona para el encabezado
    lc_nombre  varchar(200);
    lc_dir     varchar(200);
    lc_tel     varchar(70);
    lc_movil   varchar(70);
    lc_ciudad  varchar(80);
BEGIN

    -- ─── Parámetro centro de costo general ───
    BEGIN
        SELECT cp.valor::integer INTO centro_costo_general
        FROM conf_parametros cp WHERE cp.parametro = 'centro_costo_general';
    EXCEPTION WHEN OTHERS THEN
        centro_costo_general := null;
    END;

    -- ─── Datos de la persona (cliente) ───
    -- Ajusta los campos según tu modelo personas_persona
    SELECT
        p.n_completo,
        pd.descripcion,
        pt.valor,
        pt.valor,
        pd.ciudad_id
    INTO lc_nombre, lc_dir, lc_tel, lc_movil, lc_ciudad
    FROM personas_persona p
	inner join personas_direccion pd on pd.persona_id = p.id and pd.incluir_a_factura is true
	inner join personas_telefono pt on pt.persona_id = p.id
    WHERE p.id = in_persona_id;

    -- ══════════════════════════════════════════
    -- CREAR O ACTUALIZAR DOCUMENTO
    -- ══════════════════════════════════════════
    IF in_id_factura = 0 THEN

        INSERT INTO cont_documentos (
            created, modified,
            fecha, fecha_vencimiento,
            tipo_documento_id, personas_id,
            subtotal, pdescuento, descuento,
            iva, gtotal,
            prtefte, prteiva, prteica,
            rtefte, rteiva, rteica,
            total,
            detalle,
            uc_id,
            nombre, direccion, telefono, movil, ciudad,
            fpago,
            nota_parcial,
            estado, numero, concepto_id
        ) VALUES (
            NOW(), NOW(),
            in_fecha, in_fecha_venc,
            in_tipo_documento, in_persona_id,
            ROUND(in_subtotal), in_pdescuento, in_descuento,
            in_iva, ROUND(in_gtotal),
            in_prtefte, in_prteiva, in_prteica,
            COALESCE(in_rtefte, 0), COALESCE(in_rteiva, 0), COALESCE(in_rteica, 0),
            in_total,
            UPPER(in_detalle),
            in_usuario,
            lc_nombre, lc_dir, lc_tel, lc_movil, lc_ciudad,
            in_forma_pago,
            in_nota_parcial,
            1, '', 1  -- estado ABIERTO, número se actualiza después
        ) RETURNING id INTO out_id;

    ELSE

        UPDATE cont_documentos SET
            modified          = NOW(),
            fecha             = in_fecha,
            fecha_vencimiento = in_fecha_venc,
            personas_id       = in_persona_id,
            subtotal          = in_subtotal,
            pdescuento        = in_pdescuento,
            descuento         = in_descuento,
            iva               = in_iva,
            gtotal            = in_gtotal,
            detalle           = UPPER(in_detalle),
            prtefte           = in_prtefte,
            prteiva           = in_prteiva,
            prteica           = in_prteica,
            rtefte            = COALESCE(in_rtefte, 0),
            rteiva            = COALESCE(in_rteiva, 0),
            rteica            = COALESCE(in_rteica, 0),
            total             = in_total,
            nombre            = lc_nombre,
            direccion         = lc_dir,
            telefono          = lc_tel,
            movil             = lc_movil,
            ciudad            = lc_ciudad,
            fpago             = in_forma_pago
        WHERE id = in_id_factura;

        out_id     := in_id_factura;
        out_documento := '';

    END IF;

    -- ══════════════════════════════════════════
    -- MOVIMIENTOS DE CONTABILIZACIÓN
    -- ══════════════════════════════════════════
    FOR pre_i IN SELECT * FROM json_array_elements(in_preconta) LOOP

        -- Centro de costo automático
        IF (
            SELECT COUNT(*) FROM contabilidad_mayor cm
            WHERE cm.id = (pre_i->>'mayor_id')::integer
            AND COALESCE(cm.maneja_ccosto, false) IS TRUE
        ) > 0 THEN
            centro_costo := COALESCE(
                (pre_i->>'cc_id')::integer,
                centro_costo_general
            );
        ELSE
            centro_costo := (pre_i->>'cc_id')::integer;
        END IF;

        IF (pre_i->>'mov_id')::integer = 0 THEN

            INSERT INTO contabilidad_mov (
                documento_id,
                mayor_id,
                valor_db,
                valor_cr,
                centro_costos_id,
                persona_id,
                base,
                docref,
                nittercero,
                concepto_id,
                detalle,
                sistema,
                conciliado
            ) VALUES (
                out_id,
                (pre_i->>'mayor_id')::integer,
                COALESCE((pre_i->>'valor_db')::decimal, 0),
                COALESCE((pre_i->>'valor_cr')::decimal, 0),
                centro_costo,
                COALESCE((pre_i->>'persona_id')::integer, in_persona_id),
                COALESCE((pre_i->>'base')::decimal, 0),
                COALESCE(pre_i->>'docref', ''),
                (pre_i->>'nittercero_id')::integer,
                (pre_i->>'concepto_id')::integer,
                UPPER(COALESCE(pre_i->>'detalle', '')),
                0,
                false
            ) RETURNING id INTO outmov;

        ELSE

            UPDATE contabilidad_mov SET
                mayor_id         = (pre_i->>'mayor_id')::integer,
                valor_db         = COALESCE((pre_i->>'valor_db')::decimal, 0),
                valor_cr         = COALESCE((pre_i->>'valor_cr')::decimal, 0),
                centro_costos_id = centro_costo,
                persona_id       = COALESCE((pre_i->>'persona_id')::integer, in_persona_id),
                base             = COALESCE((pre_i->>'base')::decimal, 0),
                docref           = COALESCE(pre_i->>'docref', ''),
                nittercero       = (pre_i->>'nittercero_id')::integer,
                concepto_id      = (pre_i->>'concepto_id')::integer,
                detalle          = UPPER(COALESCE(pre_i->>'detalle', '')),
                sistema          = 0
            WHERE id = (pre_i->>'mov_id')::integer;

            outmov := (pre_i->>'mov_id')::integer;

        END IF;

        cadenamov := CONCAT(cadenamov, ',', outmov);

    END LOOP;

    -- Eliminar movimientos que ya no están
    IF in_id_factura > 0 AND LENGTH(LTRIM(cadenamov)) > 0 THEN
        DELETE FROM contabilidad_mov
        WHERE documento_id = in_id_factura
        AND id NOT IN (
            SELECT UNNEST(
                STRING_TO_ARRAY(SUBSTRING(cadenamov FROM 2), ',')::integer[]
            )
        );
    END IF;

    -- ══════════════════════════════════════════
    -- DETALLE DE ITEMS DE LA FACTURA
    -- ══════════════════════════════════════════

    -- Limpiar items anteriores al editar
    IF in_id_factura > 0 THEN
        DELETE FROM contabilidad_detallefacturas
        WHERE documentos_id = out_id;
    END IF;

    FOR det_i IN SELECT * FROM json_array_elements(in_detalle_fac) LOOP

        orden_detalle := orden_detalle + 1;

        INSERT INTO contabilidad_detallefacturas (
            documentos_id,
            cantidad,
            detalle,
            valor,
            piva,
            concepto_id,
            orden,
            prtefuente,
            prteica,
            prteiva
        ) VALUES (
            out_id,
            det_i->>'cantidad',
            UPPER(COALESCE(det_i->>'detalle', '')),
            ROUND((det_i->>'valor')::decimal),
            COALESCE((det_i->>'piva')::decimal, 0),
            (det_i->>'concepto')::integer,
            COALESCE((det_i->>'orden')::integer, orden_detalle),
            COALESCE((det_i->>'prtefuente')::decimal, 0),
            COALESCE((det_i->>'prteica')::decimal, 0),
            COALESCE((det_i->>'prteiva')::decimal, 0)
        );

    END LOOP;

   -- ══════════════════════════════════════════
	-- NUMERACIÓN — solo documentos nuevos
	-- ══════════════════════════════════════════
	IF in_id_factura = 0 THEN
	
	    lnnuevo   := 1;
	    lnvalidar := 0;
	
	    -- Bloquear tipo documento para evitar concurrencia
	    PERFORM 1 FROM contabilidad_tipos_documentos
	    WHERE id = in_tipo_documento FOR UPDATE;
	
	    -- ─── Verificar si tiene resolución activa ───
		DECLARE
		    resolucion_id       integer;
		    rango_final         integer;
		    rango_inicial       integer;
		BEGIN
		
		    SELECT
		        rf.id,
		        COALESCE(rf.rango_final, 0),
		        COALESCE(rf.rango_inicial, 0),
		        COALESCE(rf.consecutivo_actual, rf.rango_inicial, 1),
		        COALESCE(td.ndigitos, 6),
		        COALESCE(td.prefijo, '')
		    INTO
		        resolucion_id,
		        rango_final,
		        rango_inicial,
		        lnnumero,
		        lnndigitos,
		        lcprefijo
		    FROM contabilidad_tipos_documentos td
		    LEFT JOIN contabilidad_resolucion_facturacion rf
		        ON rf.tipo_documento_id = td.id
		        AND rf.activa = true
		        AND CURRENT_DATE BETWEEN rf.fecha_inicio AND rf.fecha_fin
		    WHERE td.id = in_tipo_documento
		    ORDER BY rf.id DESC
		    LIMIT 1;
		
		    --
		    lnnumero := COALESCE(lnnumero, 1);
	
	        -- ─── Generar número ───
	        WHILE lnvalidar = 0 LOOP
	
	            lcnumero := CONCAT(
	                RTRIM(lcprefijo),
	                CASE
	                    WHEN lnndigitos > 0
	                    THEN REPLACE(LPAD(lnnumero::text, lnndigitos), ' ', '0')
	                    ELSE lnnumero::varchar(20)
	                END
	            );
	
	            SELECT COUNT(*) INTO lncantidad
	            FROM cont_documentos
	            WHERE numero = lcnumero
	            AND tipo_documento_id = in_tipo_documento;
	
	            IF lncantidad = 0 THEN
	                lnvalidar := 1;
	            ELSE
	                lnnumero := lnnumero + 1;
	            END IF;
	
	        END LOOP;
	
	        out_documento := lcnumero;
	
	        -- ─── Actualizar consecutivo ───
	        IF resolucion_id IS NOT NULL THEN
	            -- ✅ Tiene resolución — actualizar consecutivo_actual
	            -- y validar que no se pase del rango
	            IF lnnumero < rango_final THEN
	                UPDATE contabilidad_resolucion_facturacion
	                SET consecutivo_actual = lnnumero + 1
	                WHERE id = resolucion_id;
	            ELSE
	                -- Llegó al límite — solo registra, no incrementa
	                -- Aquí podrías agregar una alerta/log si lo necesitas
	                UPDATE contabilidad_resolucion_facturacion
	                SET consecutivo_actual = lnnumero
	                WHERE id = resolucion_id;
	            END IF;
	
	            -- ✅ También actualizar el numero en TiposDocumentos
	            -- para que el procedimiento de notas contables siga funcionando
	            UPDATE contabilidad_tipos_documentos
	            SET numero = lnnumero + 1
	            WHERE id = in_tipo_documento;
	
	        ELSE
	            -- Sin resolución — solo actualiza TiposDocumentos
	            UPDATE contabilidad_tipos_documentos
	            SET numero = lnnumero + 1
	            WHERE id = in_tipo_documento;
	        END IF;
	
	        UPDATE cont_documentos
	        SET numero = lcnumero
	        WHERE id = out_id;
	
	    END;
	
	END IF;
    -- ══════════════════════════════════════════
    -- BITÁCORA
    -- ══════════════════════════════════════════
    SELECT doc.estado, doc.numero INTO VarEstado, Vardoc
    FROM cont_documentos doc WHERE doc.id = out_id;

    INSERT INTO cont_documentos_bita (
        documentos_id, usuario_id, fecha, evento, estado_id
    ) VALUES (
        out_id, in_usuario, NOW(),
        CONCAT(
            'DOCUMENTO ',
            CASE WHEN lnnuevo = 1 THEN 'CREADO' ELSE 'MODIFICADO' END,
            ' No. ', Vardoc
        ),
        VarEstado
    );

    out_documento := COALESCE(out_documento, Vardoc);

EXCEPTION WHEN OTHERS THEN
    RAISE;

END
$function$
;
