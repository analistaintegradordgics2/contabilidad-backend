import logging
from django.db import connection

logger = logging.getLogger("database")


def log_database_error(error, sql=None, params=None, sql_completo=None):

    try:

        logger.exception(
            "Error de base de datos. Tipo=%s Mensaje=%s",
            type(error).__name__,
            str(error)
        )

        if sql:
            logger.error("SQL:\n%s", sql)

        if params:
            logger.error("PARAMS:\n%s", params)
        
        if sql_completo:

            logger.error(
                "SQL COMPLETO:\n%s",
                sql_completo
            )

        if hasattr(error, "pgcode"):
            logger.error("Codigo PG: %s", error.pgcode)

        if hasattr(error, "diag"):

            diag = error.diag

            for attr in dir(diag):

                if attr.startswith("_"):
                    continue

                try:

                    value = getattr(diag, attr)

                    if value:

                        logger.error(
                            "PG_DIAG.%s: %s",
                            attr,
                            value
                        )

                except Exception:
                    pass

    except Exception as log_error:

        logger.error(
            "Error registrando log: %s",
            str(log_error)
        )

def execute_query(sql, params=None):

    try:

        with connection.cursor() as cursor:

            sql_completo = None

            if params:
                try:
                    sql_completo = cursor.mogrify(
                        sql,
                        params
                    ).decode("utf-8")
                except Exception:
                    pass

            cursor.execute(sql, params)

            return cursor.fetchall()

    except Exception as e:

        log_database_error(
            error=e,
            sql=sql,
            params=params,
            sql_completo=sql_completo
        )

        raise


def execute_procedure(sql, params=None):

    return execute_query(
        sql=sql,
        params=params
    )