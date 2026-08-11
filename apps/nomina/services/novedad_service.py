from django.db import transaction
from django.db.models import Q
from apps.nomina.models.novedades import Novedad, NovedadesCentroCosto
from apps.nomina.models.parametrizacion import BaseLiquidacionNovedad
from apps.utils.funciones import Funciones

class NovedadService:

    @staticmethod
    @transaction.atomic
    def crear_o_actualizar(data, user_id):
        """
        Crea o actualiza una Novedad con sus relaciones de centros de costos
        y bases de liquidación. Trabaja directamente con modelos.
        Maneja correctamente las relaciones ForeignKey convirtiendo IDs a instancias.
        """
        novedad_id = data.get('id')
        uc_id = data.get('uc_id', user_id)
        um_id = data.get('um_id', user_id)

        if novedad_id:
            # Actualizar existente
            novedad = Novedad.objects.filter(pk=novedad_id).first()
            if not novedad:
                return None
            for attr, value in data.items():
                if attr not in ['id', 'uc_id', 'um_id'] and value is not None:
                    # Resolver FKs antes de setattr
                    value = Funciones.resolver_fk(value, attr, novedad)
                    setattr(novedad, attr, value)
            novedad.save()
        else:
            # Crear nuevo
            data['uc_id'] = user_id
            novedad = Novedad.objects.create(**data)

        # Manejar centros de costo de la novedad
        if data.get('entidad') is not None:
            # Si hay entidad, manejar NovedadesCentroCosto por entidad
            existentes = NovedadesCentroCosto.objects.filter(
                entidades_centro_costos__entidad_id=data['entidad'],
                eliminado=False
            )

            if len(existentes) == 0:
                # Nueva relación - crear registro
                NovedadesCentroCosto.objects.create(
                    entidades_centro_costos_id=data['entidad'],
                    novedades_id=novedad.id,
                    uc_id=uc_id
                )
            else:
                # Actualizar relación existente
                for item in existentes:
                    item.um_id = um_id
                    if 'eliminado' in data:
                        item.eliminado = data['eliminado']
                    item.save()
        else:
            # Sin entidad - manejar centros de costo directamente
            for item in data.get('centro_costos', []):
                # Buscar si existe
                ccosto = NovedadesCentroCosto.objects.filter(
                    centro_costos_id=item['centro_costos'],
                    novedades_id=novedad.id
                ).first()
                if ccosto:
                    ccosto.um_id = um_id
                    if 'eliminado' in item:
                        ccosto.eliminado = item['eliminado']
                    ccosto.save()
                else:
                    # Crear nuevo
                    NovedadesCentroCosto.objects.create(
                        centro_costos_id=item['centro_costos'],
                        novedades_id=novedad.id,
                        mayor_cta_debito_id=item.get('mayor_cta_debito'),
                        mayor_cta_credito_id=item.get('mayor_cta_credito'),
                        eliminado=item.get('eliminado', False),
                        uc_id=uc_id
                    )

        # Manejar bases de liquidación
        if BaseLiquidacionNovedad.objects.filter(novedades=novedad.id).exists():
            # Ya existen - actualizar
            for item in data.get('base_liquidacion_empleado', []):
                bl = BaseLiquidacionNovedad.objects.filter(
                    novedades_id=novedad.id,
                    base_liquidacion_id=item['base_liquidacion']
                ).first()
                if bl:
                    bl.um_id = um_id
                    if 'eliminado' in item:
                        bl.eliminado = item['eliminado']
                    bl.save()
                else:
                    BaseLiquidacionNovedad.objects.create(
                        novedades_id=novedad.id,
                        base_liquidacion_id=item['base_liquidacion'],
                        uc_id=uc_id
                    )

            for item in data.get('base_liquidacion_empresa', []):
                bl = BaseLiquidacionNovedad.objects.filter(
                    novedades_id=novedad.id,
                    base_liquidacion_id=item['base_liquidacion']
                ).first()
                if bl:
                    bl.um_id = um_id
                    if 'eliminado' in item:
                        bl.eliminado = item['eliminado']
                    bl.save()
                else:
                    BaseLiquidacionNovedad.objects.create(
                        novedades_id=novedad.id,
                        base_liquidacion_id=item['base_liquidacion'],
                        uc_id=uc_id
                    )
        else:
            # No existen - crear todas
            for item in data.get('base_liquidacion_empleado', []):
                BaseLiquidacionNovedad.objects.create(
                    novedades_id=novedad.id,
                    base_liquidacion_id=item['base_liquidacion'],
                    uc_id=uc_id
                )

            for item in data.get('base_liquidacion_empresa', []):
                BaseLiquidacionNovedad.objects.create(
                    novedades_id=novedad.id,
                    base_liquidacion_id=item['base_liquidacion'],
                    uc_id=uc_id
                )

        return novedad