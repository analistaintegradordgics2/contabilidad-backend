import hashlib
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import connection, transaction

import pdb, os

class Command(BaseCommand):
    help = 'Sincroniza procedimientos almacenados'

    def add_arguments(self, parser):
        parser.add_argument(
            '--funcion',
            type=str,
            help='Sincronizar únicamente una función'
        )

        parser.add_argument(
            '--listar',
            action='store_true',
            help='Listar funciones disponibles'
        )

    def handle(self, *args, **options):
        procedures_path = Path(os.path.join(settings.ROOT_DIR, 'sql', 'procedimientos'))
        
        archivos = procedures_path.rglob('*.sql')

        if options['listar']:
            for archivo in archivos:
                self.stdout.write(archivo.stem)
            return
        
        funcion = options.get('funcion')

        for archivo in archivos:
            nombre = archivo.stem

            if funcion and nombre != funcion:
                continue

            self.sync_procedure(nombre, archivo)

    def sync_procedure(self, nombre, archivo):

        contenido = archivo.read_text(encoding='utf-8')
        hash_actual = hashlib.sha256(
            contenido.encode('utf-8')
        ).hexdigest()

        with connection.cursor() as cursor:

            cursor.execute("""
                SELECT hash
                FROM procedimientos_sync
                WHERE nombre = %s
            """, [nombre])

            row = cursor.fetchone()

            # Ya está actualizado
            if row and row[0] == hash_actual:
                self.stdout.write(
                    self.style.SUCCESS(
                        f'{nombre}: sin cambios'
                    )
                )
                return
            
            try:

                with transaction.atomic():

                    # Ejecutar procedure
                    self._ejecutar_procedure(cursor, nombre, contenido)

                    if row:

                        cursor.execute("""
                            UPDATE procedimientos_sync
                            SET
                                hash = %s,
                                fecha_sync = NOW()
                            WHERE nombre = %s
                        """, [
                            hash_actual,
                            nombre
                        ])

                        accion = 'actualizado'

                    else:

                        cursor.execute("""
                            INSERT INTO procedimientos_sync (
                                nombre,
                                hash,
                                fecha_sync
                            )
                            VALUES (
                                %s,
                                %s,
                                NOW()
                            )
                        """, [
                            nombre,
                            hash_actual
                        ])

                        accion = 'creado'

                self.stdout.write(
                    self.style.SUCCESS(
                        f'{nombre}: {accion}'
                    )
                )

            except Exception as e:

                self.stdout.write(
                    self.style.ERROR(
                        f'{nombre}: ERROR -> {e}'
                    )
                )

    def _ejecutar_procedure(self, cursor, nombre, contenido):
        try:
            cursor.execute('SAVEPOINT antes_create')
            cursor.execute(contenido)
            cursor.execute('RELEASE SAVEPOINT antes_create')

        except Exception as e:
            msg = str(e).lower()
            cursor.execute('ROLLBACK TO SAVEPOINT antes_create')

            if 'tipo de retorno' in msg or 'return type' in msg:
                self.stdout.write(
                    self.style.WARNING(f'{nombre}: tipo de retorno cambió, intentando DROP...')
                )
                try:
                    cursor.execute(f'DROP FUNCTION IF EXISTS {nombre};')
                    cursor.execute(contenido)
                except Exception as ee:
                    raise Exception('No se pudo eliminar el procedimiento... Posiblemente algún otro procedimiento/trigger/vista... dependa de él.')
            else:
                raise
