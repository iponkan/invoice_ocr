from __future__ import annotations

from datetime import datetime
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

    last_error: PermissionError | None = None
    for candidate in _output_candidates(path):
        try:
            df.to_excel(candidate, index=False, engine="openpyxl")
            _adjust_column_width(candidate)
            return candidate
        except PermissionError as exc:
            last_error = exc

    raise PermissionError(
        f"无法写入Excel文件，可能文件正在被打开: {path}"
    ) from last_error


def _output_candidates(path: Path) -> list[Path]:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return [
        path,
        path.with_name(f"{path.stem}_{timestamp}{path.suffix}"),
        path.with_name(f"{path.stem}_{timestamp}_2{path.suffix}"),
    ]


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
