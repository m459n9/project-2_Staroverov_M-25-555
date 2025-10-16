ALLOWED_TYPES = {"int", "str", "bool"}

def create_table(metadata, table_name, columns):
    """Создает таблицу с заданными столбцами."""
    tables = metadata.setdefault("tables", {})

    if table_name in tables:
        print(f'Ошибка: Таблица "{table_name}" уже существует.')
        return metadata
    
    parsed_columns = []
    for col in columns:
        if ":" not in col:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        name, type_ = col.split(":", 1)
        if type_ not in ALLOWED_TYPES:
            print(f"Некорректное значение: {col}. Попробуйте снова.")
            return metadata
        parsed_columns.append({"name": name, "type": type_})

    if not any(col["name"] == "ID" for col in parsed_columns):
        parsed_columns.insert(0, {"name": "ID", "type": "int"})

    tables[table_name] = parsed_columns
    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f'{c["name"]}:{c["type"]}' for c in parsed_columns)
    )
    return metadata

def drop_table(metadata, table_name):
    """Удаляет таблицу по имени."""
    tables = metadata.setdefault("tables", {})

    if table_name not in tables:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del tables[table_name]
    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

def list_tables(metadata):
    """Показывает список таблиц."""
    tables = metadata.get("tables", {})
    if not tables:
        print("Таблиц пока нет.")
    else:
        for name in tables.keys():
            print(f"- {name}")