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

    SELECT
        CASE

            WHEN in_tipo_retencion = 1 THEN COALESCE(p.retefuente,false)
            WHEN in_tipo_retencion = 2 THEN COALESCE(p.reteica,false)
            WHEN in_tipo_retencion = 3 THEN COALESCE(p.reteiva,false)

            ELSE false

        END
    INTO v_aplica
    FROM personas_persona p
    WHERE p.id = in_persona_id;

    RETURN COALESCE(v_aplica,false);

END;
$$;