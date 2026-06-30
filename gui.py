from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import QObject, QThread, Signal, Slot
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QProgressBar,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from batch_processor import BatchProcessor
from config import APP_NAME, DEFAULT_EXCEL_NAME


class BatchWorker(QObject):
    progress = Signal(int, int, str)
    finished = Signal(str, int, int, int)
    failed = Signal(str)

    def __init__(self, folder: str, output_path: str) -> None:
        super().__init__()
        self.folder = folder
        self.output_path = output_path

    @Slot()
    def run(self) -> None:
        try:
            processor = BatchProcessor()
            result = processor.process_folder(
                self.folder,
                self.output_path,
                progress_callback=self.progress.emit,
            )
            self.finished.emit(
                str(result.output_path),
                result.total,
                result.success,
                result.failed,
            )
        except Exception as exc:
            self.failed.emit(str(exc))


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(680, 360)
        self.thread: QThread | None = None
        self.worker: BatchWorker | None = None
        self._setup_ui()

    def _setup_ui(self) -> None:
        root = QWidget(self)
        layout = QVBoxLayout(root)

        folder_layout = QHBoxLayout()
        self.folder_edit = QLineEdit()
        self.folder_edit.setReadOnly(True)
        self.folder_edit.setPlaceholderText("请选择包含PDF票据的文件夹")
        self.select_button = QPushButton("选择文件夹")
        self.select_button.clicked.connect(self.select_folder)
        folder_layout.addWidget(self.folder_edit)
        folder_layout.addWidget(self.select_button)

        self.start_button = QPushButton("开始处理")
        self.start_button.clicked.connect(self.start_processing)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        self.status_label = QLabel("等待选择文件夹")
        self.log_edit = QPlainTextEdit()
        self.log_edit.setReadOnly(True)

        layout.addLayout(folder_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.progress_bar)
        layout.addWidget(self.status_label)
        layout.addWidget(self.log_edit)
        self.setCentralWidget(root)

    @Slot()
    def select_folder(self) -> None:
        folder = QFileDialog.getExistingDirectory(self, "选择PDF文件夹")
        if folder:
            self.folder_edit.setText(folder)
            self.status_label.setText("已选择文件夹")
            self.log_edit.appendPlainText(f"输入目录: {folder}")

    @Slot()
    def start_processing(self) -> None:
        folder = self.folder_edit.text().strip()
        if not folder:
            QMessageBox.warning(self, "提示", "请先选择PDF文件夹")
            return

        output_path = str(Path(folder) / DEFAULT_EXCEL_NAME)
        self._set_running(True)
        self.progress_bar.setValue(0)
        self.log_edit.appendPlainText("开始处理，首次加载模型可能需要几分钟...")

        self.thread = QThread(self)
        self.worker = BatchWorker(folder, output_path)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.progress.connect(self.on_progress)
        self.worker.finished.connect(self.on_finished)
        self.worker.failed.connect(self.on_failed)
        self.worker.finished.connect(self.thread.quit)
        self.worker.failed.connect(self.thread.quit)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    @Slot(int, int, str)
    def on_progress(self, current: int, total: int, message: str) -> None:
        percent = int(current / total * 100) if total else 0
        self.progress_bar.setValue(percent)
        self.status_label.setText(message)
        self.log_edit.appendPlainText(message)

    @Slot(str, int, int, int)
    def on_finished(self, output_path: str, total: int, success: int, failed: int) -> None:
        self._set_running(False)
        self.progress_bar.setValue(100)
        message = f"处理完成：共{total}个PDF，成功{success}个，失败{failed}个。\nExcel路径：{output_path}"
        self.status_label.setText("处理完成")
        self.log_edit.appendPlainText(message)
        QMessageBox.information(self, "完成", message)
        self.worker = None
        self.thread = None

    @Slot(str)
    def on_failed(self, error: str) -> None:
        self._set_running(False)
        self.status_label.setText("处理失败")
        self.log_edit.appendPlainText(f"处理失败: {error}")
        QMessageBox.critical(self, "错误", error)
        self.worker = None
        self.thread = None

    def _set_running(self, running: bool) -> None:
        self.select_button.setEnabled(not running)
        self.start_button.setEnabled(not running)
