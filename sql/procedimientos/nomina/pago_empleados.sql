-- DROP FUNCTION public.pago_empleados(json, json);

CREATE OR REPLACE FUNCTION public.pago_empleados(in_filtros json, in_data json)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
declare
	----------------------------------------------------------------------------------------------------------------------------------------------
	--  Variables locales
	tipo_documento integer;
	cta_caja_id integer;
	cta_banco_id integer;
	banco_origen_id integer;
	concepto_pago_id integer;
	detalle_concepto varchar;
	novedad_sueldo_id integer;
	persona_empresa_id integer;
	resultado json;
	item json;
	movimiento json;
	pagos_json json;
	liquidaciones integer[] := '{}';
	rta_doc_id integer;
	rta_num_doc varchar;
	num_cheque integer;
	forma_pago_val integer;
	tipo_generacion_val integer;
	total_pagar_val numeric(18,2) := 0;
	neto_item numeric(18,2) := 0;
	usuario_val integer;
	fecha_doc_val date;
	persona_doc_val integer;
	descripcion_val text;
	----------------------------------------------------------------------------------------------------------------------------------------------
begin
	
	--------------------------------------- Parámetros necesarios para el funcionamiento ---------------------------------------------------------
	select np.valor::integer into cta_caja_id from nomina_parametros np where np.parametro = 'cta_caja';
	select np.valor::integer into concepto_pago_id from nomina_parametros np where np.parametro = 'concepto_pago_nomina';
	select np.valor::integer into novedad_sueldo_id from nomina_parametros np where np.parametro = 'sueldo';
	select cp.valor::integer into persona_empresa_id from parametros_parametros cp where cp.parametro = 'persona_id_empresa';
	
	select coalesce(cc.detalle, cc.nombre, 'PAGO NOMINA') into detalle_concepto 
	from contabilidad_conceptos cc where cc.id = concepto_pago_id;
	
	forma_pago_val := cast(in_filtros->>'forma_pago' as text)::integer;
	tipo_generacion_val := coalesce(cast(in_filtros->>'tipo_generacion_documento' as text)::integer, 1);
	usuario_val := cast(in_filtros->>'usuario' as text)::integer;
	fecha_doc_val := (in_filtros->>'fecha_doc')::date;
	descripcion_val := coalesce(cast(in_filtros->>'descripcion' as text), '');

	if forma_pago_val = 1 then
		select np.valor::integer into tipo_documento from nomina_parametros np where np.parametro = 'egreso_caja';
	elsif forma_pago_val = 2 then
		select np.valor::integer into tipo_documento from nomina_parametros np where np.parametro = 'egreso_cheque';
		select ccb.mayor_id, ccb.banco_id into cta_banco_id, banco_origen_id 
		from contabilidad_cuentabancaria ccb where ccb.id = cast(in_filtros->>'ctabanco' as text)::integer;
	else
		select np.valor::integer into tipo_documento from nomina_parametros np where np.parametro = 'egreso_banco';
		select ccb.mayor_id, ccb.banco_id into cta_banco_id, banco_origen_id 
		from contabilidad_cuentabancaria ccb where ccb.id = cast(in_filtros->>'ctabanco' as text)::integer;
	end if;
	----------------------------------------------------------------------------------------------------------------------------------------------

	create temp table if not exists temp_mov (
		mov_id integer,
		mayor_id integer,
		persona_id integer,
		concepto_id integer,
		detalle text,
		valor_db decimal(18,2),
		valor_cr decimal(18,2),
		docref varchar(20),
		base decimal(18,2),
		cc_id integer,
		tercero_id integer,
		pago_id integer
	);

	-- Se crea tabla temporal para guardar los resultados de los documentos generados.
	create temp table if not exists temp_resultados (
		documento_id integer,
		numero_documento varchar,
		liquidacion_id integer null
	);
	
	num_cheque := coalesce(cast(in_filtros->>'num_cheque' as text)::integer, 1) - 1;

	if tipo_generacion_val = 1 then
		-- =====================================================================
		-- Caso 1: Se genera un documento individual por cada empleado
		-- =====================================================================
		for item in
			select * from json_array_elements(cast(in_data as json))
		loop
			neto_item := cast(item->>'neto' as text)::numeric;

			-- Mov crédito (Caja o Banco)
			insert into temp_mov (
				mov_id, mayor_id, persona_id, concepto_id, detalle,
				valor_db, valor_cr, docref, base, cc_id, tercero_id, pago_id
			) values (
				0,
				case when forma_pago_val = 1 then cta_caja_id else cta_banco_id end,
				cast(item->'persona'->>'id' as text)::integer,
				concepto_pago_id,
				concat(detalle_concepto, ' ', descripcion_val),
				0,
				neto_item,
				null,
				0,
				null,
				null,
				null
			);

			-- Mov débito (Pasivo / Sueldo según Centro de Costo)
			insert into temp_mov (
				mov_id, mayor_id, persona_id, concepto_id, detalle,
				valor_db, valor_cr, docref, base, cc_id, tercero_id, pago_id
			) values (
				0,
				(
					select nvc.mayor_cta_credito_id
					from nomina_novedadescentrocosto nvc
					where nvc.centro_costos_id = cast(item->>'centro_costos_id' as text)::integer
					  and nvc.novedades_id = novedad_sueldo_id
					  and coalesce(nvc.eliminado, false) is false
					limit 1
				),
				cast(item->'persona'->>'id' as text)::integer,
				concepto_pago_id,
				concat(detalle_concepto, ' ', descripcion_val),
				neto_item,
				0,
				null,
				0,
				cast(item->>'centro_costos_id' as text)::integer,
				null,
				null
			);

			select coalesce(json_agg(json_build_object(
				'mov_id', mov.mov_id,
				'mayor_id', mov.mayor_id,
				'persona_id', mov.persona_id,
				'concepto_id', mov.concepto_id,
				'detalle', mov.detalle,
				'valor_db', mov.valor_db,
				'valor_cr', mov.valor_cr,
				'docref', mov.docref,
				'base', mov.base,
				'cc_id', mov.cc_id,
				'tercero_id', mov.tercero_id,
				'pago_id', mov.pago_id
			)), '[]'::json) into movimiento from temp_mov mov;

			-- Construir estructura de pagos
			if forma_pago_val = 1 then
				pagos_json := json_build_array(json_build_object(
					'tipo', 'efectivo',
					'forma_pago_id', forma_pago_val,
					'valor', neto_item
				));
			elsif forma_pago_val = 4 then
				num_cheque := num_cheque + 1;
				pagos_json := json_build_array(json_build_object(
					'tipo', 'cheque',
					'forma_pago_id', forma_pago_val,
					'banco_id', banco_origen_id,
					'numero', num_cheque::text,
					'fecha', fecha_doc_val,
					'valor', neto_item
				));
			elsif forma_pago_val = 5 then
				pagos_json := json_build_array(json_build_object(
					'tipo', 'transferencia',
					'forma_pago_id', forma_pago_val,
					'banco_destino_id', cast(item->'forma_pago'->'banco'->>'id' as text)::integer,
					'cuenta_destino', cast(item->'forma_pago'->>'num_cuenta' as text),
					'cuenta_origen_id', cast(in_filtros->>'ctabanco' as text)::integer,
					'referencia', 'PAGO NOMINA',
					'valor', neto_item
				));
			else
				pagos_json := '[]'::json;
			end if;

			-- Generar documento de EGRESO mediante addingresos con su nueva firma de 11 argumentos
			select out_id, out_numero into rta_doc_id, rta_num_doc
			from addingresos (
				0,
				tipo_documento,
				fecha_doc_val,
				concepto_pago_id,
				concat(detalle_concepto, ' ', descripcion_val),
				case when forma_pago_val = 2 then num_cheque::text else '' end,
				cast(item->'persona'->>'id' as text)::integer,
				neto_item,
				usuario_val,
				movimiento,
				pagos_json
			);

			-- Marcar la liquidación como pagada y asociar el documento
			update nomina_liquidaciones nl set 
				pago = true,
				documento_id = rta_doc_id,
				fecha_pago = now(),
				usuario_pago_id = usuario_val
			where nl.id = cast(item->>'liquidacion_id' as text)::integer;

			-- Identificar el documento como pago de nómina
			update cont_documentos cd set origen = 'PAGOEMPLE', automatico = true where cd.id = rta_doc_id;

			-- Registrar en la tabla temporal de resultados para retorno a Python
			insert into temp_resultados values (rta_doc_id, rta_num_doc, cast(item->>'liquidacion_id' as text)::integer);

			-- Limpiar tabla temporal de movimientos para el siguiente ciclo
			truncate table temp_mov;
		end loop;

	else
		-- =====================================================================
		-- Caso 2: Se genera un único documento agrupado por todos los pagos
		-- =====================================================================
		total_pagar_val := coalesce(cast(in_filtros->>'total_pagar' as text)::numeric, 0);
		persona_doc_val := coalesce(cast(in_filtros->>'persona' as text)::integer, persona_empresa_id);

		if total_pagar_val = 0 then
			select sum(cast(elem->>'neto' as text)::numeric) into total_pagar_val
			from json_array_elements(cast(in_data as json)) elem;
		end if;

		-- Mov crédito por el total general (Caja o Banco)
		insert into temp_mov (
			mov_id, mayor_id, persona_id, concepto_id, detalle,
			valor_db, valor_cr, docref, base, cc_id, tercero_id, pago_id
		) values (
			0,
			case when forma_pago_val = 1 then cta_caja_id else cta_banco_id end,
			persona_doc_val,
			concepto_pago_id,
			concat(detalle_concepto, ' ', descripcion_val),
			0,
			total_pagar_val,
			null,
			0,
			null,
			null,
			null
		);

		-- Mov débito por cada empleado
		for item in
			select * from json_array_elements(cast(in_data as json))
		loop
			neto_item := cast(item->>'neto' as text)::numeric;

			insert into temp_mov (
				mov_id, mayor_id, persona_id, concepto_id, detalle,
				valor_db, valor_cr, docref, base, cc_id, tercero_id, pago_id
			) values (
				0,
				(
					select nvc.mayor_cta_credito_id
					from nomina_novedadescentrocosto nvc
					where nvc.centro_costos_id = cast(item->>'centro_costos_id' as text)::integer
					  and nvc.novedades_id = novedad_sueldo_id
					  and coalesce(nvc.eliminado, false) is false
					limit 1
				),
				cast(item->'persona'->>'id' as text)::integer,
				concepto_pago_id,
				concat(detalle_concepto, ' ', descripcion_val),
				neto_item,
				0,
				null,
				0,
				cast(item->>'centro_costos_id' as text)::integer,
				null,
				null
			);

			liquidaciones := array_append(liquidaciones, cast(item->>'liquidacion_id' as text)::integer);
		end loop;

		select coalesce(json_agg(json_build_object(
			'mov_id', mov.mov_id,
			'mayor_id', mov.mayor_id,
			'persona_id', mov.persona_id,
			'concepto_id', mov.concepto_id,
			'detalle', mov.detalle,
			'valor_db', mov.valor_db,
			'valor_cr', mov.valor_cr,
			'docref', mov.docref,
			'base', mov.base,
			'cc_id', mov.cc_id,
			'tercero_id', mov.tercero_id,
			'pago_id', mov.pago_id
		)), '[]'::json) into movimiento from temp_mov mov;

		-- Construir estructura de pagos para documento agrupado
		if forma_pago_val = 1 then
			pagos_json := json_build_array(json_build_object(
				'tipo', 'efectivo',
				'forma_pago_id', forma_pago_val,
				'valor', total_pagar_val
			));
		elsif forma_pago_val = 4 then
			num_cheque := num_cheque + 1;
			pagos_json := json_build_array(json_build_object(
				'tipo', 'cheque',
				'forma_pago_id', forma_pago_val,
				'banco_id', banco_origen_id,
				'numero', num_cheque::text,
				'fecha', fecha_doc_val,
				'valor', total_pagar_val
			));
		elsif forma_pago_val = 5 then
			pagos_json := json_build_array(json_build_object(
				'tipo', 'transferencia',
				'forma_pago_id', forma_pago_val,
				'cuenta_origen_id', cast(in_filtros->>'ctabanco' as text)::integer,
				'referencia', 'PAGO NOMINA',
				'valor', total_pagar_val
			));
		else
			pagos_json := '[]'::json;
		end if;
		
		raise notice 'pagos_json=% forma_pago_val=%', pagos_json, forma_pago_val;

		-- Generar documento de EGRESO único mediante addingresos
		select out_id, out_numero into rta_doc_id, rta_num_doc
		from addingresos (
			0,
			tipo_documento,
			fecha_doc_val,
			concepto_pago_id,
			concat(detalle_concepto, ' ', descripcion_val),
			case when forma_pago_val = 2 then num_cheque::text else '' end,
			persona_doc_val,
			total_pagar_val,
			usuario_val,
			movimiento,
			pagos_json
		);

		-- Marcar todas las liquidaciones como pagadas
		update nomina_liquidaciones nl set 
			pago = true,
			documento_id = rta_doc_id,
			fecha_pago = now(),
			usuario_pago_id = usuario_val
		where nl.id = any(liquidaciones);

		-- Identificar el documento como pago de nómina
		update cont_documentos cd set origen = 'PAGOEMPLE', automatico = true where cd.id = rta_doc_id;

		-- Registrar en la tabla temporal de resultados para retorno a Python
		insert into temp_resultados values (rta_doc_id, rta_num_doc, null);

		truncate table temp_mov;
	end if;

	resultado := (
		select 
			coalesce(json_agg(json_build_object(
				'documento_id', tr.documento_id,
				'numero_documento', tr.numero_documento,
				'liquidacion_id', tr.liquidacion_id
			)), '[]'::json)
		from temp_resultados tr
	);

	drop table if exists temp_mov;
	drop table if exists temp_resultados;
	
	return resultado;
end 
$function$
;
