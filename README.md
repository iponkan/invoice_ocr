# 票据 PDF 批处理工具

本工具用于本地批量读取带文字层的中国电子票据 PDF，并导出 Excel。

## 安装与运行

```bash
cd invoice_ocr
uv sync
uv run python main.py
```

程序会直接读取 PDF 内置文字层，不再内置 OCR 模型。扫描图片版 PDF 无法处理，需要先转成带文字层的 PDF。

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
