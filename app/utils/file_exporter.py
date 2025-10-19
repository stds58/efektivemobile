"""
Сохраняет данные в файл
"""

import os
import json
from datetime import datetime
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class FileExporter(ABC):
    def __init__(self, file_name: str):
        self.project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        self.file_path = os.path.join(self.project_root, "data")
        self.file_name = file_name

    def _generate_filename(self, extension: str) -> str:
        """Генерирует имя файла с меткой времени."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_base = "".join(
            c if c.isalnum() or c in "._-" else "_" for c in self.file_name
        )
        return os.path.join(self.file_path, f"{safe_base}_{timestamp}{extension}")

    @abstractmethod
    def export_data(self) -> Path:
        pass


class JsonExporter(FileExporter):
    """Экспортирует данные в формате json"""

    def export_data(self, data: Any) -> Path:
        filepath = self._generate_filename(".json")
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        return filepath


class TextExporter(FileExporter):
    """Экспортирует данные в текстовом формате (str или repr)."""

    def export_data(self, data: Any) -> Path:
        filepath = self._generate_filename(".txt")
        content = data if isinstance(data, str) else repr(data)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return filepath


if __name__ == "__main__":
    data = {"name": "product", "quantity": 56546}
    jsonfile = JsonExporter("_test_exporter_file")
    jsonfile_path = jsonfile.export_data(data)
    print(jsonfile_path)
    textfile = TextExporter("_test_exporter_file")
    textfile_path = textfile.export_data(data)
    print(textfile_path)
