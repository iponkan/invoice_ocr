from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from config import DEFAULT_EXCEL_NAME, EXCEL_COLUMNS
from excel_writer import write_excel
from ocr_engine import OCREngine
from parser import parse_invoice_text
from utils import find_pdf_files, safe_stem

ProgressCallback = Callable[[int, int, str], None]


@dataclass
class BatchResult:
    output_path: Path
    total: int
    success: int
    failed: int
    records: list[dict[str, str]]


class BatchProcessor:
    def __init__(self, ocr_engine: OCREngine | None = None) -> None:
        self.ocr_engine = ocr_engine or OCREngine()

    def process_folder(
        self,
        folder: str | Path,
        output_path: str | Path | None = None,
        progress_callback: ProgressCallback | None = None,
    ) -> BatchResult:
        input_folder = Path(folder)
        pdf_files = find_pdf_files(input_folder)
        if not pdf_files:
            raise ValueError("选择的文件夹中没有PDF文件")

        excel_path = Path(output_path) if output_path else input_folder / DEFAULT_EXCEL_NAME
        records: list[dict[str, str]] = []
        success = 0
        failed = 0
        total = len(pdf_files)

        for index, pdf_path in enumerate(pdf_files, start=1):
            if progress_callback:
                progress_callback(index - 1, total, f"正在识别: {pdf_path.name}")
            try:
                text = self.ocr_engine.extract_text(pdf_path)
                record = parse_invoice_text(text, pdf_path)
                record["处理状态"] = "成功"
                record["错误信息"] = ""
                success += 1
            except Exception as exc:
                record = _empty_record(pdf_path)
                record["处理状态"] = "失败"
                record["错误信息"] = str(exc)
                failed += 1
            records.append(record)
            if progress_callback:
                progress_callback(index, total, f"完成: {pdf_path.name}")

        write_excel(records, excel_path)
        if progress_callback:
            progress_callback(total, total, f"Excel已生成: {excel_path}")

        return BatchResult(
            output_path=excel_path,
            total=total,
            success=success,
            failed=failed,
            records=records,
        )


def _empty_record(pdf_path: Path) -> dict[str, str]:
    record = {column: "" for column in EXCEL_COLUMNS}
    record["名称"] = safe_stem(pdf_path)
    return record
