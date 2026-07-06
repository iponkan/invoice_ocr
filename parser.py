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

TABLE_HEADER_LABELS = {
    "项目编码",
    "项目名称",
    "单位",
    "数量",
    "标准",
    "金额",
    "金额（元）",
    "备注",
}


def parse_invoice_text(text: str, pdf_path: str | Path) -> dict[str, str]:
    normalized = normalize_spaces(text or "")
    data = {
        "名称": safe_stem(pdf_path),
        "交款人": _extract_payer(normalized),
        "项目名称": _extract_project_name(normalized),
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


def _extract_payer(text: str) -> str:
    lines = _clean_lines(text)
    for index, line in enumerate(lines):
        compact = re.sub(r"\s+", "", line)
        if not re.match(r"^(交款人|缴款人)", compact):
            continue
        if "统一社会信用代码" in compact:
            continue

        value = re.sub(r"^(交\s*款\s*人|缴\s*款\s*人)\s*[:：]?", "", line).strip()
        if _is_valid_payer(value):
            return _clean_value(value)

        candidates = [_clean_value(item) for item in lines[index + 1 :] if _is_valid_payer(item)]
        if candidates:
            return max(candidates, key=_payer_score)

    return _extract_text_value(
        text,
        [
            r"交\s*款\s*人\s*[:：]\s*([^\n\r]+)",
            r"缴\s*款\s*人\s*[:：]\s*([^\n\r]+)",
        ],
    )


def _extract_project_name(text: str) -> str:
    lines = _clean_lines(text)

    match = re.search(r"收费\s*项\s*目\s*[:：]?\s*([^\n\r]+)", text)
    if match:
        value = _clean_project_name(match.group(1))
        if value:
            return value

    for index, line in enumerate(lines):
        if re.sub(r"\s+", "", line) != "项目名称":
            continue
        for next_line in lines[index + 1 :]:
            value = _clean_project_name(next_line)
            if value:
                return value

    for line in lines:
        if re.match(r"^\d{6,}\s+\S+", line):
            value = _clean_project_name(line)
            if value:
                return value

    for line in lines:
        value = _clean_project_name(line)
        if value and re.search(r"费|专利|服务|税|款|证书|登记", value):
            return value

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
    amounts = re.findall(r"(?<!\d)([0-9]+\.[0-9]{2})(?!\d)", text)
    if amounts:
        return _format_amount(amounts[-1])
    return ""


def _extract_application_no(text: str) -> str:
    label_patterns = [
        r"申\s*请\s*号\s*[:：]?\s*(\d{8,20})",
        r"申\s*请\s*编\s*号\s*[:：]?\s*(\d{8,20})",
        r"业\s*务\s*号\s*[:：]?\s*(\d{8,20})",
    ]
    compact = re.sub(r"\s+", "", text)
    for pattern in label_patterns:
        match = re.search(pattern, compact)
        if match:
            return match.group(1)

    match = re.search(r"(?<!\d)(\d{8,20})(?!\d)", compact)
    return match.group(1) if match else ""


def _extract_date(text: str) -> str:
    patterns = [
        r"缴\s*费\s*日\s*期\s*[:：]?\s*([0-9]{4}[年\-./][0-9]{1,2}[月\-./][0-9]{1,2}日?)",
        r"开\s*票\s*日\s*期\s*[:：]?\s*([0-9]{4}[年\-./][0-9]{1,2}[月\-./][0-9]{1,2}日?)",
        r"日\s*期\s*[:：]?\s*([0-9]{4}[年\-./][0-9]{1,2}[月\-./][0-9]{1,2}日?)",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return _normalize_date(match.group(1))
    return ""


def _clean_lines(text: str) -> list[str]:
    return [clean_cell_text(line) for line in text.splitlines() if clean_cell_text(line)]


def _is_field_boundary(value: str) -> bool:
    compact = re.sub(r"\s+", "", value)
    return any(label in compact for label in FIELD_LABELS)


def _is_valid_payer(value: str) -> bool:
    value = clean_cell_text(value)
    if not value:
        return False
    compact = re.sub(r"\s+", "", value)
    if "统一社会信用代码" in compact or re.fullmatch(r"[0-9A-Z]{12,25}", compact):
        return False
    if _is_field_boundary(value):
        return False
    if compact in TABLE_HEADER_LABELS:
        return False
    if re.fullmatch(r"[0-9.\-年月日]+", compact):
        return False
    if any(
        label in compact
        for label in (
            "财政部监制",
            "票据号码",
            "票据代码",
            "校验码",
            "收款单位",
            "复核人",
            "收款人",
            "金额合计",
            "其他信息",
        )
    ):
        return False
    return len(compact) >= 4


def _payer_score(value: str) -> int:
    compact = re.sub(r"\s+", "", value)
    score = len(compact)
    if "有限公司" in compact:
        score += 40
    elif "公司" in compact:
        score += 30
    for keyword in ("研究院", "学院", "学校", "医院", "中心", "事务所"):
        if keyword in compact:
            score += 20
    return score


def _clean_project_name(value: str) -> str:
    value = clean_cell_text(value)
    if not value:
        return ""
    compact = re.sub(r"\s+", "", value)
    if compact in TABLE_HEADER_LABELS:
        return ""
    if re.fullmatch(r"[0-9.]+", compact):
        return ""
    if compact in {"元", "合计", "其他信息"}:
        return ""
    if "票据" in compact:
        return ""
    if "金额合计" in compact or "小写" in compact or "申请号" in compact:
        return ""

    value = re.sub(r"^\d{6,}\s*", "", value)
    value = re.sub(r"\s+元\s+[0-9,.]+(?:\s+[0-9,.]+)*$", "", value)
    return _clean_value(value)


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
