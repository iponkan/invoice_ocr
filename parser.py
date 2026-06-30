from __future__ import annotations

import re
from pathlib import Path

from utils import clean_cell_text, normalize_spaces, safe_stem

FIELD_LABELS = [
    "交款人",
    "项目名称",
    "小写",
    "金额",
    "申请号",
    "缴费日期",
    "开票日期",
]


def parse_invoice_text(text: str, pdf_path: str | Path) -> dict[str, str]:
    normalized = normalize_spaces(text or "")
    data = {
        "名称": safe_stem(pdf_path),
        "交款人": _extract_text_value(
            normalized,
            [
                r"交\s*款\s*人\s*[:：]?\s*([^\n\r]+)",
                r"缴\s*款\s*人\s*[:：]?\s*([^\n\r]+)",
            ],
        ),
        "项目名称": _extract_text_value(
            normalized,
            [
                r"项\s*目\s*名\s*称\s*[:：]?\s*([^\n\r]+)",
                r"收费\s*项\s*目\s*[:：]?\s*([^\n\r]+)",
            ],
        ),
        "金额": _extract_amount(normalized),
        "申请号": _extract_application_no(normalized),
        "缴费日期": _extract_date(normalized),
    }
    return data


def _extract_text_value(text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _clean_value(match.group(1))
    return ""


def _extract_amount(text: str) -> str:
    patterns = [
        r"小\s*写\s*[:：]?\s*(?:人民币)?\s*[¥￥]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"\(小\s*写\)\s*(?:人民币)?\s*[¥￥]?\s*([0-9]+(?:\.[0-9]{1,2})?)",
        r"[¥￥]\s*([0-9]+(?:\.[0-9]{1,2})?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            return _format_amount(match.group(1))
    return ""


def _extract_application_no(text: str) -> str:
    label_patterns = [
        r"申\s*请\s*号\s*[:：]?\s*(\d{8,12})",
        r"申\s*请\s*编\s*号\s*[:：]?\s*(\d{8,12})",
        r"业\s*务\s*号\s*[:：]?\s*(\d{8,12})",
    ]
    compact = re.sub(r"\s+", "", text)
    for pattern in label_patterns:
        match = re.search(pattern, compact)
        if match:
            return match.group(1)

    match = re.search(r"(?<!\d)(\d{8,12})(?!\d)", compact)
    return match.group(1) if match else ""


def _extract_date(text: str) -> str:
    patterns = [
        r"开\s*票\s*日\s*期\s*[:：]?\s*([0-9]{4}[年\-./][0-9]{1,2}[月\-./][0-9]{1,2}日?)",
        r"缴\s*费\s*日\s*期\s*[:：]?\s*([0-9]{4}[年\-./][0-9]{1,2}[月\-./][0-9]{1,2}日?)",
        r"日\s*期\s*[:：]?\s*([0-9]{4}[年\-./][0-9]{1,2}[月\-./][0-9]{1,2}日?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return _normalize_date(match.group(1))
    return ""


def _clean_value(value: str) -> str:
    value = clean_cell_text(value)
    for label in FIELD_LABELS:
        index = value.find(label)
        if index > 0:
            value = value[:index]
    value = re.sub(r"\s{2,}", " ", value)
    return clean_cell_text(value)


def _format_amount(value: str) -> str:
    try:
        return f"{float(value):.2f}"
    except ValueError:
        return value


def _normalize_date(value: str) -> str:
    value = value.strip().replace("年", "-").replace("月", "-").replace("日", "")
    value = value.replace("/", "-").replace(".", "-")
    parts = [part for part in value.split("-") if part]
    if len(parts) != 3:
        return value
    year, month, day = parts
    return f"{int(year):04d}-{int(month):02d}-{int(day):02d}"
