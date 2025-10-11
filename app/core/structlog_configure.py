def ordered_json_processor(logger, method_name, event_dict):
    """
    Формирует event_dict с фиксированным порядком ключей.
    Сначала системные поля, потом всё остальное.
    """
    # Определяем желаемый порядок "системных" полей
    system_keys = [
        "user_id",
        "ip",
        "method",
        "path",
        "status",
        "timestamp",
        "level",
        "logger",
        "event",
        "error",
        "business_element",
        "model_id",
        "data",
        "owner_field",
        "filters",
        "pagination",
        "isolation_level",
        "commit",
        "filename",
        "func_name",
        "lineno",

    ]

    # Создаём упорядоченный словарь
    ordered = {}

    # Сначала добавляем системные ключи (если есть)
    for key in system_keys:
        if key in event_dict:
            ordered[key] = event_dict.pop(key)

    # Затем добавляем всё остальное (в порядке появления или sorted)
    # Здесь просто добавляем остаток — порядок не важен
    ordered.update(event_dict)

    return ordered
