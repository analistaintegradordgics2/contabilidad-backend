-- DROP FUNCTION public.getbalprueba(int4, int4, int4, int4, varchar, varchar, int4, int4, bool, bool);

CREATE OR REPLACE FUNCTION public.getbalprueba(in_tipocon integer, in_anio integer, in_mes integer, in_nits integer, in_desde character varying, in_hasta character varying, in_sinmovi integer, in_mes_final integer, in_consolidado boolean, in_niif boolean)
 RETURNS TABLE(codigo character varying, nombre character varying, saldoi numeric, debitos numeric, creditos numeric, saldof numeric, color integer, codigo_id integer)
 LANGUAGE plpgsql
AS $function$
DECLARE
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	lccursor varchar(30);
	lnnumero integer;
	curdatos1 record;
	
BEGIN
	CREATE TEMP TABLE IF NOT EXISTS cur_bal (
		codigo varchar(30),
		nombre varchar(250),
		saldoi decimal(18,2),
		debitos decimal(18,2),
		creditos decimal(18,2),
		saldof decimal(18,2),
		color integer default 0,
		nits boolean default false,
		codigo_id int default 0,
		orden varchar(30)
	);
		
	CREATE TEMP TABLE IF NOT EXISTS cur_final (
		codigo varchar(30),
		nombre varchar(250),
		saldoi decimal(18,2),
		debitos decimal(18,2),
		creditos decimal(18,2),
		saldof decimal(18,2),
		color int default 0,
		orden varchar(30),
		codigo_id int default 0
	);

	if length(rtrim(in_desde)) > 0 then
		if length(rtrim(in_hasta)) > 0 then
			in_hasta := in_hasta ||'99';
		else
			in_hasta := in_desde ||'99';
		end if ;
	end if ;

	-- Traer Balance
	raise notice '--> in_consolidado %', in_consolidado;
	if in_consolidado is true and in_mes <> in_mes_final then
		 Insert into cur_bal  
	 	  select a."codigo" as codigo, a."nombre" as nombre, 
		    case --mes inicial
		        when in_mes=1  then b.sali
		        when in_mes=2  then b.sal01
		        when in_mes=3  then b.sal02
		        when in_mes=4  then b.sal03
		        when in_mes=5  then b.sal04
		        when in_mes=6  then b.sal05
		        when in_mes=7  then b.sal06
		        when in_mes=8  then b.sal07
		        when in_mes=9  then b.sal08
		        when in_mes=10 then b.sal09
		        when in_mes=11 then b.sal10
		        when in_mes=12 then b.sal11
		        when in_mes=13 then b.sal12
		    end as saldoi, 
		    CASE
                WHEN in_mes <= in_mes_final THEN
                    (SELECT SUM(value)
                     FROM (
                         VALUES 
                             (1, b.d01), (2, b.d02), (3, b.d03), (4, b.d04), (5, b.d05),
                             (6, b.d06), (7, b.d07), (8, b.d08), (9, b.d09), (10, b.d10),
                             (11, b.d11), (12, b.d12), (13, b.d13)
                     ) AS months(month, value)
                     WHERE month BETWEEN in_mes AND in_mes_final)
                ELSE 
                    0
            END as debitos, 
		    CASE
			    WHEN in_mes <= in_mes_final THEN
			        (SELECT SUM(value)
			         FROM (
			             VALUES 
			                 (1, b.h01), (2, b.h02), (3, b.h03), (4, b.h04), (5, b.h05),
			                 (6, b.h06), (7, b.h07), (8, b.h08), (9, b.h09), (10, b.h10),
			                 (11, b.h11), (12, b.h12), (13, b.h13)
			         ) AS months(month, value)
			         WHERE month BETWEEN in_mes AND in_mes_final)
			    ELSE 
			        0
			END AS creditos, 
		    CASE 
	            WHEN in_mes_final = 1 THEN b.sal01
	            WHEN in_mes_final = 2 THEN b.sal02
	            WHEN in_mes_final = 3 THEN b.sal03
	            WHEN in_mes_final = 4 THEN b.sal04
	            WHEN in_mes_final = 5 THEN b.sal05
	            WHEN in_mes_final = 6 THEN b.sal06
	            WHEN in_mes_final = 7 THEN b.sal07
	            WHEN in_mes_final = 8 THEN b.sal08
	            WHEN in_mes_final = 9 THEN b.sal09
	            WHEN in_mes_final = 10 THEN b.sal10
	            WHEN in_mes_final = 11 THEN b.sal11
	            WHEN in_mes_final = 12 THEN b.sal12
	            WHEN in_mes_final = 13 THEN b.sal13
			END AS saldof, 
		    case
		        when left(rtrim(a."codigo"),1) in ('1', '4','8') and length(rtrim(a."codigo")) = 1 then 1
		        when left(rtrim(a."codigo"),1) in ('1', '4','8') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'general' then 11
		        when left(rtrim(a."codigo"),1) in ('1', '4','8') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'auxiliar' then 12
		        when left(rtrim(a."codigo"),1) in ('2', '5','9') and length(rtrim(a."codigo")) = 1 then 2
		        when left(rtrim(a."codigo"),1) in ('2', '5','9') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'general' then 21
		        when left(rtrim(a."codigo"),1) in ('2', '5','9') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'auxiliar' then 22
		        when left(rtrim(a."codigo"),1) in ('3', '6','7') and length(rtrim(a."codigo")) = 1 then 3
		        when left(rtrim(a."codigo"),1) in ('3', '6','7') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'general' then 31
		        when left(rtrim(a."codigo"),1) in ('3', '6','7') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'auxiliar' then 32
		        end as color,
		    a.maneja_nits as nits, a.id as codigo_id, a."codigo" as orden 
		    from contabilidad_mayor a, contabilidad_saldos b 
		    where length(rtrim(a."codigo")) <= 12 and (
		    case
		        when in_mes_final=1  or in_mes=1 then b.sali
		        when in_mes_final=2  or in_mes=2 then b.sal01
		        when in_mes_final=3  or in_mes=3 then b.sal02
		        when in_mes_final=4  or in_mes=4 then b.sal03
		        when in_mes_final=5  or in_mes=5 then b.sal04
		        when in_mes_final=6  or in_mes=6 then b.sal05
		        when in_mes_final=7  or in_mes=7 then b.sal06
		        when in_mes_final=8  or in_mes=8 then b.sal07
		        when in_mes_final=9  or in_mes=9 then b.sal08
		        when in_mes_final=10 or in_mes=10 then b.sal09
		        when in_mes_final=11 or in_mes=11 then b.sal10
		        when in_mes_final=12 or in_mes=12 then b.sal11
		        when in_mes_final=13 or in_mes=13 then b.sal12
		    end  <>0  or
		    case
				WHEN in_mes <= in_mes_final and in_consolidado is true THEN
	                    (SELECT SUM(value)
	                     FROM (
	                         VALUES 
	                             (1, b.d01), (2, b.d02), (3, b.d03), (4, b.d04), (5, b.d05),
	                             (6, b.d06), (7, b.d07), (8, b.d08), (9, b.d09), (10, b.d10),
	                             (11, b.d11), (12, b.d12), (13, b.d13)
	                     ) AS months(month, value)
                     WHERE month BETWEEN in_mes AND in_mes_final)

		    end  <>0  or
		    case
				WHEN in_mes <= in_mes_final and in_consolidado is true THEN
	                    (SELECT SUM(value)
	                     FROM (
	                         VALUES 
	                             (1, b.h01), (2, b.h02), (3, b.h03), (4, b.h04), (5, b.h05),
	                             (6, b.h06), (7, b.h07), (8, b.h08), (9, b.h09), (10, b.h10),
	                             (11, b.h11), (12, b.h12), (13, b.h13)
	                     ) AS months(month, value)
                     WHERE month BETWEEN in_mes AND in_mes_final)
		    end  <>0  
		    or
		    case
		        when in_mes_final=1  or in_mes=1 then b.sal01
		        when in_mes_final=2  or in_mes=2 then b.sal02
		        when in_mes_final=3  or in_mes=3 then b.sal03
		        when in_mes_final=4  or in_mes=4 then b.sal04
		        when in_mes_final=5  or in_mes=5 then b.sal05
		        when in_mes_final=6  or in_mes=6 then b.sal06
		        when in_mes_final=7  or in_mes=7 then b.sal07
		        when in_mes_final=8  or in_mes=8 then b.sal08
		        when in_mes_final=9  or in_mes=9 then b.sal09
		        when in_mes_final=10 or in_mes=10 then b.sal10
		        when in_mes_final=11 or in_mes=11 then b.sal11
		        when in_mes_final=12 or in_mes=12 then b.sal12
		        when in_mes_final=13 or in_mes=13 then b.sal13
		    end <>0 )
		    and  b.anio = in_anio 
		    and a."codigo" >= case when length(in_desde) > 0 then in_desde else '1' end
			and a."codigo" <= case when length(in_hasta) > 0 then in_hasta else '99' end 
		    and a.id = b.mayor_id 
		    --and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
		    order by a."codigo";
	else
		Insert into cur_bal  
			select a."codigo" as codigo, a."nombre" as nombre, 
			case
				when in_mes=1  then b.sali
				when in_mes=2  then b.sal01
				when in_mes=3  then b.sal02
				when in_mes=4  then b.sal03
				when in_mes=5  then b.sal04
				when in_mes=6  then b.sal05
				when in_mes=7  then b.sal06
				when in_mes=8  then b.sal07
				when in_mes=9  then b.sal08
				when in_mes=10 then b.sal09
				when in_mes=11 then b.sal10
				when in_mes=12 then b.sal11
				when in_mes=13 then b.sal12
			end as saldoi, 
			case
				when in_mes=1  then b.d01
				when in_mes=2  then b.d02
				when in_mes=3  then b.d03
				when in_mes=4  then b.d04
				when in_mes=5  then b.d05
				when in_mes=6  then b.d06
				when in_mes=7  then b.d07
				when in_mes=8  then b.d08
				when in_mes=9  then b.d09
				when in_mes=10 then b.d10
				when in_mes=11 then b.d11
				when in_mes=12 then b.d12
				when in_mes=13 then b.d13
			end as debitos, 
			case
				when in_mes=1  then b.h01
				when in_mes=2  then b.h02
				when in_mes=3  then b.h03
				when in_mes=4  then b.h04
				when in_mes=5  then b.h05
				when in_mes=6  then b.h06
				when in_mes=7  then b.h07
				when in_mes=8  then b.h08
				when in_mes=9  then b.h09
				when in_mes=10 then b.h10
				when in_mes=11 then b.h11
				when in_mes=12 then b.h12
				when in_mes=13 then b.h13
			end as creditos, 
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
				when in_mes=13 then b.sal13
			end as saldof, 
			case
				when left(rtrim(a."codigo"),1) in ('1', '4','8') and length(rtrim(a."codigo")) = 1 then 1
				when left(rtrim(a."codigo"),1) in ('1', '4','8') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'general' then 11
				when left(rtrim(a."codigo"),1) in ('1', '4','8') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'auxiliar' then 12
				when left(rtrim(a."codigo"),1) in ('2', '5','9') and length(rtrim(a."codigo")) = 1 then 2
				when left(rtrim(a."codigo"),1) in ('2', '5','9') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'general' then 21
				when left(rtrim(a."codigo"),1) in ('2', '5','9') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'auxiliar' then 22
				when left(rtrim(a."codigo"),1) in ('3', '6','7') and length(rtrim(a."codigo")) = 1 then 3
				when left(rtrim(a."codigo"),1) in ('3', '6','7') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'general' then 31
				when left(rtrim(a."codigo"),1) in ('3', '6','7') and length(rtrim(a."codigo")) > 1 and lower(a.tipo) = 'auxiliar' then 32
			 end as color,
			a.maneja_nits as nits, a.id as codigo_id, a."codigo" as orden 
			from contabilidad_mayor a, contabilidad_saldos b 
			where length(rtrim(a."codigo")) <= in_tipocon and (
			case
				when in_mes=1  then b.sali
				when in_mes=2  then b.sal01
				when in_mes=3  then b.sal02
				when in_mes=4  then b.sal03
				when in_mes=5  then b.sal04
				when in_mes=6  then b.sal05
				when in_mes=7  then b.sal06
				when in_mes=8  then b.sal07
				when in_mes=9  then b.sal08
				when in_mes=10 then b.sal09
				when in_mes=11 then b.sal10
				when in_mes=12 then b.sal11
				when in_mes=13 then b.sal12
			end  <>0  or
			case
				when in_mes=1  then b.d01
				when in_mes=2  then b.d02
				when in_mes=3  then b.d03
				when in_mes=4  then b.d04
				when in_mes=5  then b.d05
				when in_mes=6  then b.d06
				when in_mes=7  then b.d07
				when in_mes=8  then b.d08
				when in_mes=9  then b.d09
				when in_mes=10 then b.d10
				when in_mes=11 then b.d11
				when in_mes=12 then b.d12
				when in_mes=13 then b.d13
			end  <>0  or
			case
				when in_mes=1  then b.h01
				when in_mes=2  then b.h02
				when in_mes=3  then b.h03
				when in_mes=4  then b.h04
				when in_mes=5  then b.h05
				when in_mes=6  then b.h06
				when in_mes=7  then b.h07
				when in_mes=8  then b.h08
				when in_mes=9  then b.h09
				when in_mes=10 then b.h10
				when in_mes=11 then b.h11
				when in_mes=12 then b.h12
				when in_mes=13 then b.h13
			end  <>0  
			or
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
				when in_mes=13 then b.sal13
			end <>0 )
			and  b.anio = in_anio 
			and a."codigo" >= case when length(in_desde) > 0 then in_desde else '1' end
			and a."codigo" <= case when length(in_hasta) > 0 then in_hasta else '99' end 
			and a.id = b.mayor_id 
			--and (case when coalesce(in_niif,false) is true then coalesce(a.niif,false) = coalesce(in_niif,false) else true end)
			order by a."codigo";
	end if;
	
	--Nelson Lugo 15/06/2021
	if in_nits = 1 then
		for curdatos1 in 
			select curb.codigo, curb.nombre, curb.saldoi, curb.debitos, curb.creditos, curb.saldof, curb.color, curb.nits, curb.codigo_id, curb.orden 
			from cur_bal as curb 
		loop 
			insert into cur_final 
				select concat('   ', rtrim(p.documento)) as codigo, concat('   ', rtrim(p.n_completo)) as nombre,
				case
					when in_mes=1  then sn.sali
					when in_mes=2  then sn.sal01
					when in_mes=3  then sn.sal02
					when in_mes=4  then sn.sal03
					when in_mes=5  then sn.sal04
					when in_mes=6  then sn.sal05
					when in_mes=7  then sn.sal06
					when in_mes=8  then sn.sal07
					when in_mes=9  then sn.sal08
					when in_mes=10 then sn.sal09
					when in_mes=11 then sn.sal10
					when in_mes=12 then sn.sal11
					when in_mes=13 then sn.sal12
				end as saldoi,
				CASE
	                WHEN in_mes <= in_mes_final and in_consolidado is true THEN
	                    (SELECT SUM(value)
	                     FROM (
	                         VALUES 
	                             (1, sn.d01), (2, sn.d02), (3, sn.d03), (4, sn.d04), (5, sn.d05),
	                             (6, sn.d06), (7, sn.d07), (8, sn.d08), (9, sn.d09), (10, sn.d10),
	                             (11, sn.d11), (12, sn.d12), (13, sn.d13)
	                     ) AS months(month, value)
	                     WHERE month BETWEEN in_mes AND in_mes_final)
	                ELSE 
	                    CASE
				            WHEN in_mes = 1  THEN sn.d01
				            WHEN in_mes = 2  THEN sn.d02
				            WHEN in_mes = 3  THEN sn.d03
				            WHEN in_mes = 4  THEN sn.d04
				            WHEN in_mes = 5  THEN sn.d05
				            WHEN in_mes = 6  THEN sn.d06
				            WHEN in_mes = 7  THEN sn.d07
				            WHEN in_mes = 8  THEN sn.d08
				            WHEN in_mes = 9  THEN sn.d09
				            WHEN in_mes = 10 THEN sn.d10
				            WHEN in_mes = 11 THEN sn.d11
				            WHEN in_mes = 12 THEN sn.d12
				            WHEN in_mes = 13 THEN sn.d13
				        END
	            END as debitos,

				CASE
				    WHEN in_mes <= in_mes_final and in_consolidado is true THEN
				        (SELECT SUM(value)
				         FROM (
				             VALUES 
				                 (1, sn.h01), (2, sn.h02), (3, sn.h03), (4, sn.h04), (5, sn.h05),
				                 (6, sn.h06), (7, sn.h07), (8, sn.h08), (9, sn.h09), (10, sn.h10),
				                 (11, sn.h11), (12, sn.h12), (13, sn.h13)
				         ) AS months(month, value)
				         WHERE month BETWEEN in_mes AND in_mes_final)
				    ELSE 
				        CASE
				            WHEN in_mes = 1  THEN sn.h01
				            WHEN in_mes = 2  THEN sn.h02
				            WHEN in_mes = 3  THEN sn.h03
				            WHEN in_mes = 4  THEN sn.h04
				            WHEN in_mes = 5  THEN sn.h05
				            WHEN in_mes = 6  THEN sn.h06
				            WHEN in_mes = 7  THEN sn.h07
				            WHEN in_mes = 8  THEN sn.h08
				            WHEN in_mes = 9  THEN sn.h09
				            WHEN in_mes = 10 THEN sn.h10
				            WHEN in_mes = 11 THEN sn.h11
				            WHEN in_mes = 12 THEN sn.h12
				            WHEN in_mes = 13 THEN sn.h13
				        END
				END AS creditos,
				CASE 
				    WHEN in_consolidado IS TRUE THEN
				        CASE
				            WHEN in_mes_final = 1 THEN sn.sal01
				            WHEN in_mes_final = 2 THEN sn.sal02
				            WHEN in_mes_final = 3 THEN sn.sal03
				            WHEN in_mes_final = 4 THEN sn.sal04
				            WHEN in_mes_final = 5 THEN sn.sal05
				            WHEN in_mes_final = 6 THEN sn.sal06
				            WHEN in_mes_final = 7 THEN sn.sal07
				            WHEN in_mes_final = 8 THEN sn.sal08
				            WHEN in_mes_final = 9 THEN sn.sal09
				            WHEN in_mes_final = 10 THEN sn.sal10
				            WHEN in_mes_final = 11 THEN sn.sal11
				            WHEN in_mes_final = 12 THEN sn.sal12
				            WHEN in_mes_final = 13 THEN sn.sal13
				        END
				    ELSE
				        CASE
				            WHEN in_mes = 1 THEN sn.sal01
				            WHEN in_mes = 2 THEN sn.sal02
				            WHEN in_mes = 3 THEN sn.sal03
				            WHEN in_mes = 4 THEN sn.sal04
				            WHEN in_mes = 5 THEN sn.sal05
				            WHEN in_mes = 6 THEN sn.sal06
				            WHEN in_mes = 7 THEN sn.sal07
				            WHEN in_mes = 8 THEN sn.sal08
				            WHEN in_mes = 9 THEN sn.sal09
				            WHEN in_mes = 10 THEN sn.sal10
				            WHEN in_mes = 11 THEN sn.sal11
				            WHEN in_mes = 12 THEN sn.sal12
				            WHEN in_mes = 13 THEN sn.sal13
				        END

				END AS saldof, 
				0 as color, 
				concat(curdatos1.codigo, '9') as orden, 
				0 as mayorid 
					from personas_persona p, contabilidad_saldosnits sn 
					where sn.mayor_id = curdatos1.codigo_id and sn.anio=in_anio and p.id=sn.personas_id and (
					case
						when in_mes=1  then sn.sali
						when in_mes=2  then sn.sal01
						when in_mes=3  then sn.sal02
						when in_mes=4  then sn.sal03
						when in_mes=5  then sn.sal04
						when in_mes=6  then sn.sal05
						when in_mes=7  then sn.sal06
						when in_mes=8  then sn.sal07
						when in_mes=9  then sn.sal08
						when in_mes=10 then sn.sal09
						when in_mes=11 then sn.sal10
						when in_mes=12 then sn.sal11
						when in_mes=13 then sn.sal12
					end<>0 or
					case
						WHEN in_consolidado is true then 
							CASE
								when in_mes_final=1  then sn.sali
								when in_mes_final=2  then sn.sal01
								when in_mes_final=3  then sn.sal02
								when in_mes_final=4  then sn.sal03
								when in_mes_final=5  then sn.sal04
								when in_mes_final=6  then sn.sal05
								when in_mes_final=7  then sn.sal06
								when in_mes_final=8  then sn.sal07
								when in_mes_final=9  then sn.sal08
								when in_mes_final=10 then sn.sal09
								when in_mes_final=11 then sn.sal10
								when in_mes_final=12 then sn.sal11
								when in_mes_final=13 then sn.sal12
							END
					end<>0 or
					case
						
						when in_mes=1  then sn.d01
						when in_mes=2  then sn.d02
						when in_mes=3  then sn.d03
						when in_mes=4  then sn.d04
						when in_mes=5  then sn.d05
						when in_mes=6  then sn.d06
						when in_mes=7  then sn.d07
						when in_mes=8  then sn.d08
						when in_mes=9  then sn.d09
						when in_mes=10 then sn.d10
						when in_mes=11 then sn.d11
						when in_mes=12 then sn.d12
						when in_mes=13 then sn.d13
					end<>0 or 
					case
						when in_mes=1  then sn.h01
						when in_mes=2  then sn.h02
						when in_mes=3  then sn.h03
						when in_mes=4  then sn.h04
						when in_mes=5  then sn.h05
						when in_mes=6  then sn.h06
						when in_mes=7  then sn.h07
						when in_mes=8  then sn.h08
						when in_mes=9  then sn.h09
						when in_mes=10 then sn.h10
						when in_mes=11 then sn.h11
						when in_mes=12 then sn.h12
						when in_mes=13 then sn.h13
					end <>0 
				);
			insert into cur_final (codigo, nombre, saldoi, debitos, creditos, saldof, color, orden, codigo_id) 
			values (curdatos1.codigo, curdatos1.nombre, curdatos1.saldoi, curdatos1.debitos, curdatos1.creditos, curdatos1.saldof, curdatos1.color, curdatos1.orden, curdatos1.codigo_id);
		end loop;
	
		if in_sinmovi = 1 then
			insert into cur_final 
			select t1."codigo" as codigo, t1."nombre" as nombre, 0 as saldoi, 0 as debitos, 0 as creditos, 0 as saldof,
			case
				when left(rtrim(t1."codigo"),1) in ('1', '4', '8') and length(rtrim(t1."codigo")) = 1 then 1
				when left(rtrim(t1."codigo"),1) in ('1', '4', '8') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'general' then 11
				when left(rtrim(t1."codigo"),1) in ('1', '4', '8') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'auxiliar' then 12
				when left(rtrim(t1."codigo"),1) in ('2', '5', '9') and length(rtrim(t1."codigo")) = 1 then 2
				when left(rtrim(t1."codigo"),1) in ('2', '5', '9') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'general' then 21
				when left(rtrim(t1."codigo"),1) in ('2', '5', '9') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'auxiliar' then 22
				when left(rtrim(t1."codigo"),1) in ('3', '6', '7') and length(rtrim(t1."codigo")) = 1 then 3
				when left(rtrim(t1."codigo"),1) in ('3', '6', '7') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'general' then 31
				when left(rtrim(t1."codigo"),1) in ('3', '6', '7') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'auxiliar' then 32
			end as color, t1."codigo" as orden, t1.id as mayorid
			from contabilidad_mayor t1 
			where length(rtrim(t1."codigo")) <= in_tipocon 
			and t1."codigo" >= case when length(in_desde) > 0 then in_desde else '1' end 
			and t1."codigo" <= case when length(in_hasta) > 0 then in_hasta else '99' end 
			and not exists (select null from contabilidad_saldos as t2 where t2.mayor_id = t1.id and t2.anio = in_anio) 
			and length(rtrim(t1."codigo")) > 0;
		end if;
		return QUERY select cuf.codigo, cuf.nombre, cuf.saldoi, cuf.debitos, cuf.creditos, cuf.saldof, cuf.color, cuf.codigo_id
						 from cur_final as cuf order by cuf.orden, cuf.nombre;
		drop table cur_bal;
		drop table cur_final;
	else 
		if in_sinmovi = 1 then
			insert into cur_bal 
				select t1."codigo" as codigo, t1."nombre" as nombre, 0 as saldoi, 0 as debitos, 0 as creditos, 0 as saldof,
					case
						when left(rtrim(t1."codigo"),1) in ('1', '4', '8') and length(rtrim(t1."codigo")) = 1 then 1
						when left(rtrim(t1."codigo"),1) in ('1', '4', '8') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'general' then 11
						when left(rtrim(t1."codigo"),1) in ('1', '4', '8') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'auxiliar' then 12
						when left(rtrim(t1."codigo"),1) in ('2', '5', '9') and length(rtrim(t1."codigo")) = 1 then 2
						when left(rtrim(t1."codigo"),1) in ('2', '5', '9') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'general' then 21
						when left(rtrim(t1."codigo"),1) in ('2', '5', '9') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'auxiliar' then 22
						when left(rtrim(t1."codigo"),1) in ('3', '6', '7') and length(rtrim(t1."codigo")) = 1 then 3
						when left(rtrim(t1."codigo"),1) in ('3', '6', '7') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'general' then 31
						when left(rtrim(t1."codigo"),1) in ('3', '6', '7') and length(rtrim(t1."codigo")) > 1 and lower(t1.tipo) = 'auxiliar' then 32
					end as color, false as nits, t1.id as codigo_id, t1."codigo" as orden
				from contabilidad_mayor t1 
				where length(rtrim(t1."codigo")) <= in_tipocon 
				and t1."codigo" >= case when length(in_desde) > 0 then in_desde else '1' end 
				and t1."codigo" <= case when length(in_hasta) > 0 then in_hasta else '99' end 
				and not exists (select null from contabilidad_saldos as t2 where t2.mayor_id = t1.id and t2.anio= in_anio) 
				and length(rtrim(t1."codigo")) > 0;
		end if; 
			return QUERY select crb.codigo, crb.nombre, crb.saldoi, crb.debitos, crb.creditos, crb.saldof, crb.color, crb.codigo_id from cur_bal as crb order by crb.orden;
			drop table cur_bal;
			drop table cur_final;
	end if;
END
$function$
;
