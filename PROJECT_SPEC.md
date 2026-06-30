# 🧾 票据OCR批处理工具（单机版 - uv管理）

## 🎯 项目目标

开发一个轻量级本地工具，用于批量识别中国电子票据 PDF，并导出 Excel 文件。

使用对象：非技术人员（家人使用）
运行方式：Windows exe（由Python打包）
开发环境：Ubuntu + uv

---

# ⚙️ 技术栈

- Python 3.10+
- uv（依赖管理）
- PP-StructureV3
- pandas + openpyxl
- PySide6（GUI）
- PyInstaller（打包）

---

# 📥 输入输出

## 输入

- PDF文件夹（批量处理）

## 输出

- Excel文件：result.xlsx

---

# 📊 需要提取字段

从票据中提取：

| 字段     | 来源                      |
| -------- | ------------------------- |
| 名称     | 文件名                    |
| 交款人   | “交款人”字段              |
| 项目名称 | “项目名称”                |
| 金额     | 小写金额（如 90.00）      |
| 申请号   | 数字编号（如 0010925600） |
| 缴费日期 | 开票日期                  |

---

# 🧠 OCR方案

优先使用：

## 🥇 PP-StructureV3（推荐）

用于结构化票据识别

---

# 📂 项目结构（必须遵守）

```text
invoice_ocr/
├── PROJECT_SPEC.md     # 项目说明
├── pyproject.toml      # uv项目配置
├── uv.lock             # uv锁定文件
├── main.py             # GUI入口
├── gui.py              # 界面逻辑
├── ocr_engine.py       # OCR封装
├── parser.py           # 字段解析规则
├── batch_processor.py  # 批量PDF处理
├── excel_writer.py     # Excel导出
├── config.py           # 配置
├── utils.py            # 工具函数
└── README.md           # 运行说明
```

---

# 🔄 处理流程

```text
选择文件夹
    ↓
遍历PDF
    ↓
PP-StructureV3直接识别PDF
    ↓
文本解析（regex）
    ↓
结构化数据
    ↓
写入Excel
```

---

# 🧩 字段解析规则（重要）

必须使用“宽松匹配”，避免OCR误差：

### 交款人

```regex
交款人[:：]?\s*(.+)
```

### 项目名称

```regex
项目名称\s*(.+)
```

### 金额

```regex
小写\s*([0-9.]+)
```

### 日期

```regex
开票日期[:：]?\s*([0-9-]+)
```

### 申请号

```regex
\d{8,12}
```

---

# 🖥 GUI要求（简洁即可）

必须包含：

- 选择文件夹按钮
- 开始处理按钮
- 处理进度提示（可选）
- 结果输出提示（Excel路径）

不需要复杂UI设计

---

# 📦 uv环境要求

必须使用 uv：

```bash
cd invoice_ocr
uv sync
uv run python main.py
```

---

# 📦 打包要求

使用 PyInstaller：

```bash
pyinstaller -F -w main.py
```

---

# ❗ 非目标（禁止实现）

- ❌ API服务
- ❌ Docker
- ❌ 数据库
- ❌ Web系统
- ❌ 复杂UI设计
- ❌ 云端处理

---

# 🚀 目标原则

- 简单
- 可运行
- 稳定
- 易打包
- 面向非技术用户

---