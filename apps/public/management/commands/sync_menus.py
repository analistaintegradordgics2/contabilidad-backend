import importlib

from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.public.models import Menu, PermisosMenuAcciones


class Command(BaseCommand):
    help = "Sincroniza menús y permisos sin duplicar registros ni fallar si ya existen."

    def handle(self, *args, **options):
        self.stdout.write(self.style.MIGRATE_HEADING("Iniciando sincronización de menús..."))
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
            if menus:
                self.stdout.write(self.style.SUCCESS(f"[OK] Sincronizando menús de app: {app.name}"))
                for menu_data in menus:
                    self.sincronizar_menu(menu_data)
                count_sync += 1

        self.stdout.write(self.style.SUCCESS(f"Sincronización finalizada exitosamente en {count_sync} módulos."))

    def sincronizar_menu(self, data, padre=None):
        codigo = data.get("codigo")
        if not codigo:
            return

        # Buscar si ya existen registros de menú con el mismo código
        existing = list(Menu.objects.filter(codigo=codigo))

        if existing:
            # Tomamos el primer registro como menú principal
            menu = existing[0]

            # Si existen filas duplicadas creadas previamente, las eliminamos para limpiar menús dobles
            if len(existing) > 1:
                for extra in existing[1:]:
                    self.stdout.write(
                        self.style.WARNING(f"   [LIMPIEZA] Eliminando registro duplicado de menú ID {extra.id} (código: '{codigo}')")
                    )
                    extra.delete()

            # Actualizamos las propiedades del menú existente
            menu.titulo = data.get("titulo", menu.titulo)
            menu.permiso = data.get("permiso", menu.permiso)
            menu.ruta = data.get("ruta", menu.ruta)
            menu.icono = data.get("icono", menu.icono)
            menu.menu_padre = padre
            menu.orden = data.get("orden", menu.orden or 0)
            menu.save()
            self.stdout.write(f"   [ACTUALIZADO] {menu.titulo} ({codigo})")
        else:
            # Si no existe, creamos el menú
            menu = Menu.objects.create(
                codigo=codigo,
                titulo=data.get("titulo"),
                permiso=data.get("permiso"),
                ruta=data.get("ruta"),
                icono=data.get("icono"),
                menu_padre=padre,
                orden=data.get("orden", 0)
            )
            self.stdout.write(self.style.SUCCESS(f"   [NUEVO] {menu.titulo} ({codigo})"))

        # Sincronizar permisos y acciones del menú
        self.crear_permisos(menu, data)

        # Procesar menús hijos recursivamente
        for hijo in data.get("children", []):
            self.sincronizar_menu(hijo, menu)

    def crear_permisos(self, menu, data):
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

            # Evitar MultipleObjectsReturned o duplicados en PermisosMenuAcciones
            existing_pma = list(PermisosMenuAcciones.objects.filter(menu=menu, accion=accion["codigo"]))
            if existing_pma:
                pma = existing_pma[0]
                if len(existing_pma) > 1:
                    for extra_pma in existing_pma[1:]:
                        extra_pma.delete()
                pma.permiso = permiso
                pma.save()
            else:
                PermisosMenuAcciones.objects.create(
                    menu=menu,
                    accion=accion["codigo"],
                    permiso=permiso
                )