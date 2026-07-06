import sys
from pathlib import Path

APP_NAME = "票据OCR批处理工具"
DEFAULT_EXCEL_NAME = "result.xlsx"
SUPPORTED_PDF_SUFFIXES = {".pdf"}

EXCEL_COLUMNS = [
    "名称",
    "交款人",
    "项目名称",
    "金额",
    "申请号",
    "缴费日期",
    "处理状态",
    "错误信息",
]

OCR_DEVICE = "cpu"
RUNTIME_ROOT = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
BUNDLED_MODEL_ROOT = RUNTIME_ROOT / "models"
OCR_KWARGS = {
    "device": OCR_DEVICE,
    "lang": "ch",
    "enable_mkldnn": False,
    "enable_hpi": False,
    "enable_cinn": False,
    "use_doc_orientation_classify": False,
    "use_doc_unwarping": False,
    "use_textline_orientation": False,
}

if BUNDLED_MODEL_ROOT.exists():
    OCR_KWARGS.update(
        {
            "text_detection_model_dir": str(BUNDLED_MODEL_ROOT / "PP-OCRv6_medium_det"),
            "text_recognition_model_dir": str(BUNDLED_MODEL_ROOT / "PP-OCRv6_medium_rec"),
        }
    )


PROJECT_ROOT = Path(__file__).resolve().parent
