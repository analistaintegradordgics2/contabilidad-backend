-- DROP FUNCTION public.getauxiliarper(int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getauxiliarper(in_anio integer, in_mesi integer, in_mesf integer, in_per integer)
 RETURNS TABLE(id integer, tipo character varying, numero character varying, fecha date, docref character varying, concepto character varying, detalle character varying, valor_db numeric, valor_cr numeric, saldo numeric, color integer, fuentes_id integer, orden character varying, ordenf date, base numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	tienetran	bit = 1;
	err_pa		varchar(100);
	err_linea	varchar(100);
	l_resultado varchar(100);
	lccursor	varchar(30);
	lnnumero 	numeric(18,0);
	lsql		character varying;
	sumbase 	decimal (18,2);
	sumasaldo decimal (18,2) default 0;
	curdatos1 	record;
	curdatos2 	record;
	sumadb decimal (18,2) default 0;
	sumacr decimal (18,2) default 0;
	mes_documento int;
	contador int default 1;
BEGIN
	
	CREATE TEMP TABLE IF NOT EXISTS cur_aux (
		id int,
		tipo varchar(10),
		numero varchar(20),
		fecha date,
		docref varchar(30),
		concepto varchar(10),
		detalle character varying,
		valor_db decimal(18,2), 
		valor_cr decimal(18,2),
		saldo decimal(18,2),
		color int,
		fuentes_id int,
		orden varchar(200),
		ordenf date,
		base decimal(18,2)
	);
	
	CREATE TEMP TABLE IF NOT EXISTS cur_mov (
		id int,
		tipo varchar(30),
		numero varchar(20),
		fecha date,
		docref varchar(30),
		concepto varchar(10),
		detalle character varying,
		valor_db decimal(18,2),
		valor_cr decimal(18,2),
		saldo decimal(18,2),
		color int,
		fuentes_id int,
		mayor_id int, 
		base decimal(18,2)
	);
	
	INSERT INTO cur_mov 
	SELECT enc.id AS id, RTRIM(doc.tipo) AS tipo, RTRIM(enc.numero) AS numero, enc.fecha AS fecha, RTRIM(mov.docref) AS docref, 
		co.codigo AS concepto, RTRIM(mov.detalle) AS detalle, mov.valor_db AS valor_db, mov.valor_cr AS valor_cr, 0 AS saldo, 
		0 AS color, doc.fuentes_id AS fuentes_id, mov.mayor_id AS personas_id, mov.base
	FROM cont_documentos enc, contabilidad_mov mov, contabilidad_tipos_documentos doc, contabilidad_conceptos co, contabilidad_mayor cs  
	WHERE (EXTRACT(YEAR FROM enc.fecha ) = in_anio)
	AND (EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesi AND in_mesf) 
	AND enc.estado = 2 
	AND mov.persona_id = in_per
	AND enc.id = mov.documento_id
	AND enc.tipo_documento_id = doc.id 
	AND mov.concepto_id = co.id 
	AND mov.mayor_id = cs.id
	order by enc.fecha, enc.numero, mov.concepto_id;
	
	FOR curdatos1 IN 
		SELECT mayor.id AS id, CONCAT(RTRIM(mayor."codigo"),' [', RTRIM(mayor."nombre"),' ]') AS nombre,
			CASE
				WHEN in_mesi = 1  THEN COALESCE(nits.sali, 0 ) 
				WHEN in_mesi = 2  THEN COALESCE(nits.sal01, 0 ) 
				WHEN in_mesi = 3  THEN COALESCE(nits.sal02, 0 ) 
				WHEN in_mesi = 4  THEN COALESCE(nits.sal03, 0 ) 
				WHEN in_mesi = 5  THEN COALESCE(nits.sal04, 0 ) 
				WHEN in_mesi = 6  THEN COALESCE(nits.sal05, 0 ) 
				WHEN in_mesi = 7  THEN COALESCE(nits.sal06, 0 ) 
				WHEN in_mesi = 8  THEN COALESCE(nits.sal07, 0 ) 
				WHEN in_mesi = 9  THEN COALESCE(nits.sal08, 0 ) 
				WHEN in_mesi = 10 THEN COALESCE(nits.sal09, 0 ) 
				WHEN in_mesi = 11 THEN COALESCE(nits.sal10, 0 ) 
				WHEN in_mesi = 12 THEN COALESCE(nits.sal11, 0 ) 
				WHEN in_mesi = 13 THEN COALESCE(nits.sal12, 0 ) 
				END AS saldoi,
			CASE
				WHEN in_mesf = 1  THEN COALESCE(nits.sal01, 0 ) 
				WHEN in_mesf = 2  THEN COALESCE(nits.sal02, 0 ) 
				WHEN in_mesf = 3  THEN COALESCE(nits.sal03, 0 ) 
				WHEN in_mesf = 4  THEN COALESCE(nits.sal04, 0 ) 
				WHEN in_mesf = 5  THEN COALESCE(nits.sal05, 0 ) 
				WHEN in_mesf = 6  THEN COALESCE(nits.sal06, 0 ) 
				WHEN in_mesf = 7  THEN COALESCE(nits.sal07, 0 ) 
				WHEN in_mesf = 8  THEN COALESCE(nits.sal08, 0 ) 
				WHEN in_mesf = 9  THEN COALESCE(nits.sal09, 0 ) 
				WHEN in_mesf = 10 THEN COALESCE(nits.sal10, 0 ) 
				WHEN in_mesf = 11 THEN COALESCE(nits.sal11, 0 ) 
				WHEN in_mesf = 12 THEN COALESCE(nits.sal12, 0 ) 
				WHEN in_mesf = 13 THEN COALESCE(nits.sal13, 0 ) 
				END AS saldof  
		FROM contabilidad_saldosnits nits, contabilidad_mayor mayor 
		WHERE nits.personas_id = in_per 
		AND nits.mayor_id = mayor.id 
		AND nits.anio = in_anio
	LOOP
		INSERT INTO cur_aux (detalle,color, valor_db, valor_cr, saldo, orden, ordenf) VALUES (
			curdatos1.nombre, 1, 0, 0, 0, curdatos1.nombre, '2000-01-01'
		);
		
		INSERT INTO cur_aux (detalle, valor_db, valor_cr, saldo, color, orden, ordenf) VALUES ( 
			CONCAT('SALDO A ', CASE WHEN in_mesi = 1 THEN CONCAT('DICIEMBRE ',(in_anio-1)::varchar) 
			ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((in_mesi-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar) END), 
			CASE WHEN curdatos1.saldoi > 0 THEN curdatos1.saldoi ELSE 0 END, CASE WHEN curdatos1.saldoi < 0 THEN curdatos1.saldoi * -1 ELSE 0 END, 
			0, 3, curdatos1.nombre, '2000-01-02'
		);
	
		sumbase := 0;
		sumasaldo := curdatos1.saldoi;
		mes_documento := in_mesi;
		contador := 1;
		sumadb := CASE WHEN curdatos1.saldoi > 0 THEN curdatos1.saldoi ELSE 0 END;
		sumacr := CASE WHEN curdatos1.saldoi < 0 THEN curdatos1.saldoi * -1 ELSE 0 END;
		
		for curdatos2 in 
			SELECT 
				mov.id as id,
				mov.tipo as tipo,
				mov.numero as numero,
				mov.fecha as fecha,
				mov.docref as docref,
				mov.concepto as concepto,
				mov.detalle as detalle,
				coalesce(mov.valor_db, 0) as valor_db,
				coalesce(mov.valor_cr, 0) as valor_cr,
				coalesce(mov.saldo, 0) as saldo, 
				mov.color as color,
				mov.fuentes_id as fuentes_id,
				curdatos1.nombre as orden,
				mov.fecha as fecha,
				mov.base as base
			FROM cur_mov AS mov 
			WHERE mayor_id = curdatos1.id
			order by mov.fecha, mov.numero, mov.concepto asc
		loop
			sumasaldo := sumasaldo + (curdatos2.valor_db - curdatos2.valor_cr);
			if in_mesi <> in_mesf then
				if contador = 1 then 
					mes_documento := EXTRACT(MONTH FROM curdatos2.fecha);
				end if;
				if EXTRACT(MONTH FROM curdatos2.fecha) <> mes_documento then 
					INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, orden, ordenf) 
					VALUES (CONCAT('SALDO A ', CASE WHEN EXTRACT(MONTH FROM curdatos2.fecha) = 1 THEN CONCAT('DICIEMBRE ', (in_anio-1)::varchar) 
							ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((EXTRACT(MONTH FROM curdatos2.fecha)-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar) end), 
							sumadb, sumacr, 
							3, sumasaldo - (curdatos2.valor_db - curdatos2.valor_cr), curdatos1.nombre,'2000-01-02');
				end if;
				contador := 2;
				mes_documento := EXTRACT(MONTH FROM curdatos2.fecha);
			end if;
		
			INSERT INTO cur_aux (
				id,
				tipo,
				numero,
				fecha,
				docref,
				concepto,
				detalle,
				valor_db,
				valor_cr,
				saldo,
				color,
				fuentes_id,
				orden,
				ordenf,
				base
			) values (
				curdatos2.id,
				curdatos2.tipo,
				curdatos2.numero,
				curdatos2.fecha,
				curdatos2.docref,
				curdatos2.concepto,
				curdatos2.detalle,
				curdatos2.valor_db,
				curdatos2.valor_cr,
				sumasaldo,
				curdatos2.color,
				curdatos2.fuentes_id,
				curdatos2.orden,
				curdatos2.fecha,
				curdatos2.base
			);
			sumadb := sumadb + curdatos2.valor_db;
			sumacr := sumacr + curdatos2.valor_cr;
		end loop;
	
		SELECT SUM(mov.base) INTO sumbase FROM cur_mov mov WHERE mov.mayor_id = curdatos1.id;
	
		INSERT INTO cur_aux (detalle, valor_db, valor_cr, saldo, color, orden, ordenf, base) VALUES (
		CONCAT('SALDO A ',to_char(date(CONCAT('2020/', lpad(in_mesf::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar),
		CASE WHEN curdatos1.saldof > 0 THEN curdatos1.saldof ELSE 0 END, CASE WHEN curdatos1.saldof < 0 THEN curdatos1.saldof * -1 ELSE 0 END,
		0, 3, curdatos1.nombre, '2099-01-01', sumbase	
		);
	
		--INSERT INTO cur_aux (valor_db, valor_cr, saldo, color, orden, ordenf) VALUES (0, 0, 0, 2, curdatos1.nombre, '2099-12-31');
	END LOOP;

	RETURN QUERY 
		SELECT * FROM cur_aux AS aux;
	DROP TABLE cur_aux;
	DROP TABLE cur_mov;
END
$function$
;
