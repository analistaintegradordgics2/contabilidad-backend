from django import template
from apps.utils.util import NumeroA
import os
import base64
import re
import locale
import pdb
from django.contrib.humanize.templatetags.humanize import intcomma
import re
import datetime

register = template.Library()

locale.setlocale( locale.LC_ALL, '' )

def image_as_base64(image_file, format='png'):
    """
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """
    if not os.path.isfile(image_file):
        return None
    
    encoded_string = ''
    with open(image_file, 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read())
        # pdb.set_trace()
    return 'data:image/%s;base64,%s' % (format, encoded_string)

@register.filter
def numero_mes_letra(text):
    try:
        numero = NumeroA()
        if text < 10 :
            mes = '0{}'.format(text)
            return numero.mes_letra(mes)
        else :
            return numero.mes_letra(str(text))
    except :
        return ''

@register.filter
def numero_a_positivo(val):
    try:
        num = val
        if num < 0 :
            num = val * -1
            return num
        else :
            return val
    except :
        return ''

@register.filter
def numero_a_texto(text):
    #pdb.set_trace()
    try:
        numero = NumeroA()
        return numero.numero_a_letras(text)
    except :
        return ''


@register.filter
def HelpDate(text): 
    try:
        if text is None:
            text = ""
        return text
    except:
        return ""


@register.filter
def Help(text): 
    try:
        if text is None:
            text = ""
        if len(text) > 0:
            text=text.upper()

        return text
    except:
        return ""

@register.filter
def etiquetapre(text): 
    try:
        if text is None:
            text = ""
        #if len(text) > 0:
            # text = "<br/>".join(text.split("\n"))
        return text
    except:
        return ""

        

@register.filter
def FechaVacia(fecha=""):        
    try:
        if fecha is None:
            fecha = ""       
            return fecha 
        return "A "+ fecha
    except:
        return ""
        
@register.filter
def my_float_format(number, decimal_places=0, decimal=','): 
    try:
        result = intcomma(number)
        result += decimal if decimal not in result else ''
        while len(result.split(decimal)[1]) != decimal_places:
            result += '0'
        return "$"+result
    except:
        return ""

@register.filter
def imagen_base64(imagen): 
    try:
        imagen = imagen.path
        #pdb.set_trace()
        extension = os.path.splitext(imagen)[1].replace(".","")
        
        imagen  = image_as_base64(imagen,extension)
        
        #result = re.search("'", imagen).group(1)
        # pdb.set_trace()
        return imagen #result
    except:
        return None


@register.filter
def currency(value, arg = '', symbol = True):


    saved = '.'.join([x for x in locale.getlocale() if x]) or (None, None)
    given = arg and ('.' in arg and str(arg) or str(arg) + '.UTF-8')

    # Workaround for Python bug 1699853 and other possibly related bugs.
    if '.' in saved and saved.split('.')[1].lower() in ('utf', 'utf8'):
        saved = saved.split('.')[0] + '.UTF-8'

    if saved == (None, None) and given == '':
        given = 'en_US.UTF-8'

    try:
        locale.setlocale(locale.LC_ALL, given)

        return locale.currency(value or 0, symbol, True)

    except (TypeError, locale.Error):
        return ''

    finally:
        locale.setlocale(locale.LC_ALL, saved)




