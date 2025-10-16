from prompt import string

HELP_TEXT = """
<command> exit - выйти из программы
<command> help - справочная информация
""".strip()


def welcome() -> int:
    print("Первая попытка запустить проект!\n")
    print("***")
    print(HELP_TEXT)

    while True:
        cmd = string("Введите команду: ").strip().lower()

        if cmd == "exit":
            print("Выход из программы. Пока!")
            return 0

        if cmd == "help":
            print()
            print(HELP_TEXT)
            continue

        if not cmd:
            continue

        print(f"Неизвестная команда: {cmd}. Введите 'help'.")