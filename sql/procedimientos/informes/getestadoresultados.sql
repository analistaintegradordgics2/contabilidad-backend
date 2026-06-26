-- DROP FUNCTION public.getestadoresultados(int4, int4, int4, int4, int4, bool);

CREATE OR REPLACE FUNCTION public.getestadoresultados(in_tipocon integer, in_anio integer, in_mes integer, in_nits integer, in_tinforme integer, in_niif boolean)
 RETURNS TABLE(codigo character varying, nombre character varying, parcial numeric, total numeric, color integer, nits integer, codigo_id integer, orden character varying, principal integer, occidente integer, costa integer, eje integer, aprincipal integer, aoccidente integer, acosta integer, aeje integer)
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
BEGIN
	DROP TABLE IF EXISTS cur_final;


	CREATE TEMP TABLE IF NOT EXISTS cur_bal (
		codigo varchar(20),
		nombre varchar(400),
		parcial decimal(18,2),
		total decimal(18,2),
		color int default 0,
		nits int default 0,
		codigo_id int default 0,
		orden varchar(20)
	);
		
	CREATE TEMP TABLE cur_final (
		codigo varchar(20),
		nombre varchar(400),
		parcial decimal(18,2),
		total decimal(18,2),
		color int default 0,
		nits int default 0,
		codigo_id int default 0,
		orden varchar(20)
	);
	
	-- Traer los Datos del Ingreso
	insert into cur_bal  
		select a."codigo" as codigo, a."nombre" as nombre, 
		case
			when in_mes=1  and in_tinforme=2 then b.d01 - b.h01
			when in_mes=2  and in_tinforme=2 then b.d02 - b.h02
			when in_mes=3  and in_tinforme=2 then b.d03 - b.h03
			when in_mes=4  and in_tinforme=2 then b.d04 - b.h04
			when in_mes=5  and in_tinforme=2 then b.d05 - b.h05
			when in_mes=6  and in_tinforme=2 then b.d06 - b.h06
			when in_mes=7  and in_tinforme=2 then b.d07 - b.h07
			when in_mes=8  and in_tinforme=2 then b.d08 - b.h08
			when in_mes=9  and in_tinforme=2 then b.d09 - b.h09
			when in_mes=10 and in_tinforme=2 then b.d10 - b.h10
			when in_mes=11 and in_tinforme=2 then b.d11 - b.h11
			when in_mes=12 and in_tinforme=2 then b.d12 - b.h12
		end * -1 as parcial, 
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end *-1 as total, 1 as color, 0 as nits, a.id as codigo_id, a."codigo" as orden
		from contabilidad_mayor a, contabilidad_saldos b 
		where a."codigo" = '4' 
		and b.anio = in_anio 
		and a.id = b.mayor_id 
		--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end) 
		order by a."codigo";
	
	-- Traer Detalle Ingresos ***************
	insert into cur_bal 
	select a."codigo" as codigo, concat(lpad('',LENGTH(RTRIM(a."codigo")),' '), a."nombre") as nombre, 
		case
			when in_mes=1  and in_tinforme= 1 then b.sal01
			when in_mes=2  and in_tinforme= 1 then b.sal02
			when in_mes=3  and in_tinforme= 1 then b.sal03
			when in_mes=4  and in_tinforme= 1 then b.sal04
			when in_mes=5  and in_tinforme= 1 then b.sal05
			when in_mes=6  and in_tinforme= 1 then b.sal06
			when in_mes=7  and in_tinforme= 1 then b.sal07
			when in_mes=8  and in_tinforme= 1 then b.sal08
			when in_mes=9  and in_tinforme= 1 then b.sal09
			when in_mes=10 and in_tinforme= 1 then b.sal10
			when in_mes=11 and in_tinforme= 1 then b.sal11
			when in_mes=12 and in_tinforme= 1 then b.sal12
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end *-1 as parcial, 
		case
			when in_tinforme=1 then null
			when in_mes=1  and in_tinforme= 2 then b.sal01
			when in_mes=2  and in_tinforme= 2 then b.sal02
			when in_mes=3  and in_tinforme= 2 then b.sal03
			when in_mes=4  and in_tinforme= 2 then b.sal04
			when in_mes=5  and in_tinforme= 2 then b.sal05
			when in_mes=6  and in_tinforme= 2 then b.sal06
			when in_mes=7  and in_tinforme= 2 then b.sal07
			when in_mes=8  and in_tinforme= 2 then b.sal08
			when in_mes=9  and in_tinforme= 2 then b.sal09
			when in_mes=10 and in_tinforme= 2 then b.sal10
			when in_mes=11 and in_tinforme= 2 then b.sal11
			when in_mes=12 and in_tinforme= 2 then b.sal12
		end * -1 as total, case when length(rtrim(a."codigo")) <= 6 then 11 else 12 end as color, case when a.maneja_nits = true then 1 else 0 end as nits, a.id as codigo_id, a."codigo" as orden 
		from contabilidad_mayor a, contabilidad_saldos b 
		where left(rtrim(a."codigo"),1) = '4' 
		and length(rtrim(a."codigo")) <= in_tipocon 
		and length(rtrim(a."codigo")) > 1 
		and 
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end <> 0 
		and b.anio = in_anio 
		and a.id = b.mayor_id 
		--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
		order by a."codigo";
	
	--- Traer El Total del Ingreso
	insert into cur_bal 
	select 'TOTAL' as codigo, a."nombre" as nombre,
	case 
		when in_tinforme= 1 then null
		when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
		when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
		when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
		when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
		when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
		when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
		when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
		when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
		when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
		when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
		when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
		when in_mes=12 and in_tinforme= 2 then b.d12-b.h12 
	end * -1 as parcial,
	case
		when in_mes=1  then b.sal01
		when in_mes=2  then b.sal02
		when in_mes=3  then b.sal03
		when in_mes=4  then b.sal04
		when in_mes=5  then b.sal05
		when in_mes=6  then b.sal06
		when in_mes=7  then b.sal07
		when in_mes=8  then b.sal08
		when in_mes=9  then b.sal09
		when in_mes=10 then b.sal10
		when in_mes=11 then b.sal11
		when in_mes=12 then b.sal12 
	end *-1 as total, 1 as color, 0 as nits, a.id as codigo_id, '49999990' as orden 
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo"= '4' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";

	
	--- Crear variable para sumar el Ingreso
	select 
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end *-1 into ningresos 
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '4' 
	and b.anio= in_anio 
	and a.id = b.mayor_id;
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end);	

	--- Crear la variable para sumar el Parcial de los Ingresos
	if in_tinforme = 2 then
	  select 
	  	case
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end *-1 into ningresosp 
		from contabilidad_mayor a, contabilidad_saldos b 
		where a."codigo" = '4' 
		and b.anio = in_anio 
		and a.id = b.mayor_id;
		--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end); 
	end if;

	if ningresos IS NULL then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('4', 'INGRESOS', 0, 1, '1');
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'INGRESOS', 0, 1, '49999990');
	end if;
	
	--insert into cur_bal (codigo, nombre, orden) values ('', '', '49999991');
	
	

	-----------------------------------------GASTOS------------------------------------------------

 	-- Traer los Datos de los Gastos

	insert into cur_bal 
	select a."codigo" as codigo, a."nombre" as nombre,  
		case 
			when in_tinforme= 1 then null
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end * 1 as parcial,
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end * 1 as total, 2 as color, 0 as nits, a.id as codigo_id, a."codigo" as orden 
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '5' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";

	-- Traer el Detalle de los Gastos
	insert into cur_bal 
	select a."codigo" as codigo, concat(lpad('',LENGTH(RTRIM(a."codigo")),' '), a."nombre") as nombre, 
		case
			when in_mes=1  and in_tinforme= 1 then b.sal01
			when in_mes=2  and in_tinforme= 1 then b.sal02
			when in_mes=3  and in_tinforme= 1 then b.sal03
			when in_mes=4  and in_tinforme= 1 then b.sal04
			when in_mes=5  and in_tinforme= 1 then b.sal05
			when in_mes=6  and in_tinforme= 1 then b.sal06
			when in_mes=7  and in_tinforme= 1 then b.sal07
			when in_mes=8  and in_tinforme= 1 then b.sal08
			when in_mes=9  and in_tinforme= 1 then b.sal09
			when in_mes=10 and in_tinforme= 1 then b.sal10
			when in_mes=11 and in_tinforme= 1 then b.sal11
			when in_mes=12 and in_tinforme= 1 then b.sal12
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end * 1 as parcial, 
		case
			when in_tinforme=1 then null
			when in_mes=1  and in_tinforme= 2 then b.sal01
			when in_mes=2  and in_tinforme= 2 then b.sal02
			when in_mes=3  and in_tinforme= 2 then b.sal03
			when in_mes=4  and in_tinforme= 2 then b.sal04
			when in_mes=5  and in_tinforme= 2 then b.sal05
			when in_mes=6  and in_tinforme= 2 then b.sal06
			when in_mes=7  and in_tinforme= 2 then b.sal07
			when in_mes=8  and in_tinforme= 2 then b.sal08
			when in_mes=9  and in_tinforme= 2 then b.sal09
			when in_mes=10 and in_tinforme= 2 then b.sal10
			when in_mes=11 and in_tinforme= 2 then b.sal11
			when in_mes=12 and in_tinforme= 2 then b.sal12
		end * 1 as total, case when length(rtrim(a."codigo")) <= 6 then 21 else 22 end as color, case when a.maneja_nits = true then 1 else 0 end as nits, a.id as codigo_id, a."codigo" as orden 
	from contabilidad_mayor a, contabilidad_saldos b 
	where left(rtrim(a."codigo"),1) = '5' 
	and length(rtrim(a."codigo")) <= in_tipocon 
	and length(rtrim(a."codigo")) > 1 
	and 
	case
		when in_mes=1  then b.sal01
		when in_mes=2  then b.sal02
		when in_mes=3  then b.sal03
		when in_mes=4  then b.sal04
		when in_mes=5  then b.sal05
		when in_mes=6  then b.sal06
		when in_mes=7  then b.sal07
		when in_mes=8  then b.sal08
		when in_mes=9  then b.sal09
		when in_mes=10 then b.sal10
		when in_mes=11 then b.sal11
		when in_mes=12 then b.sal12
	end <> 0 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";

	-- Totalizar Del Gasto
	
	insert into cur_bal 
	select 'TOTAL' as codigo, a."nombre" as nombre, 
		case 
			when in_tinforme= 1 then null
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end * 1 as parcial,
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end *1 as total, 2 as color, 0 as nits, a.id as codigo_id, '59999990' 
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '5' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";
	
	
	-- Cuantificar el Gasto
  	select  
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end * 1 into ngastos
	 from contabilidad_mayor a, contabilidad_saldos b 
	 where a."codigo" = '5' 
	 and b.anio = in_anio 
	 and a.id = b.mayor_id;
	 --and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end);
	
	if in_tinforme = 2 then
		select 
		  	case
				when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
				when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
				when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
				when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
				when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
				when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
				when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
				when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
				when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
				when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
				when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
				when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
			end * 1 into ngastosp 
		from contabilidad_mayor a, contabilidad_saldos b 
		where a."codigo" = '5' 
		and b.anio = in_anio 
		and a.id = b.mayor_id;
		--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end); 
	end if;

	if ngastos IS NULL then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('5', 'GASTOS', 0, 2, '5');
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'GASTOS', 0, 2, '59999990');
	end if;
	
	--insert into cur_bal (codigo, nombre, orden) values ('', '', '59999991');

	----- COSTOS DE VENTA
 
 	-- Traer los Datos de los Costos de Venta

	insert into cur_bal 
	select a."codigo" as codigo, a."nombre" as nombre, 
		case 
			when in_tinforme= 1 then null
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2  then b.d12-b.h12  
		end * 1 as parcial,
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end * 1 as total, 4 as color, 0 as nits, a.id as codigo_id, a."codigo" as orden 
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '6' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";
	
	-- Traer el Detalle de los Costos de Ventas
	insert into cur_bal 
	select a."codigo" as codigo, concat(lpad('',LENGTH(RTRIM(a."codigo")),' '), a."nombre") as nombre, 
		case
			when in_mes=1  and in_tinforme= 1 then b.sal01
			when in_mes=2  and in_tinforme= 1 then b.sal02
			when in_mes=3  and in_tinforme= 1 then b.sal03
			when in_mes=4  and in_tinforme= 1 then b.sal04
			when in_mes=5  and in_tinforme= 1 then b.sal05
			when in_mes=6  and in_tinforme= 1 then b.sal06
			when in_mes=7  and in_tinforme= 1 then b.sal07
			when in_mes=8  and in_tinforme= 1 then b.sal08
			when in_mes=9  and in_tinforme= 1 then b.sal09
			when in_mes=10 and in_tinforme= 1 then b.sal10
			when in_mes=11 and in_tinforme= 1 then b.sal11
			when in_mes=12 and in_tinforme= 1 then b.sal12
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end *-1 as parcial, 
		case
			when in_tinforme=1 then null
			when in_mes=1  and in_tinforme= 2 then b.sal01
			when in_mes=2  and in_tinforme= 2 then b.sal02
			when in_mes=3  and in_tinforme= 2 then b.sal03
			when in_mes=4  and in_tinforme= 2 then b.sal04
			when in_mes=5  and in_tinforme= 2 then b.sal05
			when in_mes=6  and in_tinforme= 2 then b.sal06
			when in_mes=7  and in_tinforme= 2 then b.sal07
			when in_mes=8  and in_tinforme= 2 then b.sal08
			when in_mes=9  and in_tinforme= 2 then b.sal09
			when in_mes=10 and in_tinforme= 2 then b.sal10
			when in_mes=11 and in_tinforme= 2 then b.sal11
			when in_mes=12 and in_tinforme= 2 then b.sal12
		end * -1 as total, case when length(rtrim(a."codigo")) <= 6 then 41 else 42 end as color, case when a.maneja_nits = true then 1 else 0 end as nits, a.id as codigo_id, a."codigo" as orden 
	from contabilidad_mayor a, contabilidad_saldos b 
	where left(rtrim(a."codigo"),1) ='6' 
	and length(rtrim(a."codigo")) <= in_tipocon 
	and length(rtrim(a."codigo")) > 1 
	and 
	case
		when in_mes=1  then b.sal01
		when in_mes=2  then b.sal02
		when in_mes=3  then b.sal03
		when in_mes=4  then b.sal04
		when in_mes=5  then b.sal05
		when in_mes=6  then b.sal06
		when in_mes=7  then b.sal07
		when in_mes=8  then b.sal08
		when in_mes=9  then b.sal09
		when in_mes=10 then b.sal10
		when in_mes=11 then b.sal11
		when in_mes=12 then b.sal12
	end <> 0 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";

	-- Totalizar el Costo de Venta
	
	insert into cur_bal 
	select 'TOTAL' as codigo, a."nombre" as nombre, 
		case 
			when in_tinforme= 1 then null
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end * 1 as parcial,
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end * 1 as total, 4 as color, 0 as nits, a.id as codigo_id, '69999990' as orden 
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '6' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";
		
	-- Cuantificar el Costo de Venta
	select 
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end * 1 into ncostosv
	 from contabilidad_mayor a, contabilidad_saldos b 
	 where a."codigo" = '6' 
	 and b.anio = in_anio 
	 and a.id = b.mayor_id;
	 --and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end); 
	 
  	if in_tinforme = 2 then
	  select 
		  	case
				when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
				when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
				when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
				when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
				when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
				when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
				when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
				when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
				when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
				when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
				when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
				when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
			end * 1 into ncostosvp 
		from contabilidad_mayor a, contabilidad_saldos b 
		where a."codigo" = '6' 
		and b.anio = in_anio 
		and a.id = b.mayor_id;
		--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end); 
	end if;

	if ncostosv IS NULL then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('6', 'COSTOS DE VENTAS', 0, 4,'6');
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'COSTOS DE VENTAS', 0, 4, '69999990');
	end if;
	
	--insert into cur_bal (codigo, nombre, orden) values ('', '', '69999991');

	---- Costos de ProducciÃ³n.
 	-- Traer los Datos de los Costos de ProducciÃ³n
	
	insert into cur_bal 
	select a."codigo" as codigo, a."nombre" as nombre, 
		case 
			when in_tinforme= 1 then null
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end * 1 as parcial,
		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end * 1 as total, 5 as color, 0 as nits, a.id as codigo_id, a."codigo" as orden 
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '7' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";

	-- Traer el Detalle de los Costos de Ventas
	insert into cur_bal 
	select a."codigo" as codigo, concat(lpad('',LENGTH(RTRIM(a."codigo")),' '), a."nombre") as nombre, 
		case
			when in_mes=1  and in_tinforme= 1 then b.sal01
			when in_mes=2  and in_tinforme= 1 then b.sal02
			when in_mes=3  and in_tinforme= 1 then b.sal03
			when in_mes=4  and in_tinforme= 1 then b.sal04
			when in_mes=5  and in_tinforme= 1 then b.sal05
			when in_mes=6  and in_tinforme= 1 then b.sal06
			when in_mes=7  and in_tinforme= 1 then b.sal07
			when in_mes=8  and in_tinforme= 1 then b.sal08
			when in_mes=9  and in_tinforme= 1 then b.sal09
			when in_mes=10 and in_tinforme= 1 then b.sal10
			when in_mes=11 and in_tinforme= 1 then b.sal11
			when in_mes=12 and in_tinforme= 1 then b.sal12
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end * 1 as parcial, 
		case
			when in_tinforme=1 then null
			when in_mes=1  and in_tinforme= 2 then b.sal01
			when in_mes=2  and in_tinforme= 2 then b.sal02
			when in_mes=3  and in_tinforme= 2 then b.sal03
			when in_mes=4  and in_tinforme= 2 then b.sal04
			when in_mes=5  and in_tinforme= 2 then b.sal05
			when in_mes=6  and in_tinforme= 2 then b.sal06
			when in_mes=7  and in_tinforme= 2 then b.sal07
			when in_mes=8  and in_tinforme= 2 then b.sal08
			when in_mes=9  and in_tinforme= 2 then b.sal09
			when in_mes=10 and in_tinforme= 2 then b.sal10
			when in_mes=11 and in_tinforme= 2 then b.sal11
			when in_mes=12 and in_tinforme= 2 then b.sal12
		end * 1 as total, case when length(rtrim(a."codigo")) <= 6 then 51 else 52 end as color, case when a.maneja_nits = true then 1 else 0 end as nits, a.id as codigo_id, a."codigo" as orden 
	from contabilidad_mayor a, contabilidad_saldos b 
	where left(rtrim(a."codigo"),1) = '7' 
	and length(rtrim(a."codigo")) <= in_tipocon 
	and length(rtrim(a."codigo")) > 1 
	and 
	case
		when in_mes=1  then b.sal01
		when in_mes=2  then b.sal02
		when in_mes=3  then b.sal03
		when in_mes=4  then b.sal04
		when in_mes=5  then b.sal05
		when in_mes=6  then b.sal06
		when in_mes=7  then b.sal07
		when in_mes=8  then b.sal08
		when in_mes=9  then b.sal09
		when in_mes=10 then b.sal10
		when in_mes=11 then b.sal11
		when in_mes=12 then b.sal12
	end <> 0 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";
	
	-- Totalizar el Costo de ProducciÃ³n
	
	insert into cur_bal  
	select 'TOTAL' as codigo, a."nombre" as nombre, 
		case 
			when in_tinforme= 1 then null
			when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
			when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
			when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
			when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
			when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
			when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
			when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
			when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
			when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
			when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
			when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
			when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
		end * 1 as parcial,
	case
		when in_mes=1  then b.sal01
		when in_mes=2  then b.sal02
		when in_mes=3  then b.sal03
		when in_mes=4  then b.sal04
		when in_mes=5  then b.sal05
		when in_mes=6  then b.sal06
		when in_mes=7  then b.sal07
		when in_mes=8  then b.sal08
		when in_mes=9  then b.sal09
		when in_mes=10 then b.sal10
		when in_mes=11 then b.sal11
		when in_mes=12 then b.sal12
	end * 1 as total, 5 as color, 0 as nits, a.id as codigo_id, '79999990' as orden 
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '7' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
	order by a."codigo";
	
	-- Cuantificar el Costo de ProducciÃ³n
  	select 
  		case
			when in_mes=1  then b.sal01
			when in_mes=2  then b.sal02
			when in_mes=3  then b.sal03
			when in_mes=4  then b.sal04
			when in_mes=5  then b.sal05
			when in_mes=6  then b.sal06
			when in_mes=7  then b.sal07
			when in_mes=8  then b.sal08
			when in_mes=9  then b.sal09
			when in_mes=10 then b.sal10
			when in_mes=11 then b.sal11
			when in_mes=12 then b.sal12
		end * 1 into ncostosp
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '7' 
	and b.anio = in_anio 
	and a.id = b.mayor_id;
	--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end); 

	if in_tinforme = 2 then
		select 
		  	case
				when in_mes=1  and in_tinforme= 2 then b.d01-b.h01
				when in_mes=2  and in_tinforme= 2 then b.d02-b.h02
				when in_mes=3  and in_tinforme= 2 then b.d03-b.h03
				when in_mes=4  and in_tinforme= 2 then b.d04-b.h04
				when in_mes=5  and in_tinforme= 2 then b.d05-b.h05
				when in_mes=6  and in_tinforme= 2 then b.d06-b.h06
				when in_mes=7  and in_tinforme= 2 then b.d07-b.h07
				when in_mes=8  and in_tinforme= 2 then b.d08-b.h08
				when in_mes=9  and in_tinforme= 2 then b.d09-b.h09
				when in_mes=10 and in_tinforme= 2 then b.d10-b.h10
				when in_mes=11 and in_tinforme= 2 then b.d11-b.h11
				when in_mes=12 and in_tinforme= 2 then b.d12-b.h12  
			end * 1 into ncostospp 
		from contabilidad_mayor a, contabilidad_saldos b 
		where a."codigo" = '7' 
		and b.anio = in_anio 
		and a.id = b.mayor_id;
		--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end); 
	end if;
	
	if ncostosp IS NULL then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('7', 'COSTOS DE PRODUCCION', 0, 5, '7');
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'COSTOS DE PRODUCCION', 0, 5, '79999990');
	end if;
	
	--insert into cur_bal (codigo, nombre, orden) values ('', '', '79999991');
	
	-- TOTAL DE EGRESOS
	
	negresos := COALESCE(ngastos, 0) + COALESCE(ncostosv, 0) + COALESCE(ncostosp, 0);
	negresosp := COALESCE(ngastosp, 0) + COALESCE(ncostosvp, 0) + COALESCE(ncostospp, 0);
	
	
	if in_tinforme = 1 then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'EGRESOS', negresos, 3, '8');
	end if;

	if in_tinforme = 2 then
		insert into cur_bal (codigo, nombre, parcial, total, color, orden) values ('TOTAL', 'EGRESOS', negresosp, negresos, 3, '8');
	end if;
	
	--insert into cur_bal (codigo, nombre, orden) values ('', '', '81');
	
	-- UTILIDAD ANTES DEL IMPUESTO
	nutilidada := COALESCE(ningresos, 0) - COALESCE(ngastos, 0) - COALESCE(ncostosp, 0) - COALESCE(ncostosv, 0);
	nutilidadaP := COALESCE(ningresosp, 0) - COALESCE(ngastosp, 0) - COALESCE(ncostospp, 0) - COALESCE(ncostosvp, 0);
	 
	if in_tinforme = 1 then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('UTILIDAD', 'ANTES DE IMPUESTO', nutilidada, 3, '82');
	end if;

	if in_tinforme = 2 then
		insert into cur_bal (codigo, nombre, parcial, total, color, orden) values ('UTILIDAD', 'ANTES DE IMPUESTO', nutilidadap, nutilidada, 3, '82');
	end if;

	if in_tinforme = 1 then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('PROVISION', 'DE IMPUESTO', nutilidada * 0.35, 3, '82');
	end if;

	if in_tinforme = 2 then
		insert into cur_bal (codigo, nombre, parcial, total, color, orden) values ('PROVISION', 'DE IMPUESTO', nutilidadap * 0.35, nutilidada * 0.35, 3, '82');
	end if;

	--insert into cur_bal (codigo, nombre, orden) values ('', '', '83');
	
	-- UTILIDAD O PERDIDA DEL EJERCICIO
	if in_tinforme = 1 then
	  insert into cur_bal (codigo, nombre, total, color, orden ) values ('UTILIDAD', 'O PERDIDA DEL EJERCICIO', nutilidada - (nutilidada * 0.35), 3, '84');
	end if;
	
	if in_tinforme = 2 then
	  insert into cur_bal (codigo, nombre, parcial, total, color, orden) values ('UTILIDAD', 'O PERDIDA DEL EJERCICIO', nutilidadap - (nutilidadap * 0.35), nutilidada - (nutilidada * 0.35), 3, '84');
	end if;
	
	if in_nits = 1 then
		for curdatos1 in 
		select cb.codigo as cb_codigo, cb.nombre, cb.parcial, cb.total, cb.color, cb.nits, cb.codigo_Id, cb.orden from cur_bal cb
		loop
			if curdatos1.nits = 1 then
				insert into cur_final 
				select null, concat(rtrim(p.documento), ' - ', rtrim(p.n_completo)) as nombre,
					case
						when in_mes=1  then COALESCE(sn.sal01,0)
						when in_mes=2  then COALESCE(sn.sal02,0)
						when in_mes=3  then COALESCE(sn.sal03,0)
						when in_mes=4  then COALESCE(sn.sal04,0)
						when in_mes=5  then COALESCE(sn.sal05,0)
						when in_mes=6  then COALESCE(sn.sal06,0)
						when in_mes=7  then COALESCE(sn.sal07,0)
						when in_mes=8  then COALESCE(sn.sal08,0)
						when in_mes=9  then COALESCE(sn.sal09,0)
						when in_mes=10 then COALESCE(sn.sal10,0)
						when in_mes=11 then COALESCE(sn.sal11,0)
						when in_mes=12 then COALESCE(sn.sal12,0)
					end, null as total, 99 as color, 0 as nits, sn.mayor_id as codigo_id, concat(curdatos1.cb_codigo, '9') as orden 
				from personas_persona p, contabilidad_saldos_nits sn 
				where
				case
					when in_mes=1  then COALESCE(sn.sal01,0)
					when in_mes=2  then COALESCE(sn.sal02,0)
					when in_mes=3  then COALESCE(sn.sal03,0)
					when in_mes=4  then COALESCE(sn.sal04,0)
					when in_mes=5  then COALESCE(sn.sal05,0)
					when in_mes=6  then COALESCE(sn.sal06,0)
					when in_mes=7  then COALESCE(sn.sal07,0)
					when in_mes=8  then COALESCE(sn.sal08,0)
					when in_mes=9  then COALESCE(sn.sal09,0)
					when in_mes=10 then COALESCE(sn.sal10,0)
					when in_mes=11 then COALESCE(sn.sal11,0)
					when in_mes=12 then COALESCE(sn.sal12,0)
				end <> 0 
				and sn.mayor_id = curdatos1.codigo_Id 
				and sn.anio = in_anio 
				and p.id = sn.personas_id;
			end if;
	
			insert into cur_final (codigo, nombre, parcial, total, color, orden) values (
				curdatos1.cb_codigo, curdatos1.nombre, curdatos1.parcial, curdatos1.total, curdatos1.color, curdatos1.orden
			);
		end loop;
	
		return QUERY 
		 	select *, 0 as principal, 0 as occidente, 0 as costa, 0 as eje, 0 as aprincipal, 0 as aoccidente, 0 as acosta, 0 as aeje 
		 	from cur_final order by orden;
	 	drop table cur_bal;
		drop table cur_final;
	 else
	 
	 	return QUERY 
		 	select cbal.*, 0 as principal, 0 as occidente, 0 as costa, 0 as eje, 0 as aprincipal, 0 as aoccidente, 0 as acosta, 0 as aeje  
		 	from cur_bal as cbal order by cbal.orden;
	 	drop table cur_bal;
		drop table cur_final;
     end if;			
END
$function$
;

-- Permissions

ALTER FUNCTION public.getestadoresultados(int4, int4, int4, int4, int4, bool) OWNER TO postgres;
GRANT ALL ON FUNCTION public.getestadoresultados(int4, int4, int4, int4, int4, bool) TO postgres;
