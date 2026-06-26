-- DROP FUNCTION public.getestadoresultados_anual(int4, int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getestadoresultados_anual(in_tipocon integer, in_anio integer, in_mes integer, in_nits integer, in_tinforme integer)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
DECLARE
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	lccursor varchar(30);
	lnnumero integer;
	jsondata jsonb[];
	curdatos1 record;
	curdatos2 record;
	curdatos3 record;
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
	total numeric;
	-- variables para calcular totales por mes
	ningresospene decimal(18,2);
	ningresospfeb decimal(18,2);
	ningresospmar decimal(18,2);
	ningresospabr decimal(18,2);
	ningresospmay decimal(18,2);
	ningresospjun decimal(18,2);
	ningresospjul decimal(18,2);
	ningresospago decimal(18,2);
	ningresospsep decimal(18,2);
	ningresospoct decimal(18,2);
	ningresospnov decimal(18,2);
	ningresospdic decimal(18,2);
	ncostosvpene decimal(18,2);
	ncostosvpfeb decimal(18,2);
	ncostosvpmar decimal(18,2);
	ncostosvpabr decimal(18,2);
	ncostosvpmay decimal(18,2);
	ncostosvpjun decimal(18,2);
	ncostosvpjul decimal(18,2);
	ncostosvpago decimal(18,2);
	ncostosvpsep decimal(18,2);
	ncostosvpoct decimal(18,2);
	ncostosvpnov decimal(18,2);
	ncostosvpdic decimal(18,2);
	ngastospene decimal(18,2);
	ngastospfeb decimal(18,2);
	ngastospmar decimal(18,2);
	ngastospabr decimal(18,2);
	ngastospmay decimal(18,2);
	ngastospjun decimal(18,2);
	ngastospjul decimal(18,2);
	ngastospago decimal(18,2);
	ngastospsep decimal(18,2);
	ngastospoct decimal(18,2);
	ngastospnov decimal(18,2);
	ngastospdic decimal(18,2);
	negresospene decimal(18,2);
	negresospfeb decimal(18,2);
	negresospmar decimal(18,2);
	negresospabr decimal(18,2); 
	negresospmay decimal(18,2);
	negresospjun decimal(18,2);
	negresospjul decimal(18,2);
	negresospago decimal(18,2);
	negresospsep decimal(18,2);
	negresospoct decimal(18,2);
	negresospnov decimal(18,2);
	negresospdic decimal(18,2);
	ncostosppene decimal(18,2);
	ncostosppfeb decimal(18,2);
	ncostosppmar decimal(18,2);
	ncostosppabr decimal(18,2);
	ncostosppmay decimal(18,2);
	ncostosppjun decimal(18,2);
	ncostosppjul decimal(18,2);
	ncostosppago decimal(18,2);
	ncostosppsep decimal(18,2);
	ncostosppoct decimal(18,2);
	ncostosppnov decimal(18,2);
	ncostosppdic decimal(18,2);
	nutilidadaPene decimal(18,2);
	nutilidadaPfeb decimal(18,2);
	nutilidadaPmar decimal(18,2);
	nutilidadaPabr decimal(18,2);
	nutilidadaPmay decimal(18,2);
	nutilidadaPjun decimal(18,2);
	nutilidadaPjul decimal(18,2);
	nutilidadaPago decimal(18,2);
	nutilidadaPsep decimal(18,2);
	nutilidadaPoct decimal(18,2);
	nutilidadaPnov decimal(18,2);
	nutilidadaPdic decimal(18,2);
	

begin
	CREATE TEMP TABLE IF NOT EXISTS cur_bal (
		codigo varchar(20),		
		nombre varchar(400),
		parcial decimal(18,2),
		total decimal(18,2),
		color int default 0,
		nits int default 0,
		codigo_id int default 0,
		orden varchar(20),
		enero decimal(18,2),
		febrero decimal(18,2),
		marzo decimal(18,2),
		abril decimal(18,2),
		mayo decimal(18,2),
		junio decimal(18,2),
		julio decimal(18,2),
		agosto decimal(18,2),
		septiembre decimal(18,2),
		octubre decimal(18,2),
		noviembre decimal(18,2),
		diciembre decimal(18,2)
	);
		
	CREATE TEMP TABLE IF NOT EXISTS cur_final (
		codigo varchar(20),
		nombre varchar(400),
		parcial decimal(18,2),
		total decimal(18,2),
		color int default 0,
		orden varchar(20),
		enero decimal(18,2),
		febrero decimal(18,2),
		marzo decimal(18,2),
		abril decimal(18,2),
		mayo decimal(18,2),
		junio decimal(18,2),
		julio decimal(18,2),
		agosto decimal(18,2),
		septiembre decimal(18,2),
		octubre decimal(18,2),
		noviembre decimal(18,2),
		diciembre decimal(18,2)
	);
		
	-- tomamos de referencia el procedimiento de estatado resultados, por eso va info de parcial y total acumulado.
	
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
		end *-1 as total, 1 as color, 0 as nits, a.id as codigo_id, a."codigo" as orden,
			(b.d01 - b.h01)*-1 as enero,
			(b.d02 - b.h02)*-1 as febrero,
			(b.d03 - b.h03)*-1 as marzo, 
			(b.d04 - b.h04)*-1 as abril,
			(b.d05 - b.h05)*-1 as mayo,
			(b.d06 - b.h06)*-1 as junio,
			(b.d07 - b.h07)*-1 as julio,
			(b.d08 - b.h08)*-1 as agosto,
			(b.d09 - b.h09)*-1 as septiembre,
			(b.d10 - b.h10)*-1 as ocutubre,
			(b.d11 - b.h11)*-1 as noviembre,
			(b.d12 - b.h12)*-1 as diciembre
		from contabilidad_mayor a, contabilidad_saldos b 
		where a."codigo" = '4' 
		and b.anio = in_anio 
		and a.id = b.mayor_id 
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
		end * -1 as total, case when length(rtrim(a."codigo")) <= 6 then 11 else 12 end as color, case when a.maneja_nits = true then 1 else 0 end as nits, a.id as codigo_id, a."codigo" as orden,
			(b.d01 - b.h01)*-1 as enero,
			(b.d02 - b.h02)*-1 as febrero,
			(b.d03 - b.h03)*-1 as marzo, 
			(b.d04 - b.h04)*-1 as abril,
			(b.d05 - b.h05)*-1 as mayo,
			(b.d06 - b.h06)*-1 as junio,
			(b.d07 - b.h07)*-1 as julio,
			(b.d08 - b.h08)*-1 as agosto,
			(b.d09 - b.h09)*-1 as septiembre,
			(b.d10 - b.h10)*-1 as ocutubre,
			(b.d11 - b.h11)*-1 as noviembre,
			(b.d12 - b.h12)*-1 as diciembre
		from contabilidad_mayor a, contabilidad_saldos b 
		where left(rtrim(a."codigo"),1) = '4' 
		and length(rtrim(a."codigo")) <= in_tipocon 
		and length(rtrim(a."codigo")) > 1 
		and 
		(b.sal01 <> 0 
		or	b.sal02 <> 0 
		or	b.sal03 <> 0  
		or	b.sal04 <> 0 
		or	b.sal05 <> 0
		or b.sal06 <> 0
		or b.sal07 <> 0
		or b.sal08 <> 0
		or b.sal09 <> 0
		or b.sal10 <> 0
		or b.sal11 <> 0 
		or b.sal12 <> 0 )
		and b.anio = in_anio 
		and a.id = b.mayor_id 
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
	end *-1 as total, 1 as color, 0 as nits, a.id as codigo_id, '49999990' as orden,
		(b.d01 - b.h01)*-1 as enero,
		(b.d02 - b.h02)*-1 as febrero,
		(b.d03 - b.h03)*-1 as marzo, 
		(b.d04 - b.h04)*-1 as abril,
		(b.d05 - b.h05)*-1 as mayo,
		(b.d06 - b.h06)*-1 as junio,
		(b.d07 - b.h07)*-1 as julio,
		(b.d08 - b.h08)*-1 as agosto,
		(b.d09 - b.h09)*-1 as septiembre,
		(b.d10 - b.h10)*-1 as ocutubre,
		(b.d11 - b.h11)*-1 as noviembre,
		(b.d12 - b.h12)*-1 as diciembre
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo"= '4' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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

	--- Crear la variable para sumar el Parcial de los Ingresos
	if in_tinforme = 2 then
	
	select 
		(b.d10 - b.h10) *-1 as ocutubre,
		(b.d01 - b.h01) *-1 as enero,
		(b.d02 - b.h02) *-1 as febrero,
		(b.d03 - b.h03) *-1 as marzo, 
		(b.d04 - b.h04) *-1 as abril,
		(b.d05 - b.h05) *-1 as mayo,
		(b.d06 - b.h06) *-1 as junio,
		(b.d07 - b.h07) *-1 as julio,
		(b.d08 - b.h08) *-1 as agosto,
		(b.d09 - b.h09)*-1 as septiembre,
		(b.d10 - b.h10)*-1 as ocutubre,
		(b.d11 - b.h11)*-1 as noviembre,
		(b.d12 - b.h12)*-1 as diciembre
		into ningresosp,ningresospene,
			ningresospfeb, ningresospmar,
			ningresospabr, ningresospmay,
			ningresospjun, ningresospjul,
			ningresospago, ningresospsep,
			ningresospoct, ningresospnov,
			ningresospdic 
		from contabilidad_mayor a, contabilidad_saldos b 
		where a."codigo" = '4' 
		and b.anio = in_anio 
		and a.id = b.mayor_id; 
	
	end if;

	if ningresos IS NULL then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('1', 'INGRESOS', 0, 1, '1');
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'INGRESOS', 0, 1, '49999990');
	end if;
	
	insert into cur_bal (codigo, nombre, orden) values ('', '', '49999991');
	
	

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
		end * 1 as total, 2 as color, 0 as nits, a.id as codigo_id, a."codigo" as orden,
			b.d01 - b.h01 as enero,
			b.d02 - b.h02 as febrero,
			b.d03 - b.h03 as marzo, 
			b.d04 - b.h04 as abril,
			b.d05 - b.h05 as mayo,
			b.d06 - b.h06 as junio,
			b.d07 - b.h07 as julio,
			b.d08 - b.h08 as agosto,
			b.d09 - b.h09 as septiembre,
			b.d10 - b.h10 as ocutubre,
			b.d11 - b.h11 as noviembre,
			b.d12 - b.h12 as diciembre
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '5' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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
		end * 1 as total, case when length(rtrim(a."codigo")) <= 6 then 21 else 22 end as color, case when a.maneja_nits = true then 1 else 0 end as nits, a.id as codigo_id, a."codigo" as orden, 
			b.d01 - b.h01 as enero,
			b.d02 - b.h02 as febrero,
			b.d03 - b.h03 as marzo, 
			b.d04 - b.h04 as abril,
			b.d05 - b.h05 as mayo,
			b.d06 - b.h06 as junio,
			b.d07 - b.h07 as julio,
			b.d08 - b.h08 as agosto,
			b.d09 - b.h09 as septiembre,
			b.d10 - b.h10 as ocutubre,
			b.d11 - b.h11 as noviembre,
			b.d12 - b.h12 as diciembre
	from contabilidad_mayor a, contabilidad_saldos b 
	where left(rtrim(a."codigo"),1) = '5' 
	and length(rtrim(a."codigo")) <= in_tipocon 
	and length(rtrim(a."codigo")) > 1 
	and (b.sal01 <> 0 
	or	b.sal02 <> 0 
	or	b.sal03 <> 0  
	or	b.sal04 <> 0 
	or	b.sal05 <> 0
	or b.sal06 <> 0
	or b.sal07 <> 0
	or b.sal08 <> 0
	or b.sal09 <> 0
	or b.sal10 <> 0
	or b.sal11 <> 0 
	or b.sal12 <> 0)
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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
		end *1 as total, 2 as color, 0 as nits, a.id as codigo_id, '59999990',
			b.d01-b.h01 as enero,
			b.d02-b.h02 as febrero,
			b.d03-b.h03 as marzo,
			b.d04-b.h04 as abril,
			b.d05-b.h05 as mayo,
			b.d06-b.h06 as junio,
			b.d07-b.h07 as julio,
			b.d08-b.h08 as agosto,
			b.d09-b.h09 as septiembre,
			b.d10-b.h10 as octubre,
			b.d11-b.h11 as noviembre,
			b.d12-b.h12 as diciembre
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '5' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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
	
	if in_tinforme = 2 then
		select
			(b.d10 - b.h10)*1 as ocutubre,
		  	(b.d01 - b.h01) *1 as enero,
			(b.d02 - b.h02) *1 as febrero,
			(b.d03 - b.h03) *1 as marzo, 
			(b.d04 - b.h04) *1 as abril,
			(b.d05 - b.h05) *1 as mayo,
			(b.d06 - b.h06) *1 as junio,
			(b.d07 - b.h07) *1 as julio,
			(b.d08 - b.h08) *1 as agosto,
			(b.d09 - b.h09)*1 as septiembre,
			(b.d10 - b.h10)*1 as ocutubre,
			(b.d11 - b.h11)*1 as noviembre,
			(b.d12 - b.h12)*1 as diciembre 
			 into ngastosp, ngastospene, 
			ngastospfeb, ngastospmar,
			ngastospabr, ngastospmay,
			ngastospjun, ngastospjul,
			ngastospago, ngastospsep,
			ngastospoct, ngastospnov,
			ngastospdic
		from contabilidad_mayor a, contabilidad_saldos b 
		where a."codigo" = '5' 
		and b.anio = in_anio 
		and a.id = b.mayor_id; 
	end if;

	if ngastos IS NULL then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('5', 'GASTOS', 0, 2, '5');
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'GASTOS', 0, 2, '59999990');
	end if;
	
	insert into cur_bal (codigo, nombre, orden) values ('', '', '59999991');

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
		end * 1 as total, 2 as color, 0 as nits, a.id as codigo_id, a."codigo" as orden,
		(b.d01 - b.h01)*1 as enero,
		(b.d02 - b.h02)*1 as febrero,
		(b.d03 - b.h03)*1 as marzo, 
		(b.d04 - b.h04)*1 as abril,
		(b.d05 - b.h05)*1 as mayo,
		(b.d06 - b.h06)*1 as junio,
		(b.d07 - b.h07)*1 as julio,
		(b.d08 - b.h08)*1 as agosto,
		(b.d09 - b.h09)*1 as septiembre,
		(b.d10 - b.h10)*1 as ocutubre,
		(b.d11 - b.h11)*1 as noviembre,
		(b.d12 - b.h12)*1 as diciembre
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '6' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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
		end * -1 as total, case when length(rtrim(a."codigo")) <= 6 then 21 else 22 end as color, case when a.maneja_nits = true then 1 else 0 end as nits, a.id as codigo_id, a."codigo" as orden,
		(b.d01 - b.h01)*-1 as enero,
		(b.d02 - b.h02)*-1 as febrero,
		(b.d03 - b.h03)*-1 as marzo, 
		(b.d04 - b.h04)*-1 as abril,
		(b.d05 - b.h05)*-1 as mayo,
		(b.d06 - b.h06)*-1 as junio,
		(b.d07 - b.h07)*-1 as julio,
		(b.d08 - b.h08)*-1 as agosto,
		(b.d09 - b.h09)*-1 as septiembre,
		(b.d10 - b.h10)*-1 as ocutubre,
		(b.d11 - b.h11)*-1 as noviembre,
		(b.d12 - b.h12)*-1 as diciembre
		
	from contabilidad_mayor a, contabilidad_saldos b 
	where left(rtrim(a."codigo"),1) ='6' 
	and length(rtrim(a."codigo")) <= in_tipocon 
	and length(rtrim(a."codigo")) > 1 
	and (b.sal01 <> 0 
	or	b.sal02 <> 0 
	or	b.sal03 <> 0  
	or	b.sal04 <> 0 
	or	b.sal05 <> 0
	or b.sal06 <> 0
	or b.sal07 <> 0
	or b.sal08 <> 0
	or b.sal09 <> 0
	or b.sal10 <> 0
	or b.sal11 <> 0 
	or b.sal12 <> 0)
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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
		end * 1 as total, 2 as color, 0 as nits, a.id as codigo_id, '69999990' as orden,
		b.d01 - b.h01 as enero,
		b.d02 - b.h02 as febrero,
		b.d03 - b.h03 as marzo, 
		b.d04 - b.h04 as abril,
		b.d05 - b.h05 as mayo,
		b.d06 - b.h06 as junio,
		b.d07 - b.h07 as julio,
		b.d08 - b.h08 as agosto,
		b.d09 - b.h09 as septiembre,
		b.d10 - b.h10 as ocutubre,
		b.d11 - b.h11 as noviembre,
		b.d12 - b.h12 as diciembre
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '6' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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
	 
  	if in_tinforme = 2 then
  	
	  	select 
			(b.d10 - b.h10)*1 as ocutubre,
			(b.d01 - b.h01) *1 as enero,
			(b.d02 - b.h02) *1 as febrero,
			(b.d03 - b.h03) *1 as marzo, 
			(b.d04 - b.h04) *1 as abril,
			(b.d05 - b.h05) *1 as mayo,
			(b.d06 - b.h06) *1 as junio,
			(b.d07 - b.h07) *1 as julio,
			(b.d08 - b.h08) *1 as agosto,
			(b.d09 - b.h09) *1 as septiembre,
			(b.d10 - b.h10) *1 as ocutubre,
			(b.d11 - b.h11) *1 as noviembre,
			(b.d12 - b.h12) *1 as diciembre
			
			into ncostosvp,ncostosvpene, 
				ncostosvpfeb, ncostosvpmar,
				ncostosvpabr, ncostosvpmay,
				ncostosvpjun, ncostosvpjul,
				ncostosvpago, ncostosvpsep,
				ncostosvpoct, ncostosvpnov,
				ncostosvpdic
			from contabilidad_mayor a, contabilidad_saldos b 
			where a."codigo" = '6' 
			and b.anio = in_anio 
			and a.id = b.mayor_id; 
  	
	end if;

	if ncostosv IS NULL then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('6', 'COSTOS DE VENTAS', 0, 2,'6');
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'COSTOS DE VENTAS', 0, 2, '69999990');
	end if;
	
	insert into cur_bal (codigo, nombre, orden) values ('', '', '69999991');

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
		end * 1 as total, 2 as color, 0 as nits, a.id as codigo_id, a."codigo" as orden,
		b.d01 - b.h01 as enero,
		b.d02 - b.h02 as febrero,
		b.d03 - b.h03 as marzo, 
		b.d04 - b.h04 as abril,
		b.d05 - b.h05 as mayo,
		b.d06 - b.h06 as junio,
		b.d07 - b.h07 as julio,
		b.d08 - b.h08 as agosto,
		b.d09 - b.h09 as septiembre,
		b.d10 - b.h10 as ocutubre,
		b.d11 - b.h11 as noviembre,
		b.d12 - b.h12 as diciembre
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '7' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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
		end * 1 as total, case when length(rtrim(a."codigo")) <= 6 then 21 else 22 end as color, case when a.maneja_nits = true then 1 else 0 end as nits, a.id as codigo_id, a."codigo" as orden,
		b.d01 - b.h01 as enero,
		b.d02 - b.h02 as febrero,
		b.d03 - b.h03 as marzo, 
		b.d04 - b.h04 as abril,
		b.d05 - b.h05 as mayo,
		b.d06 - b.h06 as junio,
		b.d07 - b.h07 as julio,
		b.d08 - b.h08 as agosto,
		b.d09 - b.h09 as septiembre,
		b.d10 - b.h10 as ocutubre,
		b.d11 - b.h11 as noviembre,
		b.d12 - b.h12 as diciembre
	from contabilidad_mayor a, contabilidad_saldos b 
	where left(rtrim(a."codigo"),1) = '7' 
	and length(rtrim(a."codigo")) <= in_tipocon 
	and length(rtrim(a."codigo")) > 1 
	and b.sal01 <> 0 
	and	b.sal02 <> 0 
	and	b.sal03 <> 0  
	and	b.sal04 <> 0 
	and	b.sal05 <> 0
	and b.sal06 <> 0
	and b.sal07 <> 0
	and b.sal08 <> 0
	and b.sal09 <> 0
	and b.sal10 <> 0
	and b.sal11 <> 0 
	and b.sal12 <> 0
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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
	end * 1 as total, 2 as color, 0 as nits, a.id as codigo_id, '79999990' as orden,
		b.d01 - b.h01 as enero,
		b.d02 - b.h02 as febrero,
		b.d03 - b.h03 as marzo, 
		b.d04 - b.h04 as abril,
		b.d05 - b.h05 as mayo,
		b.d06 - b.h06 as junio,
		b.d07 - b.h07 as julio,
		b.d08 - b.h08 as agosto,
		b.d09 - b.h09 as septiembre,
		b.d10 - b.h10 as ocutubre,
		b.d11 - b.h11 as noviembre,
		b.d12 - b.h12 as diciembre
	from contabilidad_mayor a, contabilidad_saldos b 
	where a."codigo" = '7' 
	and b.anio = in_anio 
	and a.id = b.mayor_id 
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

	if in_tinforme = 2 then
		select  	
		(b.d10 - b.h10) as ocutubre,
		(b.d01 - b.h01) as enero,
		(b.d02 - b.h02) as febrero,
		(b.d03 - b.h03) as marzo, 
		(b.d04 - b.h04) as abril,
		(b.d05 - b.h05) as mayo,
		(b.d06 - b.h06) as junio,
		(b.d07 - b.h07) as julio,
		(b.d08 - b.h08) as agosto,
		(b.d09 - b.h09) as septiembre,
		(b.d10 - b.h10) as ocutubre,
		(b.d11 - b.h11) as noviembre,
		(b.d12 - b.h12) as diciembre
		 into ncostospp,
		 ncostosppene, ncostosppfeb,
		 ncostosppmar, ncostosppabr,
		 ncostosppmay, ncostosppjun,
		 ncostosppjul, ncostosppago,
		 ncostosppsep, ncostosppoct,
		 ncostosppnov, ncostosppdic
		from contabilidad_mayor a, contabilidad_saldos b 
		where a."codigo" = '7' 
		and b.anio = in_anio 
		and a.id = b.mayor_id; 
	end if;
	
	if ncostosp IS NULL then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('7', 'COSTOS DE PRODUCCION', 0, 2, '7');
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'COSTOS DE PRODUCCION', 0, 2, '79999990');
	end if;
	
	insert into cur_bal (codigo, nombre, orden) values ('', '', '79999991');
	
	-- TOTAL DE EGRESOS
	
	negresos := COALESCE(ngastos, 0) + COALESCE(ncostosv, 0) + COALESCE(ncostosp, 0);
	negresosp := COALESCE(ngastosp, 0) + COALESCE(ncostosvp, 0) + COALESCE(ncostospp, 0);

	negresospene := COALESCE(ngastospene, 0) + COALESCE(ncostosvpene, 0) + COALESCE(ncostosppene, 0); 
	negresospfeb := COALESCE(ngastospfeb, 0) + COALESCE(ncostosvpfeb, 0) + COALESCE(ncostosppfeb, 0);
	negresospmar := COALESCE(ngastospmar, 0) + COALESCE(ncostosvpmar, 0) + COALESCE(ncostosppmar, 0);
	negresospabr := COALESCE(ngastospabr, 0) + COALESCE(ncostosvpabr, 0) + COALESCE(ncostosppabr, 0);
	negresospmay := COALESCE(ngastospmay, 0) + COALESCE(ncostosvpmay, 0) + COALESCE(ncostosppmay, 0);
	negresospjun := COALESCE(ngastospjun, 0) + COALESCE(ncostosvpjun, 0) + COALESCE(ncostosppjun, 0);
	negresospjul := COALESCE(ngastospjul, 0) + COALESCE(ncostosvpjul, 0) + COALESCE(ncostosppjul, 0);
	negresospago := COALESCE(ngastospago, 0) + COALESCE(ncostosvpago, 0) + COALESCE(ncostosppago, 0);
	negresospsep := COALESCE(ngastospsep, 0) + COALESCE(ncostosvpsep, 0) + COALESCE(ncostosppsep, 0);
	negresospoct := COALESCE(ngastospoct, 0) + COALESCE(ncostosvpoct, 0) + COALESCE(ncostosppoct, 0);
	negresospnov := COALESCE(ngastospnov, 0) + COALESCE(ncostosvpnov, 0) + COALESCE(ncostosppnov, 0);
	negresospdic := COALESCE(ngastospdic, 0) + COALESCE(ncostosvpdic, 0) + COALESCE(ncostosppdic, 0);


	if in_tinforme = 1 then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('TOTAL', 'EGRESOS', negresos, 3, '8');
	end if;

	if in_tinforme = 2 then
		insert into cur_bal (codigo, nombre, parcial, total, color, orden, enero, febrero, marzo, abril, mayo, junio, julio, agosto, septiembre,
			octubre, noviembre, diciembre) values ('TOTAL', 'EGRESOS', negresosp, negresos, 3, '8', negresospene, negresospfeb, negresospmar,negresospabr, negresospmay,
			negresospjun, negresospjul, negresospago,negresospsep, negresospoct, negresospnov, negresospdic);

	end if;
	
	insert into cur_bal (codigo, nombre, orden) values ('', '', '81');
	
	-- UTILIDAD ANTES DEL IMPUESTO
	nutilidada := COALESCE(ningresos, 0) - COALESCE(ngastos, 0) - COALESCE(ncostosp, 0) - COALESCE(ncostosv, 0);
	nutilidadaP := COALESCE(ningresosp, 0) - COALESCE(ngastosp, 0) - COALESCE(ncostospp, 0) - COALESCE(ncostosvp, 0);

	nutilidadaPene := COALESCE(ningresospene, 0) - COALESCE(ngastospene, 0) - COALESCE(ncostosppene, 0) - COALESCE(ncostosvpene, 0);
	nutilidadaPfeb := COALESCE(ningresospfeb, 0) - COALESCE(ngastospfeb, 0) - COALESCE(ncostosppfeb, 0) - COALESCE(ncostosvpfeb, 0);
	nutilidadaPmar := COALESCE(ningresospmar, 0) - COALESCE(ngastospmar, 0) - COALESCE(ncostosppmar, 0) - COALESCE(ncostosvpmar, 0);
	nutilidadaPabr := COALESCE(ningresospabr, 0) - COALESCE(ngastospabr, 0) - COALESCE(ncostosppabr, 0) - COALESCE(ncostosvpabr, 0);
	nutilidadaPmay := COALESCE(ningresospmay, 0) - COALESCE(ngastospmay, 0) - COALESCE(ncostosppmay, 0) - COALESCE(ncostosvpmay, 0);
	nutilidadaPjun := COALESCE(ningresospjun, 0) - COALESCE(ngastospjun, 0) - COALESCE(ncostosppjun, 0) - COALESCE(ncostosvpjun, 0);
	nutilidadaPjul := COALESCE(ningresospjul, 0) - COALESCE(ngastospjul, 0) - COALESCE(ncostosppjul, 0) - COALESCE(ncostosvpjul, 0);
	nutilidadaPago := COALESCE(ningresospago, 0) - COALESCE(ngastospago, 0) - COALESCE(ncostosppago, 0) - COALESCE(ncostosvpago, 0);
	nutilidadaPsep := COALESCE(ningresospsep, 0) - COALESCE(ngastospsep, 0) - COALESCE(ncostosppsep, 0) - COALESCE(ncostosvpsep, 0);
	nutilidadaPoct := COALESCE(ningresospoct, 0) - COALESCE(ngastospoct, 0) - COALESCE(ncostosppoct, 0) - COALESCE(ncostosvpoct, 0);
	nutilidadaPnov := COALESCE(ningresospnov, 0) - COALESCE(ngastospnov, 0) - COALESCE(ncostosppnov, 0) - COALESCE(ncostosvpnov, 0);
	nutilidadaPdic := COALESCE(ningresospdic, 0) - COALESCE(ngastospdic, 0) - COALESCE(ncostosppdic, 0) - COALESCE(ncostosvpdic, 0);

	 
	if in_tinforme = 1 then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('UTILIDAD', 'ANTES DE IMPUESTO', nutilidada, 3, '82');
	end if;

	if in_tinforme = 2 then
		insert into cur_bal (codigo, nombre, parcial, total, color, orden, enero, febrero, marzo, abril, mayo, junio, julio, agosto, septiembre,
			octubre, noviembre, diciembre) values ('UTILIDAD', 'ANTES DE IMPUESTO', nutilidadap, nutilidada, 3, '82', nutilidadaPene,
			nutilidadaPfeb, nutilidadaPmar, nutilidadaPabr, nutilidadaPmay, nutilidadaPjun, nutilidadaPjul, nutilidadaPago, nutilidadaPsep, nutilidadaPoct, nutilidadaPnov,nutilidadaPdic);
	end if;

	if in_tinforme = 1 then
		insert into cur_bal (codigo, nombre, total, color, orden) values ('PROVISIÃ“N', 'DE IMPUESTO', nutilidada * 0.35, 3, '82');
	end if;

	if in_tinforme = 2 then
		insert into cur_bal (codigo, nombre, parcial, total, color, orden, enero, febrero, marzo, abril, mayo, junio, julio, agosto, septiembre,
			octubre, noviembre, diciembre) values ('PROVISIÃ“N', 'DE IMPUESTO', nutilidadap * 0.35, nutilidada * 0.35, 3, '82', nutilidadaPene * 0.35,
			nutilidadaPfeb* 0.35, nutilidadaPmar* 0.35, nutilidadaPabr* 0.35, nutilidadaPmay* 0.35, nutilidadaPjun* 0.35, nutilidadaPjul* 0.35, nutilidadaPago* 0.35, nutilidadaPsep* 0.35, nutilidadaPoct* 0.35, nutilidadaPnov* 0.35,nutilidadaPdic* 0.35);
	end if;

	insert into cur_bal (codigo, nombre, orden) values ('', '', '83');
	
	-- UTILIDAD O PERDIDA DEL EJERCICIO
	if in_tinforme = 1 then
	  insert into cur_bal (codigo, nombre, total, color, orden ) values ('UTILIDAD', 'O PERDIDA DEL EJERCICIO', nutilidada - (nutilidada * 0.35), 3, '84');
	end if;
	
	if in_tinforme = 2 then
	  insert into cur_bal (codigo, nombre, parcial, total, color, orden, enero, febrero, marzo, abril, mayo, junio, julio, agosto, septiembre,
			octubre, noviembre, diciembre) values ('UTILIDAD', 'O PERDIDA DEL EJERCICIO', nutilidadap - (nutilidadap * 0.35), nutilidada - (nutilidada * 0.35), 3, '84',nutilidadaPene-(nutilidadaPene * 0.35),
			nutilidadaPfeb-(nutilidadaPfeb* 0.35), nutilidadaPmar-(nutilidadaPmar* 0.35), nutilidadaPabr-(nutilidadaPabr* 0.35), nutilidadaPmay-(nutilidadaPmay* 0.35), nutilidadaPjun-(nutilidadaPjun* 0.35),
			nutilidadaPjul-(nutilidadaPjul* 0.35), nutilidadaPago-(nutilidadaPago* 0.35), nutilidadaPsep-(nutilidadaPsep* 0.35), nutilidadaPoct-(nutilidadaPoct* 0.35), nutilidadaPnov-(nutilidadaPnov* 0.35), nutilidadaPdic-(nutilidadaPdic* 0.35));
	end if;
	
	--if in_nits = 1 then
		/*for curdatos1 in 
		select codigo, nombre, parcial, total, color, nits, codigo_Id, orden from cur_bal 
		loop
			if curdatos1.nits = 1 then
				insert into cur_final 
				select null as codigo, concat(rtrim(p.documento), ' - ', rtrim(p.n_completo)) as nombre,
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
					end, null as total, 0 as color, concat(curdatos1.codigo, '9') as orden 
				from personas_persona p, contabilidad_saldosnits sn 
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
				curdatos1.codigo, curdatos1.nombre, curdatos1.parcial, curdatos1.total, curdatos1.color, curdatos1.orden
			);
		end loop;
	*/
		/*Empezamos a recorrer la data para ir insertando los terceros solicitados en la bita: 50340*/
	
		for curdatos2 in select * from cur_bal loop
			
			total := curdatos2.enero      	+ curdatos2.febrero + curdatos2.marzo 	  + curdatos2.abril  +
		             	 curdatos2.mayo 	+ curdatos2.junio   + curdatos2.julio 	  + curdatos2.agosto +
		             	 curdatos2.septiembre 	+ curdatos2.octubre + curdatos2.noviembre + curdatos2.diciembre;
		            
			jsondata := jsondata || jsonb_build_object(
			
						'codigo', 		curdatos2.codigo,
						'nombre', 		curdatos2.nombre,
						'parcial', 		curdatos2.parcial,
						'total', 		total,
						'color', 		curdatos2.color,
						'nits', 		curdatos2.nits,
						'codigo_id', 		curdatos2.codigo_id,
						'orden', 		curdatos2.orden,
						'enero', 		curdatos2.enero,
						'febrero', 		curdatos2.febrero,
						'marzo', 		curdatos2.marzo,
						'abril', 		curdatos2.abril,
						'mayo', 		curdatos2.mayo,
						'junio', 		curdatos2.junio,
						'julio', 		curdatos2.julio,
						'agosto', 		curdatos2.agosto,
						'septiembre', 		curdatos2.septiembre,
						'octubre', 		curdatos2.octubre,
						'noviembre', 		curdatos2.noviembre,
						'diciembre', 		curdatos2.diciembre
						
					);
			if curdatos2.nits = 1 and in_nits = 1 then
				for curdatos3 in select
										*
									from
										contabilidad_saldosnits csn
									inner join personas_persona tp on
										tp.id = csn.personas_id
									where
										csn.anio = in_anio
										and csn.mayor_id = curdatos2.codigo_id
									order by
										tp.n_completo loop
											
					 total := (curdatos3.h01 - curdatos3.d01) + (curdatos3.h02 - curdatos3.d02) + (curdatos3.h03 - curdatos3.d03) + (curdatos3.h04 - curdatos3.d04) +
		                      (curdatos3.h05 - curdatos3.d05) + (curdatos3.h06 - curdatos3.d06) + (curdatos3.h07 - curdatos3.d07) + (curdatos3.h08 - curdatos3.d08) +
		                      (curdatos3.h09 - curdatos3.d09) + (curdatos3.h10 - curdatos3.d10) + (curdatos3.h11 - curdatos3.d11) + (curdatos3.h12 - curdatos3.d12);
					
					jsondata := jsondata || jsonb_build_object(
						'codigo', 		curdatos3.documento,
						'nombre', 		curdatos3.n_completo,
						'parcial',		0,
						'total',  		total,
						'color',  		0,
						'nits',   		curdatos2.nits,
						'codigo_id',		curdatos2.codigo_id,
						'orden', 		curdatos2.orden,
						'enero', 		(curdatos3.h01 - curdatos3.d01),
						'febrero',  		(curdatos3.h02 - curdatos3.d02),
						'marzo', 		(curdatos3.h03 - curdatos3.d03),
						'abril', 		(curdatos3.h04 - curdatos3.d04),
						'mayo', 		(curdatos3.h05 - curdatos3.d05),
						'junio',		(curdatos3.h06 - curdatos3.d06),
						'julio', 		(curdatos3.h07 - curdatos3.d07),
						'agosto', 		(curdatos3.h08 - curdatos3.d08),
						'septiembre', 	(curdatos3.h09 - curdatos3.d09),
						'octubre', 		(curdatos3.h10 - curdatos3.d10),
						'noviembre', 	(curdatos3.h11 - curdatos3.d11),
						'diciembre', 	(curdatos3.h12 - curdatos3.d12)
					);
				end loop;
			end if;
		end loop;

		RETURN array_to_json(jsondata);
		 	/*select *, 0 as principal, 0 as occidente, 0 as costa, 0 as eje, 0 as aprincipal, 0 as aoccidente, 0 as acosta, 0 as aeje 
		 	from cur_final order by orden;*/
	 	drop table cur_bal;
		drop table cur_final;
	-- else
	 
	 	/*return QUERY 
		 	select cbal.*, 0 as principal, 0 as occidente, 0 as costa, 0 as eje, 0 as aprincipal, 0 as aoccidente, 0 as acosta, 0 as aeje  
		 	from cur_bal as cbal order by cbal.orden;
	 	drop table cur_bal;
		drop table cur_final;*/
     --end if;	
END
$function$
;
