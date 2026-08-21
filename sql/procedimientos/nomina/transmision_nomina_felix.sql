-- DROP FUNCTION public.transmision_nomina_felix(int4, varchar);

CREATE OR REPLACE FUNCTION public.transmision_nomina_felix(in_anio integer, in_mes character varying)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
declare
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	cont record;
	item record;
	datos json[];
	resultado json;
	horas_extras integer[];
	vacaciones integer[];
	incapacidades integer[];
	licencias integer[];
	devengados integer[];
	deducciones integer[];
	array_otros_devengados integer[];
	array_otros_deducciones integer[];
	array_ausentismos integer [];
	array_auxilios integer [];
	array_bonificaciones integer [];
	array_compensaciones integer [];
	array_bonos integer[];
	array_viaticos integer[];

	-- Variables para parametros
	param_forma_liquidacion varchar;
	param_sueldo integer;
	param_aux_transporte integer;
	param_primas integer;
	param_salud integer;
	param_pension integer;
	param_cesantias integer;
	param_int_cesantias integer;
	param_arl integer;
	param_vacaciones integer;
	param_transmitir_provisiones boolean;
	porc_cesantias_empleador integer;
	-- Variables adicionales
	in_anio_id integer;
	ultimo_dia_mes integer;
	validacion boolean default false;



json_tmp json;

