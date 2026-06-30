from __future__ import annotations

import os
from collections.abc import Iterable
from pathlib import Path
from typing import Any

from config import OCR_KWARGS
from utils import normalize_spaces


def _configure_paddle_runtime() -> None:
    os.environ.setdefault("FLAGS_use_mkldnn", "0")
    os.environ.setdefault("FLAGS_enable_onednn", "0")


class OCREngine:
    def __init__(self) -> None:
        self._pipeline: Any | None = None

    def extract_text(self, pdf_path: str | Path) -> str:
        path = Path(pdf_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF文件不存在: {path}")
        if path.suffix.lower() != ".pdf":
            raise ValueError(f"不是PDF文件: {path}")

        pipeline = self._get_pipeline()
        output = pipeline.predict(input=str(path))
        markdown_pages: list[dict[str, Any]] = []
        text_chunks: list[str] = []

        for result in output:
            markdown = getattr(result, "markdown", None)
            if isinstance(markdown, dict):
                markdown_pages.append(markdown)
            elif isinstance(markdown, str):
                text_chunks.append(markdown)
            text_chunks.extend(_extract_text_chunks(result))

        if markdown_pages:
            try:
                markdown_text = pipeline.concatenate_markdown_pages(markdown_pages)
                if isinstance(markdown_text, str):
                    text_chunks.insert(0, markdown_text)
                else:
                    text_chunks.extend(_extract_text_chunks(markdown_text))
            except Exception:
                text_chunks.extend(_extract_text_chunks(markdown_pages))

        return normalize_spaces("\n".join(_dedupe(text_chunks)))

    def _get_pipeline(self) -> Any:
        if self._pipeline is None:
            _configure_paddle_runtime()

            from paddleocr import PaddleOCR

            self._pipeline = PaddleOCR(**OCR_KWARGS)
        return self._pipeline


def _extract_text_chunks(value: Any) -> list[str]:
    chunks: list[str] = []
    _walk_result(value, chunks)
    return chunks


def _walk_result(value: Any, chunks: list[str]) -> None:
    if value is None:
        return
    if isinstance(value, str):
        if _looks_like_text(value):
            chunks.append(value)
        return
    if isinstance(value, bytes):
        return
    if isinstance(value, dict):
        for item in value.values():
            _walk_result(item, chunks)
        return

    for attr in ("json", "to_dict"):
        if hasattr(value, attr):
            try:
                obj = getattr(value, attr)
                obj = obj() if callable(obj) else obj
            except Exception:
                continue
            _walk_result(obj, chunks)
            return

    if isinstance(value, Iterable) and not isinstance(value, (str, bytes)):
        for item in value:
            _walk_result(item, chunks)
        return


def _looks_like_text(value: str) -> bool:
    value = value.strip()
    if not value:
        return False
    if value.startswith("data:image"):
        return False
    if len(value) > 5000 and "\n" not in value:
        return False
    return True


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
