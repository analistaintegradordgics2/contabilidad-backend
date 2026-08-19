-- DROP FUNCTION public.liquidar_nomina(int4, varchar, int4, varchar, json, json, varchar, varchar, int4);

CREATE OR REPLACE FUNCTION public.liquidar_nomina(in_anio integer, in_mes character varying, in_periodo integer, in_descripcion character varying, in_totales json, in_data json, in_fecha_inicial character varying, in_fecha_final character varying, in_usuario integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
declare
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	item json;
	nove json;
	resultado json;
	empresa_id integer;
	out_documento_id integer;
	documento_num_empleado varchar;
	documento_num_empleador varchar;
	nota_contable_id integer;
	concepto_nomina_liquidacion integer;
	nombre_concepto_nomina_liquidacion varchar;
	total_empleado numeric default 0;
	total_empleador numeric default 0;
	mov_empleador json;
	mov_empleado json;
	rta_cerrar_doc varchar;
	out_liquidacion_id integer;
	valor_otros_devengados numeric(15, 2) default 0.00;
	valor_otros_deducidos numeric(15, 2) default 0.00;
	licencias_no_remuneradas integer [];
	concepto_id integer;
	detalle_concepto varchar;
	cta_arr_id integer;
	codigo_cliente_bita varchar;
	liquidaciones_generadas integer [] := '{}';
	cta_db_salud_empleado integer;
	cta_db_pension_empleado integer;
	out_id_doc_empleador integer;
	out_id_doc_empleado integer;
begin
	
	-------------------------------------------------------------- Parametros necesarios para el funcionamiento --------------------------------------------------------------
	select cp.valor::integer into empresa_id from parametros_parametros cp where cp.parametro = 'persona_id_empresa';
	select cp.valor::integer into nota_contable_id from parametros_parametros cp where cp.parametro = 'nota_contable_id';
	select np.valor::integer into concepto_nomina_liquidacion from nomina_parametros np where np.parametro = 'concepto_nomina_liquidacion';
	select cc.nombre into nombre_concepto_nomina_liquidacion from contabilidad_conceptos cc where cc.id = concepto_nomina_liquidacion;
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into licencias_no_remuneradas from nomina_parametros np where np.parametro = 'licencias_no_remuneradas';
	select cp.valor::integer into cta_arr_id from parametros_parametros cp where cp.parametro = 'cta_arr_id'; 
	select cp.valor into codigo_cliente_bita from parametros_parametros cp where cp.parametro = 'codigo_cliente_bita';
	select np.valor::integer into cta_db_salud_empleado from nomina_parametros np where np.parametro = 'cta_db_salud_empleado';
	select np.valor::integer into cta_db_pension_empleado from nomina_parametros np where np.parametro = 'cta_db_pension_empleado';
	------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	create temp table if not exists temp_mov_empleador (
		mov_id integer,
		mayor_id integer,
		persona_id integer,
		concepto_id integer,
		detalle text,
		valordb decimal(18,2),
		valorcr decimal(18,2),
		docref varchar(20),
		base decimal(18,2),
		cc_id integer,
		tercero_id integer,
		pago_id integer
	);
	
	create temp table if not exists temp_mov_empleado (
		mov_id integer,
		mayor_id integer,
		persona_id integer,
		concepto_id integer,
		detalle text,
		valordb decimal(18,2),
		valorcr decimal(18,2),
		docref varchar(20),
		base decimal(18,2),
		cc_id integer,
		tercero_id integer,
		pago_id integer
	);

	create temp table if not exists temp_detalle_liquidacion (
		descripcion text,
		cantidad integer,
		valor_empleado numeric,
		valor_patrono numeric,
		fecha_inicial timestamptz,
		fecha_final timestamptz,
		liquidacion_id integer,
		novedad_id integer
	);


	for item in
		select * from json_array_elements(cast(in_data as json))
	loop
		total_empleado := total_empleado + (cast(item->'empleado'->'sueldo'->>'valor' as text)::numeric + cast(item->'empleado'->'aux_transporte'->>'valor' as text)::numeric + cast(item->'empleado'->'salud'->>'valor' as text)::numeric + cast(item->'empleado'->'pension'->>'valor' as text)::numeric);

		valor_otros_devengados := 0;
		valor_otros_deducidos := 0;

		raise notice 'item=%', item;

		-- G U A R D A R  LA  L I Q U I D A C I O N  P O R  E M P L E A D O
		-- Para anular una liquidación se necesita primero crear la liquidación para asociar su ID al movimiento del documento contable, esto aplica para el documento del empleador
		insert into nomina_liquidaciones (
			created,
			modified,
			descripcion,
			dias_laborados,
			sueldo_trabajado,
			auxilio_transporte,
			otros_devengados,
			salud,
			pension,
			otros_deducidos,
			total,
			fecha_inicial,
			fecha_final,
			contabilizado,
			pago,
			estado,
			anio_id,
			contrato_id,
			mes_id,
			periodo_id,
			uc_id,
			um_id
		) values (
			(select current_date),
			(select current_date),
			concat(item->>'nombre', ' [', item->>'documento', '] ', in_descripcion),
			cast(item->'dias' as text)::integer,
			cast(item->'empleado'->'sueldo'->'valor' as text)::numeric,
			cast(item->'empleado'->'aux_transporte'->'valor' as text)::numeric,
			valor_otros_devengados,
			cast(item->'empleado'->'salud'->'valor' as text)::numeric,
			cast(item->'empleado'->'pension'->'valor' as text)::numeric,
			valor_otros_deducidos,
			cast(item->'empleado'->'neto' as text)::numeric,
			(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
			(select to_date(in_fecha_final, 'YYYY-MM-DD')),
			true,
			false,
			true,
			(select ca.id from parametros_anio ca where ca.nombre = in_anio),
			cast(item->'id' as text)::integer,
			(select cm.id from parametros_mes cm where cm.numero = in_mes),
			in_periodo,
			in_usuario,
			null
		) returning id into out_liquidacion_id;

		liquidaciones_generadas := array_append(liquidaciones_generadas, out_liquidacion_id);
		
		-- C R E A R  M O V I M I E N T O S  P A R A  E L  E M P L E A D O R
		
		-- Movimiento para censantias - empleador
		if cast(item->'empleador'->'cesantias'->'valor' as text)::numeric > 0 then
			total_empleador := (total_empleador + (cast(item->'empleador'->'cesantias'->>'valor' as text)::numeric));
			
			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleador'->'cesantias'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;

			-- D E B I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'cesantias'->'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer, -- id del empleado
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'cesantias'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'cesantias'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleador'->'cesantias'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
			
			-- C R E D I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'cesantias'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer, -- id del empleado
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'cesantias'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'cesantias'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleador'->'cesantias'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleador'->'cesantias'->>'detalle',
				cast(item->'dias' as text)::integer,
				0,
				cast(item->'empleador'->'cesantias'->>'valor' as text)::numeric,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleador'->'cesantias'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para censantias
	
		-- Movimiento para intereses censantias - empleador
		if cast(item->'empleador'->'int_cesantias'->'valor' as text)::numeric > 0 then
			total_empleador := (total_empleador + (cast(item->'empleador'->'int_cesantias'->>'valor' as text)::numeric));

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleador'->'int_cesantias'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;			

			-- D E B I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'int_cesantias'->'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer, -- id del empleado
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'int_cesantias'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'int_cesantias'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleador'->'int_cesantias'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);

			-- C R E D I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'int_cesantias'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer, -- id del empleado
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'int_cesantias'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'int_cesantias'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleador'->'int_cesantias'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleador'->'int_cesantias'->>'detalle',
				cast(item->'dias' as text)::integer,
				0,
				cast(item->'empleador'->'int_cesantias'->>'valor' as text)::numeric,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleador'->'int_cesantias'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para intereses censantias
	
		-- Movimiento para primas - empleador
		if cast(item->'empleador'->'primas'->'valor' as text)::numeric > 0 then
			total_empleador := (total_empleador + (cast(item->'empleador'->'primas'->>'valor' as text)::numeric));

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleador'->'primas'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;
			
			-- D E B I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'primas'->'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer, -- id del empleado
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'primas'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'primas'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleador'->'primas'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
			
			-- C R E D I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'primas'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer, -- id del empleado
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'primas'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'primas'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleador'->'primas'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleador'->'primas'->>'detalle',
				cast(item->'dias' as text)::integer,
				0,
				cast(item->'empleador'->'primas'->>'valor' as text)::numeric,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleador'->'primas'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para primas
	
		-- Movimiento para vacaciones - empleador
		if cast(item->'empleador'->'vacaciones'->'valor' as text)::numeric > 0 then
			total_empleador := (total_empleador + (cast(item->'empleador'->'vacaciones'->>'valor' as text)::numeric));

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleador'->'vacaciones'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;

			-- D E B I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'vacaciones'->'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer, -- id del empleado
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'vacaciones'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'vacaciones'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleador'->'vacaciones'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
			
			-- C R E D I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'vacaciones'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer, -- id del empleado
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'vacaciones'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'vacaciones'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleador'->'vacaciones'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleador'->'vacaciones'->>'detalle',
				cast(item->'dias' as text)::integer,
				0,
				cast(item->'empleador'->'vacaciones'->'valor' as text)::numeric,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleador'->'vacaciones'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para vacaciones
	
		-- Movimiento para salud - empleador
		if cast(item->'empleador'->'salud'->'valor' as text)::numeric > 0 then
			total_empleador := (total_empleador + (cast(item->'empleador'->'salud'->'valor' as text)::numeric));

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleador'->'salud'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;
			
			-- D E B I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'salud'->'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(item->'empleador'->'salud'->'id' as text)::integer, -- id de la entidad
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'salud'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'salud'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleador'->'salud'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
			
			-- C R E D I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'salud'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'empleador'->'salud'->'id' as text)::integer, -- id de la entidad
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'salud'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'salud'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleador'->'salud'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleador'->'salud'->>'detalle',
				cast(item->'dias' as text)::integer,
				0,
				cast(item->'empleador'->'salud'->'valor' as text)::numeric,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleador'->'salud'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para salud
		
		-- Movimiento para pension - empleador
		if cast(item->'empleador'->'pension'->'valor' as text)::numeric > 0 then
			total_empleador := (total_empleador + (cast(item->'empleador'->'pension'->'valor' as text)::numeric));

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleador'->'pension'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;

			-- D E B I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'pension'->'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(item->'empleador'->'pension'->'id' as text)::integer, -- id de la entidad
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'pension'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'pension'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleador'->'pension'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);

			-- C R E D I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'pension'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'empleador'->'pension'->'id' as text)::integer, -- id de la entidad
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'pension'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'pension'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleador'->'pension'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleador'->'pension'->>'detalle',
				cast(item->'dias' as text)::integer,
				0,
				cast(item->'empleador'->'pension'->'valor' as text)::numeric,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleador'->'pension'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para pension
	
		-- Movimiento para ARL - empleador
		if cast(item->'empleador'->'arl'->'valor' as text)::numeric > 0 then
			if cast(item->'centro_costo'->'id' as text)::integer > 0 then
				total_empleador := (total_empleador + (cast(item->'empleador'->'arl'->'valor' as text)::numeric));
	
				-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
				select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleador'->'arl'->'novedad_id' as text)::integer;
				if concepto_id is not null then
					select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
				else 
					concepto_id := concepto_nomina_liquidacion;
					detalle_concepto := nombre_concepto_nomina_liquidacion;
				end if;
				
				-- D E B I T O
				insert into temp_mov_empleador
				values (
					/*mov_id*/			0,
					/*mayor_id*/		cast(item->'empleador'->'arl'->'cta_debito_id' as text)::integer,
					/*persona_id*/		cast(item->'empleador'->'arl'->'id' as text)::integer, -- id de la entidad
					/*concepto_id*/		concepto_id,
										-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'arl'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'arl'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
					/*valordb*/			cast(item->'empleador'->'arl'->'valor' as text)::numeric,
					/*valorcr*/			0,
					/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
					/*base*/			0,
					/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
					/*tercero_id*/		null,
					/*pago_id*/			null
				);
				
				-- C R E D I T O
				insert into temp_mov_empleador
				values (
					/*mov_id*/			0,
					/*mayor_id*/		cast(item->'empleador'->'arl'->'cta_credito_id' as text)::integer,
					/*persona_id*/		cast(item->'empleador'->'arl'->'id' as text)::integer, -- id de la entidad
					/*concepto_id*/		concepto_id,
										-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'arl'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'arl'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
					/*valordb*/			0,
					/*valorcr*/			cast(item->'empleador'->'arl'->'valor' as text)::numeric,
					/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
					/*base*/			0,
					/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
					/*tercero_id*/		null,
					/*pago_id*/			null
				);
			
				insert into temp_detalle_liquidacion 
				values (
					item->'empleador'->'arl'->>'detalle',
					cast(item->'dias' as text)::integer,
					0,
					cast(item->'empleador'->'arl'->'valor' as text)::numeric,
					(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
					(select to_date(in_fecha_final, 'YYYY-MM-DD')),
					null,
					cast(item->'empleador'->'arl'->>'novedad_id' as text)::integer
				);
			end if;
		end if;
		-- Fin Movimiento para ARL
	
		-- Movimiento para caja de compensacion - empleador
		if cast(item->'empleador'->'caja_compensacion'->'valor' as text)::numeric > 0 then
			total_empleador := (total_empleador + (cast(item->'empleador'->'caja_compensacion'->>'valor' as text)::numeric));

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleador'->'caja_compensacion'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;
			
			-- D E B I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'caja_compensacion'->'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(item->'empleador'->'caja_compensacion'->'id' as text)::integer, -- id de la entidad
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'caja_compensacion'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'caja_compensacion'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleador'->'caja_compensacion'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);

			-- C R E D I T O
			insert into temp_mov_empleador
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleador'->'caja_compensacion'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'empleador'->'caja_compensacion'->'id' as text)::integer, -- id de la entidad
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleador'->'caja_compensacion'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleador'->'caja_compensacion'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleador'->'caja_compensacion'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ PATRO: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleador'->'caja_compensacion'->>'detalle',
				cast(item->'dias' as text)::integer,
				0,
				cast(item->'empleador'->'caja_compensacion'->>'valor' as text)::numeric,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleador'->'caja_compensacion'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para caja de compensacion
	
		-- C R E A R  M O V I M I E N T O S  P A R A  E L  E M P L E A D O
	
		-- Movimiento para sueldo - empleado
		if cast(item->'empleado'->'sueldo'->'valor' as text)::numeric > 0 then

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleado'->'sueldo'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;

			-- D E B I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleado'->'sueldo'->'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleado'->'sueldo'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleado'->'sueldo'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleado'->'sueldo'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);

			-- C R E D I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleado'->'sueldo'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleado'->'sueldo'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleado'->'sueldo'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleado'->'sueldo'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleado'->'sueldo'->>'detalle',
				cast(item->'dias' as text)::integer,
				cast(item->'empleado'->'sueldo'->>'valor' as text)::numeric,
				0,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleado'->'sueldo'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para sueldo
	
		-- Movimiento para auxilio de transporte - empleado
		if cast(item->'empleado'->'aux_transporte'->'valor' as text)::numeric > 0 then
			
			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleado'->'aux_transporte'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;

			-- D E B I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleado'->'aux_transporte'->'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleado'->'aux_transporte'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleado'->'aux_transporte'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleado'->'aux_transporte'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);

			-- C R E D I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleado'->'aux_transporte'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'persona_id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleado'->'aux_transporte'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleado'->'aux_transporte'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleado'->'aux_transporte'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleado'->'aux_transporte'->>'detalle',
				cast(item->'dias' as text)::integer,
				cast(item->'empleado'->'aux_transporte'->>'valor' as text)::numeric,
				0,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleado'->'aux_transporte'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para auxilio de transporte
	
		-- Movimiento para salud - empleado
		if cast(item->'empleado'->'salud'->'valor' as text)::numeric > 0 then

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleado'->'salud'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;

			-- D E B I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
									-- Nelson Lugo 22/04/2025 Bita #66592 - Se solicitó que la novedad de salud del empleado, se parametrizara una cuenta debito en especifico diferente a la que se asigna en la novedad.
				/*mayor_id*/		case when cta_db_salud_empleado is not null then cta_db_salud_empleado else cast(item->'empleado'->'salud'->'cta_debito_id' as text)::integer end,
									-- Nelson Lugo 22/04/2025 Bita #66592 - Se solicitó que el nit de la cuenta debito sea el del empleado
				/*persona_id*/		cast(item->'persona_id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleado'->'salud'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleado'->'salud'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleado'->'salud'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);

			-- C R E D I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleado'->'salud'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'empleado'->'salud'->'id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleado'->'salud'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleado'->'salud'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleado'->'salud'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleado'->'salud'->>'detalle',
				cast(item->'dias' as text)::integer,
				cast(item->'empleado'->'salud'->>'valor' as text)::numeric,
				0,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleado'->'salud'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para salud
	
		-- Movimiento para pension - empleado
		if cast(item->'empleado'->'pension'->'valor' as text)::numeric > 0 then

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(item->'empleado'->'pension'->'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;

			-- D E B I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
									-- Nelson Lugo 22/04/2025 Bita #66592 - Se solicitó que la novedad de salud del empleado, se parametrizara una cuenta debito en especifico diferente a la que se asigna en la novedad.
				/*mayor_id*/		case when cta_db_pension_empleado is not null then cta_db_pension_empleado else cast(item->'empleado'->'pension'->'cta_debito_id' as text)::integer end,
									-- Nelson Lugo 22/04/2025 Bita #66592 - Se solicitó que el nit de la cuenta debito sea el del empleado
				/*persona_id*/		cast(item->'persona_id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleado'->'pension'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleado'->'pension'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(item->'empleado'->'pension'->'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);

			-- C R E D I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(item->'empleado'->'pension'->'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(item->'empleado'->'pension'->'id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(item->'empleado'->'pension'->>'detalle', ' ',  in_descripcion)
									else
										concat(item->'empleado'->'pension'->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(item->'empleado'->'pension'->'valor' as text)::numeric,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				item->'empleado'->'pension'->>'detalle',
				cast(item->'dias' as text)::integer,
				cast(item->'empleado'->'pension'->>'valor' as text)::numeric,
				0,
				(select to_date(in_fecha_inicial, 'YYYY-MM-DD')),
				(select to_date(in_fecha_final, 'YYYY-MM-DD')),
				null,
				cast(item->'empleado'->'pension'->>'novedad_id' as text)::integer
			);
		end if;
		-- Fin Movimiento para pension		
	
		-- Novedades del empleado
		for nove in
			select * from json_array_elements(cast(item->'empleado'->>'novedades' as json))
		loop
			
			total_empleado := total_empleado + (coalesce(cast(nove->>'valor' as text)::numeric, 0));
			
			if cast(nove->>'tipo_novedad' as text)::integer = 3 then
				-- Otras novedades de tipo devengado exceptuando las licencias no remuneradas por que estas restan a los devengados
				if not cast(nove->>'novedad_id' as text)::integer = any(licencias_no_remuneradas) then
					valor_otros_devengados := valor_otros_devengados + cast(nove->>'valor' as text)::numeric;
				end if;
			elsif cast(nove->>'tipo_novedad' as text)::integer = 2 then
				-- Otras novedades de tipo deducidos
				valor_otros_deducidos := valor_otros_deducidos + cast(nove->>'valor' as text)::numeric;
			end if;
			
			--if cast(nove->>'valor' as text)::numeric > 0 then

			-- Nelson Lugo 02/10/2024 Bita #59404 - Se valida si la novedad tiene concepto contable, si no tiene entonces se deja por defecto el que esta parametrizado
			select nn.concepto_id into concepto_id from nomina_novedades nn where nn.id = cast(nove->>'novedad_id' as text)::integer;
			if concepto_id is not null then
				select cc.detalle into detalle_concepto from contabilidad_conceptos cc where cc.id = concepto_id;
			else 
				concepto_id := concepto_nomina_liquidacion;
				detalle_concepto := nombre_concepto_nomina_liquidacion;
			end if;

			-- D E B I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(nove->>'cta_debito_id' as text)::integer,
				/*persona_id*/		cast(nove->>'persona_id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(nove->>'detalle', ' ',  in_descripcion)
									else
										concat(nove->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			cast(nove->>'valor' as text)::numeric,
				/*valorcr*/			0,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			-- C R E D I T O
			insert into temp_mov_empleado
			values (
				/*mov_id*/			0,
				/*mayor_id*/		cast(nove->>'cta_credito_id' as text)::integer,
				/*persona_id*/		cast(nove->>'persona_id' as text)::integer,
				/*concepto_id*/		concepto_id,
									-- Nelson Lugo 11/03/2025 Bita #65379 - Se valida si la inmobiliaria es ruiz perea, entonces en el detalle no va el nombre del empleado
				/*detalle*/ 		case when codigo_cliente_bita = 'c9d68a30fb29e135c70702a32667871a' then
										concat(nove->>'detalle', ' ',  in_descripcion)
									else
										concat(nove->>'detalle', ' ', item->>'nombre', ' [', item->>'documento', '] ', in_descripcion)
									end,
				/*valordb*/			0,
				/*valorcr*/			cast(nove->>'valor' as text)::numeric,
				/*docref*/			concat('LIQ EMPLE: [', out_liquidacion_id, ']'),
				/*base*/			0,
				/*cc_id*/			cast(item->'centro_costo'->'id' as text)::integer,
				/*tercero_id*/		null,
				/*pago_id*/			null
			);
		
			insert into temp_detalle_liquidacion 
			values (
				nove->>'detalle',
				cast(nove->'dias' as text)::integer,
				cast(nove->>'valor' as text)::numeric,
				0,
				(select nc.fecha_inicial from nomina_contratonominanovedades nc where nc.id = cast(nove->>'id' as text)::integer),
				(select nc.fecha_final from nomina_contratonominanovedades nc where nc.id = cast(nove->>'id' as text)::integer),
				null,
				cast(nove->>'novedad_id' as text)::integer
			);
			--end if;
		end loop;
		
		-- INSERTAR EL DETALLE DE LA LIQUIDACIÓN
		insert into nomina_detalle_liquidaciones (
			created,
			modified,
			descripcion,
			cantidad,
			valor_empleado,
			valor_patrono,
			fecha_inicial,
			fecha_final,
			liquidacion_id,
			novedad_id,
			uc_id
		)
		select
			(select current_date),
			(select current_date),
			tdl.descripcion,
			tdl.cantidad,
			tdl.valor_empleado,
			tdl.valor_patrono,
			tdl.fecha_inicial,
			tdl.fecha_final,
			out_liquidacion_id,
			tdl.novedad_id,
			in_usuario
		from temp_detalle_liquidacion tdl;
		
		-- Nelson Lugo 15/05/2025 - Se actualiza el total de otros devengados y otros deducidos en la liquidación
		update nomina_liquidaciones nl set otros_devengados = valor_otros_devengados, otros_deducidos = valor_otros_deducidos where nl.id = out_liquidacion_id;
	
		truncate table temp_detalle_liquidacion;
	end loop;

	-- N O T A  P A R A  E L  E M P L E A D O R
	if (select count(*) from temp_mov_empleador) > 0 then
		select coalesce(json_agg(json_build_object(
			'mov_id', mov.mov_id,
			'mayor_id', mov.mayor_id,
			'persona_id', mov.persona_id,
			'concepto_id', mov.concepto_id,
			'detalle', mov.detalle,
			'valor_db', mov.valordb,
			'valor_cr', mov.valorcr,
			'docref', mov.docref,
			'base', mov.base,
			'cc_id', mov.cc_id,
			'tercero_id', mov.tercero_id,
			'pago_id', mov.pago_id
		)), '[]'::json) into mov_empleador from temp_mov_empleador mov;
	
		select out_id, out_numero into out_documento_id, documento_num_empleador from addingresos (
			0,
			nota_contable_id,
			(select to_date(cast(in_totales->>'fecha_doc' as text), 'DD/MM/YYYY')),
			concepto_nomina_liquidacion,
			concat((select cc.nombre from contabilidad_conceptos cc where cc.id = concepto_nomina_liquidacion), ' ', in_descripcion),
			'',
			empresa_id,
			total_empleador,
			in_usuario,
			mov_empleador, 
			null
		);

		out_id_doc_empleador := out_documento_id;
	
		-- Se ejecuta el procedimiento para cerrar para el documento que se acaba de crear.
		--select out_resultado into rta_cerrar_doc from cerrardoc (out_documento_id, in_usuario);
	
		raise notice 'DOCUMENTO EMPLEADOR ----> %', documento_num_empleado;		
	end if;

	-- N O T A  P A R A  E L  E M P L E A D O
	if (select count(*) from temp_mov_empleado) > 0 then
		select json_agg(json_build_object(
			'mov_id', mov.mov_id,
			'mayor_id', mov.mayor_id,
			'persona_id', mov.persona_id,
			'concepto_id', mov.concepto_id,
			'detalle', mov.detalle,
			'valor_db', mov.valordb,
			'valor_cr', mov.valorcr,
			'docref', mov.docref,
			'base', mov.base,
			'cc_id', mov.cc_id,
			'tercero_id', mov.tercero_id,
			'pago_id', mov.pago_id
		)) into mov_empleado from temp_mov_empleado mov;

		select out_id, out_numero into out_documento_id, documento_num_empleado from addingresos (
			0,
			nota_contable_id,
			(select to_date(cast(in_totales->>'fecha_doc' as text), 'DD/MM/YYYY')),
			concepto_nomina_liquidacion,
			concat((select cc.nombre from contabilidad_conceptos cc where cc.id = concepto_nomina_liquidacion), ' ', in_descripcion),
			'',
			empresa_id,
			total_empleado,
			in_usuario,
			mov_empleado,
			null
		);

		out_id_doc_empleado := out_documento_id;
	
		-- Se ejecuta el procedimiento para cerrar para el documento que se acaba de crear.
		--select out_resultado into rta_cerrar_doc from cerrardoc (out_documento_id, in_usuario);
	
		raise notice 'DOCUMENTO EMPLEADO ----> %', documento_num_empleado;

		-- Asigar el documento_id generado a las liquidaciones generadas
		update nomina_liquidaciones nl set documento_id = out_documento_id where nl.id = any(liquidaciones_generadas);
	end if;

	drop table temp_mov_empleador;
	drop table temp_mov_empleado;
	drop table temp_detalle_liquidacion;

	resultado := (select json_build_object(
		'documento_empleador', documento_num_empleador,
		'documento_empleado', documento_num_empleado,
		'out_id_doc_empleador', out_id_doc_empleador,
		'out_id_doc_empleado', out_id_doc_empleado
	));

	return resultado;
end 
$function$
;