begin
	
	-------------------------------------------------------------- Parametros necesarios para el funcionamiento --------------------------------------------------------------
	select np.valor into param_forma_liquidacion from nomina_parametros np where np.parametro = 'forma_liquidacion';
	select np.valor::integer into param_sueldo from nomina_parametros np where np.parametro = 'sueldo';
	select np.valor::integer into param_aux_transporte from nomina_parametros np where np.parametro = 'aux_transporte';
	select np.valor::integer into param_primas from nomina_parametros np where np.parametro = 'primas';
	select np.valor::integer into param_salud from nomina_parametros np where np.parametro = 'salud';
	select np.valor::integer into param_pension from nomina_parametros np where np.parametro = 'pension';
	select np.valor::integer into param_cesantias from nomina_parametros np where np.parametro = 'cesantias';
	select np.valor::integer into param_int_cesantias from nomina_parametros np where np.parametro = 'int_cesantias';
	select np.valor::integer into param_vacaciones from nomina_parametros np where np.parametro = 'vacaciones';
	select np.valor::boolean into param_transmitir_provisiones from nomina_parametros np where np.parametro = 'transmitir_provisiones';
	select np.valor::integer into param_arl from nomina_parametros np where np.parametro = 'arl';
	select cast(np.valor as numeric(15, 2)) into porc_cesantias_empleador from nomina_parametros np where np.parametro = 'porc_cesantias_empleador';
	select string_to_array(replace(replace(np.valor, '[', ''), ']', ''), ',')::integer[] into array_ausentismos from nomina_parametros np where np.parametro = 'ausentismo';
	select ca.id into in_anio_id from parametros_anio ca where ca.nombre = in_anio;
	select to_char(date_trunc('MONTH', concat(in_anio, '-', in_mes, '-01')::date) + interval '1 month' - interval '1 day', 'DD') into ultimo_dia_mes;

	horas_extras := array[1, 2, 3, 4, 5, 6, 7];
	vacaciones := array[2, 3];
	incapacidades := array[1, 2, 3];
	licencias := array[1, 2, 3];
	devengados := array[16, 17, 18, 19, 20, 21, 22, 23, 24];
	deducciones := array[7, 8, 10, 11, 12, 13, 14, 15, 16, 17, 18];
	array_otros_devengados := array[6,7,9,10,11,12,13,14,15,16,17,18,19,20,26];
	array_otros_deducciones := array[7,9,12,16,6,5,4,10,8,11,13,14,15,16,17,18];
	array_bonificaciones := array[6];
	array_auxilios := array[7];
	array_compensaciones := array[10];
	array_bonos := array[11];
	array_viaticos := array[25, 26];
	------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
	
	create temp table if not exists temp_detalle_liquidacion (
		liquidacion integer,
		contrato integer,
		cantidad integer,
		valor numeric(15, 2) default 0.00,
		valor_empleado numeric(15, 2) default 0.00,
		valor_patrono numeric(15, 2) default 0.00,
		novedad integer,
		descripcion text, 
		tipo_novedad integer,
		fecha_ini timestamptz,
		fecha_fin timestamptz,
		grupo integer,
		subgrupo integer,
		cod_dian integer,
		patrono boolean default false
	);

	create temp table if not exists temp_total_novedades (
		contrato integer,
		cantidad integer,
		valor numeric(15, 2) default 0.00,
		novedad integer,
		descripcion text,
		patrono boolean default false,
		tipo_novedad integer,
		grupo integer
	);

	for cont in 
		select 
			nl.contrato_id
		from nomina_liquidaciones nl
		inner join nomina_contrato nc on nc.id = nl.contrato_id 
		inner join personas_persona tp on tp.id = nc.persona_id
		where nl.anio_id = in_anio_id
		and nl.mes_id = in_mes::integer
		and nl.estado is true
		group by nl.contrato_id, tp.n_completo
		order by tp.n_completo asc
	loop 
		-- Se valida si el contrato de ese mes y año no haya sido transmitido a la DIAN
		if (select count(*) from nomina_nominaelectronica nn where nn.contrato_id = cont.contrato_id and nn.mes_id = in_mes::integer and nn.anio_id = in_anio_id and nn.estado_id = 4) = 0 then
			
			-- Esta validacion se realizar para saber si la persona ya tiene las dos liquidaciones del mes si la forma de liquidacion es quincenal
			validacion := false;
			if lower(param_forma_liquidacion) <> 'mensual' then
				if (
						select 
							count(*) 
						from nomina_liquidaciones nl
						where nl.contrato_id = cont.contrato_id
						and nl.mes_id = in_mes::integer
						and nl.anio_id = in_anio_id
						and nl.estado is true
					) < 2
				then 
					-- Si el empleado no tiene las dos liquidaciones de la quincina, entonces se valida si su fecha se ingreso o retiro esta dentro del mes que se va transmitir
					-- esto indica que solo se liquido una sola quincena y es valido para transmitir
					if (
							select 
								count(*)
							from nomina_contrato nc
							where nc.id = cont.contrato_id
							--and nl.estado is true
							and (
								nc.fecha_ingreso between to_date(concat(in_anio, '-', in_mes, '-01'), 'YYYY-MM-DD') and to_date(concat(in_anio, '-', in_mes, '-', ultimo_dia_mes), 'YYYY-MM-DD')
								or (nc.fecha_retiro between to_date(concat(in_anio, '-', in_mes, '-01'), 'YYYY-MM-DD') and to_date(concat(in_anio, '-', in_mes, '-', ultimo_dia_mes), 'YYYY-MM-DD') and nc.fecha_retiro is not null)
							)
						) > 0
					then
						validacion := true;
					end if;
				else 
					validacion := true;
				end if;
			else 
				validacion := true;
			end if;
			
			if validacion is true then
				insert into temp_detalle_liquidacion
				select 
					ndl.liquidacion_id,
					nl.contrato_id,
					ndl.cantidad,
					(case when ndl.valor_empleado > 0 then ndl.valor_empleado else ndl.valor_patrono end) as valor,
					ndl.valor_empleado,
					ndl.valor_patrono,
					ndl.novedad_id,
					ndl.descripcion,
					(select nn.tipo_novedad_id from nomina_novedades nn where nn.id = ndl.novedad_id),
					ndl.fecha_inicial,
					ndl.fecha_final,
					(select nn.grupo_nomina_id from nomina_novedades nn where nn.id = ndl.novedad_id),
					(select nn.sub_grupo_nomina_id from nomina_novedades nn where nn.id = ndl.novedad_id),
					(
						select 
							ns.codigo 
						from nomina_subgruponomina ns 
						where ns.id = (select nn.sub_grupo_nomina_id from nomina_novedades nn where nn.id = ndl.novedad_id)
					),
					(case when ndl.valor_patrono > 0 then true else false end)
				from nomina_detalle_liquidaciones ndl
				inner join nomina_liquidaciones nl on nl.id = ndl.liquidacion_id
				where nl.contrato_id = cont.contrato_id
				and nl.mes_id = in_mes::integer
				and nl.anio_id = in_anio_id
				and case when param_transmitir_provisiones is false
					then
						not ndl.novedad_id in (param_cesantias, param_int_cesantias, param_primas, param_vacaciones)
					else 
						true
					end
				and not ndl.novedad_id in (param_arl)
				and case when ndl.valor_patrono > 0 
					then 
						not ndl.novedad_id in (param_salud, param_pension) 
					else 
						true 
					end;

				for item in select * from temp_detalle_liquidacion td loop
					if item.novedad = any(array[param_sueldo, param_aux_transporte, param_salud, param_pension]) then
					    if (select count(*) from temp_total_novedades ttd where ttd.novedad = item.novedad) = 0 then
					        insert into temp_total_novedades (contrato, cantidad, valor, novedad, descripcion, patrono, tipo_novedad, grupo)
					        values (item.contrato, item.cantidad, item.valor, item.novedad, item.descripcion, item.patrono, item.tipo_novedad, item.grupo);
					    else
					        update temp_total_novedades tn
					        set valor = (valor + item.valor), cantidad = (cantidad + item.cantidad)
					        where tn.novedad = item.novedad and tn.patrono = item.patrono;
					    end if;
					else 
						insert into temp_total_novedades (contrato, cantidad, valor, novedad, descripcion, patrono, tipo_novedad, grupo)
				        values (item.contrato, item.cantidad, item.valor, item.novedad, item.descripcion, item.patrono, item.tipo_novedad, item.grupo);
					end if;
				end loop;

				datos := datos || json_build_object(
					'TipoDocumento', 11, -- Nómina Electrónica
					'TipoPeriodo', (select np.cod_dian from nomina_periodo np where (case when param_forma_liquidacion = 'quincenal' then np.id in(1, 2) else np.id = 3 end) limit 1),
					'FechaHoraGeneracion', (select to_char(now(), 'YYYY-MM-DD HH24:MI:SS')),
					'FechaLiquidacionInicio', concat(in_anio, '-', in_mes, '-01'),
					'FechaLiquidacionFin', concat(in_anio, '-', in_mes, '-', ultimo_dia_mes),
					'FechaPago', concat(in_anio, '-', in_mes, '-', ultimo_dia_mes),
					'Notas', '',
					'TipoNomina', '102', -- (102) Nomina individual | (103) Nomina individual de ajuste | (Por ahora no se maneja nominas de ajuste)
					-- 'TipoNota', '', -- Solo aplica si TipoNomina es de ajuste | (1) Reemplazar | (2) Eliminar
					-- 'codigoNominaReferencia', ''  -- Solo aplica si TipoNomina es de ajuste
					'TotalDevengados', (
						(
							select coalesce(sum(td.valor)::integer, 0)
							from temp_total_novedades td
							where td.tipo_novedad in (3, 5) -- Devengados
							and td.grupo <> 22 -- No envío dian felix
						)
					),
					'TotalDeducciones', (
						(
							select coalesce(sum(td.valor)::integer, 0)
							from temp_total_novedades td
							where td.tipo_novedad in (1, 2) -- Deducidos y aportes a seguridad social
							and td.grupo <> 22 -- No envío dian felix
						)
					),
					'TotalDocumento', (
						(select coalesce(sum(td.valor)::integer, 0)
						from temp_total_novedades td
						where td.tipo_novedad in (3, 5) -- Devengados
						and td.grupo <> 22)
						-
						(select coalesce(sum(td.valor)::integer, 0)
						from temp_total_novedades td
						where td.tipo_novedad in (1, 2)  -- Deducidos y aportes a seguridad social
						and td.grupo <> 22)
					),
					'Empleado', (
						json_build_object(
							'Codigo', concat('C', cont.contrato_id),
							'TipoIdentificacion', (select ttd.codigo from personas_tipodocumento ttd where ttd.id = tp.tipo_documento_id),
							'Identificacion', tp.documento,
							'PrimerNombre', coalesce(tp.p_nombre, ''),
							'SegundoNombre', coalesce(tp.s_nombre, ''),
							'PrimerApellido', coalesce(tp.p_apellido, ''),
							'SegundoApellido', coalesce(tp.s_apellido, ''),
							'TipoTrabajador', coalesce((select nt.cod_dian from nomina_tipotrabajador nt where nt.id = nc.tipo_trabajador_id), ''),
							'SubTipoTrabajador', '00', --coalesce(nc.subtipo_trabajador, ''),
							'Ciudad', (select uc.coddane from parametros_ubicacion_ciudades uc where uc.id = (select td.ciudad_id from personas_direccion td where td.persona_id = tp.id and td.incluir_a_factura is true and coalesce(td.eliminado,false) is false)),
							'TipoContrato', coalesce((select nt.cod_dian from nomina_tipocontrato nt where nt.id = nc.tipo_contrato_id), ''),
							'CorreoElectronico', tp.email,
							'Direccion', (select td.descripcion from personas_direccion td where td.persona_id = tp.id and td.incluir_a_factura is true and coalesce(td.eliminado,false) is false),
							'ActividadAltoRiesgo', nc.alto_riesgo_pension,
							'SalarioIntegral', nc.salario_integral,
							'Sueldo', nc.sueldo::integer,
							'FechaIngreso', (select to_char(nc.fecha_ingreso, 'YYYY-MM-DD')),
							'FechaRetiro', coalesce((select to_char(nc.fecha_retiro, 'YYYY-MM-DD')), ''),
							'Area', coalesce((select nc2.nombre from nomina_cargo nc2 where nc2.id = nc.cargo_id), ''),
							'Cargo', coalesce((select nc2.nombre from nomina_cargo nc2 where nc2.id = nc.cargo_id), ''),
							'TipoMedioPago', coalesce((select cm.codigo from contabilidad_mediopagoelectro cm where cm.id = ndp.medio_pago_id), ''),
							'TipoCuentaBancaria', coalesce(ndp.tipo_cuenta_id::text, ''),
							'NombreBanco', coalesce((select cb.nombre from conf_bancos cb where cb.id = ndp.banco_id), ''),
							'NumeroCuentaBancaria', coalesce(ndp.numero_cuenta, ''),
							'CodigoSucursal', coalesce((select ccc.cod_sucursal from contabilidad_centrocostos ccc where ccc.id = nc.centro_costo_id), ''),
							'Pais', 'CO',
							'Departamento', (select upper(uc.departamento) from parametros_ubicacion_ciudades uc where uc.id = (select td.ciudad_id from personas_direccion td where td.persona_id = tp.id and td.incluir_a_factura is true and coalesce(td.eliminado,false) is false)),
							'TiempoLaborado', extract(day from now() - nc.fecha_ingreso)
						) 
					),
					'ConfiguracionNomina', (
						select json_build_object(
							'Departamento', upper(city.departamento),
							'Municipio', city.coddane,
							'Pais', 'CO',
							'PeriodoNomina', (case when 'mensual' = (select lower(n_param.valor) from nomina_parametros n_param where n_param.parametro = 'forma_liquidacion') then 5 else 4 end )
						) 
						from parametros_ubicacion_ciudades city
						where city.id = (select param.valor::integer from parametros_parametros param where param.parametro = 'ciudad_empresa')
					),
					'Devengados', (
						json_build_object(
							'Basico', (
								select json_build_object(
									'DiasTrabajados', sum(td.cantidad),
									'Salario', coalesce(sum(td.valor)::integer, 0)
								)
								from temp_detalle_liquidacion td
								where td.contrato = cont.contrato_id
								and td.novedad = param_sueldo
							),
							'Transporte', (
								select json_build_object(
									'count', count(*),
									'Auxilio', coalesce(sum(case when td.cod_dian is null then td.valor end)::integer, 0),
									'ViaticosSalarial', coalesce(sum(case when td.cod_dian = 25 and nb.novedades_id is not null then td.valor end)::integer, 0), 
									'ViaticosNoSalarial',  coalesce(sum(case when td.cod_dian = 26 and nb.novedades_id is null then td.valor end)::integer, 0)
								)
								from temp_detalle_liquidacion td
								left join (
								    select distinct novedades_id
								    from nomina_baseliquidacionnovedad
								) nb on nb.novedades_id = td.novedad
								where td.contrato = cont.contrato_id
								and td.novedad = param_aux_transporte
								and td.grupo = 23 --  devengados para FELIX
								or td.cod_dian = any(array_viaticos)
							),
							'Prima', ( --Provisión
								select 
                                    case when count(*) > 0 then
                                        json_build_object(
                                            'Cantidad', 30, -- Por ahora se deja a 30 dia que es el mes
                                            'ValorSalarial', coalesce(sum(td.valor)::integer, 0), -- Felix Maneja la prima como salarial
                                            'ValorNoSalarial', 0 
                                        ) 
                                    else '{}' end
								from temp_detalle_liquidacion td
								where td.contrato = cont.contrato_id
								and td.novedad = param_primas
							),
							'Cesantias', (
								select json_build_object(
									'Porcentaje', porc_cesantias_empleador,
									'Valor', coalesce(sum(td.valor)::integer, 0),
									'ValorInteres', (
										select coalesce(sum(td.valor), 0)
										from temp_detalle_liquidacion td
										where td.contrato = cont.contrato_id
										and td.novedad = param_int_cesantias
									)
								)
								from temp_detalle_liquidacion td
								where td.contrato = cont.contrato_id
								and td.novedad = param_cesantias
							),
							'HorasExtra', coalesce((
								select json_agg(json_build_object(
									'TipoHoraExtra', td.cod_dian,
									'FechaHoraInicio', to_char(td.fecha_ini, 'YYYY-MM-DD'),
									'FechaHoraFin', to_char(td.fecha_fin, 'YYYY-MM-DD'),
									'Cantidad', td.cantidad,
									'Valor', coalesce(td.valor::integer, 0)
								))
								from temp_detalle_liquidacion td
								where td.contrato = cont.contrato_id
								and td.grupo = 14 -- Horas extras para FELIX
								), '[]'
							),
							'Vacaciones', coalesce((
								select json_agg(json_build_object(
									'TipoVacacion', td.cod_dian,
									'FechaInicio', to_char(td.fecha_ini, 'YYYY-MM-DD'),
									'FechaFin', to_char(td.fecha_fin, 'YYYY-MM-DD'),
									'Cantidad', td.cantidad,
									'Valor', coalesce(td.valor::integer, 0)
								))
								from temp_detalle_liquidacion td
								where td.contrato = cont.contrato_id
								and td.grupo = 19 and td.cod_dian = 1 or td.novedad = param_vacaciones -- Vacaciones comunes para FELIX
								), '[]'
							),
							'VacacionesCompensadas', coalesce((
								select json_agg(json_build_object(
									'Nvedad', td.novedad,
									'TipoVacacion', td.cod_dian,
									'FechaInicio', to_char((select ncnp.fecha_ini from nomina_contratonovedadesperiodos ncnp where ncnp.contrato_id = td.contrato and extract(year from ncnp.fecha_ini) = in_anio and extract(month from ncnp.fecha_ini) = in_mes::integer and ncnp.contrato_novedades_id = (select ncn.id from nomina_contratonominanovedades ncn where ncn.contrato_id = td.contrato and ncn.novedad_id = td.novedad and ncn.eliminado is false and extract(year from ncn.fecha_inicial) = in_anio and extract(month from ncn.fecha_inicial) = in_mes::integer limit 1) limit 1), 'YYYY-MM-DD'),
									'FechaFin', to_char((select ncnp.fecha_fin from nomina_contratonovedadesperiodos ncnp where ncnp.contrato_id = td.contrato and extract(year from ncnp.fecha_ini) = in_anio and extract(month from ncnp.fecha_ini) = in_mes::integer and ncnp.contrato_novedades_id = (select ncn.id from nomina_contratonominanovedades ncn where ncn.contrato_id = td.contrato and ncn.novedad_id = td.novedad and ncn.eliminado is false and extract(year from ncn.fecha_inicial) = in_anio and extract(month from ncn.fecha_inicial) = in_mes::integer limit 1) limit 1), 'YYYY-MM-DD'),
									'Cantidad', (select (ncnp.fecha_fin - ncnp.fecha_ini) + 1 from nomina_contratonovedadesperiodos ncnp where ncnp.contrato_id = td.contrato and extract(year from ncnp.fecha_ini) = in_anio and extract(month from ncnp.fecha_ini) = in_mes::integer and ncnp.contrato_novedades_id = (select ncn.id from nomina_contratonominanovedades ncn where ncn.contrato_id = td.contrato and ncn.novedad_id = td.novedad and ncn.eliminado is false and extract(year from ncn.fecha_inicial) = in_anio and extract(month from ncn.fecha_inicial) = in_mes::integer limit 1) limit 1),
									'Valor', round(coalesce((td.valor / ((td.fecha_fin::date - td.fecha_ini::date) + 1) * (select (ncnp.fecha_fin - ncnp.fecha_ini) + 1 from nomina_contratonovedadesperiodos ncnp where ncnp.contrato_id = td.contrato and extract(year from ncnp.fecha_ini) = in_anio and extract(month from ncnp.fecha_ini) = in_mes::integer and ncnp.contrato_novedades_id = (select ncn.id from nomina_contratonominanovedades ncn where ncn.contrato_id = td.contrato and ncn.novedad_id = td.novedad and ncn.eliminado is false and extract(year from ncn.fecha_inicial) = in_anio and extract(month from ncn.fecha_inicial) = in_mes::integer limit 1) limit 1)), 0))
								))
								from temp_detalle_liquidacion td
								where td.contrato = cont.contrato_id
								and td.grupo = 19 and td.cod_dian = 2 and td.novedad <> param_vacaciones), '[]'
							),
							'Incapacidades', coalesce((
								select json_agg(json_build_object(
									'TipoIncapacidad', td.cod_dian,
									'FechaInicio', to_char(td.fecha_ini, 'YYYY-MM-DD'),
									'FechaFin', to_char(td.fecha_fin, 'YYYY-MM-DD'),
									'Cantidad', td.cantidad,
									'Valor', coalesce(td.valor::integer, 0),
									'Incapacidad', true
								))
								from temp_detalle_liquidacion td
								where td.contrato = cont.contrato_id
								and td.grupo = 16 -- Incapacidad para FELIX
								), '[]'
							),
							'Licencias', coalesce((
								select json_agg(json_build_object(
									'TipoLicencia', td.cod_dian,
									'FechaInicio', to_char(td.fecha_ini, 'YYYY-MM-DD'),
									'FechaFin', to_char(td.fecha_fin, 'YYYY-MM-DD'),
									'Cantidad', td.cantidad,
									'Valor', coalesce(td.valor::integer, 0),
									'Incapacidad', false
								))
								from temp_detalle_liquidacion td
								where td.contrato = cont.contrato_id
								and td.grupo = 17 -- Licencia para FELIX
								), '[]'
							),
							'HuelgasLegales', coalesce((
								select json_agg(json_build_object(
									'FechaInicio', to_char(td.fecha_ini, 'YYYY-MM-DD'),
									'FechaFin', to_char(td.fecha_fin, 'YYYY-MM-DD'),
									'Cantidad', td.cantidad
								))
								from temp_detalle_liquidacion td
								where td.contrato = cont.contrato_id
								and td.grupo = 14 -- Huelga para FELIX
								), '[]'
							),
							'OtrosDevengados', coalesce((
							    select json_agg(
							        json_build_object(
							            'ValorNoSalarial', coalesce(sum_no_salarial, 0),
							            'TipoDevengado', cod_dian,
							            'Valor', coalesce(sum_salarial, 0),
							            'Descripcion', nms.nombre
							        )
							    )
							    from (
							        select 
							            td.cod_dian,
							            sum(case when td.novedad is null then td.valor end)::integer as sum_no_salarial,
							            sum(case when td.novedad is not null then td.valor end)::integer as sum_salarial
							        from temp_detalle_liquidacion td
							        where td.contrato = cont.contrato_id
							          and td.grupo = 12 -- Otros devengados para FELIX
							          and td.cod_dian = any(array_otros_devengados)
							        group by td.cod_dian
							    ) sub
							    left join nomina_subgruponomina nms
							      on nms.codigo = sub.cod_dian
							     and nms.grupo_nomina_id = 12
							), '[]')
						) 
					),
					'Deducciones', json_build_object(
						'Salud', coalesce((
							select json_build_object(
								'Porcentaje', nda.porcentaje_salud,
								'Valor', coalesce(sum(td.valor)::integer, 0),
								'ValorBase', (
									select coalesce(sum(td.valor)::integer, 0)
									from temp_total_novedades td
									where td.tipo_novedad in (3, 5) -- Devengados
								),
								'Codigo', '1'
							)
							from temp_detalle_liquidacion td
							where td.contrato = cont.contrato_id
							and td.novedad = param_salud
							), '[]'
						),
						'FondoPension', coalesce((
							select json_build_object(
								'Porcentaje', nda.porcentaje_pension,
								'Valor', coalesce(sum(td.valor)::integer, 0),
								'ValorBase', (
									select coalesce(sum(td.valor)::integer, 0)
									from temp_total_novedades td
									where td.tipo_novedad in (3, 5) -- Devengados
								),
								'Codigo', '2'
							)
							from temp_detalle_liquidacion td
							where td.contrato = cont.contrato_id
							and td.novedad = param_pension
							), '[]'
						),
						'FondoSolidaridadEmpleado', coalesce((
							select json_build_object(
								'Valor', coalesce(sum(td.valor)::integer, 0),
								'ValorBase', (
									select coalesce(sum(td.valor)::integer, 0)
									from temp_total_novedades td
									where td.tipo_novedad in (3, 5) -- Devengados
								),
								'Codigo', '3',
								'Porcentaje', '1' -- TODO -->> falta definir como sacar ese porcentaje
							)
							from temp_detalle_liquidacion td
							where td.contrato = cont.contrato_id
							and td.grupo = 11 -- Deducciones para FELIX
							and td.cod_dian = 3 -- Fondo de Solidaridad Empleado FELIX
							having count(*) > 0
							), '[]'
						),
						'OtrasDeducciones', coalesce((
							select json_agg(json_build_object(
								'Descripcion', (select nms.nombre from nomina_subgruponomina nms where nms.codigo = td.cod_dian and nms.grupo_nomina_id = 20),
								'Valor', coalesce(td.valor::integer, 0),
								'TipoDeduccion', td.cod_dian
							))
							from temp_detalle_liquidacion td
							where td.contrato = cont.contrato_id
							and td.grupo = 20 -- Otras deducciones para FELIX
							and td.cod_dian = any(array_otros_deducciones)
							), '[]'
						)
					),
					-- Estas key se deben eliminar al momento de transmitir ya que no hacen parte del json que se debe enviar a la DIAN
					'id', nl.contrato_id,
					'select', false,
					'Novedades', (
						select json_agg(json_build_object(
						    'Cantidad', td.cantidad,
						    'Novedad', td.novedad,
						    'Valor', td.valor,
						    'Descripcion', td.descripcion,
						    'Patrono', td.patrono,
						    'Ausentismo', (case when td.novedad = any(array_ausentismos) then true else false end),
						    'TipoNovedad', td.tipo_novedad
						)) 
						from (
						    select *
						    from temp_total_novedades td
						    where td.contrato = cont.contrato_id
						    order by 
						        case 
						            when td.novedad = any(array[param_sueldo, param_aux_transporte, param_salud, param_pension]) then 1  -- priorizamos estos ids
						            else 2  -- el resto va después
						        end,
						        td.novedad
						) as td
					),
					'liquidaciones', (
						select 
							coalesce(json_agg(distinct td.liquidacion), '[]'::json)
			            from temp_detalle_liquidacion td
			            where td.contrato = cont.contrato_id
			            group by td.contrato
					),
					'Arl', (
						select coalesce(sum(td.valor)::integer, 0)
						from temp_detalle_liquidacion td
						where td.contrato = cont.contrato_id
						and td.novedad = param_arl
					),
					'nomina_electronica_id', (
						select 
							nn.id
						from nomina_nominaelectronica nn 
						where nn.contrato_id = nl.contrato_id
						and nn.mes_id = in_mes::integer
						and nn.anio_id = in_anio_id
					),
					'estado', coalesce(
						(
							select 
								json_build_object(
									'id', ce.id,
									'nombre', ce.nombre
								)
							from contabilidad_estadofactelectro ce 
							where ce.id = (
								select 
									nn.estado_id
								from nomina_nominaelectronica nn 
								where nn.contrato_id = nl.contrato_id
								and nn.mes_id = in_mes::integer
								and nn.anio_id = in_anio_id
							)
						), json_build_object(
							'id', 1,
							'nombre', 'SIN TRANSMITIR'
						)
					),
					'respuesta', (
						select 
							nn.respuesta
						from nomina_nominaelectronica nn 
						where nn.contrato_id = nl.contrato_id
						and nn.mes_id = in_mes::integer
						and nn.anio_id = in_anio_id
					),
					'novedades_pendientes', coalesce((
						select json_agg(json_build_object(
							'nombre_novedad', (select nn.nombre from nomina_novedades nn where nn.id = td.novedad),
							'novedad', td.novedad,
							'descripcion', td.descripcion,
							'grupo', td.grupo,
							'subgrupo', td.subgrupo
						))
						from temp_detalle_liquidacion td
						where td.subgrupo is null or td.grupo is null
						), '[]'
					)
					-- Fin keys a eliminar
				)
				from nomina_liquidaciones nl
				inner join nomina_contrato nc on nc.id = nl.contrato_id
				inner join personas_persona tp on tp.id = nc.persona_id
				inner join nomina_datospago ndp on nc.id = ndp.contrato_id
				inner join nomina_datosaportes nda on nc.id = nda.contrato_id
				where nl.contrato_id = cont.contrato_id
				limit 1;
				
				truncate table temp_detalle_liquidacion;
				truncate table temp_total_novedades;
			end if;
		else 
			-- El contrato ya fue transmitido a la DIAN
			select 
				json_agg(json_build_object(
					'id', nn.id,
					'created', to_char(nn.created, 'DD/MM/YYYY HH12:MI AM'),
					'fecha_ini_liquidacion', nn.fecha_ini_liquidacion,
					'fecha_fin_liquidacion', nn.fecha_fin_liquidacion,
					'dias_laborados', nn.dias_laborados,
					'tipo_nomina', nn.tipo_nomina,
					'numero', nn.numero,
					'prefijo', nn.prefijo,
					'sueldo', nnv.sueldo,
					'sueldo_trabajado', nnv.sueldo_trabajado,
					'auxilio_transporte', nnv.auxilio_transporte,
					'viaticos_salarriales', nnv.viaticos_salarriales,
					'viaticos_nosalariales', nnv.viaticos_nosalariales,
					'otros_devengados', nnv.otros_devengados,
					'total_devengados', nnv.total_devengados,
					'salud', nnv.salud,
					'pension', nnv.pension,
					'fondo', nnv.fondo,
					'arl', nnv.arl,
					'otros_deducidos', nnv.otros_deducidos,
					'total_deducido', nnv.total_deducido,
					'total', nnv.total,
					'estado', (select ce.nombre from contabilidad_estadofactelectro ce where ce.id = nn.estado_id),
					'estado_id', nn.estado_id,
					'respuesta', nn.respuesta,
					'anio', (select ca.nombre from parametros_anio ca where ca.id = nn.anio_id),
					'contrato', (
						select json_build_object(
							'id', nc.id,
							'documento', tp.documento,
							'nombre', tp.n_completo
						)
						from nomina_contrato nc
						inner join personas_persona tp on tp.id = nc.persona_id
						where nc.id = nn.contrato_id
					),
					'mes', (select cm.numero from parametros_mes cm where cm.id = nn.mes_id),
					'uc', (select concat(au.first_name, ' ', au.last_name) from accounts_usuario au where au.id = nn.uc_id),
					'detalle', coalesce((
						select
							json_agg(json_build_object(
								'id', nd.id,
								'cantidad', nd.cantidad,
								'valor', nd.valor,
								'descripcion', nd.descripcion,
								'patrono', nd.patrono,
								'nomina_electronica', nd.nomina_electronica_id,
								'novedad', nd.novedad_id
							)) 
						from nomina_detallenominaelectronica nd 
						where nd.nomina_electronica_id = nn.id and (select nov.grupo_nomina_id from nomina_novedades nov where nov.id = nd.novedad_id) <> 20
					), '[]')
				)) into resultado
			from nomina_nominaelectronica nn
			join nomina_nominaelectronicavalores nnv on nnv.nomina_electronica_id = nn.id
			where nn.mes_id = in_mes::integer
			and nn.anio_id = in_anio_id
			and nn.estado_id = 4;
		end if;
	end loop;
	
	drop table temp_detalle_liquidacion;
	drop table temp_total_novedades;

	return json_build_object(
		'por_transmitir', coalesce((select json_agg(element) from unnest(datos) as element)::json, '[]'),
		'transmitidas', coalesce(resultado, '[]')
	); 
end 
$function$
;