@register.filter
def SetMoneda(num, simbolo="$", n_decimales=0,align="left"):
    try:
        if num == '':
            num = 0.00
        # return locale.currency( num, grouping=True )
        if num == None:
            if align=="left":
                return "{} 0.00".format(simbolo)
            else:
                return "0.00 {}".format(simbolo)
        elif num == 0:
            if align=="left":
                return "{} {}".format(simbolo,num)
            else:
                return "{} {}".format(num,simbolo)
        elif num != 0:
            if num != None:
                # return num
                #con abs, nos aseguramos que los dec. sea un positivo.
                n_decimales = abs(n_decimales)    
                #se redondea a los decimales idicados.
                if n_decimales>0:
                    num = round(num, n_decimales)                
                #se divide el entero del decimal y obtenemos los string                
                try:
                    num, dec = str(num).split(".") 
                except:
                    num =  str(num)
                    dec = "00"
                #si el num tiene menos decimales que los que se quieren mostrar,
                #se completan los faltantes con ceros.
                dec += "0" * (n_decimales - len(dec))    
                #se invierte el num, para facilitar la adicion de comas.
                num = num[::-1]    
                #se crea una lista con las cifras de miles como elementos.
                l = [num[pos:pos+3][::-1] for pos in range(0,50,3) if (num[pos:pos+3])]
                l.reverse()    
                #se pasa la lista a string, uniendo sus elementos con comas.
                num = str.join(",", l)    
                #si el numero es negativo, se quita una coma sobrante.
                try:
                    if num[0:2] == "-,":
                        num = "-%s" % num[2:]
                except IndexError:
                    pass    
                #si no se especifican decimales, se retorna un numero entero.
                if not n_decimales:
                    if align=="left":
                        return "%s %s" % (simbolo, num)        
                    else:
                        return "%s %s" % (num, simbolo)        
                if align=="left":
                    return "%s %s.%s" % (simbolo, num, dec)
                else:
                    return "%s.%s %s" % (num, dec,simbolo)
            else:
                if align=="left":
                    return "{} 0.00".format(simbolo)
                else:
                    return "0.00 {}".format(simbolo)
                
        else:
            if align=="left":
                return "{} 0.00".format(simbolo)
            else:
                return "0.00 {}".format(simbolo)
    except:
        if align=="left":
            return "{} 0.00".format(simbolo)
        else:
            return "0.00 {}".format(simbolo)  


@register.simple_tag
def substr(texto,inicial,final):
    try:
        return texto[inicial:final]
    except :
        return ''
   


@register.simple_tag
def SetValorNumerico(num, simbolo="$", n_decimales=0,align="left"):
    try:
        # return locale.currency( num, grouping=True )
        if num == None:
            if align=="left":
                return "{} 0.00".format(simbolo)
            else:
                return "0.00 {}".format(simbolo)
        elif num == 0:
            if align=="left":
                return "{} {}".format(simbolo,num)
            else:
                return "{} {}".format(num,simbolo)
        elif num != 0:
            if num != None:
                # return num
                #con abs, nos aseguramos que los dec. sea un positivo.
                n_decimales = abs(n_decimales)    
                #se redondea a los decimales idicados.
                if n_decimales>0:
                    num = round(num, n_decimales)                
                #se divide el entero del decimal y obtenemos los string                
                try:
                    num, dec = str(num).split(".") 
                except:
                    num =  str(num)
                    dec = "00"
                #si el num tiene menos decimales que los que se quieren mostrar,
                #se completan los faltantes con ceros.
                dec += "0" * (n_decimales - len(dec))    
                #se invierte el num, para facilitar la adicion de comas.
                num = num[::-1]    
                #se crea una lista con las cifras de miles como elementos.
                l = [num[pos:pos+3][::-1] for pos in range(0,50,3) if (num[pos:pos+3])]
                l.reverse()    
                #se pasa la lista a string, uniendo sus elementos con comas.
                num = str.join(",", l)    
                #si el numero es negativo, se quita una coma sobrante.
                try:
                    if num[0:2] == "-,":
                        num = "-%s" % num[2:]
                except IndexError:
                    pass    
                #si no se especifican decimales, se retorna un numero entero.
                if not n_decimales:
                    if align=="left":
                        return "%s %s" % (simbolo, num)        
                    else:
                        return "%s %s" % (num, simbolo)        
                if align=="left":
                    return "%s %s.%s" % (simbolo, num, dec)
                else:
                    return "%s.%s %s" % (num, dec,simbolo)
            else:
                if align=="left":
                    return "{} 0.00".format(simbolo)
                else:
                    return "0.00 {}".format(simbolo)
                
        else:
            if align=="left":
                return "{} 0.00".format(simbolo)
            else:
                return "0.00 {}".format(simbolo)
    except:
        if align=="left":
            return "{} 0.00".format(simbolo)
        else:
            return "0.00 {}".format(simbolo)        


