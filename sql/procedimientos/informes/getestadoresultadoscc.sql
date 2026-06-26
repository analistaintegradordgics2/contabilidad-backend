-- DROP FUNCTION public.getestadoresultadoscc(int4, int4);

CREATE OR REPLACE FUNCTION public.getestadoresultadoscc(in_anio integer, in_mes integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
DECLARE
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	lccursor varchar(30);
	lnnumero integer;
	curdatos1 record;
	ningresos decimal(18,2);
	ningresosp decimal(18,2);
	ngastos decimal(18,2);
	ngastosp decimal(18,2);
	ncostosv decimal(18,2);
	ncostosvp decimal(18,2);
	ncostosp decimal(18,2);
	ncostospp decimal(18,2);
	negresos decimal(18,2);
	negresosp decimal(18,2);
	nutilidada decimal(18,2);
	nutilidadap decimal(18,2);
	mov_cc record;
	centro_costos record;
	nuevo_cc varchar(30);
	contador int default 0;
	obj json;

BEGIN
	CREATE TEMP TABLE IF NOT EXISTS cur_bal (
		codigo varchar(20),
		nombre varchar(400),
		parcial decimal(18,2),
		total decimal(18,2),
		color int default 0,
		nits int default 0,
		codigo_id int default 0,
		orden varchar(20),
		cc1_valor decimal(18,2) default 0,
		cc2_valor decimal(18,2) default 0,
		cc3_valor decimal(18,2) default 0,
		cc4_valor decimal(18,2) default 0,
		cc5_valor decimal(18,2) default 0,
		cc1_id int default 0,
		cc2_id int default 0,
		cc3_id int default 0,
		cc4_id int default 0,
		cc5_id int default 0
	);
		
	CREATE TEMP TABLE IF NOT EXISTS cur_final (
		codigo varchar(20),
		nombre varchar(400),
		parcial decimal(18,2),
		total decimal(18,2),
		color int default 0,
		orden varchar(20)
	);

	CREATE TEMP TABLE IF NOT EXISTS cur_cc (
		ncod varchar(2),
		codigo varchar(20),
		mes int,
		cc_id int,
		valor decimal(18,2)
	);
	
	insert into cur_cc select left(mayor."codigo" , 1) as ncod, left(mayor."codigo", 1) as codigo, extract(month from doc.fecha) as mes, mov.centro_costos_id as cc_id,  (sum(mov.valor_db) - sum(mov.valor_cr) ) * (case when left(mayor."codigo", 1)='4' then -1 else 1 end) as valor 
	from contabilidad_mov mov, cont_documentos doc, contabilidad_mayor mayor
	Where mov.documento_id = doc.id and mov.mayor_id = mayor.id  and TO_CHAR(doc.fecha, 'YYYY') = in_anio::text and doc.estado=2 and left(mayor."codigo",1)>'3'
	group by left(mayor."codigo", 1), left(mayor."codigo", 1), extract(month from doc.fecha), mov.centro_costos_id 
	union
	select left(mayor."codigo", 1) as ncod,left(mayor."codigo", 2) as codigo, extract(month from doc.fecha) as mes, mov.centro_costos_id as cc_id,  (sum(mov.valor_db) - sum(mov.valor_cr) )* (case when left(mayor."codigo", 1)='4' then -1 else 1 end) as valor 
	from contabilidad_mov mov, cont_documentos doc, contabilidad_mayor mayor
	Where mov.documento_id = doc.id and mov.mayor_id = mayor.id  and TO_CHAR(doc.fecha, 'YYYY') = in_anio::text and doc.estado=2 and left(mayor."codigo",1)>'3'
	group by left(mayor."codigo", 1), left(mayor."codigo", 2),extract(month from doc.fecha), mov.centro_costos_id 
	union
	select left(mayor."codigo", 1) as ncod,left(mayor."codigo", 4) as codigo, extract(month from doc.fecha) as mes, mov.centro_costos_id as cc_id,  (sum(mov.valor_db) - sum(mov.valor_cr) ) * (case when left(mayor."codigo", 1)='4' then -1 else 1 end) as valor 
	from contabilidad_mov mov, cont_documentos doc, contabilidad_mayor mayor
	Where mov.documento_id = doc.id and mov.mayor_id = mayor.id  and TO_CHAR(doc.fecha, 'YYYY') = in_anio::text and doc.estado=2 and left(mayor."codigo",1)>'3'
	group by left(mayor."codigo", 1), left(mayor."codigo", 4),extract(month from doc.fecha), mov.centro_costos_id 
	union
	select left(mayor."codigo", 1) as ncod,left(mayor."codigo", 6) as codigo, extract(month from doc.fecha) as mes, mov.centro_costos_id as cc_id,  (sum(mov.valor_db) - sum(mov.valor_cr) ) * (case when left(mayor."codigo", 1)='4' then -1 else 1 end) as valor 
	from contabilidad_mov mov, cont_documentos doc, contabilidad_mayor mayor
	Where mov.documento_id = doc.id and mov.mayor_id = mayor.id  and TO_CHAR(doc.fecha, 'YYYY') = in_anio::text and doc.estado=2 and left(mayor."codigo",1)>'3'
	group by left(mayor."codigo", 1), left(mayor."codigo", 6),extract(month from doc.fecha), mov.centro_costos_id 
	union
	select left(mayor."codigo", 1) as ncod,left(mayor."codigo", 8) as codigo, extract(month from doc.fecha) as mes, mov.centro_costos_id as cc_id,  (sum(mov.valor_db) - sum(mov.valor_cr) )* (case when left(mayor."codigo", 1)='4' then -1 else 1 end) as valor 
	from contabilidad_mov mov, cont_documentos doc, contabilidad_mayor mayor
	Where mov.documento_id = doc.id and mov.mayor_id = mayor.id  and TO_CHAR(doc.fecha, 'YYYY') = in_anio::text and doc.estado=2 and left(mayor."codigo",1)>'3'
	group by left(mayor."codigo", 1), left(mayor."codigo", 8), extract(month from doc.fecha), mov.centro_costos_id 
	union
	select left(mayor."codigo", 1) as ncod,left(mayor."codigo", 10) as codigo, extract(month from doc.fecha) as mes, mov.centro_costos_id as cc_id,  (sum(mov.valor_db) - sum(mov.valor_cr) )* (case when left(mayor."codigo", 1)='4' then -1 else 1 end) as valor 
	from contabilidad_mov mov, cont_documentos doc, contabilidad_mayor mayor
	Where mov.documento_id = doc.id and mov.mayor_id = mayor.id  and TO_CHAR(doc.fecha, 'YYYY') = in_anio::text and doc.estado=2 and left(mayor."codigo",1)>'3'
	group by left(mayor."codigo", 1), left(mayor."codigo", 10), extract(month from doc.fecha), mov.centro_costos_id 
	union
	select left(mayor."codigo", 1) as ncod,left(mayor."codigo", 12) as codigo, extract(month from doc.fecha) as mes, mov.centro_costos_id as cc_id,  (sum(mov.valor_db) - sum(mov.valor_cr) )* (case when left(mayor."codigo", 1)='4' then -1 else 1 end) as valor 
	from contabilidad_mov mov, cont_documentos doc, contabilidad_mayor mayor
	Where mov.documento_id = doc.id and mov.mayor_id = mayor.id  and TO_CHAR(doc.fecha, 'YYYY') = in_anio::text and doc.estado=2 and left(mayor."codigo",1)>'3'
	group by left(mayor."codigo", 1), left(mayor."codigo", 12), extract(month from doc.fecha), mov.centro_costos_id 
	order by codigo, mes, cc_id ;
	
	SELECT json_agg(json_build_object(
		'ncod',conta.ncod,
		'codigo', conta.codigo,
		'cc_id',conta.cc_id, 
		'valor', conta.valor
	)) into obj  FROM (select sum(cur_cc.valor) as valor, cur_cc.ncod, cur_cc.codigo, cur_cc.cc_id  from cur_cc group by cur_cc.cc_id,cur_cc.ncod,cur_cc.codigo)as conta;
	
	--FOR centro_costos IN ( SELECT cc_costo.id, cc_costo.nombre, cc_costo.codigo FROM cont_centro_costos cc_costo where cc_costo.estado = 'ACTIVO' order by cc_costo.id) loop
		--contador:=contador + 1;
		--EXECUTE format('UPDATE cur_bal SET %I = %I ',concat('cc',contador,'_id'),centro_costos.id); 
		--raise notice 'Contrato! %', ;
	--end loop;
	
	return obj; 
		 
				
END
$function$
;

-- Permissions

ALTER FUNCTION public.getestadoresultadoscc(int4, int4) OWNER TO postgres;
GRANT ALL ON FUNCTION public.getestadoresultadoscc(int4, int4) TO postgres;
