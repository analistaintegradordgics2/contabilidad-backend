-- DROP FUNCTION public.getauxiliarbancos(int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getauxiliarbancos(in_anio integer, in_mesi integer, in_mesf integer, in_mayor integer)
 RETURNS TABLE(id integer, tipo character varying, numero character varying, fecha date, fechac date, docref character varying, idconc character varying, nrocg character varying, detalle text, cedula character varying, persona character varying, valor_db numeric, valor_cr numeric, color integer, fuentes_id integer, saldo numeric, order_insercion integer)
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
	lsql character varying;
	curdatos1 record;
	detcod character varying;
	saldoini numeric(18,0);
	saldofin numeric(18,0);
	saldo_anterior NUMERIC := 0;
	orden_insercion_counter int default 0;
	
BEGIN
	-- Creamos una tabla temporal para las cuentas auxiliares y los movimientos
	CREATE TEMP TABLE IF NOT EXISTS cur_aux (
		id int,
		tipo varchar(10),
		numero varchar(20),
		fecha date,
		fechac date,
		docref varchar(30),
		idconc varchar(10),
		nrocg varchar(30),
		detalle text,
		cedula varchar(50),
		persona varchar(200),
		valor_db decimal(18,2),
		valor_cr decimal(18,2),
		color int,
		fuentes_id int,
		saldo decimal(18,2),
		order_insercion int
	);
	
	SELECT CONCAT(RTRIM(mayor."codigo"), ' ::: ', RTRIM(mayor."nombre")) AS detalle, 
		CASE
			WHEN in_mesi = 1  THEN COALESCE(saldos.sali, 0) 
			WHEN in_mesi = 2  THEN COALESCE(saldos.sal01, 0) 
			WHEN in_mesi = 3  THEN COALESCE(saldos.sal02, 0) 
			WHEN in_mesi = 4  THEN COALESCE(saldos.sal03, 0) 
			WHEN in_mesi = 5  THEN COALESCE(saldos.sal04, 0) 
			WHEN in_mesi = 6  THEN COALESCE(saldos.sal05, 0) 
			WHEN in_mesi = 7  THEN COALESCE(saldos.sal06, 0) 
			WHEN in_mesi = 8  THEN COALESCE(saldos.sal07, 0) 
			WHEN in_mesi = 9  THEN COALESCE(saldos.sal08, 0) 
			WHEN in_mesi = 10 THEN COALESCE(saldos.sal09, 0) 
			WHEN in_mesi = 11 THEN COALESCE(saldos.sal10, 0) 
			WHEN in_mesi = 12 THEN COALESCE(saldos.sal11, 0) 
			WHEN in_mesi = 13 THEN COALESCE(saldos.sal12, 0) 
			END AS saldoi,
		CASE
			WHEN in_mesf = 1  THEN COALESCE(saldos.sal01, 0) 
			WHEN in_mesf = 2  THEN COALESCE(saldos.sal02, 0) 
			WHEN in_mesf = 3  THEN COALESCE(saldos.sal03, 0) 
			WHEN in_mesf = 4  THEN COALESCE(saldos.sal04, 0) 
			WHEN in_mesf = 5  THEN COALESCE(saldos.sal05, 0) 
			WHEN in_mesf = 6  THEN COALESCE(saldos.sal06, 0) 
			WHEN in_mesf = 7  THEN COALESCE(saldos.sal07, 0) 
			WHEN in_mesf = 8  THEN COALESCE(saldos.sal08, 0) 
			WHEN in_mesf = 9  THEN COALESCE(saldos.sal09, 0) 
			WHEN in_mesf = 10 THEN COALESCE(saldos.sal10, 0) 
			WHEN in_mesf = 11 THEN COALESCE(saldos.sal11, 0) 
			WHEN in_mesf = 12 THEN COALESCE(saldos.sal12, 0) 
			WHEN in_mesf = 13 THEN COALESCE(saldos.sal13, 0) 
			END AS saldof INTO detcod, saldoini, saldofin 
	FROM contabilidad_saldos saldos, contabilidad_mayor mayor
	WHERE saldos.anio = in_anio
	AND saldos.mayor_id = mayor.id
	AND saldos.mayor_id = in_mayor;
	
	if detcod is null then 
		detcod := (select CONCAT(RTRIM(cm."codigo"), ' ::: ', RTRIM(cm."nombre")) AS detalle from contabilidad_mayor cm where cm.id = in_mayor);
	end if;

	INSERT INTO cur_aux (detalle, color, valor_db, valor_cr,order_insercion) VALUES (detcod, 1, 0, 0,1);
	
	orden_insercion_counter := 1;
	INSERT INTO cur_aux (detalle, valor_db, valor_cr, color,order_insercion) VALUES (
		CONCAT('SALDO A ', CASE WHEN in_mesi = 1 THEN CONCAT('DICIEMBRE ', (in_anio-1)::varchar) 
		ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((in_mesi-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar) end), 
		CASE WHEN saldoini > 0 THEN saldoini ELSE 0 END, CASE WHEN saldoini < 0 THEN saldoini * -1 ELSE 0 END, 3,orden_insercion_counter + 1
	);

	saldo_anterior := saldoini;
	orden_insercion_counter := orden_insercion_counter + 1;
	FOR curdatos1 IN 
		SELECT 
		    enc.id AS id,
		    RTRIM(doc.tipo) AS tipo,
		    RTRIM(enc.numero) AS numero,
		    enc.fecha AS fecha,
		    cons.fecha AS consfecha,
		    mov.docref AS docref,
		    RTRIM(co.codigo::text) AS concepto,
		    cons.numero AS consnumero,
		    RTRIM(mov.detalle) AS detalle,
		    per.documento AS documento,
		    per.n_completo AS ncompleto,
		    COALESCE(mov.valor_db, 0) AS valor_db,
		    COALESCE(mov.valor_cr, 0) AS valor_cr,
		    doc.fuentes_id AS fuentes_id,
		    (COALESCE(ABS(mov.valor_db), 0) - COALESCE(ABS(mov.valor_cr), 0)) AS saldo
		FROM contabilidad_mov mov
		INNER JOIN cont_documentos enc
		    ON enc.id = mov.documento_id
		INNER JOIN personas_persona per
		    ON mov.persona_id = per.id
		INNER JOIN contabilidad_tipos_documentos doc
		    ON enc.tipo_documento_id = doc.id
		INNER JOIN contabilidad_conceptos co
		    ON mov.concepto_id = co.id
		LEFT JOIN contabilidad_pagodocumento pago
		    ON enc.id = pago.documento_id
		LEFT JOIN contabilidad_pagoconsignacion cons
		    ON pago.id = cons.pago_id
		WHERE EXTRACT(YEAR FROM enc.fecha) = in_anio
		  AND EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesi AND in_mesf
		  AND enc.estado = 2
		  AND mov.mayor_id = in_mayor
		ORDER BY enc.fecha, enc.numero ASC
	LOOP

		orden_insercion_counter := orden_insercion_counter + 1;
		INSERT INTO cur_aux VALUES (
			curdatos1.id, curdatos1.tipo, curdatos1.numero, curdatos1.fecha, curdatos1.consfecha, curdatos1.docref, curdatos1.concepto, 
			curdatos1.consnumero, curdatos1.detalle, curdatos1.documento, curdatos1.ncompleto, curdatos1.valor_db, curdatos1.valor_cr, 
			0, curdatos1.fuentes_id, (curdatos1.saldo + saldo_anterior),orden_insercion_counter
		);
	saldo_anterior := curdatos1.saldo + saldo_anterior;
	END LOOP;

	INSERT INTO cur_aux (detalle, valor_db, valor_cr, color,order_insercion) VALUES (
		CONCAT('SALDO A ', CONCAT(to_char(date(CONCAT('2020/', lpad(in_mesf::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar)),
		CASE WHEN saldofin > 0 THEN saldofin ELSE 0 END, CASE WHEN saldofin < 0 THEN saldofin * -1 ELSE 0 END, 3,orden_insercion_counter
	);
	RAISE NOTICE '%------------------', (
    SELECT json_agg(json_build_object('numero', cu.numero))
    FROM cur_aux cu 
    );

	RETURN QUERY SELECT * FROM cur_aux order by order_insercion;
	drop table cur_aux;
END
$function$
;
