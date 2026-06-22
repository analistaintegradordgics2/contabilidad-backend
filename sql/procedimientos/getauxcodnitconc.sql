-- DROP FUNCTION public.getauxcodnitconc(varchar, varchar, int4, int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getauxcodnitconc(in_codigoid character varying, in_codigo2id character varying, in_personaid integer, in_anio integer, in_mesd integer, in_mesh integer, in_concepto integer)
 RETURNS TABLE(id integer, tipo character varying, numero character varying, fecha date, docref character varying, concepto character varying, detalle character varying, valor_db numeric, valor_cr numeric, saldo numeric, color integer, fuentes_id integer, ordenf date, base numeric, inmueble_id integer, direccion text, mov_id integer, mayor_id integer)
 LANGUAGE plpgsql
AS $function$
DECLARE
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
    tienetran bit = 1;
    err_pa varchar(100);
    err_linea varchar(100);
    l_resultado varchar(100);
    lccursor varchar(30);
    lnnumero numeric(18,0);
    sumbase decimal (18,2);
    saldoi decimal (18,2);
    saldof decimal (18,2);
    sumasaldo numeric(18,2) DEFAULT 0;
    curdatos1 record;
    curdatos record;
    sumadb numeric(18,2) DEFAULT 0;
    sumacr numeric(18,2) DEFAULT 0;
    mes_documento int;
    contador int DEFAULT 1;
    ini_date date;
    end_date date;
BEGIN
    IF length(RTRIM(in_codigo2id)) = 0 THEN
        in_codigo2id := in_codigoid;
    END IF;

    in_codigo2id := CONCAT(in_codigo2id, '99');

    CREATE TEMP TABLE cur_aux (
        id integer,
        tipo varchar(10),
        numero varchar(20),
        fecha date,
        docref varchar(30),
        concepto varchar(10),
        detalle character varying,
        valor_db decimal(18,2), 
        valor_cr decimal(18,2),
        saldo decimal(18,2),
        color integer,
        fuentes_id integer,
        ordenf date,
        base decimal(18,2),
        inmueble_id integer,
        direccion text,
        mov_id integer,
        mayor_id integer
    ) ON COMMIT DROP;

    -- Determinar fechas de corte
    IF in_mesd = 1 THEN
        ini_date := make_date(in_anio, 1, 1);
    ELSIF in_mesd BETWEEN 2 AND 12 THEN
        ini_date := make_date(in_anio, in_mesd, 1);
    ELSE
        ini_date := make_date(in_anio + 1, 1, 1);
    END IF;

    IF in_mesh BETWEEN 1 AND 11 THEN
        end_date := make_date(in_anio, in_mesh + 1, 1);
    ELSE
        end_date := make_date(in_anio + 1, 1, 1);
    END IF;

    FOR curdatos IN
        SELECT mayor.id AS id,
               CONCAT(RTRIM(mayor."codigo"), ' ::: ', RTRIM(mayor."nombre")) AS nombre,
               (
                 SELECT COALESCE(SUM(mov.valor_db) - SUM(mov.valor_cr), 0)
                 FROM cont_documentos enc
                 INNER JOIN contabilidad_mov mov ON enc.id = mov.documento_id
                 INNER JOIN contabilidad_mayor cs ON mov.mayor_id = cs.id
                 WHERE enc.estado = 2
                   AND cs."codigo" BETWEEN in_codigoid AND in_codigo2id
                   AND cs.maneja_nits = true
                   AND (in_personaid IS NULL OR in_personaid = 0 OR mov.persona_id = in_personaid)
                   AND mov.concepto_id = in_concepto
                   AND enc.fecha < ini_date
                   AND NOT (
                       in_mesd = 13
                       AND EXTRACT(MONTH FROM enc.fecha) = 12
                       AND COALESCE(mov.dcierre, 0) = 1
                   )
               ) AS saldoi,
               (
                 SELECT COALESCE(SUM(mov.valor_db) - SUM(mov.valor_cr), 0)
                 FROM cont_documentos enc
                 INNER JOIN contabilidad_mov mov ON enc.id = mov.documento_id
                 INNER JOIN contabilidad_mayor cs ON mov.mayor_id = cs.id
                 WHERE enc.estado = 2
                   AND cs."codigo" BETWEEN in_codigoid AND in_codigo2id
                   AND cs.maneja_nits = true
                   AND (in_personaid IS NULL OR in_personaid = 0 OR mov.persona_id = in_personaid)
                   AND mov.concepto_id = in_concepto
                   AND enc.fecha < end_date
                   AND NOT (
                       in_mesh = 12
                       AND EXTRACT(MONTH FROM enc.fecha) = 12
                       AND COALESCE(mov.dcierre, 0) = 1
                   )
               ) AS saldof
        FROM contabilidad_mayor AS mayor
        WHERE mayor."codigo" BETWEEN in_codigoid AND in_codigo2id
        AND lower(mayor.tipo) = 'auxiliar'
        AND mayor.estado is true
        AND EXISTS (
            SELECT 1
            FROM cont_documentos enc
            JOIN contabilidad_mov mov ON enc.id = mov.documento_id
            WHERE enc.estado = 2
            AND mov.mayor_id = mayor.id
            AND (in_personaid IS NULL OR in_personaid = 0 OR mov.persona_id = in_personaid)
            AND mov.concepto_id = in_concepto
            AND EXTRACT(YEAR FROM enc.fecha) = in_anio
            AND EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesd AND in_mesh
        )
        ORDER BY RTRIM(mayor."codigo") ASC
    LOOP
        INSERT INTO cur_aux (detalle, color, valor_db, valor_cr, saldo, ordenf)
        VALUES (curdatos.nombre, 1, 0, 0, 0, '2000-01-01');

        INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, ordenf)
		SELECT v.detalle, v.valor_db, v.valor_cr, 1, 0, '2000-01-01'
		FROM (
		SELECT
			CONCAT(
			'SALDO A ',
			CASE
				WHEN in_mesd = 1 THEN CONCAT('DICIEMBRE ', (in_anio - 1)::varchar)
				ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((in_mesd - 1)::varchar, 2,'0')::varchar, '/01')), 'FMMonth'), ' ', in_anio::varchar)
			END
			) AS detalle,
			CASE WHEN curdatos.saldoi > 0 THEN coalesce(curdatos.saldoi, 0) ELSE 0 END AS valor_db,
			CASE WHEN curdatos.saldoi > 0 THEN 0 ELSE coalesce(curdatos.saldoi, 0) * -1 END AS valor_cr
		) v
		WHERE NOT EXISTS (
		SELECT 1 FROM cur_aux ca WHERE ca.detalle = v.detalle AND ca.ordenf = '2000-01-01'
		);

        sumasaldo := curdatos.saldoi;
        sumadb := CASE WHEN curdatos.saldoi > 0 THEN curdatos.saldoi ELSE 0 END;
        sumacr := CASE WHEN curdatos.saldoi < 0 THEN curdatos.saldoi * -1 ELSE 0 END;

        FOR curdatos1 IN
            SELECT
                enc.id as id,
                RTRIM(doc.tipo) as tipo,
                RTRIM(enc.numero) as numero,
                enc.fecha as fecha,
                RTRIM(mov.docref) as docref,
                co.codigo as concepto,
                RTRIM(mov.detalle) as detalle,
                coalesce(mov.valor_db, 0) as valor_db,
                coalesce(mov.valor_cr, 0) as valor_cr,
                0 as saldo,
                0 as color,
                doc.fuentes_id as fuentes_id,
                enc.fecha as fecha,
                mov.base as base,
                mov.inmueble_id as inmueble_id,
                mov.id as mov_id,
                mov.mayor_id as mayor_id
            FROM cont_documentos enc
            INNER JOIN contabilidad_mov mov ON enc.id = mov.documento_id
            INNER JOIN contabilidad_tipos_documentos doc ON enc.tipo_documento_id = doc.id
            INNER JOIN contabilidad_mayor cs on mov.mayor_id = cs.id
            INNER JOIN contabilidad_conceptos co on mov.concepto_id = co.id
            WHERE (EXTRACT(YEAR FROM enc.fecha) = in_anio)
              AND (EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesd AND in_mesh)
              AND enc.estado = 2
              AND cs."codigo" BETWEEN in_codigoid AND in_codigo2id
              AND (in_personaid IS NULL OR in_personaid = 0 OR mov.persona_id = in_personaid)
              AND mov.concepto_id = in_concepto
              AND cs.maneja_nits = true
        	ORDER BY enc.fecha, enc.numero, mov.inmueble_id, mov.concepto_id asc
        LOOP
            sumasaldo := coalesce(sumasaldo, 0) + (coalesce(curdatos1.valor_db, 0) - coalesce(curdatos1.valor_cr, 0));

            IF in_mesd <> in_mesh THEN
                IF contador = 1 THEN
                    mes_documento := EXTRACT(MONTH FROM curdatos1.fecha);
                END IF;
                IF EXTRACT(MONTH FROM curdatos1.fecha) <> mes_documento THEN
                    INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, ordenf)
                    VALUES (
                        CONCAT(
                            'SALDO A ',
                            CASE
                                WHEN EXTRACT(MONTH FROM curdatos1.fecha) = 1 THEN CONCAT('DICIEMBRE ', (in_anio - 1)::varchar)
                                ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((EXTRACT(MONTH FROM curdatos1.fecha) - 1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar)
                            END
                        ),
                        sumadb, sumacr, 3, sumasaldo - (curdatos1.valor_db - curdatos1.valor_cr), '2000-01-02'
                    );
                    contador := 1;
                END IF;
                mes_documento := EXTRACT(MONTH FROM curdatos1.fecha);
                contador := 2;
            END IF;

            INSERT INTO cur_aux (
                id, tipo, numero, fecha, docref, concepto, detalle,
                valor_db, valor_cr, saldo, color, fuentes_id, ordenf, base,
                inmueble_id, direccion, mov_id, mayor_id
            )
            VALUES (
                curdatos1.id, curdatos1.tipo, curdatos1.numero, curdatos1.fecha, curdatos1.docref,
                curdatos1.concepto, curdatos1.detalle, curdatos1.valor_db, curdatos1.valor_cr,
                sumasaldo, curdatos1.color, curdatos1.fuentes_id, curdatos1.fecha, curdatos1.base,
                curdatos1.inmueble_id,
                (SELECT ii.direccion FROM inmueble_inmuebles ii WHERE ii.id = curdatos1.inmueble_id),
                curdatos1.mov_id, curdatos1.mayor_id
            );

            sumadb := coalesce(sumadb, 0) + coalesce(curdatos1.valor_db, 0);
            sumacr := coalesce(sumacr, 0) + coalesce(curdatos1.valor_cr, 0);
        END LOOP; 

        SELECT SUM(aux.base) INTO sumbase FROM cur_aux AS aux;

        INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, ordenf, base)
        VALUES (
            CONCAT('SALDO A ', to_char(date(CONCAT('2020/', lpad((in_mesh)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar),
            CASE WHEN curdatos.saldof > 0 THEN coalesce(curdatos.saldof, 0) ELSE 0 END,
            CASE WHEN curdatos.saldof < 0 THEN coalesce(curdatos.saldof, 0) * -1 ELSE 0 END,
            1, coalesce(curdatos.saldof, 0), '2099-01-01', sumbase
        );

    END LOOP;


    IF in_mesd <> in_mesh THEN
        RETURN QUERY SELECT * FROM cur_aux AS aux;
    ELSE
        RETURN QUERY SELECT * FROM cur_aux AS aux ORDER BY aux.ordenf;
    END IF;
	DROP TABLE cur_aux;
END;
$function$
;
