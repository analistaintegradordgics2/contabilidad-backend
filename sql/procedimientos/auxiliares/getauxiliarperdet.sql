-- DROP FUNCTION public.getauxiliarperdet(int4, int4, int4, int4);

CREATE OR REPLACE FUNCTION public.getauxiliarperdet(in_anio integer, in_mesi integer, in_mesf integer, in_per integer)
 RETURNS TABLE(id bigint, tipo character varying, numero character varying, fecha date, docref character varying, concepto character varying, detalle character varying, valor_db numeric, valor_cr numeric, saldo numeric, color integer, fuentes_id bigint, observa character varying, base numeric)
 LANGUAGE plpgsql
AS $function$
DECLARE
	------------------------------------------------------------------------------------------------------------------------
	--  Variables locales adicionales
	------------------------------------------------------------------------------------------------------------------------
	tienetran	bit = 1;
	err_pa		varchar(100);
	err_linea	varchar(100);
	l_resultado varchar(100);
	lccursor	varchar(30);
	lnnumero 	numeric(18,0);
	lsql		character varying;
	sumbase 	decimal (18,2);
	sumasaldo decimal (18,2) default 0;
	curdatos1 	record;
	curdatos2 	record;
BEGIN
	RETURN QUERY 
	SELECT enc.id AS id, RTRIM(doc.tipo)::VARCHAR AS tipo, RTRIM(enc.numero)::VARCHAR AS numero, enc.fecha AS fecha, 
		CONCAT(cs."codigo",'  [ ', LTRIM(cs."nombre"),' ]')::VARCHAR AS docref, co.codigo::VARCHAR AS concepto, RTRIM(mov.detalle)::VARCHAR AS detalle,
		coalesce(mov.valor_db, 0) AS valor_db, coalesce(mov.valor_cr, 0) AS valor_cr, (0)::numeric AS saldo, (0) AS color, doc.fuentes_id AS fuentes_id, ('')::VARCHAR AS observa, 
		mov.base::DECIMAL
	FROM cont_documentos enc, contabilidad_mov mov, contabilidad_tipos_documentos doc, contabilidad_conceptos co, contabilidad_mayor cs   
	WHERE (EXTRACT(YEAR FROM enc.fecha ) = in_anio) 
	AND (EXTRACT(MONTH FROM enc.fecha) BETWEEN in_mesi AND in_mesf) 
	AND enc.estado = 2 
	AND mov.persona_id = in_per 
	AND enc.id = mov.documento_id 
	AND enc.tipo_documento_id = doc.id 
	AND mov.concepto_id = co.id 
	AND mov.mayor_id = cs.id 
	ORDER BY fecha, enc.numero, co.id asc;
END
$function$
;
