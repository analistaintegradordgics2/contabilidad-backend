-- DROP FUNCTION public.getauxiliarcodigo(int4, int4, int4, varchar, varchar);

CREATE OR REPLACE FUNCTION public.getauxiliarcodigo(in_anio integer, in_mesi integer, in_mesf integer, in_desde character varying, in_hasta character varying)
 RETURNS TABLE(id integer, tipo character varying, numero character varying, fecha date, docref character varying, concepto character varying, nits character varying, nombre character varying, detalle character varying, valor_db numeric, valor_cr numeric, saldo numeric, color integer, fuentes_id integer, orden character varying, ordenf date, base numeric)
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
	curdatos1 record;
	curdatos2 record;
	sumadb decimal (18,2) default 0;
	sumacr decimal (18,2) default 0;
	mes_documento int;
	contador int default 1;
BEGIN

	IF  length(RTRIM(in_hasta)) = 0 THEN
		in_hasta := in_desde;
	END IF;
	
	in_hasta := CONCAT(in_hasta, '99');
	-- Creamos una tabla temporal para las cuentas auxiliares y los movimientos
	CREATE TEMP TABLE IF NOT EXISTS cur_aux (
		id int,
		tipo varchar(10),
		numero varchar(20),
		fecha date,
		docref varchar(30),
		concepto varchar(10),
		nits varchar(500),
		nombre varchar(500),
		detalle character varying,
		valor_db decimal(18,2),
		valor_cr decimal(18,2),
		saldo decimal(18,2),
		color int,
		fuentes_id int,
		orden character varying,
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
		nits varchar(500),
		nombre varchar(500),
		detalle character varying,
		valor_db decimal(18,2),
		valor_cr decimal(18,2),
		saldo decimal(18,2),
		color int,
		fuentes_id int,
		personas_id int,
		base decimal(18,2)
	);
	
	INSERT INTO cur_mov 
	SELECT enc.id AS id, RTRIM(doc.tipo) AS tipo, RTRIM(enc.numero) AS numero, enc.fecha AS fecha, RTRIM(mov.docref) as docref, 
	co.codigo AS concepto, RTRIM(per.documento) as nits, RTRIM(per.n_completo) as nombre, RTRIM(mov.detalle) AS detalle, 
	mov.valor_db AS valor_db, mov.valor_cr AS valor_cr, 0 AS saldo,0 AS color, doc.fuentes_id AS fuentes_id, mov.mayor_id AS personas_id,
	mov.base
	FROM cont_documentos enc, contabilidad_mov mov, contabilidad_tipos_documentos doc , contabilidad_conceptos co , contabilidad_mayor cs, personas_persona per   
	WHERE (EXTRACT(YEAR FROM enc.fecha ) = in_anio) 
	AND (EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesi AND in_mesf) 
	AND enc.estado = 2 
	AND (cs."codigo" BETWEEN in_desde AND in_hasta) 
	AND enc.id = mov.documento_id 
	AND enc.tipo_documento_id = doc.id 
	AND mov.concepto_id = co.id 
	AND mov.mayor_id = cs.id 
	AND mov.persona_id = per.id
	order by enc.fecha, enc.numero, mov.concepto_id asc;

	
	
	FOR curdatos1 IN 		
		SELECT mayor.id AS id, CONCAT(RTRIM(mayor."codigo"), ' ::: ', RTRIM(mayor."nombre")) AS nombre, 
			CASE
			    WHEN in_mesi = 1  THEN COALESCE(saldos.sali, 0 ) 
				WHEN in_mesi = 2  THEN COALESCE(saldos.sal01, 0 ) 
				WHEN in_mesi = 3  THEN COALESCE(saldos.sal02, 0 ) 
				WHEN in_mesi = 4  THEN COALESCE(saldos.sal03, 0 ) 
				WHEN in_mesi = 5  THEN COALESCE(saldos.sal04, 0 ) 
				WHEN in_mesi = 6  THEN COALESCE(saldos.sal05, 0 ) 
				WHEN in_mesi = 7  THEN COALESCE(saldos.sal06, 0 ) 
				WHEN in_mesi = 8  THEN COALESCE(saldos.sal07, 0 ) 
				WHEN in_mesi = 9  THEN COALESCE(saldos.sal08, 0 ) 
				WHEN in_mesi = 10 THEN COALESCE(saldos.sal09, 0 ) 
				WHEN in_mesi = 11 THEN COALESCE(saldos.sal10, 0 ) 
				WHEN in_mesi = 12 THEN COALESCE(saldos.sal11, 0 ) 
				WHEN in_mesi = 13 THEN COALESCE(saldos.sal12, 0 ) 
				END AS saldoi,
			CASE
				WHEN in_mesf = 1  THEN COALESCE(saldos.sal01, 0 ) 
				WHEN in_mesf = 2  THEN COALESCE(saldos.sal02, 0 ) 
				WHEN in_mesf = 3  THEN COALESCE(saldos.sal03, 0 ) 
				WHEN in_mesf = 4  THEN COALESCE(saldos.sal04, 0 ) 
				WHEN in_mesf = 5  THEN COALESCE(saldos.sal05, 0 ) 
				WHEN in_mesf = 6  THEN COALESCE(saldos.sal06, 0 ) 
				WHEN in_mesf = 7  THEN COALESCE(saldos.sal07, 0 ) 
				WHEN in_mesf = 8  THEN COALESCE(saldos.sal08, 0 ) 
				WHEN in_mesf = 9  THEN COALESCE(saldos.sal09, 0 ) 
				WHEN in_mesf = 10 THEN COALESCE(saldos.sal10, 0 ) 
				WHEN in_mesf = 11 THEN COALESCE(saldos.sal11, 0 ) 
				WHEN in_mesf = 12 THEN COALESCE(saldos.sal12, 0 ) 
				WHEN in_mesf = 13 THEN COALESCE(saldos.sal13, 0 ) 
			    END AS saldof  
		FROM contabilidad_saldos AS saldos, contabilidad_mayor AS mayor 
		WHERE mayor."codigo" BETWEEN in_desde AND in_hasta 
		AND saldos.mayor_id = mayor.id 
		AND saldos.anio = in_anio 
		AND lower(mayor.tipo) = 'auxiliar' 
		ORDER BY RTRIM(mayor."codigo") ASC 
	loop
		raise notice '---> se totea aca';
		INSERT INTO cur_aux (detalle, color, valor_db, valor_cr, saldo, orden, ordenf) VALUES (
			curdatos1.nombre, 1, 0, 0, 0, curdatos1.nombre, '2000-01-01'
		);
	
		INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, orden, ordenf) VALUES (
			CONCAT('SALDO A ', CASE WHEN in_mesi = 1 THEN CONCAT('DICIEMBRE ', (in_anio-1)::varchar) 
			ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((in_mesi-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar)END),
			0, 0, 3, curdatos1.saldoi, curdatos1.saldof, '2000-01-02'
		);
			
		sumasaldo := curdatos1.saldoi;
		mes_documento := in_mesi;
		contador := 1;
		sumacr := 0;
		
		for curdatos2 in 
			SELECT 
				mov.id as id,
				mov.tipo as tipo,
				mov.numero as numero,
				mov.fecha as fecha,
				mov.docref as docref,
				mov.concepto as concepto,
				mov.nits as nits,
				mov.nombre as nombre,
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
			WHERE personas_id = curdatos1.id
			ORDER BY mov.fecha, mov.numero, mov.concepto asc
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
			raise notice '---> se totea aca 2 % % % %', curdatos2.numero,curdatos2.valor_db,curdatos2.valor_cr,sumasaldo;
			INSERT INTO cur_aux (
				id,
				tipo,
				numero,
				fecha,
				docref,
				concepto,
				nits,
				nombre,
				detalle,
				valor_db,
				valor_cr,
				saldo,
				color,
				fuentes_id,
				orden,
				ordenf,
				base
			) 
			values ( 
				curdatos2.id,
				curdatos2.tipo,
				curdatos2.numero,
				curdatos2.fecha,
				curdatos2.docref,
				curdatos2.concepto,
				curdatos2.nits,
				curdatos2.nombre,
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
		
		SELECT SUM(mov.base) INTO sumbase FROM cur_mov AS mov WHERE mov.persona_id = curdatos1.id;
	
		INSERT INTO cur_aux (id, detalle, valor_db, valor_cr, color, saldo, orden, ordenf, base) VALUES (
			99,
			CONCAT('SALDO A ',CONCAT(to_char(date(CONCAT('2020/',lpad(in_mesf::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ',in_anio::varchar)),
			0, 0, 3, curdatos1.saldof, curdatos1.nombre, '2099-01-01', sumbase
		);
	
		--INSERT INTO cur_aux (valor_db, valor_cr, color, saldo, orden, ordenf) VALUES (0, 0, 2, 0, curdatos1.nombre, '2099-01-02');
	END LOOP;

	RETURN QUERY SELECT * FROM cur_aux as aux;
	DROP TABLE cur_aux;
	DROP TABLE cur_mov;

END
$function$
;
