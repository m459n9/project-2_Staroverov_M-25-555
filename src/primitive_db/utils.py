import json
from pathlib import Path

from .constants import DATA_DIR


def load_metadata(filepath: str) -> dict:
    """Загружает метаданные из JSON-файла. Если файла нет — возвращает {}."""
    try:
        with open(filepath, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

def save_metadata(filepath: str, data: dict) -> None:
    """Сохраняет метаданные в JSON-файл."""
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)

def load_table_data(table_name: str) -> list[dict]:
    """Загружает данные таблицы из data/<table_name>.json."""
    path = Path(DATA_DIR) / f"{table_name}.json"
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)

def save_table_data(table_name: str, data: list[dict]) -> None:
    """Сохраняет данные таблицы в data/<table_name>.json."""
    path = Path(DATA_DIR)
    path.mkdir(exist_ok=True)
    with (path / f"{table_name}.json").open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)