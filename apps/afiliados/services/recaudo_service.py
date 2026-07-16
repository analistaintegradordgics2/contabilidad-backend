from apps.afiliados.models.afiliado import Afiliado
from apps.afiliados.serializers.afiliado import AfiliadoResumenSerializer

import pdb, requests

class RecaudoService:
    
    @staticmethod
    def listar():
        url = "https://pagodgi.webdgi.site/api/restful/sincronizacion/"
        response = requests.get(url)

        if response.status_code != 200:
            return response.json()
        
        result = []
        for item in response.json():
            afiliado = Afiliado.objects.filter(cupon__numero=item['ref_1']).first()
            serializer = AfiliadoResumenSerializer(afiliado).data
            item['afiliado'] = serializer

            result.append(item)
    
        return result
    