from django.db.models import Q, F, Value
from django.db.models.functions import Concat
from django.shortcuts import get_object_or_404

from apps.personas.models.persona import Persona


TIPOS_DEFAULT = [12, 11, 6]


def _base_select(qs, extra_fields=None):
    fields = {
        'id': F('id'),
        'n_completo': F('n_completo'),
        'documento': F('documento'),
        'documento_nombre': Concat(F('documento'), Value(' - '), F('n_completo'))
    }

    if extra_fields:
        fields.update(extra_fields)

    return qs.values(**fields)


def _apply_search(qs, search, include_email=False):
    if not search:
        return qs

    search = search.strip()

    if search.isdigit():
        return qs.filter(documento__icontains=search)

    qs = qs.annotate(
        pn_pa=Concat('p_nombre', Value(' '), 'p_apellido')
    )

    filters = (
        Q(n_completo__icontains=search.upper()) |
        Q(pn_pa__icontains=search.upper())
    )

    if include_email:
        filters |= Q(email__icontains=search)

    return qs.filter(filters)


# =============================

def select_all_personas(tipos=None):
    tipos = tipos or TIPOS_DEFAULT

    qs = Persona.objects.filter(
        estado=1,
        personas_tipos_personas_persona__tipo_persona__in=tipos
    ).distinct()

    return _base_select(qs)


def select_personas(search=None):
    qs = Persona.objects.filter(estado=1)

    qs = _apply_search(qs, search)

    return _base_select(qs)[:10]


def select_email_personas(search=None):
    qs = Persona.objects.filter(estado=1)

    qs = _apply_search(qs, search, include_email=True)

    return _base_select(qs, extra_fields={
        'email': F('email')
    })[:10]


def buscar_personas_avanzado(search, tipo_persona=None):
    palabras = search.strip().split()

    query = Q(estado=1)

    for palabra in palabras:
        query &= (
            Q(p_nombre__icontains=palabra) |
            Q(s_nombre__icontains=palabra) |
            Q(p_apellido__icontains=palabra) |
            Q(s_apellido__icontains=palabra) |
            Q(n_completo__icontains=palabra) |
            Q(documento__icontains=palabra)
        )

    qs = Persona.objects.filter(query)

    if tipo_persona:
        qs = qs.filter(
            personas_tipos_personas_persona__tipo_persona__in=tipo_persona
        )

    return qs.distinct().order_by('n_completo')[:10]


def get_persona_by_id(persona_id):
    return get_object_or_404(Persona, pk=persona_id)


def get_personas_por_tipo(tipos):
    qs = Persona.objects.filter(
        estado_id=1,
        personas_tipos_personas_persona__tipo_persona__in=tipos
    ).distinct()

    return _base_select(qs)