import os, errno

from django.conf import settings

from apps.utils.render import Render
from apps.common_db.db import execute_procedure

class TransmisionService:

    @staticmethod
    def list(anio, mes):

        sql = "select * from transmision_nomina_felix(%s, %s);"
        params = [anio, mes]

        result = execute_procedure(sql, params)

        if len(result) > 0 :
            return result[0][0]

        return []

    @staticmethod
    def archivos_transmision():
        nomina_path = os.path.join(settings.MEDIA_ROOT, "nomina")
        data_path = os.path.join(nomina_path, "data.txt")
        ws_path = os.path.join(nomina_path, "webservicenomina.txt")

        if not os.path.exists(nomina_path):
            os.mkdir(nomina_path)

        # Se crear los dos archivos de transmision
        with open(data_path, "a") as file:
            file.close()
        with open(ws_path, "a") as file:
            file.close()

        files = []
        files.append(data_path)
        files.append(ws_path)
        folderzip = nomina_path
        nombre = "archivos_transmision"
        retornar = Render.downloadZip(folderzip, files, "{}.zip".format(nombre), ".txt")
        return retornar