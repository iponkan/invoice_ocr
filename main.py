import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from gui import MainWindow


def main() -> int:
    if len(sys.argv) >= 3 and sys.argv[1] == "--self-test":
        from ocr_engine import OCREngine
        from parser import parse_invoice_text

        pdf_path = Path(sys.argv[2])
        output_path = Path(sys.argv[3]) if len(sys.argv) >= 4 else None
        text = OCREngine().extract_text(pdf_path)
        result = parse_invoice_text(text, pdf_path)
        if output_path:
            output_path.write_text(str(result), encoding="utf-8")
        return 0

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
