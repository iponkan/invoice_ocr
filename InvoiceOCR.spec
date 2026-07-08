# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

excluded_modules = [
    "datasets",
    "einops",
    "fastdeploy",
    "gradio",
    "hf_xet",
    "huggingface_hub",
    "matplotlib",
    "notebook",
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
    datas=[
        (
            r"C:\Users\can\.paddlex\official_models\PP-OCRv6_medium_det",
            r"models\PP-OCRv6_medium_det",
        ),
        (
            r"C:\Users\can\.paddlex\official_models\PP-OCRv6_medium_rec",
            r"models\PP-OCRv6_medium_rec",
        ),
    ],
    hiddenimports=(
        collect_submodules("paddleocr")
        + collect_submodules("pypdfium2")
    ),
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
