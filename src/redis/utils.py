def path_param_key_builder(func, namespace: str, request, *args, **kwargs) -> str:
    """
    Универсальный key_builder для разных эндпоинтов с path параметрами.
    Формирует ключ из namespace и параметров пути.
    """
    path_params = request.path_params

    if not path_params:
        raise ValueError("Не удалось получить path параметры из запроса")

    key_parts = [namespace] + [str(value) for value in path_params.values()]
    cache_key = ":".join(key_parts)

    return cache_key
