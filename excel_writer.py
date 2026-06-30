from __future__ import annotations

from pathlib import Path

import pandas as pd
from openpyxl import load_workbook

from config import EXCEL_COLUMNS


def write_excel(records: list[dict[str, str]], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    df = pd.DataFrame(records)
    for column in EXCEL_COLUMNS:
        if column not in df.columns:
            df[column] = ""
    df = df[EXCEL_COLUMNS]
    df.to_excel(path, index=False, engine="openpyxl")
    _adjust_column_width(path)
    return path


def _adjust_column_width(path: Path) -> None:
    workbook = load_workbook(path)
    sheet = workbook.active
    for column_cells in sheet.columns:
        max_length = 0
        column_letter = column_cells[0].column_letter
        for cell in column_cells:
            value = "" if cell.value is None else str(cell.value)
            max_length = max(max_length, len(value))
        sheet.column_dimensions[column_letter].width = min(max(max_length + 2, 10), 40)
    workbook.save(path)