@register.simple_tag
def estado_aprobados(texto='',nestado=True):      
    texto = str(texto)
    # pdb.set_trace()
    
    estado = "APROBADA"
    if texto.find("EN ESTUDIO") >= 0 :
        estado = "EN ESTUDIO" 
    if texto.find("EN ESTUDIO (pre-estudio)") >= 0 :
        estado = "EN ESTUDIO (pre-estudio)" 
    if texto.find("INCOMPLETA") >= 0 :
        estado = "INCOMPLETA" 
    if texto.find("PENDIENTE") >= 0 :
        estado = "PENDIENTE" 
    if texto.find("REGISTRADA") >= 0 :
        estado = "REGISTRADA" 
    if texto.find("SIN REGISTRAR ") >= 0 :
        estado = "SIN REGISTRAR "     
    if texto.find("NO AFIANZABLE") >= 0 :
        estado = "NO AFIANZABLE"
    if texto.find("DESISTIDA") >= 0 :
        estado = "DESISTIDA"
    if texto.find("REESTUDIO") >= 0 :
        estado = "REESTUDIO"
    if texto.find("REVISION JURIDICA") >= 0 :
        estado = "APROBADA"
    if texto.find("APROBA") >= 0 :
        estado = "APROBADA"
    if texto.find("AFIANZADA") >= 0 :
        estado = "APROBADA"
    if texto.find("REPORTADO") >= 0 :
        estado = "APROBADA"
    if texto.find("GESTION DE COBRO") >= 0 :
        estado = "APROBADA"
    if texto.find("PREJURÍDICO") >= 0 :
        estado = "APROBADA"
    if texto.find("JURÍDICO") >= 0 :
        estado = "APROBADA"
    if texto.find("RETIRADO") >= 0 :
        estado = "RETIRADO"
    if texto.find("FINALIZADA") >= 0 :
        estado = "FINALIZADA"
    if texto.find("PRE-APROBADO") >= 0 :
        estado = "PRE-APROBADO"
    
    return estado 

@register.filter
def concat_array(array):    
    text= ''
    for obj in  array :
        text = text + str(obj.numero_solicitud)+", "
    temp = len(text)
    text = text[:temp - 2]
    return text

@register.filter
def tiempoLetras(minutos) :
    valor = '';
    seconds = (minutos * 60)
    ndias   = (minutos / 1440)
    horas   = ((minutos % 1440) / 60)
    minutos = (minutos  % 60)
    
    if ndias > 0 :
        if ndias > 1 :
            valor = str(int(ndias)) + " días"
        if  1 == ndias :
            valor = "Un día"
        else :
            valor += ""

    if horas > 0 :
        if ndias > 0 :
            if valor :
                valor = valor + " y "
        if  horas > 1 :
            valor = valor + str(int(horas)) + " horas"
        else :
            if  ndias > 0 :
                valor = valor + " una hora"
            else :
                valor = valor + " Una hora"

    if minutos > 0 :
        if horas > 0 :
            valor = valor + " con " + str(int(minutos)) + " minutos"
        else :
            valor = valor + " " + str(int(minutos)) + " minutos"
    if '' == valor:
        valor = '0 Minutos'
    return valor

@register.filter
def getDias(minutos) :
    ndias   = (minutos / 1440)
    return int(ndias)

@register.filter
def getHoras(minutos) :
    horas = (minutos / 60)
    return int(horas)
 
@register.simple_tag
def setvar(val=None):
  return val
