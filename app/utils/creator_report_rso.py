"""
Рассчитывает просроченную задолженность на конец периода
Выполняет агрегацию по РСО
Создаёт отчёт по РСО
Выгружает в формат json
"""
import pandas as pd
from app.utils.file_loader import ExcelLoader
from app.utils.file_exporter import JsonExporter


class OverdueCalculator:
    """
        Рассчитывает просроченную задолженность на конец периода по формуле:
        max(0, Дебиторская_на_конец - Кредиторская_на_конец - Начислено_за_период)
        Предполагаются следующие названия столбцов:
        - 'Дебиторская задолженность на конец периода'
        - 'Кредиторская задолженность на конец периода'
        - 'Начислено за период'
    """
    @staticmethod
    def calculate(df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        required_cols = [
            "Дебиторская задолженность на конец периода",
            "Кредиторская задолженность на конец периода",
            "Начислено за период"
        ]

        for col in required_cols:
            if col not in required_cols:
                raise KeyError(f"Отсутствует обязательный столбец: '{col}'")
            # Заменяем неразрывные пробелы на обычные и конвертируем в float
            df[col] = (
                df[col].astype(str)
                .str.replace("\xa0", " ", regex=False)
                .str.replace(" ", "", regex=False)
                .replace("", "0")
                .astype(float)
            )
        overdue = df[required_cols[0]] - df[required_cols[1]] - df[required_cols[2]]
        df["Просроченная задолженность на конец периода"] = overdue.clip(lower=0)
        return df


class RSOAggregator:
    """Выполняет агрегацию по РСО"""
    @staticmethod
    def aggregate(df: pd.DataFrame) -> dict[str, float]:
        if "РСО" not in df.columns or "Просроченная задолженность на конец периода" not in df.columns:
            raise ValueError("Требуемые столбцы отсутствуют")
        return (
            df.groupby("РСО")["Просроченная задолженность на конец периода"]
            .sum()
            .round(2)
            .to_dict()
        )


class DebtReport:
    """Создаёт отчёт по РСО и выгружает в формат json"""
    def __init__(
        self,
        input_file: str,
        sheet_name: str,
    ):
        self.input_file = input_file
        self.sheet_name = sheet_name

    def generate(self) -> dict[str, float]:
        # 1. Загрузка
        loader = ExcelLoader(self.input_file)
        df = loader.load_data(self.sheet_name)

        # 2. Расчёт
        df_with_overdue = OverdueCalculator.calculate(df)

        # 3. Агрегация
        result = RSOAggregator.aggregate(df_with_overdue)

        return result


if __name__ == "__main__":
    report = DebtReport(
        input_file="309b91f2-5157-4310-be57-56c220857515.xlsx",
        sheet_name="data",
    )
    result = report.generate()
    jsonfile = JsonExporter("_test_overdue_by_rso")
    jsonfile_path = jsonfile.export_data(result)
    print({"сохранено в": jsonfile_path, "report": result})
