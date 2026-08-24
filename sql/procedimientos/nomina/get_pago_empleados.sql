-- DROP FUNCTION public.get_pago_empleados(int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.get_pago_empleados(in_periodo_id integer, in_mes_id integer, in_anio_id integer, in_centro_costo_id integer DEFAULT NULL::integer)
 RETURNS json
 LANGUAGE plpgsql
AS $function$
declare
	----------------------------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	resultado json;
	----------------------------------------------------------------------------------------------------------------------------------------------
begin
	
	--------------------------------------- Parametros necesarios para el funcionamiento ---------------------------------------------------------
	
	----------------------------------------------------------------------------------------------------------------------------------------------
	
	resultado := (
		select coalesce(json_agg(json_build_object(
			'select', false,
			'liquidacion_id', obj.id,
			'contrato_id', obj.contrato_id,
			'centro_costos_id', obj.centro_costos_id,
			'persona', obj.persona,
			'total_devengado', obj.total_devengado,
			'total_deducido', obj.total_deducido,
			'neto', obj.neto,
			'forma_pago', obj.forma_pago,
			'detalle_liquidacion', obj.detalle_liquidacion,
			'pago', obj.pago,
			'documento', obj.documento,
			'fecha_pago', obj.fecha_pago,
			'usuario_pago', obj.usuario_pago
		)), '[]')
		from (
			with detalle_liquidaciones as (
			    select
			        ndl.liquidacion_id,
			        sum(
			            case 
			                when nn.tipo_novedad_id = 3 and ndl.valor_empleado > 0 then ndl.valor_empleado::integer
			                else 0
			            end
			        ) as total_devengado,
			        sum(
			            case 
			                when nn.tipo_novedad_id in (1, 2) and ndl.valor_empleado > 0 then ndl.valor_empleado::integer
			                else 0
			            end
			        ) as total_deducido
			    from nomina_detalle_liquidaciones ndl
			    inner join nomina_novedades nn on nn.id = ndl.novedad_id
			    group by ndl.liquidacion_id
			)
			select
			    nl.id,
				nc.id as contrato_id,
				nc.centro_costo_id as centro_costos_id,
			    (
			    	json_build_object(
			    		'id', tp.id,
			    		'documento', tp.documento,
			    		'nombre', tp.n_completo
			    	) 
			    ) as persona,
			    dl.total_devengado,
			    dl.total_deducido,
			    (dl.total_devengado - dl.total_deducido) as neto,
			    (
			    	json_build_object(
			    		'banco', json_build_object(
			    			'id', cb.id,
			    			'nombre', cb.nombre
			    		),
			    		'forma_pago', json_build_object(
			    			'id', cfp.id,
			    			'nombre', cfp.nombre
			    		),
						'tipo_cuenta', json_build_object(
			    			'id', ct.id,
			    			'nombre', ct.nombre
			    		),
			    		'num_cuenta', ndp.numero_cuenta
			    	) 
			    ) as forma_pago,
			    (
			        select 
			            json_agg(
			                json_build_object(
			                    'id', ndl.id,
			                    'novedad_id', ndl.novedad_id,
			                    'cantidad', ndl.cantidad,
			                    'valor', ndl.valor_empleado,
			                    'tipo_valor_novedad', json_build_object(
			                        'id', ntv.id,
			                        'nombre', ntv.nombre
			                    ),
			                    'tipo_novedad', json_build_object(
			                        'id', tn.id,
			                        'nombre', tn.nombre
			                    ),
			                    'descripcion', ndl.descripcion
			                )
			            )
			        from nomina_detalle_liquidaciones ndl
			        inner join nomina_novedades nn on nn.id = ndl.novedad_id
			        left join nomina_tipovalornovedad ntv on ntv.id = nn.tipo_valor_novedad_id
			        left join nomina_tiponovedad tn on tn.id = nn.tipo_novedad_id
			        where ndl.liquidacion_id = nl.id
			        and ndl.valor_empleado > 0
			    ) as detalle_liquidacion,
				nl.pago,
				(
					json_build_object(
						'id', cd.id,
						'numero', cd.numero
					)
				) as documento,
				to_char(nl.fecha_pago, 'DD/MM/YYYY HH:MI AM') as fecha_pago,
				(
					json_build_object(
						'id', au.id,
						'nombre', concat(au.first_name, ' ', au.last_name)
					)
				) as usuario_pago
			from nomina_liquidaciones nl
			inner join nomina_contrato nc on nc.id = nl.contrato_id
			inner join personas_persona tp on tp.id = nc.persona_id
            inner join nomina_datospago ndp on ndp.contrato_id = nc.id
			left join conf_bancos cb on cb.id = ndp.banco_id
			left join contabilidad_formapagoelectro cfp on cfp.id = ndp.forma_pago_id
			left join contabilidad_tipocuenta ct on ct.id = ndp.tipo_cuenta_id
			left join detalle_liquidaciones dl on dl.liquidacion_id = nl.id
			left join cont_documentos cd on cd.id = nl.documento_id
			left join accounts_usuario au on au.id = nl.usuario_pago_id
			where nl.periodo_id = in_periodo_id
			and nl.mes_id = in_mes_id
			and nl.anio_id = in_anio_id
			and nl.estado is true
			and (in_centro_costo_id is null or nc.centro_costo_id = in_centro_costo_id)
			order by tp.n_completo asc
		) as obj
	);

	return resultado;
end 
$function$
;

-- Permissions

ALTER FUNCTION public.get_pago_empleados(int4, int4, int4, int4) OWNER TO postgres;
GRANT ALL ON FUNCTION public.get_pago_empleados(int4, int4, int4, int4) TO postgres;
