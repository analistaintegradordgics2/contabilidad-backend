class SaldosService:

    @staticmethod
    def _obtener_campo_saldo_inicio(mes) -> str:
        if mes == 1:
            return 'sali'
        else:
            if mes < 10:
                return "sal0{}".format((mes - 1))
            else:
                if (mes - 1) < 10:
                    return "sal0{}".format((mes - 1))
                else:
                    return "sal{}".format((mes - 1))


    @staticmethod
    def _obtener_campo_saldo_fin(mes) -> str:
        if mes < 10:
            return "sal0{}".format(mes)
        else:
            return "sal{}".format(mes)