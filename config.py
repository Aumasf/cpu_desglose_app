import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
OUTPUT_DIR = os.path.join(BASE_DIR, "static", "output")

TEMPLATE_PDF_PATH = os.path.join(BASE_DIR, "static", "template_desglose.pdf")
DEFAULT_LOGO_PATH = os.path.join(BASE_DIR, "static", "default_logo.png")

# Coordenadas (en puntos PDF) – AJUSTÁ SOLO ESTO para ubicar texto/logo
# 1 punto = 1/72 inch
# A4: 595 x 842 aprox. (portrait)
LOGO_X = 430
LOGO_Y = 760
LOGO_W = 140
LOGO_H = 55

# Posición de la descripción (tercera fila, a la derecha del N° ítem)
DESC_X = 220
DESC_Y = 775
DESC_MAX_WIDTH = 330  # ancho para "wrap"
DESC_FONT_SIZE = 8    # más chico para que se lea
DESC_LEADING = 9

# Fuente: NO usamos calibri.ttf (archivo externo).
# ReportLab NO trae Calibri por defecto. Si querés Calibri, necesitás el TTF.
# Aquí dejamos Helvetica para evitar errores.
FONT_NAME = "Helvetica"

# Encabezados aceptados (normalizados sin acentos)
HEADER_CANDIDATES = [
    "descripcion",
    "descripciones",
    "descripcion del bien",
    "descripcion del item",
    "descripcion del ítem",  # igual normaliza
]