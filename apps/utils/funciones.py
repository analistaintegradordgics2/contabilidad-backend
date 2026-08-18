

class Funciones:

    @staticmethod
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

    @staticmethod
    def resolver_fk(value, attr_name, instance):
        """
        Convierte un entero ID a instancia de modelo si el campo es ForeignKey.
        Django's ForeignKey espera una instancia, no un ID puro.
        
        :param value: Valor a verificar (puede ser int o instancia)
        :param attr_name: Nombre del atributo/campo en el modelo
        :param instance: Instancia del modelo donde está el campo
        :return: Instancia de modelo si value es int y es FK, sino el valor original
        """
        if isinstance(value, int):
            try:
                field = instance._meta.get_field(attr_name)
                if field.is_relation:
                    related_model = field.related_model
                    return related_model.objects.get(pk=value)
            except Exception:
                pass
        return value