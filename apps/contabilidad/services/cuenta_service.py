from django.db.models import Value, Subquery, OuterRef, CharField
from django.db.models.functions import Concat
from django.db.models.functions import Coalesce
from django.db import transaction
from apps.contabilidad.models.cuenta import Mayor
from apps.contabilidad.serializers.cuenta import MayorSerializer


class MayorService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(data, mayor_id=None):
        """
        Crea o actualiza una cuenta Mayor
        """
        if not mayor_id:
            existe = Mayor.objects.filter(codigo=data.get('codigo')).exists()
            if existe:
                raise Exception("Ya existe una cuenta con ese código")
        
        instance = None

        # Actualizar
        if mayor_id:
            instance = Mayor.objects.filter(pk=mayor_id).first()
            if not instance:
                raise Exception("La cuenta no existe")

            serializer = MayorSerializer(instance, data=data, partial=True)

        # Crear
        else:
            serializer = MayorSerializer(data=data)

        # Validar
        serializer.is_valid(raise_exception=True)

        mayor = serializer.save()

        return mayor
    
    @staticmethod
    def get_cuentas_auxiliares(cuenta_mayor):
        return (
            Mayor.objects
            .filter(
                codigol__gt=str(cuenta_mayor),
                codigol__lte=f"{cuenta_mayor}99"
            )
            .values('id', 'codigo', 'estado')
            .annotate(
                saldo=Coalesce(
                    Subquery(
                        Saldos.objects
                        .filter(mayor_id=OuterRef('id'))
                        .values('sal03')[:1]
                    ),
                    Value(0)
                )
            )
            .order_by('codigo')
        )
    
    @staticmethod
    def inactivar_cuenta(mayor_id, codigo):

        # Validar cuentas auxiliares
        auxiliares = MayorService.get_cuentas_auxiliares(codigo)

        for aux in auxiliares or []:

            if aux.get('saldo', 0) != 0:
                return False, f'Auxiliar "{aux.get("codigo")}" tiene saldos'

            if aux.get('estado') == 'Activa':
                return False, f'Auxiliar "{aux.get("codigo")}" está activa'

        # Validar Saldos
        tiene_saldos = Saldos.objects.filter(
            mayor_id=mayor_id
        ).exclude(
            sal13=0  
        ).exists()

        if tiene_saldos:
            return False, 'Esta cuenta tiene saldos, no se puede inactivar'

        return True, None

    @staticmethod
    def validar_codigo(codigo, mayor_id=None):
        """
        Reglas PUC:
        - 1 dígito  → clase (1-9)
        - 2 dígitos → grupo
        - 4 dígitos → cuenta
        - 6+ dígitos → cuenta/auxiliar (mínimo 6)
        - Siempre pares excepto el primer nivel
        - Debe existir cuenta padre
        """

        # 1. Longitud válida
        longitud = len(codigo)
        if longitud > 1 and longitud % 2 != 0:
            return False, 'El código ingresado no es válido — debe tener cantidad par de dígitos'

        # 2. Auxiliar con mínimo 6 dígitos
        cuenta = Mayor.objects.filter(codigo=codigo).exclude(pk=mayor_id).first()
        if cuenta:
            return False, 'El código de la cuenta ya existe en el sistema'

        # 3. Verificar que existe cuenta padre
        if longitud > 1:
            # Para longitud 2 → padre es 1 dígito
            # Para longitud 4 → padre es 2 dígitos
            # Para longitud 6+ → padre son los últimos 2 dígitos menos
            padre_codigo = codigo[:-1] if longitud == 2 else codigo[:-2]

            padre = Mayor.objects.filter(codigo=padre_codigo).first()

            if not padre:
                return False, f'No existe cuenta padre para el código {padre_codigo}'

            if padre.tipo == 'Auxiliar':
                return False, 'La cuenta padre es de tipo auxiliar, no se puede crear esta cuenta'

        # 4. Si es edición — verificar que no tenga hijas
        if mayor_id:
            tiene_hijas = Mayor.objects.filter(
                codigo__startswith=codigo
            ).exclude(pk=mayor_id).exists()

            if tiene_hijas:
                return False, 'No se puede modificar la cuenta, ya tiene cuentas hijas'

        return True, None
    
    @staticmethod
    def get_mayor_select(solo_auxiliar=True, estado=True, rango=None, cxc=False, search=''):
        queryset = Mayor.objects.all()

        if estado:
            queryset = queryset.filter(estado__icontains=estado)
        if solo_auxiliar:
            queryset = queryset.filter(tipo='Auxiliar')
        if rango:
            queryset = queryset.filter(codigol__range=rango)
        if cxc:
            queryset = queryset.filter(cxc=True)
        if search:
            queryset = queryset.filter(
                Q(codigol__istartswith=search) | Q(nombrel__istartswith=search)
            )

        return queryset.annotate(
            codigo_nombre=Concat('codigo', Value(' - '), 'nombre', output_field=CharField())
        ).order_by('codigo')[:10]

    @staticmethod
    def format_mayor_select(item, include_model=False):
        
        result = {
            'value': item.id,
            'label': f"{item.codigo} - {item.nombre}",
            'nombre': item.nombre,
        }
        if include_model:
            result['model'] = MayorSerializer(item).data
        return result