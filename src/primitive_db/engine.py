import shlex

from prompt import string

from .constants import META_FILE
from .core import (
    create_table,
    delete,
    drop_table,
    info,
    insert,
    list_tables,
    select,
    update,
)
from .utils import load_metadata, save_metadata


def print_help() -> None:
    """Выводит справку для всех команд"""
    print("\n***База данных***")
    print("Функции управления таблицами:")
    print(
        "<command> create_table <имя> <столб1:тип> <столб2:тип> .. - "
        "создать таблицу"
    )
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя> - удалить таблицу")
    print("\nФункции работы с данными:")
    print(
        "<command> insert into <имя> values (<знач1>, <знач2>, ...) - "
        "создать запись"
    )
    print(
        "<command> select from <имя> where <столбец>=<знач> - "
        "прочитать по условию"
    )
    print("<command> select from <имя> - прочитать все записи")
    print(
        "<command> update <имя> set <столб>=<знач> where <столб>=<знач> - "
        "обновить запись"
    )
    print("<command> delete from <имя> where <столб>=<знач> - удалить запись")
    print("<command> info <имя> - информация о таблице")
    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def parse_condition(expr: str) -> dict[str, str]:
    """Парсит выражение вида 'age = 28' -> {'age': '28'}."""
    if "=" not in expr:
        return {}
    col, val = expr.split("=", 1)
    return {col.strip(): val.strip().strip('"').strip("'")}

def _normalize_metadata(obj) -> dict:
    """Если метаданные повреждены (None/не dict), вернуть пустой словарь."""
    return obj if isinstance(obj, dict) else {}

def run() -> None:
    """Главный цикл программы."""
    metadata = _normalize_metadata(load_metadata(META_FILE))

    print("***База данных***\n")
    print_help()

    while True:
        try:
            user_input = string(">>> Введите команду: ")
        except EOFError:
            print("\nВвод закрыт. Выход из программы.")
            break

        if not user_input:
            continue

        try:
            args = shlex.split(user_input)
        except ValueError:
            print("Некорректный ввод. Попробуйте снова.")
            continue

        cmd = args[0].lower()

        if cmd == "exit":
            print("Выход из программы.")
            break

        if cmd == "help":
            print_help()
            continue

        if cmd == "create_table":
            if len(args) < 3:
                print("Ошибка: недостаточно аргументов.")
                continue
            table_name = args[1]
            columns = args[2:]
            result = create_table(metadata, table_name, columns)
            if isinstance(result, dict):
                metadata = _normalize_metadata(result)
                save_metadata(META_FILE, metadata)
            continue

        if cmd == "list_tables":
            list_tables(metadata)
            continue

        if cmd == "drop_table":
            if len(args) < 2:
                print("Ошибка: укажите имя таблицы.")
                continue
            table_name = args[1]
            result = drop_table(metadata, table_name)
            if isinstance(result, dict):
                metadata = _normalize_metadata(result)
                save_metadata(META_FILE, metadata)
            continue

        if cmd == "insert":
            has_into = len(args) >= 4 and args[1] == "into"
            has_values = "values" in args
            if not (has_into and has_values):
                print(
                    "Некорректный синтаксис. Пример: "
                    'insert into users values ("Sergei", 28, true)'
                )
                continue

            table_name = args[2]
            start = user_input.lower().find("values") + len("values")
            values_part = user_input[start:].strip()
            if not (values_part.startswith("(") and values_part.endswith(")")):
                print("Ошибка: значения должны быть в скобках ().")
                continue

            values_str = values_part[1:-1]
            values = [
                v.strip().strip('"').strip("'") for v in values_str.split(",")
            ]
            insert(metadata, table_name, values)
            continue

        if cmd == "select":
            if len(args) < 3:
                print("Ошибка: недостаточно аргументов для select.")
                continue

            rest = args[1:]
            if rest[0] == "*":
                rest = rest[1:]

            if not rest or rest[0] != "from" or len(rest) < 2:
                print("Некорректный синтаксис команды select.")
                continue

            table_name = rest[1]
            if "where" in rest:
                where_index = rest.index("where")
                where_expr = " ".join(rest[where_index + 1 :])
                where_clause = parse_condition(where_expr)
                select(metadata, table_name, where_clause)
            else:
                select(metadata, table_name)
            continue

        if cmd == "update" and "set" in args and "where" in args:
            table_name = args[1]
            set_expr = " ".join(args[args.index("set") + 1 : args.index("where")])
            where_expr = " ".join(args[args.index("where") + 1 :])
            set_clause = parse_condition(set_expr)
            where_clause = parse_condition(where_expr)
            update(metadata, table_name, set_clause, where_clause)
            continue

        if (
            cmd == "delete"
            and len(args) >= 5
            and args[1] == "from"
            and "where" in args
        ):
            table_name = args[2]
            where_expr = " ".join(args[args.index("where") + 1 :])
            where_clause = parse_condition(where_expr)
            delete(metadata, table_name, where_clause)
            continue

        if cmd == "info" and len(args) == 2:
            info(metadata, args[1])
            continue

        print(f"Функции '{cmd}' нет. Попробуйте снова.")