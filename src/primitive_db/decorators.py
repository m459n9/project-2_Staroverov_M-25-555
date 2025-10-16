import time
from functools import wraps


def handle_db_errors(func):
    """Обрабатывает стандартные ошибки БД."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            msg = "Ошибка: Файл данных не найден. " \
                  "Возможно, база данных не инициализирована."
            print(msg)
        except KeyError as err:
            print(f"Ошибка: Таблица или столбец {err} не найден.")
        except ValueError as err:
            print(f"Ошибка валидации: {err}")
        except Exception as err: 
            print(f"Произошла непредвиденная ошибка: {err}")
    return wrapper

def confirm_action(action_name: str):
    """Декоратор для подтверждения опасных операций."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            prompt = f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
            confirmation = input(prompt).strip().lower()
            if confirmation != "y":
                print(f'Операция "{action_name}" отменена.')
                return
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_time(func):
    """Измеряет время выполнения функции."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.monotonic()
        result = func(*args, **kwargs)
        elapsed = time.monotonic() - start
        print(f"Функция {func.__name__} выполнилась за {elapsed:.3f} секунд.")
        return result
    return wrapper

def create_cacher():
    """Создаёт замыкание для кэширования результатов."""
    cache: dict[str, object] = {}

    def cache_result(key: str, value_func):
        if key in cache:
            print(f"[cache hit] Результат для '{key}' найден в кэше.")
            return cache[key]
        print(f"[cache miss] Выполняется операция для '{key}'...")
        value = value_func()
        cache[key] = value
        return value

    return cache_result