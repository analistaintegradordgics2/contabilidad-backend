-- DROP FUNCTION public.addingresos(in int4, in int4, in date, in int4, in varchar, in varchar, in int4, in numeric, in int4, in json, in json, out varchar, out int4, out varchar);

CREATE OR REPLACE FUNCTION public.addingresos(in_id_documento integer, in_tipo_documento integer, in_fecha date, in_concepto integer, in_detalle character varying, in_referencia character varying, in_persona integer, in_total numeric, in_usuario integer, in_movimiento json, in_pagos json, OUT out_resultado character varying, OUT out_id integer, OUT out_numero character varying)
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
    pago_i        json;
    outmov        int;
    out_pago_id   int;
    VarEstado     int;
    Vardoc        varchar(50);
    notapormes    boolean;
    id_numeracion integer;
    centro_costo_general integer default null;
    centro_costo  integer;
BEGIN

    -- ─── Parámetro centro de costo general ───
    BEGIN
        SELECT cp.valor::integer INTO centro_costo_general
        FROM conf_parametros cp
        WHERE cp.parametro = 'centro_costo_general';
    EXCEPTION WHEN OTHERS THEN
        centro_costo_general := null;
    END;

    -- ══════════════════════════════════════════
    -- CREAR O ACTUALIZAR DOCUMENTO
    -- ══════════════════════════════════════════
    IF in_id_documento = 0 THEN

        INSERT INTO cont_documentos (
            created, modified,
            numero, fecha, referencia, detalle,
            estado, total,
            concepto_id, tipo_documento_id, personas_id,
            uc_id,
            mandato, nota_parcial, automatico, nota_saldos_iniciales
        ) VALUES (
            NOW(), NOW(),
            '', in_fecha, in_referencia, in_detalle,
            1, in_total,
            in_concepto, in_tipo_documento, in_persona,
            in_usuario,
            false, false, false, false
        ) RETURNING id INTO out_id;

    ELSE

        UPDATE cont_documentos SET
            modified         = NOW(),
            concepto_id      = in_concepto,
            detalle          = in_detalle,
            referencia       = in_referencia,
            personas_id      = in_persona,
            total            = in_total,
            uc_id            = in_usuario
        WHERE id = in_id_documento;

        out_id     := in_id_documento;
        out_numero := '';

    END IF;

    -- ══════════════════════════════════════════
    -- PAGOS — limpiar y reinsertar
    -- ══════════════════════════════════════════

    -- Insertar pagos nuevos
    FOR pago_i IN SELECT * FROM json_array_elements(in_pagos) LOOP
		
		IF (pago_i->>'id') IS NOT NULL THEN

		    out_pago_id := (pago_i->>'id')::integer;
		
		    UPDATE contabilidad_pagodocumento
		    SET
		        forma_pago_id = (pago_i->>'forma_pago_id')::integer,
		        medio_pago_id = (pago_i->>'medio_pago_id')::integer,
		        modified = NOW()
		    WHERE id = out_pago_id;
		
		ELSE
		
		     -- Crear PagoDocumento cabecera
	        INSERT INTO contabilidad_pagodocumento (
	            created, modified,
	            documento_id,
	            forma_pago_id,
	            medio_pago_id
	        ) VALUES (
	            NOW(), NOW(),
	            out_id,
	            (pago_i->>'forma_pago_id')::integer,
	            (pago_i->>'medio_pago_id')::integer
	        ) RETURNING id INTO out_pago_id;
		
		END IF;
       	
		DELETE FROM contabilidad_pagoefectivo
		WHERE pago_id = out_pago_id;
		
		DELETE FROM contabilidad_pagocheque
		WHERE pago_id = out_pago_id;
		
		DELETE FROM contabilidad_pagoconsignacion
		WHERE pago_id = out_pago_id;
		
		DELETE FROM contabilidad_pagotarjeta
		WHERE pago_id = out_pago_id;

		DELETE FROM contabilidad_pagotransferencia
		WHERE pago_id = out_pago_id;

        -- Insertar detalle según tipo de pago
        CASE pago_i->>'tipo'

            WHEN 'efectivo' THEN
                INSERT INTO contabilidad_pagoefectivo (
                    created, modified, pago_id, valor
                ) VALUES (
                    NOW(), NOW(),
                    out_pago_id,
                    (pago_i->>'valor')::decimal
                );

            WHEN 'cheque' THEN
                INSERT INTO contabilidad_pagocheque (
                    created, modified,
                    pago_id, banco_id,
                    numero, fecha, valor
                ) VALUES (
                    NOW(), NOW(),
                    out_pago_id,
                    (pago_i->>'banco_id')::integer,
                    pago_i->>'numero',
                    (pago_i->>'fecha')::date,
                    (pago_i->>'valor')::decimal
                );

            WHEN 'consignacion' THEN
                INSERT INTO contabilidad_pagoconsignacion (
                    created, modified,
                    pago_id, banco_id,
                    cuenta_bancaria_id,
                    numero, fecha, valor
                ) VALUES (
                    NOW(), NOW(),
                    out_pago_id,
                    (pago_i->>'banco_id')::integer,
                    (pago_i->>'cuenta_bancaria_id')::integer,
                    pago_i->>'numero',
                    (pago_i->>'fecha')::date,
                    (pago_i->>'valor')::decimal
                );

            WHEN 'tarjeta' THEN
                INSERT INTO contabilidad_pagotarjeta (
                    created, modified,
                    pago_id, banco_id,
                    cuenta_bancaria_id,
                    numero_tarjeta, valor
                ) VALUES (
                    NOW(), NOW(),
                    out_pago_id,
                    (pago_i->>'banco_id')::integer,
                    (pago_i->>'cuenta_bancaria_id')::integer,
                    pago_i->>'numero_tarjeta',
                    (pago_i->>'valor')::decimal
                );
			
			WHEN 'transferencia' THEN
                INSERT INTO contabilidad_pagotransferencia (
                    created, modified,
                    pago_id, banco_destino_id, cuenta_destino,
                    cuenta_origen_id,
                    numero_cheque, valor
                ) VALUES (
                    NOW(), NOW(),
                    out_pago_id,
                    (pago_i->>'banco_destino_id')::integer,
					pago_i->>'cuenta_destino',
					(pago_i->>'cuenta_origen_id')::integer,
                    pago_i->>'numero_cheque',
                    (pago_i->>'valor')::decimal
                );

        END CASE;

    END LOOP;

    -- ══════════════════════════════════════════
    -- MOVIMIENTOS
    -- ══════════════════════════════════════════
    FOR pre_i IN SELECT * FROM json_array_elements(in_movimiento) LOOP

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
		raise notice '%--------a',(pre_i->>'mov_id')::integer;
        IF (pre_i->>'mov_id')::integer = 0 THEN

            INSERT INTO contabilidad_mov (
                documento_id, mayor_id,
                valor_db, valor_cr,
                centro_costos_id, persona_id,
                base, docref,
                nittercero, concepto_id,
                detalle, sistema, conciliado
            ) VALUES (
                out_id,
                (pre_i->>'mayor_id')::integer,
                COALESCE((pre_i->>'valor_db')::decimal, 0),
                COALESCE((pre_i->>'valor_cr')::decimal, 0),
                centro_costo,
                COALESCE((pre_i->>'persona_id')::integer, in_persona),
                COALESCE((pre_i->>'base')::decimal, 0),
                COALESCE(pre_i->>'docref', ''),
                (pre_i->>'nittercero_id')::integer,
                (pre_i->>'concepto_id')::integer,
                COALESCE(pre_i->>'detalle', ''),
                0, false
            ) RETURNING id INTO outmov;

        ELSE

            UPDATE contabilidad_mov SET
                mayor_id         = (pre_i->>'mayor_id')::integer,
                valor_db         = COALESCE((pre_i->>'valor_db')::decimal, 0),
                valor_cr         = COALESCE((pre_i->>'valor_cr')::decimal, 0),
                centro_costos_id = centro_costo,
                persona_id       = COALESCE((pre_i->>'persona_id')::integer, in_persona),
                base             = COALESCE((pre_i->>'base')::decimal, 0),
                docref           = COALESCE(pre_i->>'docref', ''),
                nittercero       = (pre_i->>'nittercero_id')::integer,
                concepto_id      = (pre_i->>'concepto_id')::integer,
                detalle          = COALESCE(pre_i->>'detalle', ''),
                sistema          = 0
            WHERE id = (pre_i->>'mov_id')::integer;

            outmov := (pre_i->>'mov_id')::integer;

        END IF;

        cadenamov := CONCAT(cadenamov, ',', outmov);

    END LOOP;

    -- Eliminar movimientos que ya no están
    IF in_id_documento > 0 AND LENGTH(LTRIM(cadenamov)) > 0 THEN
        DELETE FROM contabilidad_mov
        WHERE documento_id = in_id_documento
        AND id NOT IN (
            SELECT UNNEST(
                STRING_TO_ARRAY(SUBSTRING(cadenamov FROM 2), ',')::integer[]
            )
        );
    END IF;

    -- ══════════════════════════════════════════
    -- NUMERACIÓN
    -- ══════════════════════════════════════════
    IF in_id_documento = 0 THEN

        lnnuevo   := 1;
        lnvalidar := 0;

        SELECT td.numeracionxmes INTO notapormes
        FROM contabilidad_tipos_documentos td
        WHERE td.id = in_tipo_documento;

        PERFORM 1 FROM contabilidad_tipos_documentos
        WHERE id = in_tipo_documento FOR UPDATE;

        IF notapormes = FALSE OR notapormes IS NULL THEN

            SELECT COALESCE(td.numero, 1), COALESCE(td.ndigitos, 0), COALESCE(td.prefijo, '')
            INTO lnnumero, lnndigitos, lcprefijo
            FROM contabilidad_tipos_documentos td
            WHERE td.id = in_tipo_documento;

            WHILE lnvalidar = 0 LOOP
                lcnumero := CONCAT(
                    RTRIM(lcprefijo),
                    CASE WHEN lnndigitos > 0
                        THEN REPLACE(LPAD(lnnumero::text, lnndigitos), ' ', '0')
                        ELSE lnnumero::varchar(20)
                    END
                );
                SELECT COUNT(*) INTO lncantidad
                FROM cont_documentos
                WHERE numero = lcnumero AND tipo_documento_id = in_tipo_documento;
                IF lncantidad = 0 THEN lnvalidar := 1;
                ELSE lnnumero := lnnumero + 1;
                END IF;
            END LOOP;

            out_numero := lcnumero;
            UPDATE contabilidad_tipos_documentos SET numero = lnnumero + 1 WHERE id = in_tipo_documento;
            UPDATE cont_documentos SET numero = lcnumero WHERE id = out_id;

        ELSE

            -- Crear año si no existe
            IF (SELECT COUNT(*) FROM parametros_anio WHERE nombre = EXTRACT(year FROM in_fecha)) = 0 THEN
                INSERT INTO parametros_anio (nombre) VALUES (EXTRACT(year FROM in_fecha));
            END IF;

            -- Crear numeración del mes si no existe
            IF (
                SELECT COUNT(*) FROM contabilidad_numeracion_mes_anio
                WHERE tipo_documento_id = in_tipo_documento
                AND anio_id = (SELECT id FROM parametros_anio WHERE nombre = EXTRACT(year FROM in_fecha) LIMIT 1)
                
            ) = 0 THEN
                insert into contabilidad_numeracion_mes_anio (
					numerom01,
					numerom02,
					numerom03,
					numerom04,
					numerom05,
					numerom06,
					numerom07,
					numerom08,
					numerom09,
					numerom10,
					numerom11,
					numerom12,
					anio_id,
					tipo_documento_id
				) values (
					1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 
					(select ca.id from parametros_anio ca where ca.nombre = EXTRACT(year FROM in_fecha) limit 1),
					in_tipo_documento
				);
            END IF;

            PERFORM 1 FROM contabilidad_numeracion_mes_anio
            WHERE tipo_documento_id = in_tipo_documento
            AND anio_id = (SELECT id FROM parametros_anio WHERE nombre = EXTRACT(year FROM in_fecha) LIMIT 1)
            FOR UPDATE;

            SELECT 
				CASE
				    WHEN EXTRACT(month FROM in_fecha) = 1  THEN coalesce(nma.numerom01,1)
					WHEN EXTRACT(month FROM in_fecha) = 2  THEN coalesce(nma.numerom02,1)
					WHEN EXTRACT(month FROM in_fecha) = 3  THEN coalesce(nma.numerom03,1)
					WHEN EXTRACT(month FROM in_fecha) = 4  THEN coalesce(nma.numerom04,1)
					WHEN EXTRACT(month FROM in_fecha) = 5  THEN coalesce(nma.numerom05,1)
					WHEN EXTRACT(month FROM in_fecha) = 6  THEN coalesce(nma.numerom06,1)
					WHEN EXTRACT(month FROM in_fecha) = 7  THEN coalesce(nma.numerom07,1)
					WHEN EXTRACT(month FROM in_fecha) = 8  THEN coalesce(nma.numerom08,1)
					WHEN EXTRACT(month FROM in_fecha) = 9  THEN coalesce(nma.numerom09,1)
					WHEN EXTRACT(month FROM in_fecha) = 10 THEN coalesce(nma.numerom10,1)
					WHEN EXTRACT(month FROM in_fecha) = 11 THEN coalesce(nma.numerom11,1)
					WHEN EXTRACT(month FROM in_fecha) = 12 THEN coalesce(nma.numerom12,1)
				END, 
				td.ndigitos,
                CASE EXTRACT(month FROM in_fecha)
                    WHEN 1 THEN 'ENE' WHEN 2 THEN 'FEB' WHEN 3 THEN 'MAR'
                    WHEN 4 THEN 'ABR' WHEN 5 THEN 'MAY' WHEN 6 THEN 'JUN'
                    WHEN 7 THEN 'JUL' WHEN 8 THEN 'AGO' WHEN 9 THEN 'SEP'
                    WHEN 10 THEN 'OCT' WHEN 11 THEN 'NOV' WHEN 12 THEN 'DIC'
                END,
                nma.id
            INTO lnnumero, lnndigitos, lcprefijo, id_numeracion
            FROM contabilidad_numeracion_mes_anio nma
            JOIN contabilidad_tipos_documentos td ON td.id = in_tipo_documento
            WHERE nma.tipo_documento_id = in_tipo_documento
            AND nma.anio_id = (SELECT id FROM parametros_anio WHERE nombre = EXTRACT(year FROM in_fecha) LIMIT 1);

            WHILE lnvalidar = 0 LOOP
                lcnumero := CONCAT(
                    RTRIM(lcprefijo),
                    CASE WHEN lnndigitos > 0
                        THEN REPLACE(LPAD(lnnumero::text, lnndigitos), ' ', '0')
                        ELSE lnnumero::varchar(20)
                    END
                );
                SELECT COUNT(*) INTO lncantidad
                FROM cont_documentos
                WHERE numero = lcnumero AND tipo_documento_id = in_tipo_documento
                AND EXTRACT(year FROM fecha) = EXTRACT(year FROM in_fecha);
                IF lncantidad = 0 THEN lnvalidar := 1;
                ELSE lnnumero := lnnumero + 1;
                END IF;
            END LOOP;

            out_numero := lcnumero;
			
			update contabilidad_numeracion_mes_anio set 
			numerom01 = (case when EXTRACT(month FROM in_fecha)=1 then lnnumero + 1 else numerom01 end),
			numerom02 = (case when EXTRACT(month FROM in_fecha)=2 then lnnumero + 1 else numerom02 end),
			numerom03 = (case when EXTRACT(month FROM in_fecha)=3 then lnnumero + 1 else numerom03 end),
			numerom04 = (case when EXTRACT(month FROM in_fecha)=4 then lnnumero + 1 else numerom04 end),
			numerom05 = (case when EXTRACT(month FROM in_fecha)=5 then lnnumero + 1 else numerom05 end),
			numerom06 = (case when EXTRACT(month FROM in_fecha)=6 then lnnumero + 1 else numerom06 end),
			numerom07 = (case when EXTRACT(month FROM in_fecha)=7 then lnnumero + 1 else numerom07 end),
			numerom08 = (case when EXTRACT(month FROM in_fecha)=8 then lnnumero + 1 else numerom08 end),
			numerom09 = (case when EXTRACT(month FROM in_fecha)=9 then lnnumero + 1 else numerom09 end),
			numerom10 = (case when EXTRACT(month FROM in_fecha)=10 then lnnumero + 1 else numerom10 end),
			numerom11 = (case when EXTRACT(month FROM in_fecha)=11 then lnnumero + 1 else numerom11 end),
			numerom12 = (case when EXTRACT(month FROM in_fecha)=12 then lnnumero + 1 else numerom12 end)
			where id = id_numeracion;
            UPDATE cont_documentos SET numero = lcnumero WHERE id = out_id;

        END IF;

    END IF;

    -- ══════════════════════════════════════════
    -- BITÁCORA
    -- ══════════════════════════════════════════
    SELECT doc.estado, doc.numero INTO VarEstado, Vardoc
    FROM cont_documentos doc WHERE doc.id = out_id;

    INSERT INTO cont_documentos_bita (documentos_id, usuario_id, fecha, evento, estado_id)
    VALUES (
        out_id, in_usuario, NOW(),
        CONCAT('DOCUMENTO ', CASE WHEN lnnuevo = 1 THEN 'CREADO' ELSE 'MODIFICADO' END, ' No. ', Vardoc),
        VarEstado
    );

    out_resultado := 'OK';

EXCEPTION WHEN OTHERS THEN
    out_resultado := SQLERRM;
    RAISE;

END
$function$
;
