-- DROP FUNCTION public.get_liquidar_vacaciones(int4);

CREATE OR REPLACE FUNCTION public.get_liquidar_vacaciones(in_novedad integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
declare
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	resultado json;
begin
	select 
		json_build_object(
			'id', nn.id,
			'contrato', nc.id,
			'nombre', tp.n_completo,
			'documento', tp.documento,
			'vacaciones_liquidadas', nn.vacaciones_liquidadas,
			'vacaciones_id', (select nv.id from nomina_vacaciones nv where nv.contrato_novedades_id = in_novedad),
			'tipo_contrato', (select nt.nombre from nomina_tipocontrato nt where nt.id = nc.tipo_contrato_id),
			'sueldo', nc.sueldo,
			'dias', nn.valor,
			'dias_laborados', ABS(nn.periodo_fin_vacaciones - nn.periodo_ini_vacaciones),
			'proc_salud', round(nda.porcentaje_salud, 2),
			'proc_pension', round(nda.porcentaje_pension, 2),
			'valor_dia', round(nc.sueldo / 30),
			'cargo', (select ncc.nombre from nomina_cargo ncc where ncc.id = nc.cargo_id),
			'fecha_ingreso', (select to_char(nc.fecha_ingreso, 'YYYY-MM-DD')),
			'periodo_vacaciones', (select json_build_object(
				'fecha_ini', nn.periodo_ini_vacaciones,
				'fecha_fin', nn.periodo_fin_vacaciones
			)),
			'fecha_vacaciones', (select json_build_object(
				'fecha_ini', (select to_char(nn.fecha_inicial, 'YYYY-MM-DD')),
				'fecha_fin', (select to_char(nn.fecha_final, 'YYYY-MM-DD')),
				'fecha_reintegro', (select to_char(nn.fecha_reintegro, 'YYYY-MM-DD'))
			)),
			'salud', (select json_build_object(
				'dias', (select sum(np.valor) from nomina_contratonovedadesperiodos np where np.contrato_novedades_id = nn.id),
				'valor_porcentaje', round(((nc.sueldo / 30) * nda.porcentaje_salud) / 100, 2),
				'total', round((((nc.sueldo / 30) * nda.porcentaje_salud) / 100) * (select sum(np.valor) from nomina_contratonovedadesperiodos np where np.contrato_novedades_id = nn.id))
			)),
			'pension', (select json_build_object(
				'dias', (select sum(np.valor) from nomina_contratonovedadesperiodos np where np.contrato_novedades_id = nn.id),
				'valor_porcentaje', round(((nc.sueldo / 30) * nda.porcentaje_pension) / 100, 2),
				'total', round((((nc.sueldo / 30) * nda.porcentaje_pension) / 100) * (select sum(np.valor) from nomina_contratonovedadesperiodos np where np.contrato_novedades_id = nn.id))
			)),
			'subtotal', round((nc.sueldo / 30) * nn.valor),
			'total_deducciones', (
				round((((nc.sueldo / 30) * nda.porcentaje_salud) / 100) * (select sum(np.valor) from nomina_contratonovedadesperiodos np where np.contrato_novedades_id = nn.id)) + 
				round((((nc.sueldo / 30) * nda.porcentaje_pension) / 100) * (select sum(np.valor) from nomina_contratonovedadesperiodos np where np.contrato_novedades_id = nn.id))
			),
			'total', (
				round((nc.sueldo / 30) * nn.valor) - (
					round((((nc.sueldo / 30) * nda.porcentaje_salud) / 100) * (select sum(np.valor) from nomina_contratonovedadesperiodos np where np.contrato_novedades_id = nn.id)) + 
					round((((nc.sueldo / 30) * nda.porcentaje_pension) / 100) * (select sum(np.valor) from nomina_contratonovedadesperiodos np where np.contrato_novedades_id = nn.id))
				)
			)
		) into resultado
	from 
	nomina_contratonominanovedades nn
	inner join nomina_contrato nc on nc.id = nn.contrato_id
    inner join nomina_datosaportes nda on nda.contrato_id = nc.id
	inner join personas_persona tp on tp.id = nc.persona_id
	where nn.id = in_novedad;
	
	return resultado;
end 
$function$
;

-- Permissions

ALTER FUNCTION public.get_liquidar_vacaciones(int4) OWNER TO postgres;
GRANT ALL ON FUNCTION public.get_liquidar_vacaciones(int4) TO postgres;
