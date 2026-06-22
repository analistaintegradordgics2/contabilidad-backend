-- DROP FUNCTION public.getauxiliarnit(int4, int4, int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getauxiliarnit(in_anio integer, in_mesi integer, in_mesf integer, in_mayor integer, in_sinsal integer, in_sinmov integer)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
   datos_array jsonb[];
   
	tienetran bit = 1;
	err_pa varchar(100);
	err_linea varchar(100);
	l_resultado varchar(100);
	lccursor varchar(30);
	lnnumero numeric(18,0);
	lsql character varying;
	cantmov int = 0;
	cantsal int = 0;
	sumbase decimal (18,2);
	sumasaldo decimal (18,2) default 0;
	curdatos1 record;
	curdatos2 record;
	sumadb decimal (18,2) default 0;
	sumacr decimal (18,2) default 0;
	mes_documento int;
	contador int default 1;
	saldo_cero boolean default false;
begin

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
		orden varchar(200),
		ordenf date,
		base decimal(18,2)
	);
	
	CREATE TEMP TABLE IF NOT EXISTS cur_mov (
		id integer,
		tipo varchar(30),
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
		personas_id integer,
		base decimal(18,2)
	);

	CREATE TEMP TABLE IF NOT EXISTS cur_temp (
		id integer,
		nombre varchar(255),
		saldoi decimal(18,2),
		saldof decimal(18,2)
	);

	INSERT INTO cur_mov
	SELECT enc.id AS id, RTRIM(doc.tipo) AS tipo, RTRIM(enc.numero) AS numero, enc.fecha AS fecha, RTRIM(mov.docref) AS docref, 
		   co.codigo as concepto, RTRIM(mov.detalle) AS detalle, mov.valor_db AS valor_db, mov.valor_cr AS valor_cr,
		   0 AS saldo, 0 AS color, doc.fuentes_id AS fuentes_id, mov.persona_id AS personas_id, mov.base
	FROM cont_documentos enc, contabilidad_mov mov, contabilidad_tipos_documentos doc, contabilidad_conceptos co, contabilidad_mayor cs   
	WHERE (EXTRACT(YEAR FROM enc.fecha ) = in_anio) 
	AND (EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesi AND in_mesf) 
	AND enc.estado = 2
	AND mov.mayor_id = in_mayor 
	AND enc.id = mov.documento_id 
	AND enc.tipo_documento_id = doc.id 
	AND mov.concepto_id = co.id 
	AND mov.mayor_id = cs.id
	order by enc.fecha, enc.numero, mov.concepto_id asc;

	insert into cur_temp 
		SELECT per.id AS id, CONCAT(RTRIM(per.n_completo), ' [ ', RTRIM(per.documento), ' ]') AS nombre, 
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
		FROM contabilidad_saldosnits AS nits, personas_persona AS per 
		WHERE nits.mayor_id = in_mayor 
		AND nits.personas_id = per.id 
		AND nits.anio = in_anio;
	
	
	for curdatos1 in select * from cur_temp as cur order by RTRIM(cur.nombre) loop
		RAISE NOTICE 'Datos: llega hasta aqui % ', curdatos1.nombre;	
        datos_array := datos_array || jsonb_build_object(
            'detalle', curdatos1.nombre,
            'color', 1,
            'valor_db', 0,
            'valor_cr', 0,
            'saldo', 0,
            'orden', curdatos1.nombre,
            'ordenf', '2000-01-01',
            'id', null,	
			'tipo', null,	
			'numero', null,	
			'fecha', null,	
			'docref', null,	
			'concepto', null,	
			'fuentes_id', null,	
			'base', null,
			'persona_id', curdatos1.id
        );
		
		
		datos_array := datos_array || jsonb_build_object(
			'detalle', CONCAT('SALDO A ', CASE WHEN in_mesi = 1 THEN CONCAT('DICIEMBRE ', (in_anio-1)::varchar) ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((in_mesi-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar) end),
			'color', 3,
			'valor_db', CASE WHEN curdatos1.saldoi > 0 THEN curdatos1.saldoi ELSE 0 END,
			'valor_cr', CASE WHEN curdatos1.saldoi < 0 THEN curdatos1.saldoi * -1 ELSE 0 END,
			'saldo', CASE WHEN curdatos1.saldoi < 0 THEN curdatos1.saldoi * -1 ELSE 0 END,
			'orden', curdatos1.nombre,
			'ordenf', '2000-01-02',
			'id', null,	
			'tipo', null,	
			'numero', null,	
			'fecha', null,	
			'docref', null,	
			'concepto', null,	
			'fuentes_id', null,	
			'base', null,
			'persona_id', curdatos1.id
		);
	
			sumbase := 0;
			sumasaldo := curdatos1.saldoi;
			sumadb := CASE WHEN curdatos1.saldoi > 0 THEN curdatos1.saldoi ELSE 0 END;
			sumacr := CASE WHEN curdatos1.saldoi < 0 THEN curdatos1.saldoi * -1 ELSE 0 END;
			--saldo_cero := CASE WHEN curdatos1.saldoi < 0 THEN false ELSE true END;
		
		for curdatos2 in 
				SELECT 
					mov.id as id,
					mov.tipo as tipo,
					mov.numero as numero,
					mov.fecha as fecha,
					mov.docref as docref,
					mov.concepto as concepto,
					CONCAT(mov.detalle, CASE WHEN POSITION(' BASE ' in mov.detalle) < 1 AND mov.base > 0 THEN CONCAT(' BASE: ', mov.base::money) ELSE '' end) as detalle,
					coalesce(mov.valor_db, 0) as valor_db,
					coalesce(mov.valor_cr, 0) as valor_cr, 
					coalesce(mov.saldo, 0) as saldo,
					mov.color as color,
					mov.fuentes_id as fuentes_id,
					curdatos1.nombre AS orden,
					mov.fecha as fecha,
					mov.base as base
				FROM cur_mov AS mov WHERE mov.persona_id = curdatos1.id
				order by mov.fecha, mov.numero asc
			loop
				
				sumasaldo := sumasaldo + (coalesce(curdatos2.valor_db, 0) - coalesce(curdatos2.valor_cr, 0));
			
				if in_mesi <> in_mesf then
					if contador = 1 then 
						mes_documento := EXTRACT(MONTH FROM curdatos2.fecha);
					end if;
					if EXTRACT(MONTH FROM curdatos2.fecha) <> mes_documento then 
						datos_array := datos_array || jsonb_build_object(
							'detalle', CONCAT('SALDO A ', CASE WHEN in_mesi = 1 THEN CONCAT('DICIEMBRE ', (in_anio-1)::varchar) ELSE CONCAT(to_char(date(CONCAT('2020/', lpad((in_mesi-1)::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar) end),
							'color', 3,
							'valor_db', CASE WHEN curdatos1.saldoi > 0 THEN curdatos1.saldoi ELSE 0 END,
							'valor_cr', CASE WHEN curdatos1.saldoi < 0 THEN curdatos1.saldoi * -1 ELSE 0 END,
							'saldo', CASE WHEN curdatos1.saldoi < 0 THEN curdatos1.saldoi * -1 ELSE 0 END,
							'orden', curdatos1.nombre,
							'ordenf', '2000-01-02',
							'id', null,	
							'tipo', null,	
							'numero', null,	
							'fecha', null,	
							'docref', null,	
							'concepto', null,	
							'fuentes_id', null,	
							'base', null,
							'persona_id', curdatos1.id
						);
						--saldo_cero := CASE WHEN saldo_cero is false or curdatos1.saldoi < 0 THEN false ELSE true END;
					end if;
					contador := 2;
					mes_documento := EXTRACT(MONTH FROM curdatos2.fecha);
				end if;
			
					datos_array := datos_array || jsonb_build_object(
						'id', curdatos2.id,
						'tipo', curdatos2.tipo,
						'numero', curdatos2.numero, 
						'fecha', curdatos2.fecha, 
						'docref', curdatos2.docref, 
						'concepto', curdatos2.concepto, 
						'detalle', curdatos2.detalle, 
						'valor_db', coalesce(curdatos2.valor_db, 0), 
						'valor_cr', coalesce(curdatos2.valor_cr, 0), 
						'saldo', sumasaldo, 
						'color', curdatos2.color, 
						'fuentes_id', curdatos2.fuentes_id, 
						'orden', curdatos2.orden, 
						'ordenf', curdatos2.fecha, 
						'base', curdatos2.base,
						'persona_id', curdatos1.id
					);
					--saldo_cero := CASE WHEN saldo_cero is false or sumasaldo <> 0 THEN false ELSE true END;
				
				sumadb := sumadb + coalesce(curdatos2.valor_db, 0);
				sumacr := sumacr + coalesce(curdatos2.valor_cr, 0);
			end loop;
	
		
			SELECT SUM(mov.base) INTO sumbase FROM cur_mov AS mov WHERE mov.persona_id = curdatos1.id;

			saldo_cero := CASE WHEN curdatos1.saldof::int <> 0 THEN false ELSE true END;
		
			datos_array := datos_array || jsonb_build_object(
				'detalle', CONCAT('SALDO A ', CONCAT(to_char(date(CONCAT('2020/', lpad(in_mesf::varchar, 2,'0')::varchar, '/01')),'MONTH'), ' ', in_anio::varchar)),
				'color', 3,
				'valor_db', CASE WHEN curdatos1.saldof > 0 THEN curdatos1.saldof ELSE 0 END,
				'valor_cr', CASE WHEN curdatos1.saldof < 0 THEN curdatos1.saldof * -1 ELSE 0 END,
				'saldo', CASE WHEN curdatos1.saldof > 0 THEN curdatos1.saldof ELSE 0 END,
				'orden', curdatos1.nombre,
				'ordenf', '2099-01-01',
				'base', sumbase,
				'id', '99',
				'tipo', null,	
				'numero', null,	
				'fecha', null,	
				'docref', null,	
				'concepto', null,	
				'fuentes_id', null,	
				'base', null,
				'persona_id', curdatos1.id,
				'saldo_cero', saldo_cero
			);	
			
	END LOOP;
	
	RETURN jsonb_agg(datos_array);
	

	drop table cur_aux;
	drop table cur_mov;
	drop table cur_temp;
END
$function$
;
