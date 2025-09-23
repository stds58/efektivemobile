#!/usr/bin/env python3
"""
tree.py - выводит дерево проекта, исключая мусорные директории и файлы
python app/utils/tree.py .
"""
import sys
from pathlib import Path


# Список игнорируемых элементов
IGNORE_LIST = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    ".env",
    ".env.local",
    ".env.prod",
    ".DS_Store",
    ".pytest_cache",
    ".mypy_cache",
    ".vscode",
    ".idea",
    "*.pyc",
    "*.log",
    "*.tmp",
    "Thumbs.db",
    "__init__.py",
    "tree.py",
}


def should_ignore(name: str) -> bool:
    """Проверяет, нужно ли игнорировать файл/папку по имени."""
    return any(
        name == pattern or (pattern.startswith("*.") and name.endswith(pattern[1:]))
        for pattern in IGNORE_LIST
    )


def tree(dir_path: Path, prefix: str = ""):
    """Рекурсивно выводит структуру директории."""
    # Получаем содержимое, фильтруем игнорируемые элементы
    try:
        contents = sorted(
            [p for p in dir_path.iterdir() if not should_ignore(p.name)],
            key=lambda p: (p.is_file(), p.name.lower())
        )
    except PermissionError:
        print(prefix + "└── [не доступно]")
        return

    pointers = ["├── "] * (len(contents) - 1) + ["└── "]

    for pointer, path in zip(pointers, contents):
        print(prefix + pointer + path.name)
        if path.is_dir():
            extension = "│   " if pointer == "├── " else "    "
            tree(path, prefix + extension)


def print_python_files_content(root_path: Path, current_path: Path = None):
    """
    Рекурсивно печатает относительный путь и содержимое всех .py файлов.
    """
    if current_path is None:
        current_path = root_path

    try:
        for item in current_path.iterdir():
            if should_ignore(item.name):
                continue

            if item.is_dir():
                print_python_files_content(root_path, item)
            elif item.is_file() and item.suffix == ".py":
                # Относительный путь от корня
                rel_path = item.relative_to(root_path)
                print(f"\n{'='*80}")
                print(f"{rel_path}")
                print(f"{'='*80}")
                try:
                    with open(item, "r", encoding="utf-8") as f:
                        content = f.read()
                        # Выводим содержимое с отступом для читаемости
                        for line in content.splitlines():
                            print(f"    {line}")
                except Exception as e:
                    print(f"    [Ошибка чтения файла: {e}]")
    except PermissionError:
        print(f"[Нет доступа к директории: {current_path}]")


if __name__ == "__main__":
    root_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")

    if not root_path.exists():
        print(f"Ошибка: путь '{root_path}' не существует.")
        sys.exit(1)

    print("СТРУКТУРА ПРОЕКТА:")
    print(root_path.name + "/")
    tree(root_path)

    print("\n\n" + "="*100)
    print("СОДЕРЖИМОЕ ВСЕХ .PY ФАЙЛОВ:")
    print("="*100)

    print_python_files_content(root_path)
