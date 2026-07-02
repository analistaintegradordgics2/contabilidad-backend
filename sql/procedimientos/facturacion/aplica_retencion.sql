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

            WHEN in_tipo_retencion = 1 THEN false
            WHEN in_tipo_retencion = 2 THEN false
            WHEN in_tipo_retencion = 3 THEN false

            ELSE false

        END
    INTO v_aplica
    FROM personas_persona p
    WHERE p.id = in_persona_id;

    RETURN COALESCE(v_aplica,false);

END;
$$;