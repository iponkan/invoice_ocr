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
PP_STRUCTURE_KWARGS = {
    "device": OCR_DEVICE,
    "use_doc_orientation_classify": False,
    "use_doc_unwarping": False,
    "use_textline_orientation": True,
}


PROJECT_ROOT = Path(__file__).resolve().parent
