# 票据 OCR 批处理工具

本工具用于本地批量识别中国电子票据 PDF，并导出 Excel。

## 安装与运行

```bash
cd invoice_ocr
uv sync
uv run python main.py
```

程序会直接把 PDF 文件交给 PP-StructureV3 识别，PP-StructureV3 会按页处理 PDF。首次运行时会下载模型文件，耗时较长。模型缓存完成后，后续运行会快一些。

## 打包

```bash
uv run pyinstaller -y InvoiceOCR.spec
```

Windows 上打包结果在 `dist/InvoiceOCR/InvoiceOCR.exe`。Linux 上打包会生成 Linux 可执行文件，不能改名成 `.exe` 给 Windows 使用。

## 输出字段

- 名称
- 交款人
- 项目名称
- 金额
- 申请号
- 缴费日期
- 处理状态
- 错误信息
