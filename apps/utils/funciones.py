

class Funciones:
    
    def calcular_digito_verificacion(val: str):
        """
        Calcula el dígito de verificación de un NIT en Colombia.
        
        :param val: NIT en forma de string (solo números).
        :return: Dígito de verificación o None.
        """
        vpri = [0, 3, 7, 13, 17, 19, 23, 29, 37, 41, 43, 47, 53, 59, 67, 71]
        z = len(val)
        x = 0
        for i in range(z):
            y = int(val[i])
            x += y * vpri[z - i]
        y = x % 11
        return 11 - y if y > 1 else y
    