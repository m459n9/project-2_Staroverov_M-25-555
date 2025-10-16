import shlex
from prompt import string
from .core import create_table, drop_table, list_tables
from .utils import load_metadata, save_metadata


def print_help():
    """Вывод справочной информации."""
    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    """Главная функция запуска БД."""
    print("***База данных***\n")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> <столбец2:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")

    filepath = "db_meta.json"

    while True:
        metadata = load_metadata(filepath)
        user_input = string("Введите команду: ")

        try:
            args = shlex.split(user_input)
        except ValueError:
            print(f"Некорректное значение: {user_input}. Попробуйте снова.")
            continue

        if not args:
            continue

        command = args[0]
        params = args[1:]

        if command == "exit":
            print("Выход из программы.")
            break
        elif command == "help":
            print_help()
        elif command == "create_table":
            metadata = create_table(metadata, params[0], params[1:]) if len(params) >= 2 else metadata
            save_metadata(filepath, metadata)
        elif command == "list_tables":
            list_tables(metadata)
        elif command == "drop_table":
            metadata = drop_table(metadata, params[0]) if params else metadata
            save_metadata(filepath, metadata)
        else:
            print(f"Функции {command} нет. Попробуйте снова.")