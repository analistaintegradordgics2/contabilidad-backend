-- DROP FUNCTION public.getcomprobante(_int4, varchar, varchar, int4, int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getcomprobante(in_doc integer[], in_fdesde character varying, in_fhasta character varying, in_abierto integer, in_cerrado integer, in_anulado integer, in_tag integer, in_tipo integer)
 RETURNS TABLE(numero character varying, fecha date, codigo character varying, nombre character varying, documento character varying, nombrecompleto character varying, nombre_concepto character varying, detalle character varying, valor_db numeric, valor_cr numeric, estado integer, encabezado integer, total numeric, tipodocumento bigint, tipo character varying, id bigint)
 LANGUAGE plpgsql
AS $function$
DECLARE
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	l_resultado varchar(100);
	lsql character varying;
	consulta character varying;
	tiposdoc character varying;
	tiposdo character varying;
	tipo json;
	curdatos1 record;

BEGIN
	
	consulta := concat('( ', case when in_abierto = 1 then '1, 4' else '' end, 
					         case when in_abierto = 1 and in_cerrado = 1 then ',' else '' end,
					         case when in_cerrado = 1 then '2' else '' end,
					         case when (in_abierto = 1 or in_cerrado = 1) and in_anulado = 1 then ',' else '' end,
					         case when in_anulado = 1 then '3' else '' end, ' )');
					        
	
					        
	if in_abierto = 0 and in_cerrado = 0 and in_anulado = 0 then
		consulta := '(99)';
	end if;

	for tipo in (SELECT unnest(in_doc)) loop
		tiposdo := concat(tiposdo,(case WHEN tiposdo != '' then ',' else '' end),tipo);
		tiposdoc := concat('( ',tiposdo,' )');
		raise notice '%', tiposdoc;
	end loop;
	
	
	if in_tipo = 1 then
		--raise notice '%', (json_array_elements(in_doc :: json));
		lsql := concat(
			'select cont.numero, cont.fecha, puc."codigo", puc."nombre", per.documento, per.n_completo, conc.nombre as nombre_concepto, mov.detalle::varchar,mov.valor_db, mov.valor_cr, 
			cont.estado, 2 as encabezado, 0.00 as total, tip.fuentes_id as tipodocumento, tip.prefijo, cont.id
			from cont_documentos cont, contabilidad_mayor puc, personas_persona per, contabilidad_conceptos conc, contabilidad_mov mov, contabilidad_tipos_documentos tip 
			where tip.fuentes_id in ', tiposdoc , ' and (cont.fecha between ''', in_fdesde, ''' and ''', in_fhasta, ''') and cont.estado in ',
			consulta, ' and mov.documento_id = cont.id and mov.mayor_id = puc.id and mov.persona_id = per.id and tip.id = cont.tipo_documento_id 
			and mov.concepto_id = conc.id', ' 
			union
			select cont.numero, cont.fecha, '''' as codigo, '''' as nombre, '''' as documento, cont.detalle as nombrecompleto, '''' as nombre_concepto, '''' as detalle, 
			null as valor_db, null as valor_cr, cont.estado, 1 as encabezado, 0.00 as total,  tip.fuentes_id as tipodocumento, tip.prefijo, cont.id
			from cont_documentos cont, contabilidad_tipos_documentos tip where tip.fuentes_id in ', tiposdoc, ' and (cont.fecha between ''', in_fdesde, ''' and ''', 
			in_fhasta, ''') and cont.estado in ', consulta, 
			' and tip.id = cont.tipo_documento_id
			union
			select cont.numero, cont.fecha, '''' as codigo, '''' as nombre, '''' documento, ''SUMAS IGUALES'' as nombrecompleto,  '''' as nombre_concepto, '''' as detalle,
			sum(mov.valor_db), sum(mov.valor_cr) as valor_cr, cont.estado as estado, 3 as encabezado, 0.00 as total,  tip.fuentes_id as tipodocumento, tip.prefijo, cont.id
			from cont_documentos cont, contabilidad_mov mov, contabilidad_tipos_documentos tip 
			where tip.fuentes_id in ',  tiposdoc, ' and (cont.fecha between ''', in_fdesde, ''' and ''', in_fhasta, ''') and cont.estado in ', consulta, '
			and mov.documento_id = cont.id  and tip.id = cont.tipo_documento_id
			group by cont.numero, cont.fecha, cont.estado, tip.fuentes_id, tip.prefijo, cont.id order by fecha, numero, encabezado; ');
	else
		lsql := concat(
			'select null::varchar as numero, null::date as fecha, puc."codigo", puc."nombre", null::varchar as documento, null::varchar as nombrecompleto, 
			null::varchar as nombre_concepto, null::varchar as detalle, sum(mov.valor_db) as valor_db, sum(mov.valor_cr) as valor_cr, null::integer as estado, 
			null::integer as encabezado, sum(mov.valor_db - mov.valor_cr) as total,  tip.fuentes_id  as tipodocumento, tip.prefijo, cont.id
			from cont_documentos cont, contabilidad_mayor puc, contabilidad_mov mov, contabilidad_tipos_documentos tip
			where (cont.fecha between ''', in_fdesde, ''' and ''', in_fhasta, ''') and cont.estado =2 and
			mov.documento_id = cont.id and 
			mov.mayor_id = puc.id  group by  puc."codigo", puc."nombre",tip.fuentes_id, tip.prefijo, cont.id;');
	end if;
	--raise notice '%', lsql;
	return QUERY EXECUTE lsql;			
END
$function$
;

-- Permissions

ALTER FUNCTION public.getcomprobante(_int4, varchar, varchar, int4, int4, int4, int4, int4) OWNER TO postgres;
GRANT ALL ON FUNCTION public.getcomprobante(_int4, varchar, varchar, int4, int4, int4, int4, int4) TO postgres;
