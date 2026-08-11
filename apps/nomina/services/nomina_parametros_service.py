from django.db import transaction
from datetime import datetime
from apps.nomina.models.parametrizacion import NominaParametros
from apps.parametros.models.parametrizacion import Anio as AnioModel


class NominaParametrosService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(data):
        """
        Crea o actualiza la parametrización de nómina directamente con modelos.
        Actualiza los parámetros y el año configurado.
        """
        # Actualizar parámetros de nómina
        for item in data.get('parametros', []):
            params = NominaParametros.objects.get(pk=item['id'])
            params.valor = item['valor']
            if item.get('grupo') == '7':
                if params.valor is not None:
                    params.comentario = 'actualizado'
            params.save()

        # Actualizar o crear configuración del año actual
        anio_actual = datetime.now().strftime('%Y')

        if data.get('anio', {}).get('actualizado') == False:
            # Crear/actualizar año
            anio_data = data.get('anio', {})
            anio_obj, created = AnioModel.objects.get_or_create(nombre=anio_actual)
            anio_obj.salario_minimo = anio_data.get('salario_minimo', anio_obj.salario_minimo)
            anio_obj.aux_transporte = anio_data.get('aux_transporte', anio_obj.aux_transporte)
            anio_obj.actualizado = anio_data.get('actualizado', False)
            anio_obj.save()
        else:
            # Si ya está actualizado, buscar el año y actualizar sus valores
            anio_obj = AnioModel.objects.filter(nombre=anio_actual).order_by('-id').first()
            if anio_obj:
                anio_obj.salario_minimo = data.get('anio', {}).get('salario_minimo', anio_obj.salario_minimo)
                anio_obj.aux_transporte = data.get('anio', {}).get('aux_transporte', anio_obj.aux_transporte)
                anio_obj.actualizado = data.get('anio', {}).get('actualizado', True)
                anio_obj.save()

        return True