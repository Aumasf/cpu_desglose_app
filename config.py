from __future__ import annotations

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
SERVICES_DIR = BASE_DIR / "services"
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"
TMP_DIR = BASE_DIR / "tmp"

# Asegurar carpetas
DATA_DIR.mkdir(exist_ok=True)
STATIC_DIR.mkdir(exist_ok=True)
TMP_DIR.mkdir(exist_ok=True)

# Archivos esperados
MATCH_XLSX_PATH = DATA_DIR / "match.xlsx"  # (no lo usamos en este modo prueba)
DEFAULT_LOGO_PATH = STATIC_DIR / "default_logo.png"
TEMPLATE_PDF_PATH = STATIC_DIR / "template_desglose.pdf"

load_dotenv()

APP_PASSWORD = os.getenv("APP_PASSWORD", "")
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")

if not APP_PASSWORD:
    # No rompemos el arranque, pero avisamos en consola.
    print("⚠️ APP_PASSWORD no está definido en .env (o no se cargó).")