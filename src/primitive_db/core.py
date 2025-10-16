import os

from prettytable import PrettyTable

from .decorators import confirm_action, create_cacher, handle_db_errors, log_time
from .utils import load_table_data, save_table_data

ALLOWED_TYPES = {"int", "str", "bool"}

cache_result = create_cacher()

@handle_db_errors
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
            print(f"Некорректный тип данных: {type_}. Разрешены int, str, bool.")
            return metadata
        parsed_columns.append({"name": name, "type": type_})

    if not any(col["name"] == "ID" for col in parsed_columns):
        parsed_columns.insert(0, {"name": "ID", "type": "int"})

    tables[table_name] = parsed_columns

    os.makedirs("data", exist_ok=True)
    save_table_data(table_name, [])

    print(
        f'Таблица "{table_name}" успешно создана со столбцами: '
        + ", ".join(f'{c["name"]}:{c["type"]}' for c in parsed_columns)
    )
    return metadata

@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Удаляет таблицу по имени и её данные."""
    tables = metadata.setdefault("tables", {})

    if table_name not in tables:
        print(f'Ошибка: Таблица "{table_name}" не существует.')
        return metadata

    del tables[table_name]

    data_path = os.path.join("data", f"{table_name}.json")
    if os.path.exists(data_path):
        os.remove(data_path)
        print(f'Файл данных "{data_path}" удалён.')

    print(f'Таблица "{table_name}" успешно удалена.')
    return metadata

@handle_db_errors
def list_tables(metadata):
    """Показывает список всех таблиц."""
    tables = metadata.get("tables", {})
    if not tables:
        print("Таблиц пока нет.")
    else:
        print("Список таблиц:")
        for name in tables.keys():
            print(f"- {name}")

@handle_db_errors
@log_time
def insert(metadata, table_name, values):
    """Добавляет запись в таблицу."""
    tables = metadata.get("tables", {})
    if table_name not in tables:
        raise KeyError(table_name)

    schema = tables[table_name]
    columns = [c["name"] for c in schema if c["name"] != "ID"]

    if len(values) != len(columns):
        raise ValueError("Количество значений не совпадает с количеством столбцов.")

    data = load_table_data(table_name)
    new_id = max((row["ID"] for row in data), default=0) + 1

    new_row = {"ID": new_id}
    for val, col in zip(values, columns):
        col_type = next(c["type"] for c in schema if c["name"] == col)
        if col_type == "int":
            val = int(val)
        elif col_type == "bool":
            val = str(val).lower() in ("true", "1", "yes")
        new_row[col] = val

    data.append(new_row)
    save_table_data(table_name, data)
    print(f'Запись с ID={new_id} успешно добавлена в таблицу "{table_name}".')

@handle_db_errors
@log_time
def select(metadata, table_name, where=None):
    """Выводит записи из таблицы (с кэшированием)."""
    tables = metadata.get("tables", {})
    if table_name not in tables:
        raise KeyError(table_name)

    # создаём уникальный ключ кэша
    cache_key = f"{table_name}:{str(where)}"

    # получаем данные через кэш
    data = cache_result(cache_key, lambda: load_table_data(table_name))

    if where:
        col, val = next(iter(where.items()))
        data = [row for row in data if str(row.get(col)) == str(val)]

    if not data:
        print("Нет данных для отображения.")
        return

    table = PrettyTable()
    table.field_names = data[0].keys()
    for row in data:
        table.add_row(row.values())
    print(table)

@handle_db_errors
@confirm_action("удаление записей")
def delete(metadata, table_name, where):
    """Удаляет записи по условию."""
    data = load_table_data(table_name)
    col, val = next(iter(where.items()))
    new_data = [r for r in data if str(r.get(col)) != str(val)]
    removed = len(data) - len(new_data)
    save_table_data(table_name, new_data)
    print(f"Удалено записей: {removed}")

@handle_db_errors
def update(metadata, table_name, set_clause, where):
    """Обновляет записи."""
    data = load_table_data(table_name)
    if not data:
        print("Таблица пуста.")
        return

    col_where, val_where = next(iter(where.items()))
    col_set, val_set = next(iter(set_clause.items()))

    updated = 0
    for row in data:
        if str(row.get(col_where)) == str(val_where):
            row[col_set] = val_set
            updated += 1

    save_table_data(table_name, data)
    print(f"Обновлено записей: {updated}")

@handle_db_errors
def info(metadata, table_name):
    """Выводит информацию о таблице."""
    tables = metadata.get("tables", {})
    if table_name not in tables:
        raise KeyError(table_name)

    schema = tables[table_name]
    data = load_table_data(table_name)
    cols = ", ".join(f"{c['name']}:{c['type']}" for c in schema)
    print(f"Таблица: {table_name}")
    print(f"Столбцы: {cols}")
    print(f"Количество записей: {len(data)}")