-- DROP FUNCTION public.getauxiliarcodigocc(int4, int4, int4, varchar, varchar, int4);

CREATE OR REPLACE FUNCTION public.getauxiliarcodigocc(in_anio integer, in_mesi integer, in_mesf integer, in_desde character varying, in_hasta character varying, cc integer)
 RETURNS TABLE(id integer, tipo character varying, numero character varying, fecha date, docref character varying, persona_id integer, concepto character varying, nits character varying, nombre character varying, detalle character varying, valor_db numeric, valor_cr numeric, saldo numeric, color integer, fuentes_id integer, orden character varying, ordenf date, centro_costos_id integer, base numeric)
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
	curdatos1 	record;
	curdatos2 	record;
	curcc		record;
	idcc		numeric(18,0);
	incc		Varchar(50);
	saldocci	decimal (18,2)=0;
	saldoccf	decimal (18,2)=0;
	sumasaldo int default 0;
	sumadb int default 0;
	sumacr int default 0;
	mes_documento int;
	contador int default 1;
BEGIN

	IF  length(RTRIM(in_hasta)) = 0 THEN
		in_hasta := in_desde;
	END IF;
	
	in_hasta := CONCAT(in_hasta, '99');
	
	CREATE TEMP TABLE IF NOT EXISTS cur_saldos (
		mayor_id int,
		mes int,
		cc_id int,
		suma decimal(18,2)
	);
	
	INSERT INTO cur_saldos 
	SELECT mov.mayor_id AS mayor_id, EXTRACT(MONTH FROM doc.fecha) AS mes, COALESCE(mov.centro_costos_id, 0 ) AS cc_id, 
	SUM(mov.valor_db - mov.valor_cr) AS suma 
	FROM contabilidad_mov mov, cont_documentos doc, contabilidad_mayor mayor
	WHERE mov.documento_id = doc.id
	AND mov.mayor_id = mayor.id
	AND EXTRACT(MONTH FROM doc.fecha) = in_anio
	AND doc.estado = 2 
	AND (mayor."codigo" BETWEEN in_desde AND in_hasta) 
	AND EXTRACT(MONTH FROM doc.fecha) <= in_mesf
	GROUP BY mov.mayor_id, EXTRACT(MONTH FROM doc.fecha), mov.centro_costos_id;
	
	CREATE TEMP TABLE IF NOT EXISTS cur_aux (
		id int,
		tipo varchar(10),
		numero varchar(20),
		fecha date,
		docref varchar(30),
		persona_id int,
		concepto varchar(10),
		nits varchar(500),
		nombre varchar(500),
		detalle character varying,
		valor_db decimal(18,2),
		valor_cr decimal(18,2),
		saldo decimal(18,2),
		color int,
		fuentes_id int,
		orden varchar(200),
		ordenf date,
		centro_costos_id int,
		base decimal(18,2)
	);
	
	CREATE TEMP TABLE IF NOT EXISTS cur_mov (
		id int,
		tipo varchar(30),
		numero varchar(20),
		fecha date,
		docref varchar(30),
		concepto varchar(10),
		persona_id int,
		nits varchar(500),
		nombre varchar(500),
		detalle character varying, 
		valor_db decimal(18,2),
		valor_cr decimal(18,2),
		saldo decimal(18,2),
		color int,
		fuentes_id int,
		mayor_id int,
		centro_costos_id int,
		base decimal(18,2)
	);
	
	CREATE TEMP TABLE IF NOT EXISTS curcc1 (
		centro_costos_id int
	);
	
	IF cc = 0 THEN
		INSERT INTO curcc1 VALUES (0);
		INSERT INTO curcc1 SELECT ccos.id FROM contabilidad_centrocostos AS ccos;
	ELSE
		INSERT INTO curcc1 SELECT ccos.id FROM contabilidad_centrocostos AS ccos WHERE ccos.id = cc;
	END IF;
	
	INSERT INTO cur_mov 
	SELECT enc.id AS id, RTRIM(doc.tipo) AS tipo, RTRIM(enc.numero) AS numero, enc.fecha AS fecha, RTRIM(mov.docref) AS docref, 
	co.codigo AS concepto, mov.persona_id as persona_id, RTRIM(per.documento) as nits, RTRIM(per.n_completo) as nombre, RTRIM(mov.detalle) AS detalle, 
	mov.valor_db AS valor_db, mov.valor_cr AS valor_cr, 0 AS saldo, 0 AS color, doc.fuentes_id AS fuentes_id, mov.mayor_id as mayor_id, 
	COALESCE(mov.centro_costos_id, 0), mov.base
	FROM  cont_documentos enc, contabilidad_mov mov, contabilidad_tipos_documentos doc, contabilidad_conceptos co, contabilidad_mayor cs, personas_persona per 
	WHERE (EXTRACT(YEAR FROM enc.fecha ) = in_anio) 
	AND (EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesi AND in_mesf)
	AND enc.estado = 2 
	and (cs."codigo" BETWEEN in_desde AND in_hasta) 
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
		WHERE (mayor."codigo" BETWEEN in_desde AND in_hasta) 
		AND saldos.mayor_id = mayor.id 
		AND saldos.anio = in_anio 
		AND lower(mayor.tipo) = 'auxiliar' 
		ORDER BY RTRIM(mayor."codigo") ASC 
	LOOP
		INSERT INTO cur_aux (detalle,color, valor_db, valor_cr, saldo, orden, ordenf) VALUES (
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
		sumadb := CASE WHEN curdatos1.saldoi > 0 THEN curdatos1.saldoi ELSE 0 END;
		sumacr := CASE WHEN curdatos1.saldoi < 0 THEN curdatos1.saldoi * -1 ELSE 0 END;
	
		FOR curcc IN SELECT COALESCE(curc.centro_costos_id, 0) AS idcc FROM curcc1 AS curc GROUP BY curc.centro_costos_id LOOP
			
			SELECT COALESCE(SUM(curs.suma), 0) INTO saldocci 
			FROM cur_saldos curs 
			WHERE curs.mayor_id = curdatos1.id 
			AND cc_id =  curcc.idcc 
			AND mes <= (in_mesi-1);
		
			IF curcc.idcc = 0 THEN
				INSERT INTO cur_aux (id, detalle, color, valor_db, valor_cr, saldo) 
				VALUES (99, 'SIN CENTRO DE COSTOS', 4, 0, 0, CASE WHEN in_mesi = 1 THEN 0 ELSE saldocci END);
			ELSE
				SELECT CONCAT('CENTRO DE COSTO [', cc.codigo, ']  ', RTRIM(cc.nombre)) INTO incc
				FROM contabilidad_centrocostos cc 
				WHERE cc.id = curcc.idcc;
				INSERT INTO cur_aux (detalle, color, valor_db, valor_cr, saldo) VALUES (
					incc, 4, 0, 0, CASE WHEN in_mesi = 1 THEN 0 ELSE saldocci END
				);
			END IF;
			
			for curdatos2 in 
				SELECT 
					mov.id as id,
					mov.tipo as tipo,
					mov.numero as numero,
					mov.fecha as fecha,
					mov.docref as docref,
					mov.persona_id as persona_id,
					mov.concepto as concepto,
					mov.nits as nits,
					mov.nombre as nombre_persona,
					mov.detalle as detalle,
					coalesce(mov.valor_db, 0) as valor_db,
					coalesce(mov.valor_cr, 0) as valor_cr, 
					coalesce(mov.saldo, 0) as saldo,
					mov.color as color,
					mov.fuentes_id as fuentes_id,
					curdatos1.nombre as nombre,
					mov.fecha AS ordenf,
					mov.centro_costos_id as centro_costos_id,
					mov.base
				FROM cur_mov AS mov 
				WHERE mov.mayor_id = curdatos1.id
				AND mov.centro_costos_id = curcc.idcc
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
					persona_id,
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
					centro_costos_id,
					base
				) values (
					curdatos2.id,
					curdatos2.tipo,
					curdatos2.numero,
					curdatos2.fecha,
					curdatos2.docref,
					curdatos2.persona_id,
					curdatos2.concepto,
					curdatos2.nits,
					curdatos2.nombre_persona,
					curdatos2.detalle,
					curdatos2.valor_db,
					curdatos2.valor_cr,
					sumasaldo,
					curdatos2.color,
					curdatos2.fuentes_id,
					curdatos2.nombre,
					curdatos2.ordenf,
					curdatos2.centro_costos_id,
					curdatos2.base
				);	
			
				sumadb := sumadb + curdatos2.valor_db;
				sumacr := sumacr + curdatos2.valor_cr;
			
			end loop;
			
			SELECT COALESCE(sum(curs.suma),0) INTO saldoccf FROM cur_saldos AS curs
			WHERE curs.mayor_id = curdatos1.id 
			AND curs.cc_id = curcc.idcc 
			AND curs.mes <= in_mesf;
		
			IF curcc.idcc = 0 THEN
				INSERT INTO cur_aux (id, detalle, valor_db, valor_cr, color, saldo) VALUES (
				99,
				CASE WHEN in_mesi = 1 THEN CONCAT('DICIEMBRE ',(in_anio-1)::varchar) 
				ELSE CONCAT(to_char(date(CONCAT('2020/',lpad(in_mesi::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar) END,
				0, 0, 4, saldoccf
				);
			ELSE 
				INSERT INTO cur_aux (id, detalle, valor_db, valor_cr, color, saldo) VALUES (
				99,
				CONCAT('SALDO A ', incc, ' A ', CASE WHEN in_mesi = 1 THEN CONCAT('DICIEMBRE ', (in_anio-1)::varchar) 
				ELSE CONCAT(to_char(date(CONCAT('2020/', lpad(in_mesi::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar)END),
				0, 0, 4, saldoccf
				);
			END IF;
		
			--INSERT INTO cur_aux (detalle, color, valor_db, valor_cr, saldo) VALUES ('', 2, 0, 0, 0);
		
		END LOOP;
	
		SELECT SUM(mov.base) INTO sumbase FROM cur_mov AS mov WHERE mov.persona_id = curdatos1.id;
	
		INSERT INTO cur_aux (id, detalle, valor_db, valor_cr, color, saldo, base) VALUES (
			99,
			CONCAT('SALDO A ', to_char(date(CONCAT('2020/', lpad(in_mesf::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar),
			0, 0, 3, curdatos1.saldof, sumbase
		);
	
		--INSERT INTO cur_aux (detalle, color, valor_db, valor_cr, saldo) VALUES ('', 1, 0, 0, 0);
		--INSERT INTO cur_aux (valor_db, valor_cr, color, saldo, orden, ordenf) VALUES (0, 0, 2, 0, curdatos1.nombre, '2099-01-02');
	END LOOP;

	RETURN QUERY SELECT * FROM cur_aux as aux;
	DROP TABLE cur_aux;
	DROP TABLE cur_mov;
	DROP TABLE cur_saldos;
END
$function$
;
