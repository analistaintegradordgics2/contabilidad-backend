from rest_framework import serializers
from apps.public.models import Menu, PermisosMenuAcciones, Archivo
# from cryptography.fernet import Fernet

class ArchivosSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Archivo
        """Meta class."""
        fields = ('id', 'name', 'src','tipo','delete', 'url_s3')

class MenuDinamicoSerializer(serializers.ModelSerializer):   
    submenu = serializers.SerializerMethodField('get_submenus')
    def get_submenus(self, obj):
        try:        
            list_hijos = Menu.objects.filter(menu_padre_id=obj.id).order_by('id')
            return MenuDinamicoSerializer(list_hijos, many=True).data
        except:
            return []     

    class Meta:
        model  = Menu
        fields = (
            'id',
            'titulo',
            'icono',
            'colorico', 
            'ruta',
            'orden', 
            'menu_padre',
            'permiso',
            'submenu',
        )

class PermisosMenuAccionesSerializer(serializers.ModelSerializer):
    
    menu_nombre = serializers.SerializerMethodField('get_menu_nombre')
    def get_menu_nombre(self, obj):
        try:
            return obj.menu.titulo
        except:
            return None

    class Meta:
        model = PermisosMenuAcciones
        """Meta class."""
        fields = ('id', 'accion', 'menu','permiso_accion','permiso_menu', 'menu_nombre')
