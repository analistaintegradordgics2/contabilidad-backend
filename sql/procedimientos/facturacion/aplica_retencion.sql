CREATE OR REPLACE FUNCTION aplica_retencion(
    in_persona_id integer,
    in_tipo_retencion integer
)
RETURNS boolean
LANGUAGE plpgsql
AS
$$
DECLARE
    v_aplica boolean := false;
BEGIN

    SELECT CASE in_tipo_retencion
        -- 1: ReteFuente, 2: ReteIVA, 3: ReteICA.
        WHEN 1 THEN COALESCE(pt.retefuente, false)
        WHEN 2 THEN COALESCE(pt.reteiva, false)
        WHEN 3 THEN COALESCE(pt.reteica, false)
        ELSE false
    END
    INTO v_aplica
    FROM personas_personatributario pt
    WHERE pt.persona_id = in_persona_id;

    RETURN COALESCE(v_aplica,false);

END;
$$;
