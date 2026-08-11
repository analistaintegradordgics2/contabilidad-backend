from django.db import transaction
from apps.nomina.models.entidades import Entidad, EntidadCentroCosto
from apps.personas.models.persona import Persona
from apps.personas.services.persona_service import PersonaService
from apps.utils.funciones import Funciones

class EntidadService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(data, user_id):
        """
        Crea o actualiza una Entidad con su Persona asociada y centros de costos.
        Trabaja directamente con modelos, sin serializers.
        Maneja correctamente las relaciones ForeignKey convirtiendo IDs a instancias.
        """
        persona_data = data.get('persona', {})

        if data.get('estado', False):
            persona_data['estado'] = 1
        else:
            persona_data['estado'] = 2

        # Usar PersonaService para manejar la persona (ya tiene su propia lógica de model)
        persona = PersonaService.crear_o_actualizar(data, user_id)

        # Vincular la persona a la entidad
        data['personas'] = persona.id

        if data.get('id'):
            # Actualizar existente
            entidad = Entidad.objects.filter(pk=data['id']).first()
            if not entidad:
                return None
            for attr, value in data.items():
                # Resolver FKs antes de setattr
                value = Funciones.resolver_fk(value, attr, entidad)
                setattr(entidad, attr, value)
            entidad.save()
            qentidad = entidad
        else:
            # Crear nuevo
            data['uc'] = user_id
            data['um'] = user_id
            qentidad = Entidad.objects.create(**data)

        # Manejar centros de costo
        enticcosto = EntidadCentroCosto.objects.filter(entidad_id=qentidad.id)

        if len(enticcosto) == 0:
            # Crear nuevas relaciones
            for item in data.get('entidad_centro_costo', []):
                EntidadCentroCosto.objects.create(
                    entidad=qentidad,
                    centro_costos_id=item.get('centro_costo_id'),
                    uc=user_id
                )
        else:
            # Actualizar relaciones existentes
            for item in data.get('entidad_centro_costo', []):
                ec = EntidadCentroCosto.objects.filter(
                    entidad_id=qentidad.id,
                    centro_costos_id=item.get('centro_costo_id')
                ).first()
                if ec:
                    ec.um = user_id
                    ec.save()

        return qentidad