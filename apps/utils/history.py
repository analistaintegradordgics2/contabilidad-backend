

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


def getCombinedHistory(obj, campos_principal, tipo="", m2m_relations=None, related_models=None):
    """
    Obtiene el historial combinado del modelo principal (obj) y opcionalmente
    de sus relaciones Muchos a Muchos (m2m_relations) y relaciones secundarias (related_models).
    """
    from datetime import datetime

    history_combined = []

    # 1. Historia del objeto principal
    if obj and hasattr(obj, 'history'):
        hist_principal = getHistorymodel(obj, campos_principal, tipo)
        history_combined.extend(hist_principal)

    # 2. Historia de relaciones Muchos a Muchos (M2M)
    if m2m_relations:
        for m2m in m2m_relations:
            manager = m2m.get('history_manager')
            fk_field = m2m.get('fk_field', f"{obj._meta.model_name}_id")
            rel_field = m2m.get('rel_field')
            label_relacion = m2m.get('label_relacion', 'Relación')
            nombre_campo = m2m.get('nombre_campo', 'nombre')

            if manager and hasattr(manager, 'filter'):
                filter_kwargs = {fk_field: obj.pk}
                records = manager.filter(**filter_kwargs).select_related(rel_field, 'history_user').order_by('-history_date')

                for record in records:
                    fecha_str = record.history_date.strftime("%d/%m/%Y %H:%M") if record.history_date else ""
                    usuario_str = record.history_user.username if record.history_user else None

                    rel_obj = getattr(record, rel_field, None) if rel_field else None
                    val_nombre = getattr(rel_obj, nombre_campo, 'Desconocido') if rel_obj else 'Desconocido'

                    if record.history_type == '+':
                        accion = f"Asignación de {label_relacion}"
                        valor_formateado = f"<br>Antes -> Sin asignar<br>Despues -> {val_nombre}"
                    elif record.history_type == '-':
                        accion = f"Eliminación de {label_relacion}"
                        valor_formateado = f"<br>Antes -> {val_nombre}<br>Despues -> Eliminado"
                    else:
                        accion = f"Modificación de {label_relacion}"
                        valor_formateado = val_nombre

                    history_combined.append({
                        'detalle_creacion': accion,
                        label_relacion: valor_formateado,
                        'fecha_bitacora': fecha_str,
                        'usuario_bitacora': usuario_str,
                        '_date': record.history_date
                    })


    # 3. Historia de relaciones secundarias (1 to N)
    if related_models:
        for rel in related_models:
            manager = rel.get('history_manager')
            queryset = rel.get('queryset')
            if not manager and queryset is not None and hasattr(queryset, 'model') and hasattr(queryset.model, 'history'):
                manager = queryset.model.history

            campos_rel = rel.get('campos', [])
            tipo_rel = rel.get('tipo', 'Registro')
            fk_field = rel.get('fk_field', f"{obj._meta.model_name}_id")


            if manager and hasattr(manager, 'filter'):
                filter_kwargs = {fk_field: obj.pk}
                history_qs = manager.filter(**filter_kwargs).select_related('history_user').order_by('id', '-history_date')

                records_by_id = {}
                for record in history_qs:
                    records_by_id.setdefault(record.id, []).append(record)

                for item_id, records in records_by_id.items():
                    for i, record in enumerate(records):
                        fecha_str = record.history_date.strftime("%d/%m/%Y %H:%M") if record.history_date else ""
                        usuario_str = record.history_user.username if record.history_user else None
                        next_record = records[i + 1] if i + 1 < len(records) else None

                        entry_dict = {
                            'fecha_bitacora': fecha_str,
                            'usuario_bitacora': usuario_str,
                            '_date': record.history_date
                        }

                        is_creation = (record.history_type == '+') or (next_record is None and record.history_type != '-')

                        if record.history_type == '-':
                            entry_dict['detalle_creacion'] = f"Eliminación de {tipo_rel}"
                        elif is_creation:
                            entry_dict['detalle_creacion'] = f"Creación de {tipo_rel}"
                        else:
                            entry_dict['detalle_creacion'] = f"Modificación de {tipo_rel}"

                        hay_cambios = False
                        for key_config in campos_rel:
                            campo = key_config['db']
                            label = key_config['label']

                            if campo.endswith('_id'):
                                rel_name = campo.replace('_id', '')
                                rel_obj_curr = getattr(record, rel_name, None)
                                val_curr = getattr(rel_obj_curr, key_config.get('nombre_relacion', 'id'), None) if rel_obj_curr else None

                                rel_obj_prev = getattr(next_record, rel_name, None) if next_record else None
                                val_prev = getattr(rel_obj_prev, key_config.get('nombre_relacion', 'id'), None) if rel_obj_prev else None
                            else:
                                val_curr = getattr(record, campo, None)
                                val_prev = getattr(next_record, campo, None) if next_record else None

                            if isinstance(val_curr, bool):
                                val_curr = 'SI' if val_curr else 'NO'
                            if isinstance(val_prev, bool):
                                val_prev = 'SI' if val_prev else 'NO'

                            if record.history_type == '-':
                                entry_dict[label] = f"<br>Antes -> {val_curr or 'N/A'}<br>Despues -> Eliminado"
                                hay_cambios = True
                            elif is_creation:
                                entry_dict[label] = f"{val_curr or ''}"
                                hay_cambios = True
                            elif val_curr != val_prev:
                                entry_dict[label] = f"<br>Antes -> {val_prev or ''}<br>Despues -> {val_curr or ''}"
                                hay_cambios = True

                        if hay_cambios:
                            # Si es una modificación y el identificador no cambió, incluirlo para dar contexto del registro modificado
                            if not is_creation and record.history_type != '-':
                                ident_cfg = rel.get('identificador') or (campos_rel[0] if campos_rel else None)

                                if ident_cfg:
                                    campo_id_name = ident_cfg['db']
                                    label_id_name = ident_cfg['label']
                                    if label_id_name not in entry_dict:
                                        if campo_id_name.endswith('_id'):
                                            r_name = campo_id_name.replace('_id', '')
                                            r_obj = getattr(record, r_name, None)
                                            val_ident = getattr(r_obj, ident_cfg.get('nombre_relacion', 'id'), None) if r_obj else None
                                        else:
                                            val_ident = getattr(record, campo_id_name, None)
                                        if val_ident is not None and str(val_ident).strip():
                                            entry_dict[label_id_name] = str(val_ident)

                            history_combined.append(entry_dict)


            elif queryset:
                for item in queryset:
                    if hasattr(item, 'history'):
                        hist_item = getHistorymodel(item, campos_rel, tipo_rel)
                        for entry in hist_item:
                            for k, v in list(entry.items()):
                                if k not in ['fecha_bitacora', 'usuario_bitacora', 'detalle_creacion'] and isinstance(v, str) and not v.startswith('<br>Antes ->'):
                                    entry[k] = f"<br>Antes -> Sin registrar<br>Despues -> {v}"
                            history_combined.append(entry)



    # 4. Ordenar todo el historial por fecha_bitacora
    from django.utils import timezone
    def parse_fecha(item):
        dt = None
        if '_date' in item and item['_date']:
            dt = item['_date']
        elif item.get('fecha_bitacora'):
            fecha_str = item.get('fecha_bitacora')
            try:
                dt = datetime.strptime(fecha_str, "%d/%m/%Y %H:%M")
            except Exception:
                dt = None

        if dt is None:
            return datetime.min

        if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
            return dt.astimezone(timezone.utc).replace(tzinfo=None)

        return dt


    history_combined.sort(key=parse_fecha, reverse=True)

    for item in history_combined:
        item.pop('_date', None)

    return history_combined
