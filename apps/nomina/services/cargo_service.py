from django.db import transaction
from apps.nomina.models.contratos import Cargo

from apps.utils.funciones import Funciones

class CargoService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(data):
        """
        Crea o actualiza un Cargo directamente con el modelo.
        Maneja correctamente las relaciones ForeignKey convirtiendo IDs a instancias.
        """
        cargo_id = data.get('id')

        if cargo_id:
            # Actualizar existente
            cargo = Cargo.objects.filter(pk=cargo_id).first()
            if not cargo:
                return None
            for attr, value in data.items():
                # Resolver FKs antes de setattr
                value = Funciones.resolver_fk(value, attr, cargo)
                setattr(cargo, attr, value)
            cargo.save()
            return cargo
        else:
            # Crear nuevo
            cargo = Cargo.objects.create(**data)
            return cargo