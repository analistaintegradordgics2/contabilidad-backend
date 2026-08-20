-- DROP FUNCTION public.get_nominas_por_liquidar(int4, varchar, int4, int4);

CREATE OR REPLACE FUNCTION public.get_nominas_por_liquidar(in_anio integer, in_mes character varying, in_periodo integer, in_centro_costo integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
declare
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	item record;
	nove record;
	per_nove record;
	resultado json;
	dias_trabajados integer;
	temp_dias_trabajados integer;
	dias_periodo integer;
	id_anio integer;
	id_mes integer;
	fecha_ini_periodo date;
	fecha_fin_periodo date;
	diferencia_dias integer;
	
	novedades json default '[]';
	valor_salario numeric(15, 2) default 0.00;
	valor_salario_trabajado numeric(15, 2) default 0.00;
	valor_sueldo_periodo numeric(15, 2) default 0.00;
	valor_aux_transporte numeric(15, 2) default 0.00;
	valor_salud numeric(15, 2) default 0.00;
	valor_salud_empleador numeric(15, 2) default 0.00;
	valor_pension numeric(15, 2) default 0.00;
	valor_pension_empleador numeric(15, 2) default 0.00;
	
	valor_arl numeric(15, 2) default 0.00;
	valor_cesantias numeric(15, 2) default 0.00;
	valor_int_cesantias numeric(15, 2) default 0.00;
	valor_primas numeric(15, 2) default 0.00;
	valor_vacaciones numeric(15, 2) default 0.00;
	valor_caja_compensacion numeric(15, 2) default 0.00;
	
	valor_devengados numeric(15, 2) default 0.00;
	valor_deducidos numeric(15, 2) default 0.00;
	
	-- Para parametros
	salario_minimo numeric(15, 2) default 0.00;
	aux_transporte numeric(15, 2) default 0.00;
	forma_liquidacion_salud integer [];
	forma_liquidacion_pension integer [];
	forma_liquidacion_arl integer [];
	forma_liquidacion_cesantias integer [];
	forma_liquidacion_int_cesantias integer [];
	forma_liquidacion_primas integer [];
	forma_liquidacion_vacaciones integer [];
	forma_liquidacion_caja_compensacion integer [];
	forma_liquidacion_aux_transporte integer [];
	ausentismos integer [];
	licencias_no_remuneradas integer [];
	novedad_salud_id integer default null;
	novedad_pension_id integer default null;
	
	porc_salud_empleador numeric(15, 3) default 0.00;
	porc_pension_empleador numeric(15, 3) default 0.00;
	tmp_porc_salud_empleador numeric(15, 3) default 0.00;
	tmp_porc_pension_empleador numeric(15, 3) default 0.00;
	porc_arl_empleador numeric(15, 3) default 0.00;
	porc_cesantias_empleador numeric(15, 3) default 0.00;
	porc_int_cesantias_empleador numeric(15, 3) default 0.00;
	porc_primas_empleador numeric(15, 3) default 0.00;
	porc_vacaciones_empleador numeric(15, 3) default 0.00;
	porc_caja_compen_empleador numeric(15, 3) default 0.00;
	porc_salud_sena_empleador numeric(15, 3) default 0.00;

	-- Variables para operaciones
	novedad_periodo json;
	total_dias_ausentismos integer default 0;
	valor_total_ausentismos integer default 0;
	total_dias_ausentismos_por_periodo integer default 0;
	valor_total_ausentismos_por_periodo integer default 0;
	valor_dia numeric(15, 2) default 0.00;
	valor_dia_salario_minimo numeric(15, 2) default 0.00;
	valor_hora numeric(15, 2) default 0.00;
	valor_hora_aux_transporte numeric(15, 2) default 0.00;
	valor_novedad numeric(15, 2) default 0.00;
	valor_total_novedades_devengado numeric(15, 2) default 0.00;
	valor_total_novedades_deducido numeric(15, 2) default 0.00;
	valor_total_licencias_no_remuneradas_especiales numeric(15, 2) default 0.00;
	detalle_novedad text;
	fecha_de_novedad text;
	mi_variable json;

	tmp_aux_transporte numeric(15, 2) default 0.00;
begin
	
	create temp table if not exists temp_resultado (
		id integer,
		documento varchar,
		nombre varchar,
		persona_id integer,
		cargo varchar,
		dias integer,
		empleado json,
		empleador json,
		centro_costo json,
		fecha_ini_contrato date,
		fecha_fin_contrato date,
		aux_trans boolean default false,
		tipo_contrato integer,
		tipo_contrato_nombre varchar,
		subtipo_trabajador varchar default null
	);

	create temp table if not exists temp_novedades (
		id integer,
		contrato_id integer,
		valor numeric(15, 2) default 0.00,
		valor_original integer,
		cta_debito_id integer,
		cta_credito_id integer,
		detalle text,
		novedad_id integer,
		periodo integer,
		persona_id integer,
		tipo_novedad_id integer,
		tipo_valor_novedad_id integer,
		fecha_inicial timestamptz,
		fecha_final timestamptz,
		dias integer,
		ausentismo boolean default false,
		base_liquidacion_empleado json,
		base_liquidacion_empleador json,
		vacaciones boolean default false,
		vacaciones_liquidadas boolean default false,
		automatica boolean default false
	);
	
	--------------------------------------- Parametros necesarios para el funcionamiento ---------------------------------------
	select case when np.valor = 'quincenal' then 15 else 30 end into dias_periodo from nomina_parametros np where np.parametro = 'forma_liquidacion';
	select ca.salario_minimo, ca.aux_transporte into salario_minimo, aux_transporte from parametros_anio ca where ca.nombre = in_anio;
	select cm.id into id_mes from parametros_mes cm where cm.numero = in_mes;
	select ca.id into id_anio from parametros_anio ca where ca.nombre = in_anio;

	-- Quitar las [ ] para que se pueda convertir a un array string y luego con el ANY es como un IN pero no restringe que sea solo numerico
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into forma_liquidacion_salud from nomina_parametros np where np.parametro = 'forma_liquidacion_salud';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into forma_liquidacion_pension from nomina_parametros np where np.parametro = 'forma_liquidacion_pension';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into forma_liquidacion_arl from nomina_parametros np where np.parametro = 'forma_liquidacion_arl';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into forma_liquidacion_cesantias from nomina_parametros np where np.parametro = 'forma_liquidacion_cesantias';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into forma_liquidacion_int_cesantias from nomina_parametros np where np.parametro = 'forma_liquidacion_int_cesantias';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into forma_liquidacion_primas from nomina_parametros np where np.parametro = 'forma_liquidacion_primas';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into forma_liquidacion_vacaciones from nomina_parametros np where np.parametro = 'forma_liquidacion_vacaciones';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into forma_liquidacion_caja_compensacion from nomina_parametros np where np.parametro = 'forma_liquidacion_caja_compensacion';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into forma_liquidacion_aux_transporte from nomina_parametros np where np.parametro = 'forma_liquidacion_aux_transporte';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into ausentismos from nomina_parametros np where np.parametro = 'ausentismo';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into licencias_no_remuneradas from nomina_parametros np where np.parametro = 'licencias_no_remuneradas';
	
	-- Porcentajes para empleador
	select coalesce(np.valor::numeric, 3) into tmp_porc_salud_empleador from nomina_parametros np where np.parametro = 'porc_salud_empleador';
	select coalesce(np.valor::numeric, 3) into tmp_porc_pension_empleador from nomina_parametros np where np.parametro = 'porc_pension_empleador';
	select coalesce(np.valor::numeric, 3) into porc_arl_empleador from nomina_parametros np where np.parametro = 'porc_arl_empleador';
	select coalesce(np.valor::numeric, 3) into porc_cesantias_empleador from nomina_parametros np where np.parametro = 'porc_cesantias_empleador';
	select coalesce(np.valor::numeric, 3) into porc_int_cesantias_empleador from nomina_parametros np where np.parametro = 'porc_int_cesantias_empleador';
	select coalesce(np.valor::numeric, 3) into porc_primas_empleador from nomina_parametros np where np.parametro = 'porc_primas_empleador';
	select coalesce(np.valor::numeric, 3) into porc_vacaciones_empleador from nomina_parametros np where np.parametro = 'porc_vacaciones_empleador';
	select coalesce(np.valor::numeric, 3) into porc_caja_compen_empleador from nomina_parametros np where np.parametro = 'porc_caja_compen_empleador';
	select coalesce(np.valor::numeric, 3) into porc_salud_sena_empleador from nomina_parametros np where np.parametro = 'porc_salud_sena_empleador';

	-- Parametros de novedades
	select coalesce(np.valor::integer, 0) into novedad_salud_id from nomina_parametros np where np.parametro = 'salud';
	select coalesce(np.valor::integer, 0) into novedad_pension_id from nomina_parametros np where np.parametro = 'pension';
	-----------------------------------------------------------------------------------------------------------------------------
	
	-- Construir las fecha del periodo
	if in_periodo = 1 then
		fecha_ini_periodo := (select to_date(concat(in_anio, '-', in_mes, '-01'), 'YYYY-MM-DD'));
		fecha_fin_periodo := (select to_date(concat(in_anio, '-', in_mes, '-15'), 'YYYY-MM-DD'));
	elsif in_periodo = 2 then
		fecha_ini_periodo := (select to_date(concat(in_anio, '-', in_mes, '-16'), 'YYYY-MM-DD'));
		if in_mes <> '02' then
			fecha_fin_periodo := (select to_date(concat(in_anio, '-', in_mes, '-30'), 'YYYY-MM-DD'));
		else
			-- Si el mes es febrero se toma el ultimo dia ya sea 28 o 29
			fecha_fin_periodo := (select to_date(concat(in_anio, '-', in_mes, '-', (select extract('day' from (select date_trunc('month', (select to_date(concat(in_anio, '-', in_mes, '-', '01'), 'YYYY-MM-DD'))) + interval '1 month' - interval '1 day')))), 'YYYY-MM-DD'));
		end if;
	else
		fecha_ini_periodo := (select to_date(concat(in_anio, '-', in_mes, '-01'), 'YYYY-MM-DD'));
		if in_mes <> '02' then
			fecha_fin_periodo := (select to_date(concat(in_anio, '-', in_mes, '-30'), 'YYYY-MM-DD'));
		else
			-- Si el mes es febrero se toma el ultimo dia ya sea 28 o 29
			fecha_fin_periodo := (select to_date(concat(in_anio, '-', in_mes, '-', (select extract('day' from (select date_trunc('month', (select to_date(concat(in_anio, '-', in_mes, '-', '01'), 'YYYY-MM-DD'))) + interval '1 month' - interval '1 day')))), 'YYYY-MM-DD'));
		end if;
	end if;

	for item in 
		select *, nda.porcentaje_salud, nda.porcentaje_pension, nda.porcentaje_arl, nda.entidad_salud_id, nda.entidad_pension_id, nda.caja_compensacion_id, nda.nivel_riesgo_id
		from nomina_contrato nc
		join nomina_datosaportes nda on nda.contrato_id = nc.id
		where nc.estado is true
		  and nc.fecha_ingreso <= fecha_fin_periodo
		  and (nc.fecha_retiro is null or nc.fecha_retiro >= fecha_ini_periodo)
		  and (in_centro_costo <= 0 or nc.centro_costo_id = in_centro_costo)
	loop
		
		valor_salario := 0;
		valor_aux_transporte := 0;
		valor_salud := 0;
		valor_salud_empleador := 0;
		valor_pension := 0;
		valor_pension_empleador := 0;
		valor_arl := 0;
		valor_cesantias := 0;
		valor_int_cesantias := 0;
		valor_primas := 0;
		valor_vacaciones := 0;
		valor_caja_compensacion := 0;
		dias_trabajados := dias_periodo;
		temp_dias_trabajados := 0;
		diferencia_dias := 0;
		total_dias_ausentismos := 0;
	
		porc_salud_empleador := tmp_porc_salud_empleador;
		porc_pension_empleador := tmp_porc_pension_empleador;
	
		if (
			select count(nl.id) from nomina_liquidaciones nl 
			where nl.contrato_id = item.id 
			and nl.anio_id = id_anio 
			and nl.mes_id = id_mes
			and nl.periodo_id = in_periodo
			and nl.estado is true
		) = 0 then
			
			-- Validacion que se hace para saber si un empleado ingreso a laborar dentro del perido a liquidar para no calcular el total de los dias si no solo los dias que alcanzo a laborar
			-- Ejemplo: Si se esta liquidando la quincena 2 del 16 al 30 de octubre, y el empleado ingreso el 20 de octubre entonces solo se liquida 11 dias
			if item.fecha_ingreso >= fecha_ini_periodo then
				diferencia_dias := ((select to_char(item.fecha_ingreso, 'DD')::integer) - (select to_char(fecha_ini_periodo, 'DD')::integer));
				--dias := ((select to_char(fecha_fin_periodo, 'DD')::integer) - diferencia_dias);
				dias_trabajados := (dias_periodo - diferencia_dias);
			end if;
			-- Fin
		
			if item.fecha_retiro is not null then
				if date(to_char(item.fecha_retiro, 'YYYY-MM-DD')) <= fecha_fin_periodo then
					diferencia_dias := ((select to_char(item.fecha_retiro, 'DD')::integer) - (select to_char(fecha_ini_periodo, 'DD')::integer) + 1);
					--dias_trabajados := (dias_periodo - diferencia_dias);
					dias_trabajados := diferencia_dias;
				end if;
			end if;
			
			-- Nelson Lugo - 28/02/2025 - Se agrega estas validaciones para obtener la diferencia totales de los dias que no laboró (Sin tener en cuenta licecias)
			-- Estos es para saber si el empleado ingreso o se retiro dentro del mes y año que se esta liquidando
			-- Ejemplo: Ingreso el 6 entonces 6 - 1 = 5 dias que no laboro, Se retiro el 26 entonces 30 - 26 = 4 dias que no laboro
			-- Esto se realizo para saber los dias exactos que no laboro por ingreso o retiro para el calculo de las novedades que se cobran solo en la quincena 2
			diferencia_dias := 0;
			if extract(month from item.fecha_ingreso) = in_mes::integer and extract(year from item.fecha_ingreso) = in_anio::integer then
				diferencia_dias := ((select to_char(item.fecha_ingreso, 'DD')::integer) - 1);
			end if;

			if item.fecha_retiro is not null then
				if extract(month from item.fecha_retiro) = in_mes::integer and extract(year from item.fecha_retiro) = in_anio::integer then
					diferencia_dias := diferencia_dias + (30 - (select to_char(item.fecha_retiro, 'DD')::integer));
				end if;
			end if;
		
			-- Se calcula el valor del salario.
			if item.salario_minimo is true then
				-- Se valida si la persona gana el salario minimo
				valor_salario := salario_minimo;
			else 
				-- Si gana mas o menos del salario minimo
				valor_salario := item.sueldo;
			end if;
			
			valor_dia := (valor_salario / 30);
			valor_sueldo_periodo := (valor_dia * dias_trabajados);
			valor_dia_salario_minimo := (salario_minimo / 30);
			valor_hora := (valor_dia / 8);
			valor_hora_aux_transporte := ((aux_transporte / 30) / 8);
			
			-- Recorrer Novedades
			for nove in 
				select 
					ncp.*,
					nc.id as nc_id,
					nc.centro_costos_novedades_id as nc_centro_costos_novedades_id,
					nc.porcentaje_liquidacion as nc_porcentaje_liquidacion,
					nc.fecha_inicial as nc_fecha_inicial,
					nc.fecha_final as nc_fecha_final,
					nc.vacaciones as nc_vacaciones,
					nc.vacaciones_liquidadas as nc_vacaciones_liquidadas,
					nc.descripcion as nc_descripcion,
					nn.id as nn_id,
					nn.tipo_valor_novedad_id as nn_tipo_valor_novedad_id,
					nn.tipo_novedad_id as nn_tipo_novedad_id,
					nn.grupo_nomina_id as nn_grupo_nomina_id,
					nn.sub_grupo_nomina_id as nn_sub_grupo_nomina_id,
					nn.automatica
				from nomina_contratonovedadesperiodos ncp
				inner join nomina_contratonominanovedades nc on nc.id = ncp.contrato_novedades_id and nc.eliminado is false
				inner join nomina_novedades nn on nn.id = nc.novedad_id
				where ncp.mes = in_mes
				and ncp.anio = in_anio::text
				and nn.automatica is false
				and ncp.contrato_id = item.id -- contrato_id
			loop
				-- N O V E D A D E S  D E  T I P O  A U S E N T I S M O
				if nove.nn_id = any(ausentismos) then
					valor_novedad := ((valor_dia * nove.nc_porcentaje_liquidacion::numeric) / 100);
				
					if valor_novedad < valor_dia_salario_minimo then
						valor_novedad := valor_dia_salario_minimo;
					end if;
					
					if nove.nn_id = 4 then -- Novedad de licencia no remunerada
						valor_novedad := 0;
					else
						valor_novedad := (round(valor_novedad * nove.valor, 0));
					end if;
				else 
					-- Se valida si el tipo de valor de la novedad sea de tipo Hora
					if nove.nn_tipo_valor_novedad_id = 2 then
						valor_novedad := (round(valor_hora * nove.valor, 0));
					else
						valor_novedad := nove.valor;
					end if;
				end if;
			
				/*if nove.vacaciones is true then 
					valor_novedad := 0;
				end if;*/
		
				-- Construir el detalle de la novedad
				detalle_novedad := concat(
					nove.nc_descripcion, ' ',
					(
						case when nove.nn_tipo_valor_novedad_id = 1 then -- Si el tipo_valor_novedad = 1 quiere decir que es de tipo dia, se agrega al detalle la cantidad de dias de la novedad
							(
								select concat(
									' (', nove.valor, ' ', (select nt.nombre from nomina_tipovalornovedad nt where nt.id = nove.nn_tipo_valor_novedad_id), ' DE ',
									(select (select substring(cm.nombre, 1, 3)) from parametros_mes cm where cm.numero = (select to_char(nove.fecha_ini, 'MM'))), ' ', nove.nc_porcentaje_liquidacion, '%) - ' -- Se extrae las 3 primeras letras del nombre del mes ejemplo: ENE, FEB
								)
							)
						else
							case when nove.nn_tipo_valor_novedad_id = 2 then -- Si el tipo_valor_novedad = 1 quiere decir que es de tipo Hora.
							(
								select concat(' (', nove.valor, ' HORAS) - ')
							)
							else
								' DEL '
							end
						end
					)
				);
				
				fecha_de_novedad := concat(
					(select to_char(nove.nc_fecha_inicial, 'DD')), ' DE ',
					(select (select substring(cm.nombre, 1, 3)) from parametros_mes cm where cm.numero = (select to_char(nove.nc_fecha_inicial, 'MM'))), ' DE ',
					(select to_char(nove.nc_fecha_inicial, 'YYYY')), ' AL ',
					(select to_char(nove.nc_fecha_final, 'DD')), ' DE ',
					(select (select substring(cm.nombre, 1, 3)) from parametros_mes cm where cm.numero = (select to_char(nove.nc_fecha_final, 'MM'))), ' DE ',
					(select to_char(nove.nc_fecha_final, 'YYYY'))
				);
			
				detalle_novedad := concat(detalle_novedad, fecha_de_novedad);
			
				-- Fin Construir el detalle de la novedad
				insert into temp_novedades (
					id,
					contrato_id,
					valor,
					valor_original,
					cta_debito_id,
					cta_credito_id,
					detalle,
					novedad_id,
					periodo,
					persona_id,
					tipo_novedad_id,
					tipo_valor_novedad_id,
					fecha_inicial,
					fecha_final,
					dias,
					ausentismo,
					base_liquidacion_empleado,
					base_liquidacion_empleador,
					vacaciones,
					vacaciones_liquidadas,
					automatica
				) values (
					nove.nc_id, -- id de contrato_novedad
					item.id, -- id del contrato
					valor_novedad, -- Valor de la novedad
					cast(nove.valor as integer), -- Volar de novedad original (2 Horas, 3 Dias o $50.000)
					(
						select
							coalesce(nn.mayor_cta_debito_id, (
								select
									ne.mayor_cta_debito_id 
								from nomina_entidadescentrocostos ne
								where ne.id = nn.entidades_centro_costos_id
								)
							)
						from nomina_novedadescentrocosto nn where nn.id = nove.nc_centro_costos_novedades_id
					), -- CTA debito de la novedad
					(
						select
							coalesce(nn.mayor_cta_credito_id, (
								select
									ne.mayor_cta_credito_id 
								from nomina_entidadescentrocostos ne
								where ne.id = nn.entidades_centro_costos_id
								)
							)
						from nomina_novedadescentrocosto nn where nn.id = nove.nc_centro_costos_novedades_id
					), -- CTA credito de la novedad
					detalle_novedad, -- detalle de la novedad
					nove.nn_id, -- id de la novedad
					nove.periodo_id,
					item.persona_id, -- Id del empleado
					nove.nn_tipo_novedad_id, -- Tipo de novedad
					nove.nn_tipo_valor_novedad_id, -- Tipo de valor de novedad
					nove.nc_fecha_inicial,
					nove.nc_fecha_final,
					(case when nove.nn_grupo_nomina_id = 9 and nove.nn_sub_grupo_nomina_id = 29
						then
							(nove.nc_fecha_final::date - nove.nc_fecha_inicial::date) + 1
						else 
							nove.valor
					end
					), -- Dias de la novedad
					(case when nove.nn_id = any(ausentismos) then true else false end), -- Si es ausentismo
					(
						select 
							coalesce(json_agg(json_build_object(
								'base_liquidacion_id', nb.base_liquidacion_id,
								'novedades_id', nb.novedades_id
							)), '[]') 
						from nomina_baseliquidacionnovedad nb
						inner join nomina_baseliquidacionempleado nbl on nbl.id = nb.base_liquidacion_id
						where nb.novedades_id = nove.nn_id
						and nb.eliminado is false
						and nbl.tipo = 1
					), -- Base de liquidacion de empleado
					(
						select 
							coalesce(json_agg(json_build_object(
								'base_liquidacion_id', nb.base_liquidacion_id,
								'novedades_id', nb.novedades_id
							)), '[]')
						from nomina_baseliquidacionnovedad nb
						inner join nomina_baseliquidacionempleado nbl on nbl.id = nb.base_liquidacion_id
						where nb.novedades_id = nove.nn_id
						and nb.eliminado is false
						and nbl.tipo = 2
					), -- Base de liquidacion de empleador
					nove.nc_vacaciones,
					nove.nc_vacaciones_liquidadas,
					nove.automatica
				);

			end loop;
			-- Fin Novedades

			-- Nelson Lugo 26/11/2024 Bita: 61206 - Agregar novedades automaticas a todos los empleados que tengan esta novedad
			-- Recorrer las novedades Automaticas
			for nove in 
				select
					nc.id as nc_id,
					nc.valor,
					nc.centro_costos_novedades_id as nc_centro_costos_novedades_id,
					nc.porcentaje_liquidacion as nc_porcentaje_liquidacion,
					nc.fecha_inicial as nc_fecha_inicial,
					nc.fecha_final as nc_fecha_final,
					nc.vacaciones as nc_vacaciones,
					nc.vacaciones_liquidadas as nc_vacaciones_liquidadas,
					nc.descripcion as nc_descripcion,
					nn.id as nn_id,
					nn.tipo_valor_novedad_id as nn_tipo_valor_novedad_id,
					nn.tipo_novedad_id as nn_tipo_novedad_id,
					nn.automatica
				from nomina_contratonominanovedades nc
				inner join nomina_novedades nn on nn.id = nc.novedad_id
				where nc.contrato_id = item.id -- contrato_id
				and nc.eliminado is false
				and nn.automatica is true
				and nn.periodo_automatico_id = in_periodo
			loop
				valor_novedad := nove.valor;
				detalle_novedad := nove.nc_descripcion;
				fecha_de_novedad := concat(
					' ',
					(select to_char(fecha_ini_periodo, 'DD')), ' DE ',
					(select (select substring(cm.nombre, 1, 3)) from parametros_mes cm where cm.numero = (select to_char(fecha_ini_periodo, 'MM'))), ' DE ',
					(select to_char(fecha_ini_periodo, 'YYYY')), ' AL ',
					(select to_char(fecha_fin_periodo, 'DD')), ' DE ',
					(select (select substring(cm.nombre, 1, 3)) from parametros_mes cm where cm.numero = (select to_char(fecha_fin_periodo, 'MM'))), ' DE ',
					(select to_char(fecha_fin_periodo, 'YYYY'))
				);
			
				detalle_novedad := concat(detalle_novedad, fecha_de_novedad);
			
				-- Fin Construir el detalle de la novedad
				insert into temp_novedades (
					id,
					contrato_id,
					valor,
					valor_original,
					cta_debito_id,
					cta_credito_id,
					detalle,
					novedad_id,
					periodo,
					persona_id,
					tipo_novedad_id,
					tipo_valor_novedad_id,
					fecha_inicial,
					fecha_final,
					dias,
					ausentismo,
					base_liquidacion_empleado,
					base_liquidacion_empleador,
					vacaciones,
					vacaciones_liquidadas,
					automatica
				) values (
					nove.nc_id, -- id de contrato_novedad
					item.id, -- id del contrato
					valor_novedad, -- Valor de la novedad
					cast(nove.valor as integer), -- Volar de novedad original (2 Horas, 3 Dias o $50.000)
					(
						select
							coalesce(nn.mayor_cta_debito_id, (
								select
									ne.mayor_cta_debito_id 
								from nomina_entidadescentrocostos ne
								where ne.id = nn.entidades_centro_costos_id
								)
							)
						from nomina_novedadescentrocosto nn where nn.id = nove.nc_centro_costos_novedades_id
					), -- CTA debito de la novedad
					(
						select
							coalesce(nn.mayor_cta_credito_id, (
								select
									ne.mayor_cta_credito_id 
								from nomina_entidadescentrocostos ne
								where ne.id = nn.entidades_centro_costos_id
								)
							)
						from nomina_novedadescentrocosto nn where nn.id = nove.nc_centro_costos_novedades_id
					), -- CTA credito de la novedad
					detalle_novedad, -- detalle de la novedad
					nove.nn_id, -- id de la novedad
					in_periodo,
					item.persona_id, -- Id del empleado
					nove.nn_tipo_novedad_id, -- Tipo de novedad
					nove.nn_tipo_valor_novedad_id, -- Tipo de valor de novedad
					nove.nc_fecha_inicial,
					nove.nc_fecha_final,
					nove.valor, -- Dias de la novedad
					(case when nove.nn_id = any(ausentismos) then true else false end), -- Si es ausentismo
					(
						select 
							coalesce(json_agg(json_build_object(
								'base_liquidacion_id', nb.base_liquidacion_id,
								'novedades_id', nb.novedades_id
							)), '[]') 
						from nomina_baseliquidacionnovedad nb
						inner join nomina_baseliquidacionempleado nbl on nbl.id = nb.base_liquidacion_id
						where nb.novedades_id = nove.nn_id
						and nb.eliminado is false
						and nbl.tipo = 1
					), -- Base de liquidacion de empleado
					(
						select 
							coalesce(json_agg(json_build_object(
								'base_liquidacion_id', nb.base_liquidacion_id,
								'novedades_id', nb.novedades_id
							)), '[]')
						from nomina_baseliquidacionnovedad nb
						inner join nomina_baseliquidacionempleado nbl on nbl.id = nb.base_liquidacion_id
						where nb.novedades_id = nove.nn_id
						and nb.eliminado is false
						and nbl.tipo = 2
					), -- Base de liquidacion de empleador
					nove.nc_vacaciones,
					nove.nc_vacaciones_liquidadas,
					nove.automatica
				);
			end loop;
			-- Fin Novedades Automaticas

			-- Se consulta cuales de las novedades es de tipo ausentismo del mes completo
			select 
				coalesce(sum(tn.dias), 0), coalesce(sum(tn.valor), 0)::int into total_dias_ausentismos, valor_total_ausentismos
			from temp_novedades tn
			where tn.ausentismo is true;
		
			-- Se consulta cuales de las novedades es de tipo ausentismo del periodo
			select 
				coalesce(sum(tn.dias), 0), coalesce(sum(tn.valor), 0)::int into total_dias_ausentismos_por_periodo, valor_total_ausentismos_por_periodo
			from temp_novedades tn
			where tn.ausentismo is true
			and tn.periodo = in_periodo;

		
			--dias_trabajados := (dias_trabajados - total_dias_ausentismos);
			temp_dias_trabajados := dias_trabajados;
			dias_trabajados := (dias_trabajados - total_dias_ausentismos_por_periodo);
		
			valor_salario_trabajado := round(valor_dia * dias_trabajados, 0);

			
			-- Se consulta cuales de las novedades es de tipo dias y que sean devengados para sumar a los dias laborales
			select 
				coalesce(sum(tn.valor), 0), coalesce(sum(tn.dias), 0) into valor_total_novedades_devengado, total_dias_ausentismos_por_periodo
			from temp_novedades tn
			where tn.tipo_novedad_id = 3 -- Novedades de tipo devengado
			and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
			and tn.periodo = in_periodo
			and not tn.novedad_id = any(licencias_no_remuneradas);
		
			-- Nelson Lugo - 18/03/2023 - Se busca si alguna de las novedades es licencias no remuneras especiales para restar el valor al total de devengados, ya que apesar que estas licencias sean devengados se deben restar. 
			select 
				coalesce(sum(tn.valor), 0) into valor_total_licencias_no_remuneradas_especiales
			from temp_novedades tn
			where tn.tipo_novedad_id = 3 -- Novedades de tipo devengado
			and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
			and tn.periodo = in_periodo
			and tn.novedad_id = any(licencias_no_remuneradas);
			
			-- Se consulta cuales de las novedades es de tipo dias y que sean deducidos para restarle a los dias laborales
			select 
				coalesce(sum(tn.valor), 0), coalesce(sum(tn.dias), 0) into valor_total_novedades_deducido, total_dias_ausentismos_por_periodo
			from temp_novedades tn
			where tn.tipo_novedad_id = 2 -- Novedades de tipo devengado
			and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
			and tn.periodo = in_periodo;
			-- Fin
			
			-- V A L O R  D E  A U X  T R A N S P O R T E  E M P L E A D O
			if item.auxilio_transporte is true then
				-- Base de liquidacion de empleado
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte auxilio de transporte (base_liquidacion_id = 2)
				select coalesce(sum(tn.dias), 0) into valor_novedad
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleado) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 2 -- id base de liquidacion empleado (aux transporte)
				)
				and tn.tipo_valor_novedad_id = 1 -- tipo_valor_novedad = dia
				and case when (select array_length(forma_liquidacion_aux_transporte::integer[], 1)) = 2 then tn.periodo = in_periodo else true end -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
				and not tn.novedad_id = any(licencias_no_remuneradas); -- Licencias no remuneradas (exceptuando);
				
				if item.medio_auxilio_transporte is true then
					tmp_aux_transporte = aux_transporte / 2;
				else
					tmp_aux_transporte = aux_transporte;
				end if;

				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_aux_transporte::integer[], 1)) = 2 then 
					valor_aux_transporte := round((tmp_aux_transporte / 30) * (dias_trabajados - valor_novedad), 0);
				else 
					if in_periodo = 2 then
						-- Cuando el Auxilio de transporte solo se liquida en la quincena 2, tiene un trato especial
						
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						
						if diferencia_dias > 0 then
							valor_aux_transporte := round((tmp_aux_transporte / 30) * ((30 - diferencia_dias) - (valor_novedad + total_dias_ausentismos)), 0);
						else 
							-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
							-- Nelson Lugo 31/01/2025 - Si el aux transporte solo se liquida en la quincena 2, se tiene que restar todos los ausentismos de todo el mes
							valor_aux_transporte := round((tmp_aux_transporte / 30) * ((temp_dias_trabajados * 2) - (valor_novedad + total_dias_ausentismos)), 0);
						end if;
					else 
						valor_aux_transporte := round((tmp_aux_transporte / 30) * (dias_trabajados - valor_novedad), 0);
					end if;
				end if;
				-- Se afecta el auxilio de transporte en dias
				
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte auxilio de transporte (base_liquidacion_id = 2)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'valor_original', tn.valor_original,
					'tipo_novedad_id', tn.tipo_novedad_id,
					'periodo', tn.periodo,
					'novedad_id', tn.novedad_id,
					'tipo_valor_novedad_id', tn.tipo_valor_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleado) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 2 -- id base de liquidacion empleado (aux transporte)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and tn.periodo = in_periodo; -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
			 
				-- Se filtran las novedades que afecten aux de transporte y sean de tipo devengado para SUMAR al valor del aux de transporte "exceptuando las licencias no remuneradas" que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'novedad_id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas (exceptuando);
			
				valor_aux_transporte := round(valor_aux_transporte + valor_novedad, 0);
			
				-- Se filtran las novedades que afecten aux de transporte y "sean licencias no remuneradas" de tipo hora para restar al valor de aux de transporte
				select 
					coalesce(sum(cast(obj->>'valor_original'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'tipo_valor_novedad_id'::varchar as integer) = 2 -- tipo_valor_novedad = Horas
				and cast(obj->>'novedad_id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas;

				valor_aux_transporte := round(valor_aux_transporte - (valor_hora_aux_transporte * valor_novedad), 0);

				-- Se filtran las novedades que afecten aux de transporte y "sean licencias no remuneradas" de tipo valor($) para restar al valor de aux de transporte
				select 
					coalesce(sum(cast(obj->>'valor_original'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'tipo_valor_novedad_id'::varchar as integer) = 3 -- tipo_valor_novedad = Valor
				and cast(obj->>'novedad_id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas;

				valor_aux_transporte := round(valor_aux_transporte - valor_novedad, 0);
			
				-- Se filtran las novedades que afecten aux de transporte y sean de tipo deducido para RESTAR al valor del aux de transporte
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
			
				valor_aux_transporte := round(valor_aux_transporte - valor_novedad, 0);
				-- Fin -- Base de liquidacion de empleado
			end if;
			-- F I N  V A L O R  D E  A U X  T R A N S P O R T E  E M P L E A D O
		
			-- V A L O R E S  Q U E  C O R R E S P O N D E N  A L  E M P L E A D O
		
			-- V A L O R  D E  S A L U D  E M P L E A D O
				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_salud::integer[], 1)) = 2 then 
					valor_salud := round(((valor_sueldo_periodo * item.porcentaje_salud) / 100), 0);
				else 
					if in_periodo = 2 then
					-- Cuando la salud solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_salud := round((((valor_dia * (30 - diferencia_dias)) * item.porcentaje_salud) / 100), 0);
						else 
							-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
							valor_salud := round((((valor_sueldo_periodo * 2) * item.porcentaje_salud) / 100), 0);
						end if;
					else
						valor_salud := round(((valor_sueldo_periodo * item.porcentaje_salud) / 100), 0);
					end if;
				end if;
				
				-- Base de liquidacion de empleado
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte a salud (base_liquidacion_id = 7)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'tipo_novedad_id', tn.tipo_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleado) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 7 -- id base de liquidacion empleado (salud)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and case when (select array_length(forma_liquidacion_salud::integer[], 1)) = 2 then tn.periodo = in_periodo else true end; -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
				
				-- Se filtran las novedades que afecten salud y sean de tipo devengado para SUMAR al valor del salud exceptuando las licencias no remuneradas que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_salud := round((valor_salud + ((valor_novedad * item.porcentaje_salud) / 100)), 0);
			
				-- Se filtran las novedades que afecten salud y sean licencias no remuneradas para restar al valor de salud
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_salud := round((valor_salud - ((valor_novedad * item.porcentaje_salud) / 100)), 0);
			
				-- Se filtran las novedades que afecten salud y sean de tipo devengado para RESTAR al valor del salud
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
				
				valor_salud := round((valor_salud - ((valor_novedad * item.porcentaje_salud) / 100)), 0);
				-- Fin Base de liquidacion de empleado
			
				-- Se filtran las novedades de tipo licencia no remunerada para restar esos dias a la salud del empleado ya que no los laboró esta es independiente a la de arriba
				select 
					coalesce(sum(tn.dias), 0) into valor_novedad
				from temp_novedades tn
				where tn.novedad_id = 4; -- novedad_id = 4 Licencia no remunerada
				
				valor_novedad := (valor_dia * valor_novedad);
				valor_salud := round((valor_salud - ((valor_novedad * item.porcentaje_salud) / 100)), 0);
			-- F I N  V A L O R  D E  S A L U D  E M P L E A D O
			
			-- V A L O R  D E  P E N S I O N  E M P L E A D O
				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_pension::integer[], 1)) = 2 then 
					valor_pension := round((valor_sueldo_periodo * item.porcentaje_pension) / 100, 0);
				else 
					if in_periodo = 2 then
						-- Cuando la pension solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_pension := round((((valor_dia * (30 - diferencia_dias)) * item.porcentaje_pension) / 100), 0);
						else 
							-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
							valor_pension := round((((valor_sueldo_periodo * 2) * item.porcentaje_pension) / 100), 0);
						end if;
					else 
						valor_pension := round((valor_sueldo_periodo * item.porcentaje_pension) / 100, 0);
					end if;
				end if;	
			
				-- Base de liquidacion de empleado
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte a pension (base_liquidacion_id = 5)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'tipo_novedad_id', tn.tipo_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleado) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 5 -- id base de liquidacion empleado (pension)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and case when (select array_length(forma_liquidacion_pension::integer[], 1)) = 2 then tn.periodo = in_periodo else true end; -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
			
				-- Se filtran las novedades que afecten pension y sean de tipo devengado para SUMAR al valor del pension exceptuando las licencias no remuneradas que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_pension := round((valor_pension + ((valor_novedad * item.porcentaje_pension) / 100)), 0);
			
				-- Se filtran las novedades que afecten pension y sean licencias no remuneradas para restar al valor de pension
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_pension := round((valor_pension - ((valor_novedad * item.porcentaje_pension) / 100)), 0);
			
				-- Se filtran las novedades que afecten pension y sean de tipo devengado para RESTAR al valor del pension
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
				
				valor_pension := round((valor_pension - ((valor_novedad * item.porcentaje_pension) / 100)), 0);
				-- Fin Base de liquidacion de empleado
			-- F I N  V A L O R  D E  P E N S I O N  E M P L E A D O
			
			-- F I N V A L O R E S  Q U E  C O R R E S P O N D E N  A L  E M P L E A D O
			
			-- Nelson Lugo - Bita: 51246 - Se solicito que se el valor de salud y pensión se redondeara al 100 siguiente es decir de $30.740 a $30.800 
			valor_salud := (select ceil(valor_salud::numeric / 100) * 100);
			valor_pension := (select ceil(valor_pension::numeric / 100) * 100);
		
			-- Si el tipo de contrato es SENA etapa electiva, no se le descuenta salud y pension al empleado, el empleador asume la totalidad
			if item.tipo_contrato_id = 5 then
				valor_salud := 0;
				valor_pension := 0;
				
				-- Nelson Lugo 14/04/2025 Bita #66626 - Si el parametro de porc_salud_sena_empleador es > 0, se tiene encuenta el valor de este parametro, si no se suman el porc_salud_empleador + item.porcentaje_salud
				if porc_salud_sena_empleador > 0 then
					porc_salud_empleador = porc_salud_sena_empleador;
				else 
					porc_salud_empleador := (porc_salud_empleador + item.porcentaje_salud);
				end if;
				
				porc_pension_empleador := (porc_pension_empleador + item.porcentaje_pension);
			end if;
			
			valor_devengados := (valor_salario_trabajado + valor_aux_transporte + valor_total_ausentismos_por_periodo + valor_total_novedades_devengado - valor_total_licencias_no_remuneradas_especiales);
			valor_deducidos := valor_total_novedades_deducido;
		
		
			-- V A L O R E S  Q U E  C O R R E S P O N D E N  A L  P A T R O N O
			
			-- V A L O R  D E  S A L U D  P A T R O N O
				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				-- Si el tipo de contrato es SENA etapa productiva, no se le descuenta salud y pension al empleado, el empleador asume la totalidad
				if (select array_length(forma_liquidacion_salud::integer[], 1)) = 2 then 
					valor_salud_empleador := round(((valor_sueldo_periodo * porc_salud_empleador) / 100), 0);
				else 
					if in_periodo = 2 then
						-- Cuando la salud solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_salud_empleador := round((((valor_dia * (30 - diferencia_dias)) * porc_salud_empleador) / 100), 0);
						else 
							-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
							valor_salud_empleador := round((((valor_sueldo_periodo * 2) * porc_salud_empleador) / 100), 0);
						end if;
					else
						valor_salud_empleador := round(((valor_sueldo_periodo * porc_salud_empleador) / 100), 0);
					end if;
				end if;
				
				-- Base de liquidacion de empleador
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte a salud (base_liquidacion_id = 15)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'tipo_novedad_id', tn.tipo_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleador) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 15 -- id base de liquidacion empleador (salud)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and case when (select array_length(forma_liquidacion_salud::integer[], 1)) = 2 then tn.periodo = in_periodo else true end; -- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				
				-- Se filtran las novedades que afecten salud y sean de tipo devengado para SUMAR al valor del salud exceptuando las licencias no remuneradas que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_salud_empleador := round((valor_salud_empleador + ((valor_novedad * porc_salud_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten salud y sean licencias no remuneradas para restar al valor de pension
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_salud_empleador := round((valor_salud_empleador - ((valor_novedad * porc_salud_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten salud y sean de tipo devengado para RESTAR al valor del salud
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
				
				valor_salud_empleador := round((valor_salud_empleador - ((valor_novedad * porc_salud_empleador) / 100)), 0);
				-- Fin Base de liquidacion de empleador
			-- F I N  V A L O R  D E  S A L U D  P A T R O N O
			
			-- V A L O R  D E  P E N S I O N  P A T R O N O
				-- Esta validacion de realiza para validar si esta novedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_pension::integer[], 1)) = 2 then
					-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la pension el empleador debe ser por el salario minimo
					if item.contrato_medio_tiempo is true then
						-- El valor del salario minimo se divide en 2, porque el pago del aporte a pension esta que se liquida en cada quincena, no en una sola o mensual
						valor_pension_empleador := round(((salario_minimo / 2) * porc_pension_empleador) / 100, 0);
					else 
						valor_pension_empleador := round((valor_sueldo_periodo * porc_pension_empleador) / 100, 0);
					end if;
				else 
					if in_periodo = 2 then
						-- Cuando la pension solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_pension_empleador := round((((valor_dia * (30 - diferencia_dias)) * porc_pension_empleador) / 100), 0);
						else 
							-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la pension el empleador debe ser por el salario minimo
							if item.contrato_medio_tiempo is true then
								valor_pension_empleador := round((salario_minimo * porc_pension_empleador) / 100, 0);
							else 
								-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
								valor_pension_empleador := round((((valor_sueldo_periodo * 2) * porc_pension_empleador) / 100), 0);
							end if;
						end if;
					elsif in_periodo = 1 then
						-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la pension el empleador debe ser por el salario minimo
						if item.contrato_medio_tiempo is true then
							-- El valor del salario minimo se divide en 2, porque el pago del aporte a pension esta que se liquida en cada quincena, no en una sola o mensual
							valor_pension_empleador := round(((salario_minimo / 2) * porc_pension_empleador) / 100, 0);
						else 
							valor_pension_empleador := round((valor_sueldo_periodo * porc_pension_empleador) / 100, 0);
						end if;
					else 
						-- in_periodo = 3: Mensualidad
						-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la pension el empleador debe ser por el salario minimo
						if item.contrato_medio_tiempo is true then
							valor_pension_empleador := round((salario_minimo * porc_pension_empleador) / 100, 0);
						else 
							valor_pension_empleador := round((valor_sueldo_periodo * porc_pension_empleador) / 100, 0);
						end if;
					end if;
				end if;
			
				-- Base de liquidacion de empleador
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte a pension (base_liquidacion_id = 10)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'tipo_novedad_id', tn.tipo_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleador) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 10 -- id base de liquidacion empleador (pension)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and case when (select array_length(forma_liquidacion_pension::integer[], 1)) = 2 then tn.periodo = in_periodo else true end; -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
			
				-- Se filtran las novedades que afecten pension y sean de tipo devengado para SUMAR al valor del pension exceptuando las licencias no remuneradas que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_pension_empleador := round((valor_pension_empleador + ((valor_novedad * porc_pension_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten pension y sean licencias no remuneradas para restar al valor de pension
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_pension_empleador := round((valor_pension_empleador - ((valor_novedad * porc_pension_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten pension y sean de tipo devengado para RESTAR al valor del pension
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
				
				valor_pension_empleador := round((valor_pension_empleador - ((valor_novedad * porc_pension_empleador) / 100)), 0);
				-- Fin Base de liquidacion de empleador
			-- F I N  V A L O R  D E  P E N S I O N  P A T R O N O
			
			-- V A L O R  D E  A R L  P A T R O N O
				select coalesce(sum(tn.dias), 0) into valor_novedad
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleador) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 9 -- id base de liquidacion empleador (ARL)
				)
				and tn.tipo_valor_novedad_id = 1 -- tipo_valor_novedad = dia
				and case when (select array_length(forma_liquidacion_aux_transporte::integer[], 1)) = 2 then tn.periodo = in_periodo else true end -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
				--and not tn.novedad_id = any(licencias_no_remuneradas)  -- Licencias no remuneradas (exceptuando)
				and ausentismo is true;

				valor_novedad := round((((valor_dia * valor_novedad) * item.porcentaje_arl) / 100), 0);

				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_arl::integer[], 1)) = 2 then 
					-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la arl el empleador debe ser por el salario minimo
					if item.contrato_medio_tiempo is true then
						-- El valor del salario minimo se divide en 2, porque el pago del aporte a arl esta que se liquida en cada quincena, no en una sola o mensual
						valor_arl := round(((salario_minimo / 2) * item.porcentaje_arl) / 100, 0);
					else 
						valor_arl := round((valor_sueldo_periodo * item.porcentaje_arl) / 100, 0);
					end if;
				else 
					if in_periodo = 2 then
						-- Cuando la ARL solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_arl := round((((valor_dia * (30 - diferencia_dias)) * item.porcentaje_arl) / 100), 0) - valor_novedad;
						else 
							-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la arl el empleador debe ser por el salario minimo
							if item.contrato_medio_tiempo is true then
								-- El valor del salario minimo se divide en 2, porque el pago del aporte a arl esta que se liquida en cada quincena, no en una sola o mensual
								valor_arl := round((salario_minimo * item.porcentaje_arl) / 100, 0) - valor_novedad;
							else 
								-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
								valor_arl := round((((valor_sueldo_periodo * 2) * item.porcentaje_arl) / 100), 0) - valor_novedad;
							end if;
						end if;
					elsif in_periodo = 1 then
						-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la arl el empleador debe ser por el salario minimo
						if item.contrato_medio_tiempo is true then
							-- El valor del salario minimo se divide en 2, porque el pago del aporte a arl esta que se liquida en cada quincena, no en una sola o mensual
							valor_arl := round(((salario_minimo / 2) * item.porcentaje_arl) / 100, 0) - valor_novedad;
						else 
							valor_arl := round((valor_sueldo_periodo * item.porcentaje_arl) / 100, 0) - valor_novedad;
						end if;
					else 
						-- in_periodo = 3: Mensualidad
						-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la arl el empleador debe ser por el salario minimo
						if item.contrato_medio_tiempo is true then
							valor_arl := round((salario_minimo * item.porcentaje_arl) / 100, 0) - valor_novedad;
						else 
							valor_arl := round((valor_sueldo_periodo * item.porcentaje_arl) / 100, 0) - valor_novedad;
						end if;
					end if;
				end if;
			
				-- Base de liquidacion de empleador
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte a ARL (base_liquidacion_id = 9)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'tipo_novedad_id', tn.tipo_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleador) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 9 -- id base de liquidacion empleador (ARL)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and case when (select array_length(forma_liquidacion_arl::integer[], 1)) = 2 then tn.periodo = in_periodo else true end; -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
			
				-- Se filtran las novedades que afecten ARL y sean de tipo devengado para SUMAR al valor del ARL exceptuando las licencias no remuneradas que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_arl := round((valor_arl + ((valor_novedad * item.porcentaje_arl) / 100)), 0);
			
				-- Se filtran las novedades que afecten ARL y sean licencias no remuneradas para restar al valor de ARL
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_arl := round((valor_arl - ((valor_novedad * item.porcentaje_arl) / 100)), 0);
			
				-- Se filtran las novedades que afecten ARL y sean de tipo devengado para RESTAR al valor del ARL
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
				
				valor_arl := round((valor_arl - ((valor_novedad * item.porcentaje_arl) / 100)), 0);
				-- Fin Base de liquidacion de empleador
			
				-- Se filtran las novedades de tipo licencia no remunerada para restar esos dias a la ARL del empleador ya que no los laboró
				/*select 
					coalesce(sum(tn.dias), 0) into valor_novedad
				from temp_novedades tn
				where tn.novedad_id = 4; -- novedad_id = 4 Licencia no remunerada
				
				valor_novedad := (valor_dia * valor_novedad);
				valor_arl := round((valor_arl - ((valor_novedad * item.porcentaje_arl) / 100)), 0); */
				
				-- Nelson Lugo - Bita: 51246 - Contrato SENA etapa lectiva no se aporta ARL
				if item.tipo_contrato_id = 5 then
					valor_arl := 0;
				end if;
			-- F I N  V A L O R  D E  A R L  P A T R O N O

			-- V A L O R  D E  C E S A N T I A S  P A T R O N O
				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_cesantias::integer[], 1)) = 2 then 
					valor_cesantias := round(((valor_sueldo_periodo + valor_aux_transporte) * porc_cesantias_empleador) / 100, 0);
				else 
					if in_periodo = 2 then
						-- Cuando las cesantias solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_cesantias := round(((((valor_dia * (30 - diferencia_dias)) + valor_aux_transporte) * porc_cesantias_empleador) / 100), 0);
						else 
							-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
							valor_cesantias := round(((((valor_sueldo_periodo * 2) + valor_aux_transporte) * porc_cesantias_empleador) / 100), 0);
						end if;
					else
						valor_cesantias := round(((valor_sueldo_periodo + valor_aux_transporte) * porc_cesantias_empleador) / 100, 0);
					end if;
				end if;
			
				-- Base de liquidacion de empleador
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte a cesantias (base_liquidacion_id = 11)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'tipo_novedad_id', tn.tipo_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleador) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 11 -- id base de liquidacion empleador (Cesantias)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and case when (select array_length(forma_liquidacion_cesantias::integer[], 1)) = 2 then tn.periodo = in_periodo else true end; -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
			
				-- Se filtran las novedades que afecten cesantias y sean de tipo devengado para SUMAR al valor del cesantias exceptuando las licencias no remuneradas que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_cesantias := round((valor_cesantias + ((valor_novedad * porc_cesantias_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten cesantias y sean licencias no remuneradas para restar al valor de cesantias
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_cesantias := round((valor_cesantias - ((valor_novedad * porc_cesantias_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten cesantias y sean de tipo devengado para RESTAR al valor del cesantias
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
				
				valor_cesantias := round((valor_cesantias - ((valor_novedad * porc_cesantias_empleador) / 100)), 0);
				-- Fin Base de liquidacion de empleador
			-- F I N  V A L O R  D E  C E S A N T I A S  P A T R O N O
			
			-- V A L O R  D E  I N T E R E S E S  C E S A N T I A S  P A T R O N O
				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_int_cesantias::integer[], 1)) = 2 then 
					valor_int_cesantias := round(((valor_sueldo_periodo + valor_aux_transporte) * porc_int_cesantias_empleador) / 100, 0);
				else 
					if in_periodo = 2 then
						-- Cuando los int cesantias solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_int_cesantias := round(((((valor_dia * (30 - diferencia_dias)) + valor_aux_transporte) * porc_int_cesantias_empleador) / 100), 0);
						else 
							-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
							valor_int_cesantias := round(((((valor_sueldo_periodo * 2) + valor_aux_transporte) * porc_int_cesantias_empleador) / 100), 0);
						end if;
					else
						valor_int_cesantias := round(((valor_sueldo_periodo + valor_aux_transporte) * porc_int_cesantias_empleador) / 100, 0);
					end if;
				end if;
			
				-- Base de liquidacion de empleador
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte a int cesantias (base_liquidacion_id = 12)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'tipo_novedad_id', tn.tipo_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleador) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 12 -- id base de liquidacion empleador (Int Cesantias)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and case when (select array_length(forma_liquidacion_int_cesantias::integer[], 1)) = 2 then tn.periodo = in_periodo else true end; -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
			
				-- Se filtran las novedades que afecten int cesantias y sean de tipo devengado para SUMAR al valor del int cesantias exceptuando las licencias no remuneradas que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_int_cesantias := round((valor_int_cesantias + ((valor_novedad * porc_int_cesantias_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten int cesantias y sean licencias no remuneradas para restar al valor de int cesantias
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_int_cesantias := round((valor_int_cesantias - ((valor_novedad * porc_int_cesantias_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten int cesantias y sean de tipo devengado para RESTAR al valor del int cesantias
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
				
				valor_int_cesantias := round((valor_int_cesantias - ((valor_novedad * porc_int_cesantias_empleador) / 100)), 0);
				-- Fin Base de liquidacion de empleador
			-- F I N  V A L O R  D E  I N T E R E S E S  C E S A N T I A S  P A T R O N O
			
			-- V A L O R  D E  P R I M A  P A T R O N O
				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_primas::integer[], 1)) = 2 then 
					valor_primas := round(((valor_sueldo_periodo + valor_aux_transporte) * porc_primas_empleador) / 100, 0);
				else 
					if in_periodo = 2 then
						-- Cuando la prima solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_primas := round(((((valor_dia * (30 - diferencia_dias)) + valor_aux_transporte) * porc_primas_empleador) / 100), 0);
						else 
							-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
							valor_primas := round(((((valor_sueldo_periodo * 2) + valor_aux_transporte) * porc_primas_empleador) / 100), 0);
						end if;
					else
						valor_primas := round(((valor_sueldo_periodo + valor_aux_transporte) * porc_primas_empleador) / 100, 0);
					end if;
				end if;
			
				-- Base de liquidacion de empleador
				-- Se consultan las novedades donde la base de liquidacion de empleador afecte a primas (base_liquidacion_id = 13)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'tipo_novedad_id', tn.tipo_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleador) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 13 -- id base de liquidacion empleador (primas)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and case when (select array_length(forma_liquidacion_primas::integer[], 1)) = 2 then tn.periodo = in_periodo else true end; -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
			
				-- Se filtran las novedades que afecten primas y sean de tipo devengado para SUMAR al valor del primas exceptuando las licencias no remuneradas que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_primas := round((valor_primas + ((valor_novedad * porc_primas_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten primas y sean licencias no remuneradas para restar al valor de primas
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_primas := round((valor_primas - ((valor_novedad * porc_primas_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten primas y sean de tipo devengado para RESTAR al valor del primas
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
				
				valor_primas := round((valor_primas - ((valor_novedad * porc_primas_empleador) / 100)), 0);
				-- Fin Base de liquidacion de empleador
			-- F I N  V A L O R  D E  P R I M A  P A T R O N O
			
			-- V A L O R  D E  C A J A  D E  C O M P E N S A C I O N  P A T R O N O
				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_caja_compensacion::integer[], 1)) = 2 then 
					-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la caja de compensacion el empleador debe ser por el salario minimo
					if item.contrato_medio_tiempo is true then
						-- El valor del salario minimo se divide en 2, porque el pago del aporte a caja de compensacion esta que se liquida en cada quincena, no en una sola o mensual
						valor_caja_compensacion := round(((salario_minimo / 2) * porc_caja_compen_empleador) / 100, 0);
					else 
						valor_caja_compensacion := round((valor_sueldo_periodo * porc_caja_compen_empleador) / 100, 0);
					end if;
				else 
					if in_periodo = 2 then
						-- Cuando la caja de compensacion solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_caja_compensacion := round((((valor_dia * (30 - diferencia_dias)) * porc_caja_compen_empleador) / 100), 0);
						else 
							-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la caja de compensacion el empleador debe ser por el salario minimo
							if item.contrato_medio_tiempo is true then
								valor_caja_compensacion := round((salario_minimo * porc_caja_compen_empleador) / 100, 0);
							else 
								-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
								valor_caja_compensacion := round((((valor_sueldo_periodo * 2) * porc_caja_compen_empleador) / 100), 0);
							end if;
						end if;
					elsif in_periodo = 1 then
						-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la caja de compensacion el empleador debe ser por el salario minimo
						if item.contrato_medio_tiempo is true then
							-- El valor del salario minimo se divide en 2, porque el pago del aporte a caja de compensacion esta que se liquida en cada quincena, no en una sola o mensual
							valor_caja_compensacion := round(((salario_minimo / 2) * porc_caja_compen_empleador) / 100, 0);
						else 
							valor_caja_compensacion := round((valor_sueldo_periodo * porc_caja_compen_empleador) / 100, 0);
						end if;
					else
						-- in_periodo = 3: Mensualidad
						-- Nelson Lugo - 16/04/2026 - Caso #77077 - Si el contrato del empleado es medio tiempo,el calculo del valor de la caja de compensacion el empleador debe ser por el salario minimo
						if item.contrato_medio_tiempo is true then
							valor_caja_compensacion := round((salario_minimo * porc_caja_compen_empleador) / 100, 0);
						else 
							valor_caja_compensacion := round((valor_sueldo_periodo * porc_caja_compen_empleador) / 100, 0);
						end if;
					end if;
				end if;

				-- Base de liquidacion de empleador
				-- Se consultan las novedades donde la base de liquidacion de empleado afecte a primas (base_liquidacion_id = 13)
				select json_agg(json_build_object(
					'id', tn.id,
					'valor', tn.valor,
					'tipo_novedad_id', tn.tipo_novedad_id
				)) into novedades 
				from temp_novedades tn
				where exists (
				    select 1
				    from json_array_elements(tn.base_liquidacion_empleador) as obj
				    where (cast(obj->>'base_liquidacion_id'::varchar as integer)) = 16 -- id base de liquidacion empleador (caja de compensacion)
				)
				and tn.tipo_valor_novedad_id <> 1 -- tipo_valor_novedad = Horas, Valor
				and case when (select array_length(forma_liquidacion_caja_compensacion::integer[], 1)) = 2 then tn.periodo = in_periodo else true end; -- Se valida si la novedad se liquida se liquida en las 2 quincenas, si es asi aplica el filtro del periodo
			
				-- Se filtran las novedades que afecten caja de compensacion y sean de tipo devengado para SUMAR al valor de la caja de compensacion exceptuando las licencias no remuneradas que al ser devengado restan
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and not cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_caja_compensacion := round((valor_caja_compensacion + ((valor_novedad * porc_caja_compen_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten caja de compensacion y sean licencias no remuneradas para restar al valor de primas
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 3 -- tipo_novedad_id = 3 (Devengado)
				and cast(obj->>'id'::varchar as integer) = any(licencias_no_remuneradas); -- Licencias no remuneradas
				
				valor_caja_compensacion := round((valor_caja_compensacion - ((valor_novedad * porc_caja_compen_empleador) / 100)), 0);
			
				-- Se filtran las novedades que afecten a caja de compensacion y sean de tipo deducido para RESTAR al valor de caja de compensacion
				select 
					coalesce(sum(cast(obj->>'valor'::varchar as numeric)), 0) into valor_novedad
				from json_array_elements(novedades) as obj 
				where cast(obj->>'tipo_novedad_id'::varchar as integer) = 2; -- tipo_novedad_id = 2 (Deducido)
				
				valor_caja_compensacion := round((valor_caja_compensacion + ((valor_novedad * porc_caja_compen_empleador) / 100)), 0);
			
			-- F I N  V A L O R  D E  C A J A  D E  C O M P E N S A C I O N  P A T R O N O
			
			-- V A L O R  D E  V A C A C I O N E S  P A T R O N O
				-- Esta validacion de realiza para validar si esta noovedad esta solo para liquidar en la quincena 2.
				if (select array_length(forma_liquidacion_vacaciones::integer[], 1)) = 2 then 
					valor_vacaciones := round(((valor_sueldo_periodo) * porc_vacaciones_empleador) / 100, 0);
				else 
					if in_periodo = 2 then
						-- Cuando las vacaciones solo se liquida en la quincena 2, tiene un trato especial
						-- Nelson Lugo - 28/02/2025 - Si diferencia_dias es > 0, es el total de dias que no trabajo porque ingreso o se retiro en el mes y año que se esta liquidando
						-- Ejem: Ingreso 06 entonces 6 - 1 = 5 Dias que no trabajo ó Se retiro el 26 entonces 30 - 26 = 4 Dias que no trabajo
						-- Este se usa para las novedades que solo se liquidan en la quincena 2.
						if diferencia_dias > 0 then
							valor_vacaciones := round((((valor_dia * (30 - diferencia_dias)) * porc_vacaciones_empleador) / 100), 0);
						else 
							-- Se multiplieca el valor_sueldo_periodo x 2 ya que se necesita el valor completo del mes y aca solo estaria el de una quincena
							valor_vacaciones := round((((valor_sueldo_periodo * 2) * porc_vacaciones_empleador) / 100), 0);
						end if;
					else
						valor_vacaciones := round(((valor_sueldo_periodo) * porc_vacaciones_empleador) / 100, 0);
					end if;
				end if;
			-- F I N  V A L O R  D E  V A C A C I O N E S  P A T R O N O

			-- Nelson Lugo - Bita: 65834 - Se solicito que todos los valores de prestaciones se redondeara al 100 siguiente es decir de $30.740 a $30.800 
			valor_salud_empleador := ceil(round(valor_salud_empleador::numeric / 100.0, 2)) * 100;
			valor_pension_empleador := ceil(round(valor_pension_empleador::numeric / 100.0, 2)) * 100;
			valor_arl := ceil(round(valor_arl::numeric / 100.0, 2)) * 100;
			valor_cesantias := ceil(round(valor_cesantias::numeric / 100.0, 2)) * 100;
			valor_int_cesantias := ceil(round(valor_int_cesantias::numeric / 100.0, 2)) * 100;
			valor_primas := ceil(round(valor_primas::numeric / 100.0, 2)) * 100;
			valor_vacaciones := ceil(round(valor_vacaciones::numeric / 100.0, 2)) * 100;
			valor_caja_compensacion := ceil(round(valor_caja_compensacion::numeric / 100.0, 2)) * 100;

			
			-- V A L I D A C I O N  P A R A  S A B E R  S I  L O S  V A L O R E S  N O  S E  L I Q U I D A N  E N  E L  P E R I O D O  C O N S U L T A D O
				-- Aux Transporte: Se valida si el periodo consultado no es el mismo de la forma de liquidacion entonces el valor es de cero
				if (select count(*) from nomina_periodo np where id = any(forma_liquidacion_aux_transporte)) = 1 then
					if ((select np.id  from nomina_periodo np where id = any(forma_liquidacion_aux_transporte)) = 1 and in_periodo = 2)  
						or 
						((select np.id  from nomina_periodo np where id = any(forma_liquidacion_aux_transporte)) = 2 and in_periodo = 1)
					then
						valor_devengados = valor_devengados - valor_aux_transporte;
						valor_aux_transporte := 0;
					end if;
				end if;
			
				-- Nelson Lugo - 28/02/2025 - Se valida si el valor salud es menor al valor salud del salario minimo, entonces se deja el valor de salud del salario minimo
				-- ya que por ley el valor de salud no puede ser menor al del salario minimo
				if diferencia_dias = 0 then
					if valor_salud < round(((salario_minimo * item.porcentaje_salud) / 100), 0) then
						valor_salud := (select ceil(round(((salario_minimo * item.porcentaje_salud) / 100), 0) / 100) * 100);
					end if;
				end if;

				if valor_salud_empleador < round(((salario_minimo * porc_salud_empleador) / 100), 0) then
					valor_salud_empleador := (select ceil(round(((salario_minimo * porc_salud_empleador) / 100), 0) / 100) * 100);
				end if;
				
				-- Salud: Se valida si el periodo consultado no es el mismo de la forma de liquidacion entonces el valor es de cero
				if (select count(*) from nomina_periodo np where id = any(forma_liquidacion_salud)) = 1 then
					if ((select np.id  from nomina_periodo np where id = any(forma_liquidacion_salud)) = 1 and in_periodo = 2)  
						or 
						((select np.id  from nomina_periodo np where id = any(forma_liquidacion_salud)) = 2 and in_periodo = 1)
					then
						valor_salud := 0;
						valor_salud_empleador := 0;
					else 
						valor_deducidos := (valor_deducidos + valor_salud);
					end if;
				end if;
			
				-- Nelson Lugo - 28/02/2025 - Se valida si el valor pension es menor al valor pension del salario minimo, entonces se deja el valor de pension del salario minimo
				-- ya que por ley el valor de pension no puede ser menor al del salario minimo
				if diferencia_dias = 0 then
					if valor_pension < round(((salario_minimo * item.porcentaje_pension) / 100), 0) then
						valor_pension := (select ceil(round(((salario_minimo * item.porcentaje_pension) / 100), 0) / 100) * 100);
					end if;
				end if;
				-- Pension: Se valida si el periodo consultado no es el mismo de la forma de liquidacion entonces el valor es de cero
				if (select count(*) from nomina_periodo np where id = any(forma_liquidacion_pension)) = 1 then
					if ((select np.id from nomina_periodo np where id = any(forma_liquidacion_pension)) = 1 and in_periodo = 2)  
						or 
						((select np.id from nomina_periodo np where id = any(forma_liquidacion_pension)) = 2 and in_periodo = 1)
					then
						valor_pension := 0;
						valor_pension_empleador := 0;
					else 
						valor_deducidos := (valor_deducidos + valor_pension);
					end if;
				end if;
				
				-- ARL: Se valida si el periodo consultado no es el mismo de la forma de liquidacion entonces el valor es de cero
				if (select count(*) from nomina_periodo np where id = any(forma_liquidacion_arl)) = 1 then
					if ((select np.id from nomina_periodo np where id = any(forma_liquidacion_arl)) = 1 and in_periodo = 2)  
						or 
						((select np.id from nomina_periodo np where id = any(forma_liquidacion_arl)) = 2 and in_periodo = 1)
					then
						valor_arl := 0;
					end if;
				end if;
			
				-- Cesantias: Se valida si el periodo consultado no es el mismo de la forma de liquidacion entonces el valor es de cero
				if (select count(*)  from nomina_periodo np where id = any(forma_liquidacion_cesantias)) = 1 then
					if ((select np.id  from nomina_periodo np where id = any(forma_liquidacion_cesantias)) = 1 and in_periodo = 2)  
						or 
						((select np.id  from nomina_periodo np where id = any(forma_liquidacion_cesantias)) = 2 and in_periodo = 1)
					then
						valor_cesantias := 0;
					end if;
				end if;
			
				-- Intereses de Cesantias: Se valida si el periodo consultado no es el mismo de la forma de liquidacion entonces el valor es de cero
				if (select count(*)  from nomina_periodo np where id = any(forma_liquidacion_int_cesantias)) = 1 then
					if ((select np.id  from nomina_periodo np where id = any(forma_liquidacion_int_cesantias)) = 1 and in_periodo = 2)  
						or 
						((select np.id  from nomina_periodo np where id = any(forma_liquidacion_int_cesantias)) = 2 and in_periodo = 1)
					then
						valor_int_cesantias := 0;
					end if;
				end if;
			
				-- Prima: de Cesantias: Se valida si el periodo consultado no es el mismo de la forma de liquidacion entonces el valor es de cero
				if (select count(*)  from nomina_periodo np where id = any(forma_liquidacion_primas)) = 1 then
					if ((select np.id  from nomina_periodo np where id = any(forma_liquidacion_primas)) = 1 and in_periodo = 2)  
						or 
						((select np.id  from nomina_periodo np where id = any(forma_liquidacion_primas)) = 2 and in_periodo = 1)
					then
						valor_primas := 0;
					end if;
				end if;
			
				-- Caja de compensacion: Se valida si el periodo consultado no es el mismo de la forma de liquidacion entonces el valor es de cero
				if (select count(*)  from nomina_periodo np where id = any(forma_liquidacion_caja_compensacion)) = 1 then
					if ((select np.id  from nomina_periodo np where id = any(forma_liquidacion_caja_compensacion)) = 1 and in_periodo = 2)  
						or 
						((select np.id  from nomina_periodo np where id = any(forma_liquidacion_caja_compensacion)) = 2 and in_periodo = 1)
					then
						valor_caja_compensacion := 0;
					end if;
				end if;
				
				-- Vacaciones: de Cesantias: Se valida si el periodo consultado no es el mismo de la forma de liquidacion entonces el valor es de cero
				if (select count(*)  from nomina_periodo np where id = any(forma_liquidacion_vacaciones)) = 1 then
					if ((select np.id  from nomina_periodo np where id = any(forma_liquidacion_vacaciones)) = 1 and in_periodo = 2)  
						or 
						((select np.id  from nomina_periodo np where id = any(forma_liquidacion_vacaciones)) = 2 and in_periodo = 1)
					then
						valor_vacaciones := 0;
					end if;
				end if;

			-- Nelson Lugo 07/04/2025 Bita #66453 - Si el contrato es SENA etapa electiva, la empresa no asume los valores de prima de servicios, cesantías, int cesantías, vacaciones, pensión y caja de compensación.
			if item.tipo_contrato_id in (5) then
			    valor_pension_empleador := 0;
				valor_cesantias := 0;
				valor_int_cesantias := 0;
				valor_primas := 0;
				valor_caja_compensacion := 0;
				valor_vacaciones := 0;
			end if;

			-- F I N  V A L I D A C I O N  P A R A  S A B E R  S I  L O S  V A L O R E S  N O  S E  L I Q U I D A N  E N  E L  P E R I O D O  C O N S U L T A D O
			raise notice 'enrtra--- %', item.id;
			insert into temp_resultado (
				id,
				documento,
				nombre,
				persona_id,
				cargo,
				dias,
				empleado,
				empleador,
				centro_costo,
				fecha_ini_contrato,
				fecha_fin_contrato,
				aux_trans,
				tipo_contrato,
				tipo_contrato_nombre,
				subtipo_trabajador
			) values (
				item.id,
				(select tp.documento from personas_persona tp where tp.id = item.persona_id),
				(select tp.n_completo from personas_persona tp where tp.id = item.persona_id),
				item.persona_id,
				(select nc.nombre from nomina_cargo nc where nc.id = item.cargo_id),
				dias_trabajados,
				(select json_build_object( -- empleado
					'sueldo', (select json_build_object( -- Novedad sueldo
						'id', item.persona_id, -- id del empleado
						'valor', valor_salario_trabajado,
						'cta_debito_id', (select nvc.mayor_cta_debito_id from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'sueldo') limit 1),
						'cta_credito_id', (select nvc.mayor_cta_credito_id  from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'sueldo') limit 1),
						'detalle', (
							-- Si el tipo de contrato es SENA etapa electiva se cambia el detalle de sueldo a Apoyo y sostenimiento
							case when item.tipo_contrato_id = 5 then 
								'Apoyo y sostenimiento'
							else
								(select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'sueldo') limit 1)	
							end
						),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'sueldo')
					)),
					'aux_transporte', (select json_build_object( -- Novedad aux_transporte
						'id', item.persona_id, -- id del empleado
						'valor', valor_aux_transporte,
						'cta_debito_id', (select nvc.mayor_cta_debito_id from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'aux_transporte') limit 1),
						'cta_credito_id', (select nvc.mayor_cta_credito_id  from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'aux_transporte') limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'aux_transporte') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'aux_transporte'),
						'valor_total', aux_transporte
					)),
					'salud', (select json_build_object( -- Entidad salud
						'id', (select ne.personas_id from nomina_entidades ne where ne.id = item.entidad_salud_id),
						'valor', valor_salud,
						'cta_debito_id', (select nec.mayor_cta_debito_id from nomina_entidadescentrocostos nec where nec.entidad_id = item.entidad_salud_id and nec.centro_costos_id = item.centro_costo_id and nec.eliminado is false limit 1),
						'cta_credito_id', (select nec.mayor_cta_credito_id from nomina_entidadescentrocostos nec where nec.entidad_id = item.entidad_salud_id and nec.centro_costos_id = item.centro_costo_id and nec.eliminado is false limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'salud') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'salud')
					)),
					'pension', (select json_build_object( -- Entidad pension
						'id', (select ne.personas_id from nomina_entidades ne where ne.id = item.entidad_pension_id), -- Id Persona
						-- Si el empleado ya es pensionado, no se le genera cargo de pesion al empleador y empleador (01 - Dependiente pensionado por vejez activo)
						'valor', (case when item.subtipo_trabajador = '01' then 0 else valor_pension end),
						'cta_debito_id', (select nec.mayor_cta_debito_id from nomina_entidadescentrocostos nec where nec.entidad_id = item.entidad_pension_id and nec.centro_costos_id = item.centro_costo_id and nec.eliminado is false limit 1),
						'cta_credito_id', (select nec.mayor_cta_credito_id from nomina_entidadescentrocostos nec where nec.entidad_id = item.entidad_pension_id and nec.centro_costos_id = item.centro_costo_id and nec.eliminado is false limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'pension') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'pension')
					)),
					'novedades', (
						select coalesce(json_agg(json_build_object( -- Novedades
							'id', tn.id,
							'persona_id', tn.persona_id,
							'valor', tn.valor,
							'cta_debito_id', tn.cta_debito_id,
							'cta_credito_id', tn.cta_credito_id,
							'detalle', tn.detalle,
							'novedad_id', tn.novedad_id,
							'tipo_novedad', tn.tipo_novedad_id,
							'fecha_inicial', tn.fecha_inicial,
							'fecha_final', tn.fecha_final,
							'dias', tn.dias,
							'vacaciones', tn.vacaciones,
							'vacaciones_liquidadas', tn.vacaciones_liquidadas
						)), '[]') from temp_novedades tn where tn.periodo = in_periodo
					),
					'total_devengado', valor_devengados,
					'total_deducido', valor_deducidos,
					'neto', (valor_devengados - valor_deducidos),
					'salario', item.sueldo
				)),
				(select json_build_object( -- empleador
					'salud', (select json_build_object( -- Novedad salud
						'id', (select ne.personas_id from nomina_entidades ne where ne.id = item.entidad_salud_id), -- Id Persona entidad
						'valor', valor_salud_empleador,
						'dias', dias_periodo,
						'cta_debito_id', (select nvc.mayor_cta_debito_id from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'salud') limit 1),
						'cta_credito_id', (select nvc.mayor_cta_credito_id  from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'salud') limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'salud') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'salud')
					)),
					'pension', (select json_build_object( -- Novedad pension
						'id', (select ne.personas_id from nomina_entidades ne where ne.id = item.entidad_pension_id), -- Id Persona entidad
						-- Si el empleado ya es pensionado, no se le genera cargo de pesion al empleador y empleador (01 - Dependiente pensionado por vejez activo)
						'valor', (case when item.subtipo_trabajador = '01' then 0 else valor_pension_empleador end),
						'dias', dias_periodo,
						'cta_debito_id', (select nvc.mayor_cta_debito_id from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'pension') limit 1),
						'cta_credito_id', (select nvc.mayor_cta_credito_id  from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'pension') limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'pension') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'pension')
					)),
					'cesantias', (select json_build_object( -- Novedad cesantias
						'id', item.persona_id, -- id del empleado
						'valor', valor_cesantias,
						'dias', dias_periodo,
						'cta_debito_id', (select nvc.mayor_cta_debito_id from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'cesantias') limit 1),
						'cta_credito_id', (select nvc.mayor_cta_credito_id  from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'cesantias') limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'cesantias') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'cesantias')
					)),
					'int_cesantias', (select json_build_object( -- Novedad int cesantias
						'id', item.persona_id, -- id del empleado
						'valor', valor_int_cesantias,
						'dias', dias_periodo,
						'cta_debito_id', (select nvc.mayor_cta_debito_id from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'int_cesantias') limit 1),
						'cta_credito_id', (select nvc.mayor_cta_credito_id  from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'int_cesantias') limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'int_cesantias') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'int_cesantias')
					)),
					'arl', (select json_build_object( -- Entidad ARL
						'id', (select ne.personas_id from nomina_entidades ne where ne.id = item.arl_id), -- Id Persona entidad
						'valor', valor_arl,
						'dias', dias_periodo,
						'cta_debito_id', (select nec.mayor_cta_debito_id from nomina_entidadescentrocostos nec where nec.entidad_id = item.arl_id and nec.centro_costos_id = item.centro_costo_id and nec.eliminado is false limit 1),
						'cta_credito_id', (select nec.mayor_cta_credito_id from nomina_entidadescentrocostos nec where nec.entidad_id = item.arl_id and nec.centro_costos_id = item.centro_costo_id and nec.eliminado is false limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'arl')),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'arl')
					)),
					'primas', (select json_build_object( -- Novedad primas
						'id', item.persona_id, -- id del empleado
						'valor', valor_primas,
						'dias', dias_periodo,
						'cta_debito_id', (select nvc.mayor_cta_debito_id from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'primas') limit 1),
						'cta_credito_id', (select nvc.mayor_cta_credito_id  from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'primas') limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'primas') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'primas')
					)),
					'vacaciones', (select json_build_object( -- Novedad vacaiones
						'id', item.persona_id, -- id del empleado
						'valor', valor_vacaciones,
						'dias', dias_periodo,
						'cta_debito_id', (select nvc.mayor_cta_debito_id from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'vacaciones') limit 1),
						'cta_credito_id', (select nvc.mayor_cta_credito_id  from nomina_novedadescentrocosto nvc where nvc.centro_costos_id = item.centro_costo_id and nvc.eliminado is false and nvc.novedades_id = (select np.valor::integer from nomina_parametros np where np.parametro = 'vacaciones') limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'vacaciones') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'vacaciones' limit 1)
					)),
					'sena', (select json_build_object( -- Entidad
						'id', null,
						'valor', 0,
						'dias', dias_periodo,
						'cta_debito_id', null,
						'cta_credito_id', null,
						'detalle', 'SENA'
					)),
					'icbf', (select json_build_object( -- Entidad
						'id', null,
						'valor', 0,
						'dias', dias_periodo,
						'cta_debito_id', null,
						'cta_credito_id', null,
						'detalle', 'ICBF'
					)),
					'caja_compensacion', (select json_build_object( -- Entidad
						'id', (select ne.personas_id from nomina_entidades ne where ne.id = item.caja_compensacion_id), -- Id Persona entidad
						'valor', valor_caja_compensacion,
						'dias', dias_periodo,
						'cta_debito_id', (select nec.mayor_cta_debito_id from nomina_entidadescentrocostos nec where nec.entidad_id = item.caja_compensacion_id and nec.centro_costos_id = item.centro_costo_id and nec.eliminado is false limit 1),
						'cta_credito_id', (select nec.mayor_cta_credito_id from nomina_entidadescentrocostos nec where nec.entidad_id = item.caja_compensacion_id and nec.centro_costos_id = item.centro_costo_id and nec.eliminado is false limit 1),
						'detalle', (select nn.nombre from nomina_novedades nn where nn.id = (select np.valor::integer from nomina_parametros np where np.parametro = 'caja_compensacion') limit 1),
						'novedad_id', (select np.valor::integer from nomina_parametros np where np.parametro = 'caja_compensacion')
					)),
					'total', (valor_devengados - valor_deducidos + valor_salud_empleador + valor_pension_empleador + valor_arl + valor_cesantias + valor_int_cesantias + valor_primas + valor_caja_compensacion + valor_vacaciones)
				)),
				(select json_build_object(
					'id', item.centro_costo_id,
					'nombre', (select ccc.nombre from contabilidad_centrocostos ccc where ccc.id = item.centro_costo_id)
				)), -- centro_costo
				item.fecha_ingreso,
				item.fecha_retiro,
				item.auxilio_transporte,
				item.tipo_contrato_id,
				(select nt.nombre from nomina_tipocontrato nt where nt.id = item.tipo_contrato_id),
				item.subtipo_trabajador
			);
		end if;
		truncate table temp_novedades;
	end loop;
	
	select coalesce(
	    json_agg(
	        json_build_object(
	            'id', tmp.id,
	            'documento', tmp.documento,
	            'nombre', upper(tmp.nombre),
	            'persona_id', tmp.persona_id,
	            'cargo', tmp.cargo,
	            'dias', tmp.dias,
	            'empleado', tmp.empleado,
	            'empleador', tmp.empleador,
	            'centro_costo', tmp.centro_costo,
	            'fecha_ini_contrato', to_char(tmp.fecha_ini_contrato, 'yyyy-mm-dd'),
	            'fecha_fin_contrato', to_char(tmp.fecha_fin_contrato, 'yyyy-mm-dd'),
	            'aux_trans', tmp.aux_trans,
	            'tipo_contrato', tmp.tipo_contrato,
	            'tipo_contrato_nombre', tmp.tipo_contrato_nombre,
	            'subtipo_trabajador', tmp.subtipo_trabajador,
	            'select', false,
	            'error', false
	        ) 
	        order by tmp.nombre
	    ), '[]') into resultado
	from temp_resultado tmp;

	drop table temp_resultado;
	drop table temp_novedades;
	
	return (select json_build_object(
		'por_liquidar', resultado,
		'liquidadas', (
			select coalesce(json_agg(json_build_object(
				'id', nl.id,
				'documento', tp.documento,
				'nombre', upper(tp.n_completo),
				'cargo', (select nc2.nombre from nomina_cargo nc2 where nc2.id = nc.cargo_id),
				'contrato', nl.contrato_id,
				'tipo_contrato', nc.tipo_contrato_id,
				'tipo_contrato_nombre', (select nt.nombre from nomina_tipocontrato nt where nt.id = nc.tipo_contrato_id),
				'fecha_ini_contrato', (select to_char(nc.fecha_ingreso, 'YYYY-MM-DD')),
				'fecha_fin_contrato', (select to_char(nc.fecha_retiro, 'YYYY-MM-DD')),
				'aux_trans', nc.auxilio_transporte,
				'sueldo', nc.sueldo,
				'correo', tp.email,
				'dias_laborados', nl.dias_laborados,
				'sueldo_trabajado', nl.sueldo_trabajado,
				'auxilio_transporte', nl.auxilio_transporte,
				'otros_devengados', nl.otros_devengados,
				'otros_deducidos', nl.otros_deducidos,
				'total', nl.total,
				'select', false,
				'salud', nl.salud,
				'pension', nl.pension,
				'total_devengados', (nl.sueldo_trabajado + nl.auxilio_transporte + nl.otros_devengados - (coalesce((
						select 
							sum(ndl.valor_empleado)
						from nomina_detalle_liquidaciones ndl 
						where ndl.liquidacion_id = nl.id
						and ndl.novedad_id = any(licencias_no_remuneradas)
					), 0))
				),
				'total_deducidos', (nl.salud + nl.pension + nl.otros_deducidos),
				'empleado', (
					select json_agg(json_build_object(
						'id', obj.id,
						'descripcion', obj.descripcion,
						'valor', obj.valor_empleado,
						'cantidad', obj.cantidad,
						'tipo_valor_novedad_id', obj.tipo_valor_novedad_id,
						'tipo_valor_novedad', obj.tipo_valor_novedad,
						'tipo_novedad', obj.tipo_novedad_id,
						'novedad_id', obj.novedad_id
					)) from (
						select
							ndl.id,
							ndl.descripcion,
							ndl.valor_empleado,
							ndl.cantidad,
							nn.tipo_valor_novedad_id,
							nt.nombre as tipo_valor_novedad,
							nn.tipo_novedad_id,
							ndl.novedad_id
						from nomina_detalle_liquidaciones ndl
						inner join nomina_novedades nn on nn.id = ndl.novedad_id
						inner join nomina_tipovalornovedad nt on nt.id = nn.tipo_valor_novedad_id
						where ndl.liquidacion_id = nl.id
						order by ndl.id asc
					) as obj
				),
				'empleador', (
					select coalesce(json_agg(json_build_object(
						'id', obj.id,
						'descripcion', obj.descripcion,
						'valor', obj.valor_patrono,
						'cantidad', obj.cantidad,
						'tipo_valor_novedad', obj.tipo_valor_novedad,
						'tipo_novedad', obj.tipo_novedad_id,
						'novedad_id', obj.novedad_id
					)), '[]'::json) from (
						select
							ndl.id,
							ndl.descripcion,
							ndl.valor_patrono,
							ndl.cantidad,
							nt.nombre as tipo_valor_novedad,
							nn.tipo_novedad_id,
							ndl.novedad_id
						from nomina_detalle_liquidaciones ndl
						inner join nomina_novedades nn on nn.id = ndl.novedad_id
						inner join nomina_tipovalornovedad nt on nt.id = nn.tipo_valor_novedad_id
						where ndl.liquidacion_id = nl.id
						and ndl.valor_patrono > 0
						order by ndl.id asc
					) as obj
				),
				'persona_id', nc.persona_id,
				'documento_id', nl.documento_id,
				'pago', nl.pago,
				--'transmitida', (case when (select count(*) from nomina_nominaelectronica nn where nn.contrato_id = nc.id and nn.anio_id = id_anio and nn.mes_id = id_mes) > 0 then true else false end),
				'estado', nl.estado,
				'fecha_anulacion', to_char(nl."delete", 'DD/MM/YYYY HH:MI AM'),
				'usuario_anulacion', (select concat(au.first_name, ' ', au.last_name) from accounts_usuario au where au.id = nl.um_id)
			) order by tp.n_completo), '[]')
			from nomina_liquidaciones nl 
			inner join nomina_contrato nc on nc.id = nl.contrato_id 
			inner join personas_persona tp on tp.id = nc.persona_id 
			and nl.periodo_id = in_periodo
			and nl.anio_id = id_anio
			and nl.mes_id = id_mes
		)
	));
end 
$function$
;
