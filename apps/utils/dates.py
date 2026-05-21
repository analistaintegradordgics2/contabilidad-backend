import datetime
import calendar


class Fecha:

    @staticmethod
    def add_fecha(date_time, valor, opc='month'):
        """
        Suma días, meses, horas o minutos a una fecha.
        """

        # Si no envían fecha usa la actual
        if not date_time:
            date_time = datetime.datetime.now()

        # Convertir string a datetime
        if isinstance(date_time, str):
            try:
                date_time = datetime.datetime.strptime(
                    date_time,
                    '%Y-%m-%d %H:%M:%S'
                )
            except ValueError:
                raise ValueError("Formato de fecha inválido. Use YYYY-MM-DD HH:MM:SS")

        if opc == 'month':
            month = date_time.month - 1 + valor
            year = date_time.year + month // 12
            month = month % 12 + 1

            day = min(
                date_time.day,
                calendar.monthrange(year, month)[1]
            )

            return datetime.date(year, month, day)

        if opc == 'day':
            return date_time + datetime.timedelta(days=valor)

        if opc == 'hours':
            return date_time + datetime.timedelta(hours=valor)

        if opc == 'minutes':
            return date_time + datetime.timedelta(minutes=valor)

        raise ValueError("Opción inválida: use month, day, hours o minutes")

    @staticmethod
    def date_system(timestamp=True):
        """
        Retorna fecha actual.
        """
        now = datetime.datetime.now()
        return now if timestamp else now.strftime("%Y-%m-%d")