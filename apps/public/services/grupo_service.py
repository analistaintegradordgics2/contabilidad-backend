from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission

from apps.public.models import Menu, PermisosMenuAcciones

User = get_user_model()


class GrupoService:

    @staticmethod
    def obtener_grupos_lista():
        """Retorna la lista básica de todos los grupos."""
        return [
            {
                "id": item.id,
                "nombre": item.name
            }
            for item in Group.objects.all().order_by("id")
        ]

    @staticmethod
    def obtener_detalle_grupos(user_id=None):
        """
        Retorna la estructura jerárquica Grupos -> Menus -> Acciones (Permisos),
        utilizando la llave foránea `grupo_id` de `public_permisos_menu_acciones`.

        Si user_id != '0' y no es None:
          - Marca el grupo con select=True si el usuario pertenece al grupo.
          - Marca las acciones con select=True si:
            * El usuario tiene el permiso asignado en user_permissions, O
            * El usuario pertenece al grupo (relación del usuario con el grupo).
          - Marca los menús con select=True si tienen acciones seleccionadas.
        Si user_id == '0' o None:
          - Todo inicia con select=False (modo creación).
        """
        user_group_ids = set()
        user_perm_ids = set()

        es_edicion = user_id is not None and str(user_id) != "0"
        if es_edicion:
            try:
                usuario = User.objects.get(pk=user_id)
                user_group_ids = set(usuario.groups.values_list("id", flat=True))
                user_perm_ids = set(usuario.user_permissions.values_list("id", flat=True))
            except User.DoesNotExist:
                return None

        grupos_qs = Group.objects.all().order_by("id")

        permisos_por_codename = {p.codename: p.id for p in Permission.objects.all()}
        menus_dict = {m.id: m for m in Menu.objects.all()}

        # ------------------------------------------------------------------ #
        # Calcular cadena de permisos padres para cada menú                  #
        # ------------------------------------------------------------------ #
        permisos_padres_por_menu = {}
        for m_id, m in menus_dict.items():
            padres = []
            curr = m
            if curr.permiso and curr.permiso in permisos_por_codename:
                padres.append(permisos_por_codename[curr.permiso])

            while curr.menu_padre_id:
                curr = menus_dict.get(curr.menu_padre_id)
                if not curr:
                    break
                if curr.permiso and curr.permiso in permisos_por_codename:
                    padres.append(permisos_por_codename[curr.permiso])
            permisos_padres_por_menu[m_id] = padres

        # ------------------------------------------------------------------ #
        # Agrupar acciones y menús usando la llave foránea `grupo_id`        #
        # Estructura: grupo_id -> { menu_id: { info_menu, acciones: [...] } }#
        # ------------------------------------------------------------------ #
        pma_qs = PermisosMenuAcciones.objects.filter(
            grupo__isnull=False,
            menu__isnull=False,
            permiso__isnull=False
        ).select_related("menu", "permiso", "grupo").order_by("menu_id", "id")

        grupos_menus_data = {}
        for pma in pma_qs:
            g_id = pma.grupo_id
            m_id = pma.menu_id

            if g_id not in grupos_menus_data:
                grupos_menus_data[g_id] = {}

            if m_id not in grupos_menus_data[g_id]:
                menu_obj = menus_dict.get(m_id)
                permiso_menu_id = permisos_por_codename.get(menu_obj.permiso) if menu_obj else None
                padres = permisos_padres_por_menu.get(m_id, [])

                grupos_menus_data[g_id][m_id] = {
                    "menu_id": m_id,
                    "menu": menu_obj.titulo if menu_obj else "",
                    "permiso_menu_id": permiso_menu_id,
                    "permiso_menu_padre": padres,
                    "acciones": []
                }

            grupos_menus_data[g_id][m_id]["acciones"].append({
                "id": pma.id,
                "accion": pma.accion,
                "permiso": pma.permiso_id
            })

        # ------------------------------------------------------------------ #
        # Armar respuesta agrupada Grupos -> Menús -> Acciones               #
        # ------------------------------------------------------------------ #
        data = []
        for grupo in grupos_qs:
            grupo_select = grupo.id in user_group_ids
            menus_del_grupo = grupos_menus_data.get(grupo.id, {})

            array_menus = []
            for m_id, m_data in menus_del_grupo.items():
                acciones_copia = []
                menu_select = False

                for acc in m_data["acciones"]:
                    acc_select = False
                    if es_edicion:
                        # Seleccionado si el usuario tiene el permiso directo
                        # O si el usuario pertenece al grupo
                        if (acc["permiso"] in user_perm_ids) or grupo_select:
                            acc_select = True
                            menu_select = True

                    acciones_copia.append({
                        "id": acc["id"],
                        "accion": acc["accion"],
                        "permiso": acc["permiso"],
                        "select": acc_select
                    })

                array_menus.append({
                    "group_id": grupo.id,
                    "permiso_menu_id": m_data["permiso_menu_id"],
                    "permiso_menu_padre": m_data["permiso_menu_padre"],
                    "menu": m_data["menu"],
                    "acciones": acciones_copia,
                    "select": menu_select
                })

            data.append({
                "id": grupo.id,
                "nombre": grupo.name,
                "select": grupo_select,
                "menus": array_menus
            })

        return data
