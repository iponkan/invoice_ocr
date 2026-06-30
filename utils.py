from __future__ import annotations

import re
from pathlib import Path

from config import SUPPORTED_PDF_SUFFIXES


def find_pdf_files(folder: str | Path) -> list[Path]:
    root = Path(folder)
    if not root.exists() or not root.is_dir():
        raise ValueError(f"输入目录不存在: {root}")
    pdfs = [
        path
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SUPPORTED_PDF_SUFFIXES
    ]
    return sorted(pdfs, key=lambda item: str(item).lower())


def normalize_spaces(text: str) -> str:
    text = text.replace("\u3000", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def clean_cell_text(value: str) -> str:
    value = value.replace("|", " ")
    value = value.replace("：", ":")
    value = re.sub(r"^[\s:：,，;；\-]+", "", value)
    value = re.sub(r"[\s,，;；]+$", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip()


def safe_stem(path: str | Path) -> str:
    return Path(path).stem.strip()
