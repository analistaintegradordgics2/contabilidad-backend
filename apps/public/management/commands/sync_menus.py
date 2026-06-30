import importlib

from django.apps import apps
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from apps.public.models import Menu, PermisosMenuAcciones

class Command(BaseCommand):

    help = "Sincroniza menús y permisos"

    def handle(self, *args, **options):

        for app in apps.get_app_configs():
            print("Buscando:", app.name)

            try:
                modulo = importlib.import_module(f"{app.name}.menus")
                print("✔ Encontrado", modulo)
            except ModuleNotFoundError as e:
                print("✘", e)
                continue

            menus = getattr(modulo, "MENUS", [])

            for menu in menus:
                self.sincronizar_menu(menu)

    def sincronizar_menu(self, data, padre=None):

        menu,_=Menu.objects.update_or_create(

            codigo=data["codigo"],
            defaults={
                "permiso":data["permiso"],
                "titulo":data["titulo"],
                "ruta":data.get("ruta"),
                "icono":data.get("icono"),
                "menu_padre":padre,
                "orden":data.get("orden",0),

            }

        )

        self.crear_permisos(menu,data)

        for hijo in data.get("children",[]):

            self.sincronizar_menu(
                hijo,
                menu
            )


    def crear_permisos(self, menu, data):

        content_type = ContentType.objects.get_for_model(Menu)

        for accion in data.get("acciones", []):

            permiso, _ = Permission.objects.get_or_create(
                codename=f'{data["permiso"]}_{accion["codigo"]}',
                content_type=content_type,
                defaults={
                    "name": f'{data["titulo"]} - {accion["nombre"]}'
                }
            )

            PermisosMenuAcciones.objects.update_or_create(
                menu=menu,
                accion=accion["codigo"],
                defaults={
                    "permiso": permiso
                }
            )