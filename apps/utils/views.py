from django.db.models import Q
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from apps.parametros.models.ubicacion import Zona

# from xhtml2pdf import pisa

import pdb

# def render_to_pdf(template_src, context_dict={}):
#     template = get_template(template_src)
#     html = template.render(context_dict)
#     result = BytesIO()
#     pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
#     if not pdf.err:
#         return HttpResponse(result.getvalue(), content_type='application/pdf')
#     return None


class Views:
    @staticmethod
    def filtro(request, filtro, model):
        filter = Q()
        for key in filtro:
            if request.GET.get(filtro[key], None) is not None:
                filter.add(Q(**{key: request.GET.get(filtro[key], None)}), Q.OR)
        return model.filter(filter)

    @staticmethod
    def select(request, filtro, model, values, limit=5):
        filter = Q()

        for key in filtro:
            if isinstance(filtro[key], dict):
                filter.add(Q(**filtro[key]), Q.OR)
            elif request.GET.get(filtro[key], None) is not None:
                filter.add(Q(**{key: request.GET.get(filtro[key], None)}), Q.OR)
        if request.GET.get('init', None) is None:
            model = model.distinct()
        modelResp = model.filter(filter)[:limit]
        if request.GET.get('init', None) is not None:
            try:
                if type(  request.GET.get('init', 0)  ) is int:
                    modelResp = modelResp.union(model.filter(id=request.GET.get('init', None)))
                else:
                    tinit = int(request.GET.get('init', None))
                    modelResp = modelResp.union(model.filter( id = tinit ))
            except:
                print(" se daño ")
            
        return modelResp.values(*values)

def get_or_create_zona_sin_definir(ciudad_id):
    zona, _ = Zona.objects.get_or_create(
        ciudad_id=ciudad_id,
        nombre__iexact='sin definir',
        defaults={'nombre': 'Sin Definir'}
    )
    return zona
