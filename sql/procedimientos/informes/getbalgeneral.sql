-- DROP FUNCTION public.getbalgeneral(int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getbalgeneral(in_tipocon integer, in_anio integer, in_mes integer)
 RETURNS TABLE(codigo character varying, nombre character varying, parcial numeric, total numeric, color integer, tipo_cuenta character varying)
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
	cantmov int = 0;
	cantsal int = 0;
	sumbase decimal (18,2);
	curdatos1 record;
	nactivo decimal(18,2);
	npasivo decimal(18,2);
	npatrimonio	decimal(18,2);
	nexcedente decimal(18,2);

BEGIN
	-- Creamos una tabla temporal para las cuentas auxiliares y los movimientos
	CREATE TEMP TABLE IF NOT EXISTS cur_bal (
		codigo varchar(20),
		nombre varchar(100),
		parcial decimal(18,2),
		total decimal(18,2),
		color int default 0,
		tipo_cuenta varchar(20)
	);
	
	-- Traer los Datos del Activo
	INSERT INTO cur_bal
	SELECT a."codigo" AS codigo, a."nombre" AS nombre, null AS parcial, 
			CASE
			    WHEN in_mes = 1  THEN b.sal01
				WHEN in_mes = 2  THEN b.sal02
				WHEN in_mes = 3  THEN b.sal03
				WHEN in_mes = 4  THEN b.sal04
				WHEN in_mes = 5  THEN b.sal05
				WHEN in_mes = 6  THEN b.sal06
				WHEN in_mes = 7  THEN b.sal07
				WHEN in_mes = 8  THEN b.sal08
				WHEN in_mes = 9  THEN b.sal09
				WHEN in_mes = 10 THEN b.sal10
				WHEN in_mes = 11 THEN b.sal11
				WHEN in_mes = 12 THEN b.sal12 
			END AS total, 1 AS color,
			a.tipo as tipo_cuenta
		FROM contabilidad_mayor a, contabilidad_saldos b 
		WHERE a."codigo" = '1' 
		AND b.anio = in_anio 
		AND a.id = b.mayor_id 
		ORDER BY a."codigo";

	--- Traer Detalle Activo
	INSERT INTO cur_bal
	SELECT RTRIM(a."codigo") AS codigo, CONCAT(lpad('',LENGTH(RTRIM(a."codigo")),' '), a."nombre") AS nombre,
		CASE
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12 
		END AS parcial, null AS total, CASE WHEN RTRIM(lower(a.tipo)) = 'general' THEN 11 ELSE 12 END AS color,
		a.tipo as tipo_cuenta
	FROM contabilidad_mayor AS a, contabilidad_saldos AS b 
	WHERE LEFT(RTRIM(a."codigo"), 1)::VARCHAR = '1' 
	AND LENGTH(RTRIM(a."codigo")) <= in_tipocon 
	AND LENGTH(RTRIM(a."codigo")) > 1 
	AND b.anio = in_anio 
	AND a.id = b.mayor_id 
	ORDER BY a."codigo";
	
	--- Traer El Total del Activo
	INSERT INTO cur_bal 
	SELECT 'TOTAL' AS codigo, a."nombre" AS nombre, null AS parcial,
		CASE
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12
		END AS total, 1 AS color,
		a.tipo as tipo_cuenta
	FROM contabilidad_mayor a, contabilidad_saldos b 
	WHERE a."codigo" = '1' 
	AND b.anio = in_anio 
	AND a.id = b.mayor_id 
	ORDER BY a."codigo";
	
	--- Crear variable para sumar el activo
	SELECT 
		CASE
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12
		END INTO nactivo
	 FROM contabilidad_mayor a, contabilidad_saldos b 
	 WHERE a."codigo" = '1' 
	 AND b.anio = in_anio 
	 AND a.id = b.mayor_id;
	 
	 IF nactivo IS NULL THEN
		INSERT INTO cur_bal (codigo, nombre, total, color,tipo_cuenta) VALUES ('1', 'Activo', 0, 1,'');
		INSERT INTO cur_bal (codigo, nombre, total, color,tipo_cuenta) VALUES ('TOTAL', 'Activo', 0, 1,'');
	 END IF;
	 
	--INSERT INTO cur_bal (codigo, nombre) values ('','');
 	-- Traer los Datos del Pasivo

	INSERT INTO cur_bal 
	SELECT a."codigo" AS codigo, a."nombre" AS nombre, null AS parcial, 
		CASE
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12
		END * -1 AS total, 2 AS color,
		a.tipo as tipo_cuenta
	FROM contabilidad_mayor a, contabilidad_saldos b 
	WHERE a."codigo" = '2' 
	AND b.anio = in_anio 
	AND a.id = b.mayor_id 
	ORDER BY a."codigo";
	
	 -- Traer el Detalle del  Pasivo
	INSERT INTO cur_bal 
	SELECT a."codigo" AS codigo, CONCAT(lpad('',LENGTH(RTRIM(a."codigo")),' '), a."nombre") AS nombre, 
		case
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12
	END * -1 AS parcial, null AS total, CASE WHEN RTRIM(lower(a.tipo)) = 'general' THEN 21 ELSE 22 END AS color,
	a.tipo as tipo_cuenta
	FROM contabilidad_mayor a, contabilidad_saldos b 
	WHERE LEFT(RTRIM(a."codigo"), 1)::VARCHAR = '2' 
	AND LENGTH(RTRIM(a."codigo"))::NUMERIC <= in_tipocon 
	AND LENGTH(RTRIM(a."codigo")) > 1 
	AND b.anio = in_anio 
	AND a.id = b.mayor_id 
	ORDER BY codigo;
	
	-- Totalizar el Pasivo
	INSERT INTO cur_bal 
	SELECT 'TOTAL' AS codigo, a."nombre" AS nombre, null AS parcial, 
		CASE
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12
		END * -1 AS total, 2 AS color,
		a.tipo as tipo_cuenta
	FROM contabilidad_mayor a, contabilidad_saldos b 
	WHERE a."codigo" = '2' 
	AND b.anio = in_anio 
	AND a.id = b.mayor_id 
	ORDER BY a."codigo";
	
	-- Cuantificar el Pasivo
	SELECT 
		CASE
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12
		END * -1 INTO npasivo
	FROM contabilidad_mayor a, contabilidad_saldos b 
	WHERE a."codigo" = '2' 
	AND b.anio = in_anio 
	AND a.id = b.mayor_id; 
	
	IF npasivo IS NULL THEN
		INSERT INTO cur_bal (codigo, nombre, total, color,tipo_cuenta) VALUES ('2', 'PASIVO', 0, 2,'');
		INSERT INTO cur_bal (codigo, nombre, total, color,tipo_cuenta) VALUES ('TOTAL', 'PASIVO', 0, 2,'');
	END IF;
	
	--INSERT INTO cur_bal (codigo, nombre) VALUES ('','');
	
	-- Patrimonio
	-- Traer los Datos del Patrimonio

	INSERT INTO cur_bal 
	SELECT a."codigo" AS codigo, a."nombre" AS nombre, null AS parcial, 
		CASE
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12
		END AS total, 3 AS color,
		a.tipo as tipo_cuenta
	FROM contabilidad_mayor a, contabilidad_saldos b 
	WHERE a."codigo"= '3' 
	AND b.anio = in_anio 
	AND a.id = b.mayor_id 
	ORDER BY codigo;
	
	--Traer Detalle Patrimonio
	INSERT INTO cur_bal 
	SELECT a."codigo" AS codigo, CONCAT(lpad('',LENGTH(RTRIM(a."codigo")),' '), a."nombre") AS nombre, 
		CASE
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12
		END AS parcial, 0 AS total, CASE WHEN RTRIM(lower(a.tipo)) = 'general' THEN 31 ELSE 32 END AS color,
		a.tipo as tipo_cuenta
	FROM contabilidad_mayor a, contabilidad_saldos b 
	WHERE LEFT(RTRIM(a."codigo"), 1)::VARCHAR = '3' 
	AND LENGTH(RTRIM(a."codigo")) <= in_tipocon 
	AND LENGTH(RTRIM(a."codigo")) > 1 
	AND b.anio = in_anio 
	AND a.id = b.mayor_id 
	ORDER BY codigo;
	
	--- Crear variable para sumar el Patrimonio
	SELECT 
		CASE
			WHEN in_mes = 1  THEN b.sal01
			WHEN in_mes = 2  THEN b.sal02
			WHEN in_mes = 3  THEN b.sal03
			WHEN in_mes = 4  THEN b.sal04
			WHEN in_mes = 5  THEN b.sal05
			WHEN in_mes = 6  THEN b.sal06
			WHEN in_mes = 7  THEN b.sal07
			WHEN in_mes = 8  THEN b.sal08
			WHEN in_mes = 9  THEN b.sal09
			WHEN in_mes = 10 THEN b.sal10
			WHEN in_mes = 11 THEN b.sal11
			WHEN in_mes = 12 THEN b.sal12
		END INTO npatrimonio
	FROM contabilidad_mayor a, contabilidad_saldos b 
	WHERE a."codigo" = '3' 
	AND b.anio = in_anio 
	AND a.id = b.mayor_id;
	 
	IF npatrimonio IS NULL THEN
		INSERT INTO cur_bal (codigo, nombre, total, color,tipo_cuenta) VALUES ('3', 'PATRIMONIO', null, 3,'');
	END IF;

	-- Excedente
	nexcedente := COALESCE(nactivo, 0) - (COALESCE(npasivo, 0) + COALESCE(npatrimonio, 0));
	
	INSERT INTO cur_bal (nombre, total, color,tipo_cuenta) VALUES ('Excedente o perdida del ejercicio', nexcedente, 3,'');
	
	-- Total Patrimonio
	INSERT INTO cur_bal (codigo, nombre, total, color,tipo_cuenta) VALUES ('TOTAL', 'PATRIMONIO', COALESCE(npatrimonio, 0) + nexcedente, 3,'');
	
	--INSERT INTO cur_bal (codigo, nombre) VALUES ('', '');
	
	-- Total. 
  	INSERT INTO cur_bal (codigo, nombre, total, color,tipo_cuenta) VALUES (
		'TOTAL', 'PASIVO + PATRIMONIO', COALESCE(npatrimonio, 0) + COALESCE(nexcedente, 0) + COALESCE(npasivo, 0), 3,''
	);
	
	RETURN QUERY SELECT * FROM cur_bal AS cb WHERE cb.parcial <> 0 OR cb.parcial IS NULL;
	drop table cur_bal;
END
$function$
;

-- Permissions

ALTER FUNCTION public.getbalgeneral(int4, int4, int4) OWNER TO postgres;
GRANT ALL ON FUNCTION public.getbalgeneral(int4, int4, int4) TO postgres;
