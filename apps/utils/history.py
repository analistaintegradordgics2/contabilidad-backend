

def getHistorymodel(obj, campos, tipo=""):

    objhist = obj.history.all().select_related()
    objhist_values = list(obj.history.values().order_by('id', '-history_date'))

    objlist = []

    for i, item in enumerate(objhist_values):

        objT = {}
        es_creacion = i == len(objhist_values) - 1

        if es_creacion:
            objT['detalle_creacion'] = f'Creación {tipo}'

        for key in campos:
            campo = key['db']
            label = key['label']

            hay_cambio = False
            if not es_creacion and i + 1 < len(objhist_values):
                hay_cambio = item.get(campo) != objhist_values[i + 1].get(campo)

            if not (hay_cambio or es_creacion):
                continue

            # =============================
            # CAMPOS RELACIONADOS (_id)
            # =============================
            if campo.endswith('_id'):

                if campo == 'history_user_id':
                    usuario = objhist[i].history_user
                    objT[label] = usuario.username if usuario else None
                    continue

                rel_name = campo.replace('_id', '')
                valor = getattr(objhist[i], rel_name, None)

                if valor:
                    objT[label] = getattr(valor, key.get('nombre_relacion', 'id'), None)
                else:
                    objT[label] = None

            # =============================
            # FECHA
            # =============================
            elif campo == 'history_date':
                fecha = item.get(campo)
                objT[label] = fecha.strftime("%d/%m/%Y %H:%M") if fecha else None

            # =============================
            # CAMPOS NORMALES
            # =============================
            else:
                valor_actual = item.get(campo)
                valor_anterior = None

                if not es_creacion and i + 1 < len(objhist_values):
                    valor_anterior = objhist_values[i + 1].get(campo)

                # Booleanos
                if isinstance(valor_actual, bool):
                    valor_actual = 'SI' if valor_actual else 'NO'
                if isinstance(valor_anterior, bool):
                    valor_anterior = 'SI' if valor_anterior else 'NO'

                if hay_cambio:
                    objT[label] = f"<br>Antes -> {valor_anterior or ''}<br>Despues -> {valor_actual or ''}"
                else:
                    objT[label] = valor_actual

        if len(objT) > 1:
            objlist.append(objT)

    return objlist