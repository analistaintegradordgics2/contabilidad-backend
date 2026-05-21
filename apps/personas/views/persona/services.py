from django.db import transaction
from django.shortcuts import get_object_or_404

from apps.personas.models.persona import Persona, PersonaTipoPersona, PersonaTributario
from apps.personas.models.contacto import Telefono, Direccion

from apps.personas.serializers.persona import PersonaModelSerializer, PersonaTributarioSerializer
from apps.personas.serializers.contacto import (
    TelefonoModelSerializer,
    DirecionModelSerializer
)


class PersonaService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(data, user_id=None):
        import pdb
        persona_data = data.get('persona')
        # pdb.set_trace()
        telefonos = persona_data['telefonos']
        direcciones = persona_data['direcciones']
        tributario = persona_data['tributario']
        tipos = data.get('tipopersonas', [])

        persona = PersonaService._guardar_persona(persona_data)

        PersonaService._sync_relaciones(
            persona,
            telefonos,
            Telefono,
            TelefonoModelSerializer,
            campo_validacion="valor"
        )

        PersonaService._sync_relaciones(
            persona,
            direcciones,
            Direccion,
            DirecionModelSerializer,
            campo_validacion="descripcion"
        )

        PersonaService._guardar_tipos(persona, tipos)

        PersonaService._guardar_tributario(
            persona,
            tributario
        )

        return persona


    # ==============================
    # PERSONA
    # ==============================

    @staticmethod
    def _guardar_persona(persona_data):

        if persona_data.get('id'):
            persona = get_object_or_404(Persona, pk=persona_data['id'])
            serializer = PersonaModelSerializer(persona, data=persona_data)
        else:
            serializer = PersonaModelSerializer(data=persona_data)

        serializer.is_valid(raise_exception=True)
        return serializer.save()


    # ==============================
    # RELACIONES GENERICAS 
    # ==============================

    @staticmethod
    def _sync_relaciones(persona, items, model, serializer_class, campo_validacion):

        ids_enviados = []

        for item in items:

            if not item.get(campo_validacion):
                continue

            item['persona'] = persona.id
            obj = None

            if item.get('id'):
                obj = model.objects.filter(pk=item['id']).first()
                ids_enviados.append(item['id'])

            serializer = serializer_class(obj, data=item) if obj else serializer_class(data=item)
            serializer.is_valid(raise_exception=True)
            instance = serializer.save()

            ids_enviados.append(instance.id)

        model.objects.filter(persona=persona).exclude(id__in=ids_enviados).delete()


    # ==============================
    # TIPOS PERSONA
    # ==============================

    @staticmethod
    def _guardar_tipos(persona, tipos):

        PersonaTipoPersona.objects.filter(persona=persona).exclude(
            tipo_persona__in=tipos
        ).delete()

        existentes = set(
            PersonaTipoPersona.objects.filter(persona=persona)
            .values_list('tipo_persona_id', flat=True)
        )

        nuevos = [
            PersonaTipoPersona(persona=persona, tipo_persona_id=tipo)
            for tipo in tipos if tipo not in existentes
        ]

        PersonaTipoPersona.objects.bulk_create(nuevos)


    # ==============================
    # LISTA NEGRA
    # ==============================

    @staticmethod
    def cambiar_lista_negra(persona_id, lista_negra):

        persona = get_object_or_404(Persona, pk=persona_id)

        persona.lista_negra = lista_negra
        persona.save(update_fields=['lista_negra'])

        return persona
    
    @staticmethod
    def _guardar_tributario(persona, tributario_data):

        if not tributario_data:
            return

        tributario_data['persona'] = persona.id

        tributario = PersonaTributario.objects.filter(
            persona=persona
        ).first()

        serializer = PersonaTributarioSerializer(
            tributario,
            data=tributario_data
        ) if tributario else PersonaTributarioSerializer(
            data=tributario_data
        )

        serializer.is_valid(raise_exception=True)

        serializer.save()