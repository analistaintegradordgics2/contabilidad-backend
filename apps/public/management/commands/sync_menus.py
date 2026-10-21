import importlib

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.public.models import Menu, PermisosMenuAcciones


class Command(BaseCommand):
    help = "Sincroniza menús, permisos y relaciona las acciones con su grupo desde menus.py."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Iniciando sincronización de menús y grupos..."))
        count_sync = 0

        for app in apps.get_app_configs():
            module_name = f"{app.name}.menus"
            try:
                modulo = importlib.import_module(module_name)
            except ModuleNotFoundError as e:
                # Omitir silenciosamente cuando la app no contiene menus.py
                if e.name == module_name or module_name in str(e):
                    continue
                self.stdout.write(self.style.WARNING(f"[WARN] Error de importación en {module_name}: {e}"))
                continue
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"[ERROR] Excepción cargando {module_name}: {e}"))
                continue

            menus = getattr(modulo, "MENUS", [])
            # Grupo definido a nivel de módulo en menus.py (ej: GRUPO = "Gestión Contable")
            grupo_modulo = getattr(modulo, "GRUPO", None)

            if menus:
                self.stdout.write(self.style.SUCCESS(f"[OK] Sincronizando menús de app: {app.name}"))
                for menu_data in menus:
                    # El grupo puede venir en el diccionario raíz o a nivel de módulo
                    grupo_nombre = menu_data.get("grupo") or grupo_modulo or menu_data.get("titulo")
                    grupo = self.obtener_o_crear_grupo(grupo_nombre)
                    self.sincronizar_menu(menu_data, padre=None, grupo=grupo)
                count_sync += 1

        self.stdout.write(self.style.SUCCESS(f"Sincronización finalizada exitosamente en {count_sync} módulos."))

    def obtener_o_crear_grupo(self, nombre):
        """Busca el grupo coincidente en auth_group o lo crea."""
        if not nombre:
            return None

        nombre_limpio = nombre.strip()

        # Buscar coincidencia exacta o case-insensitive
        grupo = Group.objects.filter(name__iexact=nombre_limpio).first()
        if not grupo:
            grupo, _ = Group.objects.get_or_create(name=nombre_limpio)
        return grupo

    def sincronizar_menu(self, data, padre=None, grupo=None):
        codigo = data.get("codigo")
        if not codigo:
            return

        # Si el submenú redefine explícitamente su grupo, lo tomamos; sino hereda el del padre
        if data.get("grupo"):
            grupo = self.obtener_o_crear_grupo(data.get("grupo"))

        # Buscar si ya existen registros de menú con el mismo código
        existing = list(Menu.objects.filter(codigo=codigo))

        if existing:
            menu = existing[0]

            if len(existing) > 1:
                for extra in existing[1:]:
                    self.stdout.write(
                        self.style.WARNING(f"   [LIMPIEZA] Eliminando registro duplicado de menú ID {extra.id} (código: '{codigo}')")
                    )
                    extra.delete()

            menu.titulo = data.get("titulo", menu.titulo)
            menu.permiso = data.get("permiso", menu.permiso)
            menu.ruta = data.get("ruta", menu.ruta)
            menu.icono = data.get("icono", menu.icono)
            menu.menu_padre = padre
            menu.orden = data.get("orden", menu.orden or 0)
            menu.save()
            self.stdout.write(f"   [ACTUALIZADO] {menu.titulo} ({codigo}) -> Grupo: {grupo.name if grupo else 'None'}")
        else:
            menu = Menu.objects.create(
                codigo=codigo,
                titulo=data.get("titulo"),
                permiso=data.get("permiso"),
                ruta=data.get("ruta"),
                icono=data.get("icono"),
                menu_padre=padre,
                orden=data.get("orden", 0)
            )
            self.stdout.write(self.style.SUCCESS(f"   [NUEVO] {menu.titulo} ({codigo}) -> Grupo: {grupo.name if grupo else 'None'}"))

        # Sincronizar permisos y acciones del menú con su grupo
        self.crear_permisos(menu, data, grupo)

        # Procesar menús hijos recursivamente manteniendo el mismo grupo
        for hijo in data.get("children", []):
            self.sincronizar_menu(hijo, menu, grupo)

    def crear_permisos(self, menu, data, grupo=None):
        if not data.get("permiso"):
            return

        content_type = ContentType.objects.get_for_model(Menu)

        for accion in data.get("acciones", []):
            permiso_codename = f'{data["permiso"]}_{accion["codigo"]}'
            permiso, _ = Permission.objects.get_or_create(
                codename=permiso_codename,
                content_type=content_type,
                defaults={
                    "name": f'{data["titulo"]} - {accion["nombre"]}'
                }
            )

            existing_pma = list(PermisosMenuAcciones.objects.filter(menu=menu, accion=accion["codigo"]))
            if existing_pma:
                pma = existing_pma[0]
                if len(existing_pma) > 1:
                    for extra_pma in existing_pma[1:]:
                        extra_pma.delete()
                pma.permiso = permiso
                pma.grupo = grupo
                pma.save()
            else:
                PermisosMenuAcciones.objects.create(
                    menu=menu,
                    accion=accion["codigo"],
                    permiso=permiso,
                    grupo=grupo
                )
