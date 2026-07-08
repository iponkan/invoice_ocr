# -*- mode: python ; coding: utf-8 -*-

excluded_modules = [
    "datasets",
    "einops",
    "fastdeploy",
    "gradio",
    "hf_xet",
    "huggingface_hub",
    "chardet",
    "charset_normalizer",
    "lxml",
    "matplotlib",
    "numpy",
    "notebook",
    "paddle",
    "paddleocr",
    "paddlex",
    "pandas",
    "PIL",
    "psutil",
    "scipy",
    "sklearn",
    "tensorboard",
    "tiktoken",
    "tokenizers",
    "torch",
    "torchvision",
    "transformers",
]


a = Analysis(
    ["main.py"],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=["pypdfium2"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excluded_modules,
    noarchive=False,
    optimize=2,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="InvoiceOCR",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="InvoiceOCR",
)
