-- DROP FUNCTION public.getauxcodnit(int4, int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getauxcodnit(in_codigoid integer, in_personaid integer, in_anio integer, in_mesd integer, in_mesh integer)
 RETURNS TABLE(id integer, tipo character varying, numero character varying, fecha date, docref character varying, concepto character varying, detalle character varying, valor_db numeric, valor_cr numeric, saldo numeric, color integer, fuentes_id integer, ordenf date, base numeric, mov_id integer, mayor_id integer)
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
	sumasaldo int default 0;
	curdatos1 record;
	sumadb int default 0;
	sumacr int default 0;
	mes_documento int;
	contador int default 1;
BEGIN
	-- Creamos una tabla temporal para las cuentas auxiliares y los movimientos
	CREATE TEMP TABLE IF NOT EXISTS cur_aux (
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
		mov_id integer,
		mayor_id integer
	);
	
	SELECT 
		CASE
			WHEN in_mesd = 1  THEN COALESCE(nits.sali, 0) 
			WHEN in_mesd = 2  THEN COALESCE(nits.sal01, 0) 
			WHEN in_mesd = 3  THEN COALESCE(nits.sal02, 0) 
			WHEN in_mesd = 4  THEN COALESCE(nits.sal03, 0) 
			WHEN in_mesd = 5  THEN COALESCE(nits.sal04, 0) 
			WHEN in_mesd = 6  THEN COALESCE(nits.sal05, 0) 
			WHEN in_mesd = 7  THEN COALESCE(nits.sal06, 0) 
			WHEN in_mesd = 8  THEN COALESCE(nits.sal07, 0) 
			WHEN in_mesd = 9  THEN COALESCE(nits.sal08, 0) 
			WHEN in_mesd = 10 THEN COALESCE(nits.sal09, 0) 
			WHEN in_mesd = 11 THEN COALESCE(nits.sal10, 0) 
			WHEN in_mesd = 12 THEN COALESCE(nits.sal11, 0) 
			WHEN in_mesd = 13 THEN COALESCE(nits.sal12, 0) 
			END,
		CASE
			WHEN in_mesh = 1  THEN COALESCE(nits.sal01, 0) 
			WHEN in_mesh = 2  THEN COALESCE(nits.sal02, 0) 
			WHEN in_mesh = 3  THEN COALESCE(nits.sal03, 0) 
			WHEN in_mesh = 4  THEN COALESCE(nits.sal04, 0) 
			WHEN in_mesh = 5  THEN COALESCE(nits.sal05, 0) 
			WHEN in_mesh = 6  THEN COALESCE(nits.sal06, 0) 
			WHEN in_mesh = 7  THEN COALESCE(nits.sal07, 0) 
			WHEN in_mesh = 8  THEN COALESCE(nits.sal08, 0) 
			WHEN in_mesh = 9  THEN COALESCE(nits.sal09, 0) 
			WHEN in_mesh = 10 THEN COALESCE(nits.sal10, 0) 
			WHEN in_mesh = 11 THEN COALESCE(nits.sal11, 0) 
			WHEN in_mesh = 12 THEN COALESCE(nits.sal12, 0) 
			WHEN in_mesh = 13 THEN COALESCE(nits.sal13, 0) 
			END INTO saldoi, saldof
		FROM contabilidad_saldosnits AS nits 
		WHERE nits.mayor_id = in_codigoid 
		AND nits.personas_id = in_personaid 
		AND nits.anio = in_anio;
	
	INSERT INTO cur_aux ( detalle, valor_db, valor_cr, color, saldo, ordenf) VALUES (
		CONCAT('SALDO A ', CASE WHEN in_mesd = 1 THEN CONCAT('DICIEMBRE ', (in_anio-1)::varchar) 
		ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((in_mesd-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar)END), 
		CASE WHEN saldoi > 0 THEN saldoi ELSE 0 END, CASE WHEN saldoi > 0 THEN 0 ELSE saldoi * -1 END, 1, 0, '2000-01-01');																									
	
	sumasaldo := saldoi;
	sumadb := CASE WHEN saldoi > 0 THEN saldoi ELSE 0 END;
	sumacr := CASE WHEN saldoi < 0 THEN saldoi * -1 ELSE 0 END;
	--, mov.concepto_id
	for curdatos1 in
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
			mov.id as mov_id,
			mov.mayor_id as mayor_id
		FROM cont_documentos enc, contabilidad_mov mov, contabilidad_tipos_documentos doc, contabilidad_conceptos co, contabilidad_mayor cs   
		WHERE (EXTRACT(YEAR FROM enc.fecha ) = in_anio) 
		AND (EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesd AND in_mesh) 
		AND enc.estado = 2
		AND mov.mayor_id = in_codigoid 
		AND mov.persona_id = in_personaid
		AND enc.id = mov.documento_id 
		AND enc.tipo_documento_id = doc.id 
		AND mov.concepto_id = co.id 
		AND mov.mayor_id = cs.id
		AND cs.maneja_nits = true
		order by enc.fecha, 
			enc.numero, mov.concepto_id asc
		
	loop 
		sumasaldo := coalesce(sumasaldo, 0) + (coalesce(curdatos1.valor_db, 0) - coalesce(curdatos1.valor_cr, 0));
		
		if in_mesd <> in_mesh then
			if contador = 1 then 
				mes_documento := EXTRACT(MONTH FROM curdatos1.fecha);
			end if;
			if EXTRACT(MONTH FROM curdatos1.fecha) <> mes_documento then 
				INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, ordenf) 
				VALUES (CONCAT('SALDO A ', CASE WHEN EXTRACT(MONTH FROM curdatos1.fecha) = 1 THEN CONCAT('DICIEMBRE ', (in_anio-1)::varchar) 
				ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((EXTRACT(MONTH FROM curdatos1.fecha)-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar) end), 
				sumadb, sumacr, 
				3, sumasaldo - (curdatos1.valor_db - curdatos1.valor_cr),'2000-01-02');
				contador := 1;
			end if;
			mes_documento := EXTRACT(MONTH FROM curdatos1.fecha);
			contador := 2;
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
			ordenf,
			base,
			mov_id,
			mayor_id
		) values (
			curdatos1.id,
			curdatos1.tipo,
			curdatos1.numero,
			curdatos1.fecha,
			curdatos1.docref,
			curdatos1.concepto,
			curdatos1.detalle,
			curdatos1.valor_db,
			curdatos1.valor_cr,
			sumasaldo,
			curdatos1.color,
			curdatos1.fuentes_id,
			curdatos1.fecha,
			curdatos1.base,
			curdatos1.mov_id,
			curdatos1.mayor_id
		);
		sumadb := coalesce(sumadb, 0) + coalesce(curdatos1.valor_db, 0);
		sumacr := coalesce(sumacr, 0) + coalesce(curdatos1.valor_cr, 0);
	end loop;
	
	SELECT SUM(aux.base) INTO sumbase FROM cur_aux AS aux;
	
	INSERT INTO cur_aux (detalle, valor_db, valor_cr, color, saldo, ordenf, base) VALUES (
	CONCAT('SALDO A ', to_char(date(CONCAT('2020/', lpad((in_mesh)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ',in_anio::varchar), 
	CASE WHEN saldof > 0 THEN saldof ELSE 0 END, CASE WHEN saldof < 0 THEN saldof * -1 ELSE 0 END, 1, 0, '2099-01-01', sumbase);
	
	if in_mesd <> in_mesh then 
		RETURN QUERY SELECT * FROM cur_aux as aux;
	else
		RETURN QUERY SELECT * FROM cur_aux as aux order by aux.ordenf;
	end if;
	drop table cur_aux;
END
$function$
;
