from .list import lists
from apps.parametros.models.parametrizacion import Parametros
from apps.parametros.models.ubicacion import Ciudad


class NumeroA():
    MONEDA_SINGULAR = 'peso'
    MONEDA_PLURAL = 'pesos'

    CENTIMOS_SINGULAR = 'centavo'
    CENTIMOS_PLURAL = 'centavos'

    MAX_NUMERO = 999999999999

    UNIDADES = (
        '',
        'uno',
        'dos',
        'tres',
        'cuatro',
        'cinco',
        'seis',
        'siete',
        'ocho',
        'nueve'
    )

    DECENAS = (
        'diez',
        'once',
        'doce',
        'trece',
        'catorce',
        'quince',
        'dieciseis',
        'diecisiete',
        'dieciocho',
        'diecinueve'
    )

    DIEZ_DIEZ = (
        'cero',
        'diez',
        'veinte',
        'treinta',
        'cuarenta',
        'cincuenta',
        'sesenta',
        'setenta',
        'ochenta',
        'noventa'
    )

    CIENTOS = (
        '_',
        'ciento',
        'doscientos',
        'trescientos',
        'cuatroscientos',
        'quinientos',
        'seiscientos',
        'setecientos',
        'ochocientos',
        'novecientos'
    )

    def numero_a_letras(self,numero):
        numero_entero = int(numero)
        if numero_entero == 0 :
            return "cero"
        
        if numero_entero > self.MAX_NUMERO:
            raise OverflowError('Número demasiado alto')
        if numero_entero < 0:
            return 'menos %s' % self.numero_a_letras(abs(numero))
        letras_decimal = ''
        parte_decimal = int(round((abs(numero) - abs(numero_entero)) * 100))
        if parte_decimal > 9:
            letras_decimal = 'punto %s' % self.numero_a_letras(parte_decimal)
        elif parte_decimal > 0:
            letras_decimal = 'punto cero %s' % self.numero_a_letras(parte_decimal)
        if (numero_entero <= 99):
            resultado = self.leer_decenas(numero_entero)
        elif (numero_entero <= 999):
            resultado = self.leer_centenas(numero_entero)
        elif (numero_entero <= 999999):
            #pdb.set_trace()
            resultado = self.leer_miles(numero_entero)
        elif (numero_entero <= 999999999):
            resultado = self.leer_millones(numero_entero)
        else:
            resultado = self.leer_millardos(numero_entero)
        resultado = resultado.replace('uno mil', 'un mil')
        resultado = resultado.strip()
        resultado = resultado.replace(' _ ', ' ')
        resultado = resultado.replace('  ', ' ')
        if parte_decimal > 0:
            resultado = '%s %s' % (resultado, self.letras_decimal)
        return resultado

    def numero_a_moneda(self,numero):
        numero_entero = int(numero)
        parte_decimal = int(round((abs(numero) - abs(numero_entero)) * 100))
        centimos = ''
        if parte_decimal == 1:
            centimos = self.CENTIMOS_SINGULAR
        else:
            centimos = self.CENTIMOS_PLURAL
        moneda = ''
        if numero_entero == 1:
            moneda = self.MONEDA_SINGULAR
        else:
            moneda = self.MONEDA_PLURAL
        letras = self.numero_a_letras(numero_entero)
        letras = letras.replace('uno', 'un')
        letras_decimal = ''
        if parte_decimal > 0 :
            letras_decimal = 'con %s %s' % (self.numero_a_letras(parte_decimal).replace('uno', 'un'), centimos)
        letras = '%s %s %s' % (letras, moneda, letras_decimal)
        return letras

    def mes_letra(self,numero):
        numero_letras = ''
        if numero != None and numero != "" :
            if int(numero) < 10 :
                numero = '0' + str(int(numero))
            elif isinstance(numero, int):
                numero = str(numero)

        if numero == '01':
            numero_letras = 'ENERO'
        elif numero == '02':
            numero_letras = 'FEBRERO'
        elif numero == '03':
            numero_letras = 'MARZO'
        elif numero == '04':
            numero_letras = 'ABRIL'
        elif numero == '05':
            numero_letras = 'MAYO'
        elif numero == '06':
            numero_letras = 'JUNIO'
        elif numero == '07':
            numero_letras = 'JULIO'
        elif numero == '08':
            numero_letras = 'AGOSTO'
        elif numero == '09':
            numero_letras = 'SEPTIEMBRE'
        elif numero == '10':
            numero_letras = 'OCTUBRE'
        elif numero == '11':
            numero_letras = 'NOVIEMBRE'
        elif numero == '12':
            numero_letras = 'DICIEMBRE'
        elif numero == '13':
            numero_letras = 'CIERRE'

        return numero_letras
    
    def dias_a_letras(self,dia):
        dia_letras = ""

        if dia == '1' or dia == '01' :
            dia_letras = 'UN'
        elif dia == '2' or dia == '02' :
            dia_letras = 'DOS'
        elif dia == '3' or dia == '03' :
            dia_letras = 'TRES'
        elif dia == '4' or dia == '04' :
            dia_letras = 'CUATRO'
        elif dia == '5' or dia == '05' :
            dia_letras = 'CINCO'
        elif dia == '6' or dia == '06' :
            dia_letras = 'SEIS'
        elif dia == '7' or dia == '07' :
            dia_letras = 'SIETE'
        elif dia == '8' or dia == '08' :
            dia_letras = 'OCHO'
        elif dia == '9' or dia == '09' :
            dia_letras = 'NUEVE'
        elif dia == '10' :
            dia_letras = 'DIEZ'
        elif dia == '11' :
            dia_letras = 'ONCE'
        elif dia == '12' :
            dia_letras = 'DOCE'
        elif dia == '13' :
            dia_letras = 'TRECE'
        elif dia == '14' :
            dia_letras = 'CATORCE'
        elif dia == '15' :
            dia_letras = 'QUINCE'
        elif dia == '16' :
            dia_letras = 'DIECISÉIS'
        elif dia == '17' :
            dia_letras = 'DIECISIETE'
        elif dia == '18' :
            dia_letras = 'DIECIOCHO'
        elif dia == '19' :
            dia_letras = 'DIECINUEVE'
        elif dia == '20' :
            dia_letras = 'VEINTE'
        elif dia == '21' :
            dia_letras = 'VEINTIUN'
        elif dia == '22' :
            dia_letras = 'VEINTIDÓS'
        elif dia == '23' :
            dia_letras = 'VEINTITRÉS'
        elif dia == '24' :
            dia_letras = 'VEINTICUATRO'
        elif dia == '25' :
            dia_letras = 'VEINTICINCO'
        elif dia == '26' :
            dia_letras = 'VEINTISÉIS'
        elif dia == '27' :
            dia_letras = 'VEINTISIETE'
        elif dia == '28' :
            dia_letras = 'VEINTIOCHO'
        elif dia == '29' :
            dia_letras = 'VEINTINUEVE'
        elif dia == '30' :
            dia_letras = 'TREINTA'
        elif dia == '31' :
            dia_letras = 'TREINTA Y UN'

        return dia_letras
        

    def leer_decenas(self,numero):
        if numero < 10:
            return self.UNIDADES[numero]
        decena, unidad = divmod(numero, 10)
        if numero <= 19:
            resultado = self.DECENAS[unidad]
        elif numero <= 29:
            resultado = 'veinte%s' % self.UNIDADES[unidad]
        else:
            resultado = self.DIEZ_DIEZ[decena]
            if unidad > 0:
                resultado = '%s y %s' % (resultado, self.UNIDADES[unidad])
        return resultado

    def leer_centenas(self,numero):
        centena, decena = divmod(numero, 100)
        if numero == 0:
            resultado = 'cien'
        else:
            resultado = self.CIENTOS[centena]
            if decena > 0:
                resultado = '%s %s' % (resultado, self.leer_decenas(decena))
        return resultado

    def leer_miles(self,numero):
        
        millar, centena = divmod(numero, 1000)
        
        resultado = ''
        if (millar == 1):
            resultado = ''
        if (millar >= 2) and (millar <= 9):
            resultado = self.UNIDADES[millar]
        elif (millar >= 10) and (millar <= 99):
            resultado = self.leer_decenas(millar)
        elif (millar >= 100) and (millar <= 999):
           
            resultado = self.leer_centenas(millar)
        resultado = '%s mil' % resultado
        if centena > 0:
            resultado = '%s %s' % (resultado, self.leer_centenas(centena))
        return resultado

    def leer_millones(self,numero):
        millon, millar = divmod(numero, 1000000)
        resultado = ''
        if (millon == 1):
            resultado = ' un millon '
        if (millon >= 2) and (millon <= 9):
            resultado = self.UNIDADES[millon]
        elif (millon >= 10) and (millon <= 99):
            resultado = self.leer_decenas(millon)
        elif (millon >= 100) and (millon <= 999):
            resultado = self.leer_centenas(millon)
        if millon > 1:
            resultado = '%s millones' % resultado
        if (millar > 0) and (millar <= 999):
            resultado = '%s %s' % (resultado, self.leer_centenas(millar))
        elif (millar >= 1000) and (millar <= 999999):
            resultado = '%s %s' % (resultado, self.leer_miles(millar))
        return resultado

    def leer_millardos(self,numero):
        millardo, millon = divmod(numero, 1000000)
        return '%s millones %s' % (self.leer_miles(millardo), self.leer_millones(millon))
    
    def mes_abreviado(self, numero) :
        
        numero_letras = ""

        if numero == '01':
            numero_letras = 'ENE'
        elif numero == '02':
            numero_letras = 'FEB'
        elif numero == '03':
            numero_letras = 'MAR'
        elif numero == '04':
            numero_letras = 'ABR'
        elif numero == '05':
            numero_letras = 'MAY'
        elif numero == '06':
            numero_letras = 'JUN'
        elif numero == '07':
            numero_letras = 'JUL'
        elif numero == '08':
            numero_letras = 'AGO'
        elif numero == '09':
            numero_letras = 'SEP'
        elif numero == '10':
            numero_letras = 'OCT'
        elif numero == '11':
            numero_letras = 'NOV'
        elif numero == '12':
            numero_letras = 'DIC'
        
        return numero_letras
    
    def numero_a_positivo(self, numero) :
        try :
            # parametro numero debe ser entero o decimal
            if numero < 0 :
                numero = (numero * -1)
            return numero
        except :
            return numero
    def format_fecha(self, fecha, tipo):
        fecha_format = ""
        if tipo == 1 :
            listas = lists()
            dia_nombre = [item["nombre"] for item in listas.dia_semana if item["num_dia"] == int(fecha.strftime("%w"))][0]
            mes_letra = [item["nombre"] for item in listas.mes_letra if item["mes"] == int(fecha.month)][0]
            fecha_format = "{}, {} de {} de {}".format(dia_nombre, fecha.strftime("%d"), mes_letra, fecha.strftime("%Y"))
        return fecha_format

def get_ciudad_inmo() :
    try:
        ciudad_empresa = Parametros.objects.filter(parametro='ciudad_empresa').first().valor
        if ciudad_empresa == None :
            ciudad_empresa = "Bucaramanga"
        else :
            ciudad_empresa = Ciudad.objects.get(pk=ciudad_empresa)
            if ciudad_empresa == None :
                ciudad_empresa = "Bucaramanga"
            else :
                ciudad_empresa = ciudad_empresa.nombre.lower().capitalize()
        
        return ciudad_empresa
    except :
        return "Bucaramanga"
