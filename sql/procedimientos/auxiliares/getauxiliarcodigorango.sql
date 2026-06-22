-- DROP FUNCTION public.getauxiliarcodigorango(date, date, varchar, varchar);

CREATE OR REPLACE FUNCTION public.getauxiliarcodigorango(in_fechaini date, in_fechafin date, in_desde character varying, in_hasta character varying)
 RETURNS TABLE(id integer, tipo character varying, numero character varying, fecha date, docref character varying, concepto character varying, nits character varying, nombre character varying, detalle character varying, valor_db numeric, valor_cr numeric, saldo numeric, color integer, fuentes_id integer, orden character varying, ordenf date, base numeric, orden_item integer)
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
	valor_descontar decimal (18,2) default 0;
 	rec RECORD;
	contador_orden int := 0;
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
		base decimal(18,2),
		orden_item int
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
		persona_id int,
		base decimal(18,2)
	);
	
	INSERT INTO cur_mov 
		SELECT 
			enc.id AS id, 
			RTRIM(doc.tipo) AS tipo, 
			RTRIM(enc.numero) AS numero, 
			enc.fecha AS fecha, 
			RTRIM(mov.docref) as docref, 
			co.codigo AS concepto, 
			RTRIM(per.documento) as nits, 
			RTRIM(per.n_completo) as nombre, 
			RTRIM(mov.detalle) AS detalle, 
			mov.valor_db AS valor_db, 
			mov.valor_cr AS valor_cr, 
			0 AS saldo,0 AS color, 
			doc.fuentes_id AS fuentes_id, 
			mov.mayor_id AS persona_id,
			mov.base
		FROM cont_documentos enc 
			inner join contabilidad_mov mov 			on mov.documento_id = enc.id 
			inner join contabilidad_tipos_documentos doc on  enc.tipo_documento_id = doc.id 
			inner join contabilidad_conceptos co 		on  mov.concepto_id = co.id 
			inner join contabilidad_mayor cs 			on  mov.mayor_id = cs.id 
			inner join personas_persona per  	on mov.persona_id = per.id
		WHERE enc.fecha BETWEEN in_fechaini AND in_fechafin 
			AND enc.estado = 2 
			AND (LEFT(
		        TRIM(cs."codigo"),
		        LENGTH(TRIM(in_hasta))
			    )
			BETWEEN LEFT(TRIM(in_desde), LENGTH(TRIM(in_hasta)))
			    AND TRIM(in_hasta) )
			ORDER BY enc.fecha, enc.numero, mov.concepto_id ASC;

		
		valor_descontar := 0;

		SELECT 
			sum(mov.valor_db - mov.valor_cr) into valor_descontar
		FROM cont_documentos enc 
			inner join contabilidad_mov mov 			on mov.documento_id = enc.id 
			inner join contabilidad_mayor cs 			on  mov.mayor_id = cs.id 	
		WHERE enc.fecha < in_fechaini and extract(year from enc.fecha) =  extract(year from in_fechaini)
			and (EXTRACT(MONTH FROM in_fechaini) -1) < EXTRACT(MONTH FROM enc.fecha)
			AND enc.estado = 2 
			AND  (LEFT(
		        TRIM(cs."codigo"),
		        LENGTH(TRIM(in_hasta))
			    )
			BETWEEN LEFT(TRIM(in_desde), LENGTH(TRIM(in_hasta)))
			    AND TRIM(in_hasta) )  ;


	FOR curdatos1 IN 		
		SELECT 
			mayor.id AS id, 
			CONCAT(RTRIM(mayor."codigo"), ' ::: ', RTRIM(mayor."nombre")) AS nombre, 
			CASE
			    WHEN EXTRACT(MONTH FROM in_fechaini) = 1  and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sali, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 2  and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal01, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 3  and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal02, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 4  and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal03, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 5  and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal04, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 6  and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal05, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 7  and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal06, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 8  and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal07, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 9  and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal08, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 10 and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal09, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 11 and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal10, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 12 and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal11, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechaini) = 13 and saldos.anio = EXTRACT(YEAR FROM in_fechaini) THEN COALESCE(saldos.sal12, 0 ) 
				END AS saldoi,
			CASE
				WHEN EXTRACT(MONTH FROM in_fechafin) = 1  and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal01, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 2  and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal02, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 3  and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal03, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 4  and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal04, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 5  and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal05, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 6  and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal06, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 7  and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal07, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 8  and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal08, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 9  and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal09, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 10 and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal10, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 11 and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal11, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 12 and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal12, 0 ) 
				WHEN EXTRACT(MONTH FROM in_fechafin) = 13 and saldos.anio = EXTRACT(YEAR FROM in_fechafin) THEN COALESCE(saldos.sal13, 0 ) 
			    END AS saldof  
		FROM contabilidad_saldos saldos 
			inner join contabilidad_mayor mayor on  saldos.mayor_id = mayor.id 
		WHERE  (LEFT(
		        TRIM(mayor."codigo"),
		        LENGTH(TRIM(in_hasta))
			    )
			BETWEEN LEFT(TRIM(in_desde), LENGTH(TRIM(in_hasta)))
			    AND TRIM(in_hasta) )  
			AND saldos.anio BETWEEN EXTRACT(YEAR FROM in_fechaini) AND EXTRACT(YEAR FROM in_fechafin)
			AND lower(mayor.tipo) = 'auxiliar' 
			ORDER BY RTRIM(mayor."codigo") ASC 
	loop
		--raise notice '---> se totea aca';
		contador_orden := contador_orden + 1;
		INSERT INTO cur_aux (detalle, color, valor_db, valor_cr, saldo, orden, ordenf, orden_item) VALUES (	curdatos1.nombre, 1, 0, 0, 0, curdatos1.nombre, '2000-01-01', contador_orden);
		
		contador_orden := contador_orden + 1;
		INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, orden, ordenf, orden_item) VALUES (
			CONCAT('SALDO A ', CASE WHEN EXTRACT(MONTH FROM in_fechaini) = 1 THEN CONCAT('DICIEMBRE ', (EXTRACT(YEAR FROM in_fechaini)-1)::varchar) 
			ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((EXTRACT(MONTH FROM in_fechaini)-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', EXTRACT(YEAR FROM in_fechaini)::varchar)END),
			0, 0, 3, (curdatos1.saldoi + coalesce(valor_descontar,0)) , curdatos1.saldof, '2000-01-02', contador_orden);
			
		sumasaldo := coalesce(curdatos1.saldoi,0) + coalesce(valor_descontar,0)  ;
		mes_documento := EXTRACT(MONTH FROM in_fechaini);
		contador := 1;

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
			WHERE persona_id = curdatos1.id
			ORDER BY mov.fecha, mov.numero asc
		loop 			
			sumasaldo := sumasaldo + (curdatos2.valor_db - curdatos2.valor_cr);
			--raise notice 'SAlDO--->%',sumasaldo;
			if EXTRACT(MONTH FROM in_fechaini) <> EXTRACT(MONTH FROM in_fechafin) then
				if contador = 1 then 
					mes_documento := EXTRACT(MONTH FROM curdatos2.fecha);
				end if;
				if EXTRACT(MONTH FROM curdatos2.fecha) <> mes_documento then 
					contador_orden := contador_orden + 1;
					INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, orden, ordenf, orden_item) 
					VALUES (CONCAT('SALDO A ', CASE WHEN EXTRACT(MONTH FROM curdatos2.fecha) = 1 THEN CONCAT('DICIEMBRE ', (EXTRACT(YEAR FROM in_fechaini)-1)::varchar) 
					ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((EXTRACT(MONTH FROM curdatos2.fecha)-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', EXTRACT(YEAR FROM in_fechaini)::varchar) end), 
					sumadb, sumacr, 
					3, sumasaldo , curdatos1.nombre,'2000-01-02', contador_orden);
				end if;
				contador := 2;
				mes_documento := EXTRACT(MONTH FROM curdatos2.fecha);
			end if;
			--raise notice '---> se totea aca 2 % ---- % % % %', curdatos1.nombre,curdatos2.numero,curdatos2.valor_db,curdatos2.valor_cr,sumasaldo;
			contador_orden := contador_orden + 1;
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
				base,
				orden_item
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
				curdatos2.base,
				contador_orden
			);
			sumadb := sumadb + curdatos2.valor_db;
			sumacr := sumacr + curdatos2.valor_cr;
		end loop;

		SELECT SUM(mov.base) INTO sumbase FROM cur_mov AS mov WHERE mov.persona_id = curdatos1.id;
		contador_orden := contador_orden + 1;
		INSERT INTO cur_aux (id, detalle, valor_db, valor_cr, color, saldo, orden, ordenf, base, orden_item) VALUES (
			99,
			CONCAT('SALDO A ',CONCAT(to_char(date(CONCAT('2020/',lpad(EXTRACT(MONTH FROM in_fechafin)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ',EXTRACT(YEAR FROM in_fechafin)::varchar)),
			0, 0, 3, sumasaldo, curdatos1.nombre, '2099-01-01', sumbase, contador_orden
		);
	
		--INSERT INTO cur_aux (valor_db, valor_cr, color, saldo, orden, ordenf) VALUES (0, 0, 2, 0, curdatos1.nombre, '2099-01-02');
	END LOOP;


	RETURN QUERY SELECT * FROM cur_aux as aux ORDER BY aux.orden_item;
	DROP TABLE cur_aux;
	DROP TABLE cur_mov;

END
$function$
;
