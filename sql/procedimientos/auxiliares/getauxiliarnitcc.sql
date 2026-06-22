-- DROP FUNCTION public.getauxiliarnitcc(int4, int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getauxiliarnitcc(in_anio integer, in_mesi integer, in_mesf integer, in_nit integer, in_cc integer)
 RETURNS TABLE(id integer, tipo character varying, numero character varying, fecha date, docref character varying, persona_id integer, concepto character varying, nits character varying, detalle character varying, valor_db numeric, valor_cr numeric, saldo numeric, color integer, fuentes_id integer, orden character varying, ordenf date, centro_costos_id integer, base numeric)
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
	saldocci	decimal (18,2)=0;
	saldoccf	decimal (18,2)=0;
BEGIN
	
	CREATE TEMP TABLE IF NOT EXISTS cur_saldos (
		mayor_id int,
		mes int,
		cc_id int,
		suma decimal(18,2)
	);
	INSERT INTO cur_saldos
	SELECT mov.mayor_id AS mayor_id, EXTRACT(MONTH FROM doc.fecha) AS mes, COALESCE(mov.centro_costos_id, 0) AS cc_id, 
		SUM(mov.valor_db - mov.valor_cr) AS suma
	FROM contabilidad_mov mov, cont_documentos doc, contabilidad_mayor mayor
	WHERE mov.documento_id = doc.id 
	AND mov.mayor_id = mayor.id
	AND (EXTRACT(YEAR FROM doc.fecha ) = in_anio) 
	AND doc.estado = 2 
	AND mov.persona_id = in_nit 
	AND mov.centro_costos_id = in_cc
	AND (EXTRACT(MONTH FROM doc.fecha) <= in_mesf) 
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
		persona_id int,
		concepto varchar(10),
		nits varchar(500),
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
	
	INSERT INTO cur_mov 
	SELECT enc.id AS id, RTRIM(doc.tipo) AS tipo, RTRIM(enc.numero) AS numero, enc.fecha AS fecha, RTRIM(mov.docref) AS docref, 
		co.codigo AS concepto, mov.persona_id as persona_id, RTRIM(mov.detalle) AS detalle, CONCAT(RTRIM(per.documento),' - ',RTRIM(per.n_completo)) AS nits, 
		mov.valor_db AS valor_db, mov.valor_cr AS valor_cr, 0 AS saldo, 0 AS color, doc.fuentes_id AS fuentes_id, 
		mov.mayor_id AS mayor_id, COALESCE(mov.centro_costos_id, 0), mov.base as base
	FROM cont_documentos enc, contabilidad_mov mov, contabilidad_tipos_documentos doc, contabilidad_conceptos co, contabilidad_mayor cs, personas_persona per   
	WHERE (EXTRACT(YEAR FROM enc.fecha ) = in_anio)  
	AND (EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesi AND in_mesf) 
	AND enc.estado = 2 
	AND mov.persona_id = in_nit 
	AND mov.centro_costos_id = in_cc 
	AND enc.id = mov.documento_id 
	AND enc.tipo_documento_id = doc.id 
	AND mov.concepto_id = co.id 
	AND mov.mayor_id = cs.id 
	AND mov.persona_id = per.id
	order by enc.fecha, enc.numero, mov.concepto_id asc;
	
	FOR curdatos1 IN 
	SELECT mayor.id AS id, CONCAT(RTRIM(mayor."codigo"),' ::: ',RTRIM(mayor."nombre")) AS nombre  
	FROM cur_saldos AS saldos, contabilidad_mayor AS mayor 
	WHERE saldos.mayor_id = mayor.id 
	GROUP BY mayor.id, RTRIM(mayor."codigo"), RTRIM(mayor."nombre")
	ORDER BY rtrim(mayor."codigo") ASC 
	LOOP
		SELECT COALESCE(SUM(curs.suma),0) INTO saldocci from cur_saldos AS curs 
		WHERE curs.mayor_id = curdatos1.id 
		AND mes <= (in_mesi-1);
	
		SELECT COALESCE(SUM(curs.suma),0) INTO saldoccf from cur_saldos AS curs 
		WHERE curs.mayor_id = curdatos1.id 
		AND mes <= in_mesf;
	
		INSERT INTO cur_aux (detalle,color, valor_db, valor_cr, saldo, orden, ordenf) VALUES (
			curdatos1.nombre, 1, 0, 0, 0, curdatos1.nombre, '2000-01-01'
		);
	
		INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, orden, ordenf) VALUES (
			CONCAT('SALDO A ', CASE WHEN in_mesi = 1 THEN CONCAT('DICIEMBRE ', (in_anio-1)::varchar) 
			ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((in_mesi-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar)END),
			0, 0, 3, saldocci, curdatos1.nombre, '2000-01-02'
		);
	
		sumasaldo := saldocci;
	
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
				mov.detalle as detalle,
				coalesce(mov.valor_db, 0) as valor_db,
				coalesce(mov.valor_cr, 0) as valor_cr,
				coalesce(mov.saldo, 0) as saldo,
				mov.color as color,
				mov.fuentes_id as fuentes_id,
				curdatos1.nombre as nombre,
				mov.fecha as ordenf,
				mov.centro_costos_id as centro_costos_id,
				mov.base as base
			FROM cur_mov as mov
			WHERE mov.mayor_id = curdatos1.id 
		loop
			sumasaldo := sumasaldo + (curdatos2.valor_db - curdatos2.valor_cr);
			INSERT INTO cur_aux (
				id,
				tipo,
				numero,
				fecha,
				docref,
				persona_id,
				concepto,
				nits,
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
		end loop;
		
		SELECT SUM(mov.base) INTO sumbase FROM cur_mov AS mov WHERE mov.persona_id = curdatos1.id;
	
		INSERT INTO cur_aux (id, detalle, valor_db, valor_cr, color, saldo, base) VALUES (
			99,
			CONCAT('SALDO A ',CONCAT(to_char(date(CONCAT('2020/',lpad(in_mesf::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ',in_anio::varchar)),
			0, 0, 3, saldoccf, sumbase
		);
	
		--INSERT INTO cur_aux (detalle, color, valor_db, valor_cr, saldo) VALUES ('', 1, 0, 0, 0);
		--INSERT INTO cur_aux (valor_db, valor_cr, color, saldo, orden, ordenf) VALUES (0, 0, 2, 0, curdatos1.nombre, '2099-01-02');
	END LOOP;

	RETURN QUERY SELECT * FROM cur_aux AS aux;
	DROP TABLE cur_aux;
	DROP TABLE cur_mov;
	DROP TABLE cur_saldos;
END
$function$
;
