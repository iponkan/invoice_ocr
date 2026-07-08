from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from utils import normalize_spaces

MIN_TEXT_LAYER_CHARS = 50
TEXT_LAYER_MARKERS = ("票据", "交款人", "项目名称", "金额", "申请号")


class OCREngine:
    def extract_text(self, pdf_path: str | Path) -> str:
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"不是PDF文件: {path}")

        text_layer = _extract_pdf_text_layer(path)
        if _has_usable_text_layer(text_layer):
            return text_layer

        raise ValueError("未读取到可用PDF文字层，请确认PDF不是扫描图片版")


def _extract_pdf_text_layer(pdf_path: Path) -> str:
    try:
        import pypdfium2 as pdfium
    except Exception:
        return ""

    chunks: list[str] = []
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        try:
            for page in pdf:
                textpage = page.get_textpage()
                try:
                    chunks.append(textpage.get_text_range())
                finally:
                    _close_pdfium_object(textpage)
                _close_pdfium_object(page)
        finally:
            _close_pdfium_object(pdf)
    except Exception:
        return ""

    return normalize_spaces("\n".join(_dedupe(chunks)))


def _has_usable_text_layer(text: str) -> bool:
    compact = re.sub(r"\s+", "", text)
    if len(compact) < MIN_TEXT_LAYER_CHARS:
        return False
    return sum(1 for marker in TEXT_LAYER_MARKERS if marker in compact) >= 2


def _close_pdfium_object(value: Any) -> None:
    close = getattr(value, "close", None)
    if callable(close):
        close()


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        normalized = normalize_spaces(str(value))
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        result.append(normalized)
    return result
