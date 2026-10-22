from django.db import transaction
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from apps.personas.models.persona import Persona, PersonaTipoPersona
from apps.personas.serializers.persona import PersonaModelSerializer

User = get_user_model()


class UsuarioService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(data, request_user):
        """
        Crea o actualiza un usuario junto con su persona asociada,
        tipos de persona, departamento y permisos/grupos.

        Parámetros de data:
          - usuario  : dict con datos del usuario y su persona anidada
          - permisos : list de grupos con menus/acciones (estructura del endpoint Grupos)
          - departamento : id del departamento (puede ser None)
        """
        usuario_data = data['usuario']
        permisos     = data['permisos']
        departamento = data.get('departamento')

        # ------------------------------------------------------------------ #
        # 1. Usuario                                                          #
        # ------------------------------------------------------------------ #
        if usuario_data['id'] is None:
            user = UsuarioService._crear_usuario(usuario_data)
        else:
            user = UsuarioService._actualizar_usuario(usuario_data)

        # ------------------------------------------------------------------ #
        # 2. Persona                                                          #
        # ------------------------------------------------------------------ #
        query_persona = UsuarioService._crear_o_actualizar_persona(
            usuario_data, user, request_user
        )

        # ------------------------------------------------------------------ #
        # 3. Tipos de persona (ids 11 y 6 fijos para usuarios del sistema)   #
        # ------------------------------------------------------------------ #
        for tipo_id in [3]:
            PersonaTipoPersona.objects.get_or_create(
                persona_id=query_persona.id,
                tipo_persona_id=tipo_id
            )

        # ------------------------------------------------------------------ #
        # 4. Departamento                                                     #
        # ------------------------------------------------------------------ #
        # if departamento is not None:
        #     UsuarioService._asignar_departamento(user, departamento)

        # ------------------------------------------------------------------ #
        # 5. Grupos y permisos de menus/acciones                             #
        # ------------------------------------------------------------------ #
        UsuarioService._asignar_permisos(user, permisos)

        # ------------------------------------------------------------------ #
        # 6. Permisos adicionales: permisos_casos y permisos_ingreso_sistema  #
        # ------------------------------------------------------------------ #
        permisos_extra = (
            usuario_data.get('permisos_casos', [])
            + usuario_data.get('permisos_ingreso_sistema', [])
        )
        UsuarioService._sincronizar_permisos_extra(user, permisos_extra)

        return user, query_persona

    # ======================================================================= #
    # USUARIO                                                                  #
    # ======================================================================= #

    @staticmethod
    def _crear_usuario(usuario_data):
        """Crea un nuevo registro de User."""
        persona_data = usuario_data['persona']
        p_nombre   = persona_data['p_nombre']
        s_nombre   = persona_data.get('s_nombre') or ''
        p_apellido = persona_data['p_apellido']
        s_apellido = persona_data.get('s_apellido') or ''

        user = User()
        user.first_name = f"{p_nombre} {s_nombre}".strip() if s_nombre else p_nombre
        user.last_name  = f"{p_apellido} {s_apellido}".strip() if s_apellido else p_apellido
        user.username   = usuario_data['username']
        user.email      = persona_data['email']
        user.set_password(usuario_data['new_password'])
        user.save()
        return user

    @staticmethod
    def _actualizar_usuario(usuario_data):
        """Actualiza un User existente."""
        persona_data = usuario_data['persona']

        # Calcular n_completo si no viene
        if not persona_data.get('n_completo'):
            p_nombre   = persona_data.get('p_nombre', '')
            s_nombre   = persona_data.get('s_nombre') or ''
            p_apellido = persona_data.get('p_apellido', '')
            s_apellido = persona_data.get('s_apellido') or ''
            persona_data['n_completo'] = (
                f"{p_nombre} {s_nombre} {p_apellido} {s_apellido}".strip()
            )

        user = User.objects.get(pk=usuario_data['id'])

        if persona_data.get('email') and persona_data['email'] != usuario_data.get('email'):
            user.email = persona_data['email']

        p_nombre   = persona_data.get('p_nombre', '')
        s_nombre   = persona_data.get('s_nombre') or ''
        p_apellido = persona_data.get('p_apellido', '')
        s_apellido = persona_data.get('s_apellido') or ''
        user.first_name = f"{p_nombre} {s_nombre}".strip() if s_nombre else p_nombre
        user.last_name  = f"{p_apellido} {s_apellido}".strip() if s_apellido else p_apellido

        if usuario_data.get('new_password'):
            user.set_password(usuario_data['new_password'])

        user.is_active = usuario_data.get('is_active', user.is_active)
        user.save()
        return user

    # ======================================================================= #
    # PERSONA                                                                  #
    # ======================================================================= #

    @staticmethod
    def _crear_o_actualizar_persona(usuario_data, user, request_user):
        """Crea o actualiza la Persona vinculada al usuario."""
        persona_data = usuario_data['persona']

        # Construir n_completo
        pnombre    = (persona_data.get('p_nombre') or '').strip()
        snombre    = (persona_data.get('s_nombre') or '').strip()
        papellido  = (persona_data.get('p_apellido') or '').strip()
        sapellido  = (persona_data.get('s_apellido') or '').strip()

        nombres    = f"{pnombre} {snombre}".strip() if snombre else pnombre
        apellidos  = f"{papellido} {sapellido}".strip() if sapellido else papellido
        persona_data['n_completo'] = f"{apellidos} {nombres}".strip()

        if persona_data.get('id') is None:
            # Nueva persona
            persona_data['email']             = persona_data['email']
            persona_data['usuario']           = user.id
            persona_data['agente_retenedor']  = False
            persona_data['gran_contribuyente']= False
            persona_data['no_contribuyente']  = False
            persona_data['autoretenedor']     = False
            persona_data['reteica']           = False
            persona_data['reteiva']           = False
            persona_data['uc_id']             = request_user.id
            persona_data['um_id']             = None

            serializer = PersonaModelSerializer(data=persona_data)
            serializer.is_valid(raise_exception=True)
            return serializer.save()
        else:
            # Actualizar persona existente
            persona = Persona.objects.get(pk=persona_data['id'])
            persona_data['usuario'] = user.id
            persona_data['uc_id']   = persona.uc_id
            persona_data['um_id']   = request_user.id
            serializer = PersonaModelSerializer(persona, data=persona_data)
            serializer.is_valid(raise_exception=True)
            return serializer.save()

    # ======================================================================= #
    # DEPARTAMENTO                                                             #
    # ======================================================================= #

    @staticmethod
    def _asignar_departamento(user, departamento_id):
        """Asigna o actualiza el departamento del usuario."""
        # UsuariosDepartamentos no está definido como modelo en el proyecto;
        # se mantiene el bloque como referencia para cuando se implemente.
        try:
            from apps.parametros.models.parametrizacion import UsuariosDepartamentos  # noqa
            obj, _ = UsuariosDepartamentos.objects.get_or_create(user=user)
            obj.departamento_id = departamento_id
            obj.save()
        except ImportError:
            pass

    # ======================================================================= #
    # PERMISOS / GRUPOS                                                        #
    # ======================================================================= #

    @staticmethod
    def _asignar_permisos(user, grupos):
        """
        Sincroniza los grupos y permisos de menu/acciones del usuario.

        Estructura esperada de `grupos` (la misma que devuelve GruposViewSet.detalle):
          [
            {
              "id": <group_id>,
              "select": true/false,       # si el usuario debe pertenecer al grupo
              "menus": [
                {
                  "select": true/false,   # si el menu está habilitado
                  "permiso_menu_id": <permission_id>,
                  "permiso_menu_padre": [<permission_id>, ...],
                  "acciones": [
                    { "permiso": <permission_id>, "select": true/false }
                  ]
                }
              ]
            }
          ]
        """
        if not grupos:
            return

        # Limpiar grupos y permisos actuales del usuario
        user.groups.clear()
        user.user_permissions.clear()

        permisos_a_agregar = set()

        for grupo_data in grupos:
            if not grupo_data.get('select'):
                continue

            # Asignar el grupo al usuario
            user.groups.add(grupo_data['id'])

            for menu in grupo_data.get('menus', []):
                if not menu.get('select'):
                    continue

                # Permisos de menús padres
                for permiso_id in menu.get('permiso_menu_padre', []):
                    if permiso_id:
                        permisos_a_agregar.add(permiso_id)

                # Permiso del menú propio
                permiso_menu_id = menu.get('permiso_menu_id')
                if permiso_menu_id:
                    permisos_a_agregar.add(permiso_menu_id)

                # Permisos de acciones seleccionadas
                for accion in menu.get('acciones', []):
                    if accion.get('select') and accion.get('permiso'):
                        permisos_a_agregar.add(accion['permiso'])

        if permisos_a_agregar:
            permisos_qs = Permission.objects.filter(id__in=permisos_a_agregar)
            user.user_permissions.set(permisos_qs)

    @staticmethod
    def _sincronizar_permisos_extra(user, permisos_extra):
        """
        Sincroniza permisos adicionales (permisos_casos, permisos_ingreso_sistema)
        de forma individual: agrega si select=True, elimina si select=False.
        """
        if not permisos_extra:
            return

        permisos_actuales = set(
            user.user_permissions.values_list('id', flat=True)
        )

        agregar  = set()
        eliminar = set()

        for item in permisos_extra:
            permiso_id = item.get('id')
            if not permiso_id:
                continue
            if item.get('select'):
                if permiso_id not in permisos_actuales:
                    agregar.add(permiso_id)
            else:
                if permiso_id in permisos_actuales:
                    eliminar.add(permiso_id)

        if agregar:
            user.user_permissions.add(*Permission.objects.filter(id__in=agregar))
        if eliminar:
            user.user_permissions.remove(*Permission.objects.filter(id__in=eliminar))
